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
        # TUNE: This code is crap, should be refacored
        logger = logging.getLogger('cartuli.definition.Definition.decks')
        if self.__decks is None:
            self.__decks = []
            for name, deck_definition in self.__values.get('decks', {}).items():
                logger.debug(f"Deck '{name}' definition {deck_definition}")
                self.__decks.append(self._create_deck(deck_definition, name))
            if not self.__decks:
                logger.warning('No decks loaded in definition')

        return self.__decks

    def _create_deck(self, definition: dict, name: str) -> Deck:
        logger = logging.getLogger('cartuli.definition.Definition.decks')

        size = Size.from_str(definition['size'])
        front_images = []
        if 'front' in definition:
            front_filter = definition['front'].get('filter', '')
            front_image_files = sorted(glob(definition['front']['images']))
            logger.debug(f"Found {len(front_image_files)} front images for '{name}' deck")
            with Pool(processes=cpu_count() - 1) as pool:
                front_images = pool.map(
                    self.filters[front_filter].apply,
                    (CardImage(
                        path, size=size,
                        bleed=from_str(definition['front'].get('bleed', str(CardImage.DEFAULT_BLEED))),
                        name=Path(path).stem
                     ) for path in front_image_files if self.__cards_filter(path))
                )
                # TODO: Add warning if no images are found and manage it properly and do not create
                # deck
            if len(front_image_files) != len(front_images):
                logger.debug(f"Front images filterd from {len(front_image_files)} to "
                             f" {len(front_images)} for '{name}' deck")

        back_image = None
        if 'back' in definition:
            if 'image' in definition['back']:
                back_image_file = definition['back']['image']
                if self.__cards_filter(back_image_file):
                    back_filter = definition['back'].get('filter', '')
                    back_image = self.filters[back_filter].apply(
                        CardImage(
                            definition['back']['image'],
                            size=size,
                            bleed=from_str(definition['back'].get('bleed', str(CardImage.DEFAULT_BLEED))),
                            name=Path(back_image_file).stem
                        )
                    )
                    return Deck((Card(image) for image in front_images), default_back=back_image, size=size, name=name)
                else:
                    logger.debug(f"Back image '{back_image_file}' filtered for '{name}' deck")

            if 'images' in definition['back']:
                back_filter = definition['back'].get('filter', '')
                back_image_files = sorted(glob(definition['back']['images']))
                logger.debug(f"Found {len(back_image_files)} back images for '{name}' deck")
                with Pool(processes=cpu_count() - 1) as pool:
                    back_images = pool.map(
                        self.filters[back_filter].apply,
                        (CardImage(
                            path, size=size,
                            bleed=from_str(definition['back'].get('bleed', str(CardImage.DEFAULT_BLEED))),
                            name=Path(path).stem
                        ) for path in back_image_files if self.__cards_filter(path))
                    )
                    # TODO: Add warning if no images are found
                    # TODO: Add error if front and back sizes do not match
                    return Deck(
                        (Card(front_image, back_image) for front_image, back_image in zip(front_images, back_images)),
                        size=size, name=name
                    )
                if len(back_image_files) != len(back_images):
                    logger.debug(f"Back images filterd from {len(back_image_files)} to "
                                 f" {len(back_images)} for '{name}' deck")

        return Deck((Card(image) for image in front_images), size=size, name=name)

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
