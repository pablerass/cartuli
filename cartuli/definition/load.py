"""Definition file module."""
from __future__ import annotations

import yaml

from pathlib import Path

from .definition import FilesFilter, Definition


DEFAULT_CARTULIFILE = 'Cartulifile.yml'


def load_cartulifile(path: str | Path = DEFAULT_CARTULIFILE, files_filter: FilesFilter = None) -> Definition:
    if isinstance(path, str):
        path = Path(path)

    if not isinstance(path, Path):
        raise TypeError(f"{type(path)} is not a valid path")

    if path.is_dir():
        path = path / DEFAULT_CARTULIFILE

    with path.open(mode='r') as file:
        return Definition(yaml.safe_load(file), files_filter)
