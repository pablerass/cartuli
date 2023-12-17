"""Definition file module."""
from __future__ import annotations

import logging
import yaml

from collections import defaultdict
from collections.abc import Callable
from glob import glob
from itertools import chain, groupby
from multiprocessing import Pool, cpu_count
from pathlib import Path
from PIL import Image
from typing import Iterable

from .card import CardImage, Card
from .deck import Deck
from .filters import Filter, NullFilter, from_dict as filter_from_dict
from .measure import Size, from_str as measure_from_str
from .sheet import Sheet
from .template import svg_file_to_image, from_dict as template_from_dict


_CONCURRENT_PROCESSES = cpu_count() - 1

CardsFilter = Callable[[Path], bool]


class DefinitionError(Exception):
    pass


# TUNE; Certain names should just not be written at certain hours
def _convert_dict_of_lists_to_list_of_dicts(dict_of_lists: dict) -> Iterable:
    list_of_dicts = []

    keys = list(dict_of_lists.keys())

    for item in range(len(dict_of_lists[keys[0]])):
        item_dict = {}
        for key in keys:
            item_dict |= {key: dict_of_lists[key][item]}
        list_of_dicts.append(item_dict)

    return list_of_dicts


def _load_image(image_file: str | Path) -> Image.Image:
    # TUNE: I am tired of writting this and probably image_file = Path(image_file) will do the trick
    if isinstance(image_file, str):
        image_file = Path(image_file)

    if image_file.suffix == '.svg':
        return svg_file_to_image(image_file)
    else:
        return Image.open(image_file)


