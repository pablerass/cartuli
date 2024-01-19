"""Definition file module."""
from __future__ import annotations

import logging
import yaml

from collections import defaultdict
from collections.abc import Callable
from copy import deepcopy
from glob import glob
from itertools import chain, groupby
from multiprocessing import Pool, cpu_count
from pathlib import Path
from PIL import Image
from typing import Iterable

from .card import CardImage, Card
from .deck import Deck
from .filters import Filter, NullFilter
from .measure import Size, from_str as measure_from_str
from .sheet import Sheet
from .template import svg_file_to_image, Template, ParameterKey, ParameterValue


_CONCURRENT_PROCESSES = cpu_count() - 1


FilesFilter = Callable[[Path], bool]


class DefinitionError(Exception):
    pass


def _load_image(image_file: str | Path) -> Image.Image:
    image_file = Path(image_file)

    if image_file.suffix == '.svg':
        image = svg_file_to_image(image_file)
        image.filename = image_file
        return image
    else:
        return Image.open(image_file)


def _load_text(text_file: str | Path) -> str:
    text_file = Path(text_file)

    if text_file.suffix == '.md':
        # TODO: Implement convert markdown to supported svg content
        pass

    return text_file.read_text()


# TODO: Implement load template parameters from yml or CSV file
class _TemplateParameters:
    EXTENSION_MAPPINGS = {
        tuple(Image.registered_extensions()): _load_image,
        tuple(['.txt', '.html', '.md']): _load_text
    }

    def __init__(self, parameters: Iterable[dict[ParameterKey, ParameterValue]]):
        self.__parameters = parameters

    @property
    def parameters(self) -> list[dict[ParameterKey, ParameterValue]]:
        return deepcopy(self.__parameters)

    @property
    def keys(self) -> list[ParameterKey]:
        return list(self.__parameters[0].keys())

    @staticmethod
    def _convert_dict_of_lists_to_list_of_dicts(dict_of_lists: dict) -> list:
        # TODO: Make this fail if the lenghts are different
        list_of_dicts = []

        keys = list(dict_of_lists.keys())

        for item in range(len(dict_of_lists[keys[0]])):
            item_dict = {}
            for key in keys:
                item_dict |= {key: dict_of_lists[key][item]}
            list_of_dicts.append(item_dict)

        return list_of_dicts

    @classmethod
    def _load_parameter_from_file(cls, parameter_file: str | Path) -> ParameterValue:
        file_extension = Path(parameter_file).suffix

        for extensions, function in cls.EXTENSION_MAPPINGS.items():
            if file_extension in extensions:
                return function(parameter_file)

        raise ValueError(f"Unmanageable extension for '{parameter_file}'")

    @classmethod
    def from_dict(cls, definition: dict | str) -> _TemplateParameters:
        if isinstance(definition, str):
            return  # TODO: Implement

        parameter_values = {}
        for parameter in definition.keys():
            files = sorted(glob(definition[parameter]))
            parameter_values |= {
                parameter: [cls._load_parameter_from_file(file) for file in files]
            }

        return cls(cls._convert_dict_of_lists_to_list_of_dicts(parameter_values))

    def create_images(self, template: Template, name_parameter: str = None) -> list[Image.Image]:
        images = []
        for parameters in self.__parameters:
            image = template.create_image(parameters)
            if name_parameter:
                if isinstance(parameters[name_parameter], Image.Image):
                    image.filename = parameters[name_parameter].filename
                else:
                    # TUNE: This does not work as expected for filters as this does not contains the file name
                    image.filename = parameters[name_parameter]
            images.append(image)

        return images


