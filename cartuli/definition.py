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

from .card import CardImage, Card
from .deck import Deck
from .filters import Filter, NullFilter, from_dict as filter_from_dict
from .measure import Size, from_str
from .sheet import Sheet


_CONCURRENT_PROCESSES = cpu_count() - 1

CardsFilter = Callable[[Path], bool]


class DefinitionError(Exception):
    pass


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

    def _load_images(self, images_definition: dict, size: Size, deck_name: str, side: str = 'front') -> list[CardImage]:
        logger = logging.getLogger('cartuli.definition.Definition.decks')

        image_filter = images_definition.get('filter', '')
        image_files = sorted(glob(images_definition['images']))
        logger.debug(f"Found {len(image_files)} {side} images for '{deck_name}' deck")
        with Pool(processes=_CONCURRENT_PROCESSES) as pool:
            images = pool.map(
                self.filters[image_filter].apply,
                (CardImage(
                    path, size=size,
                    bleed=from_str(images_definition.get('bleed', str(CardImage.DEFAULT_BLEED))),
                    name=Path(path).stem
                ) for path in image_files if self.__cards_filter(path))
            )
        if len(image_files) != len(images):
            logger.debug(f"{side.capitalize()} images filterd from {len(image_files)} to "
                         f" {len(images)} for '{deck_name}' deck")

        return images

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
            default_back_file = definition['default_back']['image']
            if self.__cards_filter(default_back_file):
                default_back_filter = definition['default_back'].get('filter', '')
                default_back = self.filters[default_back_filter].apply(
                    CardImage(
                        default_back_file,
                        size=size,
                        bleed=from_str(definition['default_back'].get('bleed', str(CardImage.DEFAULT_BLEED))),
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
                        print_margin=from_str(sheet_definition.get('print_margin',
                                                                   str(Sheet.DEFAULT_PRINT_MARGIN))),
                        padding=from_str(sheet_definition.get('padding', str(Sheet.DEFAULT_PADDING))),
                        crop_marks_padding=from_str(
                            sheet_definition.get('crop_marks_padding', str(Sheet.DEFAULT_CROP_MARKS_PADDING)))
                    )

        return self.__sheets

    @property
    def filters(self) -> dict[str, Filter]:
        filters = defaultdict(NullFilter)

        for name, filter_definition in self._values.get('filters', {}).items():
            filters[name] = filter_from_dict(filter_definition)

        return filters