class Definition:
    """Definition."""

    DEFAULT_CARTULIFILE = 'Cartulifile.yml'

    def __init__(self, values: dict, /, cards_filter: CardsFilter = None):
        self.__values = Definition._validate(values)
        self.__decks = None
        self.__sheets = None

        if cards_filter is None:
            cards_filter = lambda x: True   # noqa: E731
        self.__cards_filter = cards_filter

    @property
    def _values(self) -> dict:
        return self.__values

    @classmethod
    def from_file(cls, path: Path | str = 'Cartulifile.yml', /, cards_filter: CardsFilter = None) -> Definition:
        if isinstance(path, str):
            path = Path(path)
        if not isinstance(path, Path):
            raise TypeError(f"{type(path)} is not a valid path")

        if path.is_dir():
            path = path / cls.DEFAULT_CARTULIFILE

        with path.open(mode='r') as file:
            return cls(yaml.safe_load(file), cards_filter)

    def _validate(values: dict) -> dict:
        # TODO: Implement validation
        if values is None:
            raise ValueError("Expected a dictionary, None found")

        return values

    @property
    def decks(self) -> list[Deck]:
        # TUNE: This code is crap, should be refacored
        logger = logging.getLogger('cartuli.definition.Definition.decks')
        if self.__decks is None:
            self.__decks = []
            for name, deck_definition in self.__values.get('decks', {}).items():
                logger.debug(f"Deck '{name}' definition {deck_definition}")
                self.__decks.append(self._load_deck(deck_definition, name))
            if not self.__decks:
                logger.warning('No decks loaded in definition')

        return self.__decks

    def _load_template(self, template_definition: dict) -> tuple[list[Path], list[Image.Image]]:
        # TODO: Support text values
        template = template_from_dict(template_definition)
        parameter_values = {}
        template_files = []
        for parameter in template.parameters:
            # TODO: Could make sense to add filters in this step?
            image_files = sorted(glob(template_definition['parameters'][parameter]))
            parameter_values |= {
                parameter: [_load_image(image_file) for image_file in image_files]
            }
            if not template_files:
                template_files = image_files

        images = [
            template.create_image(parameters)
            for parameters in _convert_dict_of_lists_to_list_of_dicts(parameter_values)
        ]

        return image_files, images

    def _load_images(self, images_definition: dict, size: Size,
                     deck_name: str, side: str = 'front') -> list[CardImage]:
        logger = logging.getLogger('cartuli.definition.Definition.decks')

        image_filter = images_definition.get('filter', '')
        if 'images' in images_definition:
            image_files = sorted(glob(images_definition['images']))
            images = [_load_image(file) for file in image_files if self.__cards_filter(file)]
        elif 'template' in images_definition:
            image_files, images = self._load_template(images_definition['template'])
        logger.debug(f"Found {len(images)} {side} images for '{deck_name}' deck")
        with Pool(processes=_CONCURRENT_PROCESSES) as pool:
            card_images = pool.map(
                self.filters[image_filter].apply,
                (CardImage(
                    image, size=size,
                    bleed=measure_from_str(images_definition.get('bleed', str(CardImage.DEFAULT_BLEED))),
                    name=Path(file).stem
                ) for image, file in zip(images, image_files))
            )
        if len(image_files) != len(images):
            logger.debug(f"{side.capitalize()} images filterd from {len(image_files)} to "
                         f" {len(images)} for '{deck_name}' deck")

        return card_images

    def _load_deck(self, definition: dict, name: str) -> Deck:
        logger = logging.getLogger('cartuli.definition.Definition.decks')

        size = Size.from_str(definition['size'])
        cards = []

        if 'front' in definition:
            front_images = self._load_images(definition['front'], size, name, 'front')
            if 'back' in definition:
                back_images = self._load_images(definition['back'], size, name, 'back')
                if len(front_images) != len(back_images):
                    raise DefinitionError(f"The number of front ({len(front_images)}) and "
                                          f"back ({len(back_images)}) images must be the same")
                # TODO Allow all back images to be filtered without errors
                cards = [Card(front_image, back_image) for front_image, back_image in zip(front_images, back_images)]
            else:
                cards = [Card(image) for image in front_images]

        if not cards:
            logger.warning(f"No cards found for deck {name} with specified fiters")

        cards = cards * definition.get('copies', 1)

        default_back = None
        if 'default_back' in definition:
            if 'image' in definition['default_back']:
                default_back_file = definition['default_back']['image']
                default_back_image = _load_image(default_back_file)
            elif 'template' in definition['default_back']:
                default_back_file, default_back_image = self._load_template(definition['template'])

            if self.__cards_filter(default_back_file):
                default_back_filter = definition['default_back'].get('filter', '')
                default_back = self.filters[default_back_filter].apply(
                    CardImage(
                        default_back_image,
                        size=size,
                        bleed=measure_from_str(definition['default_back'].get('bleed', str(CardImage.DEFAULT_BLEED))),
                        name=Path(default_back_file).stem
                    )
                )
            else:
                logger.debug(f"Default back image '{default_back_file}' filtered for '{name}' deck")

        return Deck(cards, name=name, default_back=default_back, size=size)

    @property
    def sheets(self) -> dict[tuple[str], Sheet]:
        # TODO: Replace sheets with generic outputs
        if self.__sheets is None:
            self.__sheets = {}
            if 'sheet' in self.__values['outputs']:
                sheet_definition = self.__values['outputs']['sheet']
                if sheet_definition.get('share', True):
                    group_function = lambda x: x.size   # noqa: E731
                else:
                    group_function = lambda x: x.name   # noqa: E731
                groups = groupby(sorted(self.decks, key=group_function), key=group_function)
                for _, decks in groups:
                    decks = tuple(decks)  # itertools.groypby object can only be readed once
                    deck_names = tuple(deck.name for deck in decks)
                    cards = chain.from_iterable(deck.cards for deck in decks)
                    self.__sheets[deck_names] = Sheet(
                        cards,
                        size=Size.from_str(sheet_definition.get('size', str(Sheet.DEFAULT_SIZE))),
                        print_margin=measure_from_str(
                            sheet_definition.get('print_margin', str(Sheet.DEFAULT_PRINT_MARGIN))),
                        padding=measure_from_str(sheet_definition.get('padding', str(Sheet.DEFAULT_PADDING))),
                        crop_marks_padding=measure_from_str(
                            sheet_definition.get('crop_marks_padding', str(Sheet.DEFAULT_CROP_MARKS_PADDING)))
                    )

        return self.__sheets

    @property
    def filters(self) -> dict[str, Filter]:
        filters = defaultdict(NullFilter)

        for name, filter_definition in self._values.get('filters', {}).items():
            filters[name] = filter_from_dict(filter_definition)

        return filters