class Definition:
    """Definition."""

    DEFAULT_CARTULIFILE = 'Cartulifile.yml'

    def __init__(self, values: dict, /, files_filter: FilesFilter = None):
        self.__values = Definition._validate(values)
        self.__decks = None
        self.__sheets = None

        if files_filter is None:
            files_filter = lambda x: False   # noqa: E731
        self.__files_filter = files_filter

        self.__filters = None
        self.__template_parameters = None

    @property
    def _values(self) -> dict:
        return self.__values

    @classmethod
    def from_file(cls, path: Path | str = 'Cartulifile.yml', /, files_filter: FilesFilter = None) -> Definition:
        if isinstance(path, str):
            path = Path(path)

        if not isinstance(path, Path):
            raise TypeError(f"{type(path)} is not a valid path")

        if path.is_dir():
            path = path / cls.DEFAULT_CARTULIFILE

        with path.open(mode='r') as file:
            return cls(yaml.safe_load(file), files_filter)

    def _validate(values: dict) -> dict:
        # TODO: Implement validation
        if values is None:
            raise ValueError("Expected a dictionary, None found")

        return values

    def _load_images(self, definition: dict) -> list[Image.Image]:
        if 'image' in definition:
            return [_load_image(definition['image'])]
        elif 'images' in definition:
            return [_load_image(i) for i in sorted(glob(definition['images']))]
        elif 'template' in definition:
            return self._load_template_images(definition['template'])

        raise ValueError(f"Invalid image definition {definition}")

    def _load_template_parameters(self, definition: dict) -> _TemplateParameters:
        if isinstance(definition, str):
            definition = self._template_parameters[definition]

        return _TemplateParameters.from_dict(definition)

    def _load_template_images(self, definition: dict) -> list[Image.Image]:
        if 'parameters' not in definition:
            raise ValueError(f"Template definition must specify its parameters {definition}")

        template_parameters = self._load_template_parameters(definition['parameters'])

        if 'file' not in definition:
            raise ValueError(f"Template definition must specify its file {definition}")

        name_parameter = None
        if 'name_parameter' in definition:
            name_parameter = definition['name_parameter']

        template = Template.from_file(definition['file'], template_parameters.keys)

        return template_parameters.create_images(template, name_parameter)

    def _load_filter(self, definition: dict) -> Filter:
        if isinstance(definition, str):
            return self._filters[definition]

        return Filter.from_dict(definition)

    def _load_card_images(self, definition: dict, size: Size) -> list[CardImage]:
        logger = logging.getLogger('cartuli.definition.Definition._load_card_images')

        images = self._load_images(definition)
        filtered_images = [
            image for image in images if not self.__files_filter(str(image.filename))
        ]
        if len(images) != len(filtered_images):
            logger.debug(f"'{definition}' images filterd from {len(images)} to {len(filtered_images)}")

        image_filter = NullFilter()
        if 'filter' in definition:
            image_filter = self._load_filter(definition['filter'])

        with Pool(processes=_CONCURRENT_PROCESSES) as pool:
            card_images = pool.map(
                image_filter.apply,
                (CardImage(
                    image,
                    size=size,
                    bleed=measure_from_str(definition.get('bleed', str(CardImage.DEFAULT_BLEED))),
                    name=Path(image.filename).stem
                ) for image in filtered_images)
            )

        return tuple(card_images)

    def _load_cards(self, definition: dict, size: Size) -> list[Card]:
        if 'front' not in definition:
            raise ValueError("Cards definition must have a front image")
        front_images = self._load_card_images(definition['front'], size)

        back_images = None
        if 'back' in definition:
            back_images = self._load_card_images(definition['back'], size)
            if len(front_images) != len(back_images):
                raise ValueError(f"The number of front ({len(front_images)}) and back ({len(back_images)}) images "
                                 f"must be the same in cards definition")
            return [Card(front_image, back_image, size=size)
                    for front_image, back_image in zip(front_images, back_images)]

        return [Card(image, size=size) for image in front_images]

    def _load_deck(self, definition: dict, /, name: str = '') -> Deck:
        if 'size' not in definition:
            raise ValueError("No size defined for deck")
        size = Size.from_str(definition['size'])
        cards = self._load_cards(definition, size)

        cards = cards * definition.get('copies', 1)

        default_back = None
        if 'default_back' in definition:
            if default_back_images := self._load_card_images(definition['default_back'], size):
                default_back = default_back_images[0]

        return Deck(cards, name=name, size=size, default_back=default_back)

    @property
    def decks(self) -> list[Deck]:
        logger = logging.getLogger('cartuli.definition.Definition.decks')
        if self.__decks is None:
            self.__decks = []
            for name, definition in self.__values.get('decks', {}).items():
                logger.debug(f"Deck '{name}' definition {definition}")
                self.__decks.append(self._load_deck(definition, name))
            if not self.__decks:
                logger.warning('No decks loaded in definition')

        return self.__decks

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
    def _template_parameters(self) -> dict[str, dict]:
        self.__template_parameters = self._values.get('template_parameters', {})

        return self.__template_parameters

    @property
    def _filters(self) -> dict[str, Filter]:
        if self.__filters is None:
            self.__filters = defaultdict(NullFilter)

            for name, filter_definition in self._values.get('filters', {}).items():
                self.__filters[name] = Filter.from_dict(filter_definition)

        return self.__filters
