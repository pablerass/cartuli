"""Definition file module."""
from __future__ import annotations

import logging
import yaml

from collections import defaultdict
from collections.abc import Callable
from glob import glob
from itertools import chain, groupby
from pathlib import Path

from .card import Card, CardImage
from .deck import Deck
from .filters import Filter, NullFilter, from_dict as filter_from_dict
from .measure import Size, from_str
from .sheet import Sheet


CardsFilter = Callable[[Path], bool]


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
        # TUNE: Remove front_card concept and let it in cards
        logger = logging.getLogger('cartuli.definition.Definition.decks')
        if self.__decks is None:
            self.__decks = []
            for name, deck_definition in self.__values.get('decks', {}).items():
                logger.debug(f"Deck '{name}' definition {deck_definition}")
                size = Size.from_str(deck_definition['size'])
                front_images = []
                if 'front' in deck_definition:
                    front_filter = deck_definition['front'].get('filter', '')
                    front_image_files = sorted(glob(deck_definition['front']['images']))
                    logger.debug(f"Found {len(front_image_files)} front images for '{name}' deck")
                    front_images = [
                        self.filters[front_filter].apply(
                            CardImage(
                                path, size=size,
                                bleed=from_str(deck_definition['front'].get('bleed', str(CardImage.DEFAULT_BLEED))),
                                name=Path(path).stem
                            )
                        ) for path in front_image_files if self.__cards_filter(path)
                    ]
                    if len(front_image_files) != len(front_images):
                        logger.debug(f"Front images filterd from {len(front_image_files)} to "
                                     f" {len(front_images)} for '{name}' deck")
                back_image = None
                if 'back' in deck_definition:
                    back_image_file = deck_definition['back']['image']
                    if self.__cards_filter(back_image_file):
                        back_filter = deck_definition['back'].get('filter', '')
                        back_image = self.filters[back_filter].apply(
                            CardImage(
                                deck_definition['back']['image'],
                                size=size,
                                bleed=from_str(deck_definition['back'].get('bleed', str(CardImage.DEFAULT_BLEED))),
                                name=Path(back_image_file).stem
                            )
                        )
                    else:
                        logger.debug(f"Back image '{back_image_file}' filtered for '{name}' deck")
                deck = Deck((Card(image) for image in front_images), default_back=back_image, size=size, name=name)
                self.__decks.append(deck)
            if not self.__decks:
                logger.warning('No decks loaded in definition')

        return self.__decks

    @property
    def sheets(self) -> dict[tuple[str], Sheet]:
        # TODO: Replace sheets with generic outputs
        # TODO: Add deck filters to output definition
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
                        margin=from_str(sheet_definition.get('margin', str(Sheet.DEFAULT_MARGIN))),
                        padding=from_str(sheet_definition.get('padding', str(Sheet.DEFAULT_PADDING))),
                        crop_marks_padding=from_str(
                            sheet_definition.get('crop_marks_padding', str(Sheet.DEFAULT_CROP_MARKS_PADDING))),
                        print_margin=from_str(sheet_definition.get('print_margin',
                                                                   str(Sheet.DEFAULT_PRINT_MARGIN)))
                    )

        return self.__sheets

    @property
    def filters(self) -> dict[str, Filter]:
        filters = defaultdict(NullFilter)

        for name, filter_definition in self._values.get('filters', {}).items():
            filters[name] = filter_from_dict(filter_definition)

        return filters
