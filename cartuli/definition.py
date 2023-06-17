"""Definition file module."""
from __future__ import annotations

import copy
import yaml

from pathlib import Path


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
            raise ValueError(f"Expected a dictionary, None found")

        return values

    @property
    def values(self) -> dict:
        return copy.deepcopy(self.__values)
