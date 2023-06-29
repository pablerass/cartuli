"""Definition file module."""
from __future__ import annotations

import yaml

from copy import deepcopy
from functools import partial
from pathlib import Path

from .deck import Deck
from .measure import Size
from .sheet import Sheet


class Definition:
    """Definition."""
    def __init__(self, values: dict):
        self.__values = Definition._validate(values)

    @classmethod
    def from_file(cls, path: Path | str) -> Definition:
        if isinstance(path, str):
            path = Path(path)
        if not isinstance(path, Path):
            raise TypeError(f"{type(path)} is not a valid path")

        with path.open(mode='r') as file:
            return cls(yaml.safe_load(file))

    def _validate(values: dict) -> dict:
        if values is None:
            raise ValueError("Expected a dictionary, None found")

        return values

    @property
    def decks(self) -> list[Deck]:
        decks = []
        for name, deck_definition in self.__values['decks'].items():
            decks.append(Deck(size=Size.from_str(deck_definition['size']), name=name))
        return decks

    @property
    def values(self) -> dict:
        return deepcopy(self.__values)
