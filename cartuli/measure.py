"""Measures package."""
from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from math import isclose
from reportlab.lib import pagesizes
from reportlab.lib.units import mm, cm, inch
from typing import Final

__all__ = [
    "A1", "A2", "A3", "A4", "A5",
    "LETTER", "HALF_LETTER", "LEGAL", "JUNIOR_LEGAL", "TABLOID",
    "MINI_USA", "MINI_CHIMERA", "MINI_EURO", "STANDARD_USA",
    "CHIMERA", "EURO",  "STANDARD", "MAGNUM_COPPER", "MAGNUM_SPACE",
    "SMALL_SQUARE",  "SQUARE", "MAGNUM_SILVER", "MAGNUM_GOLD", "TAROT",
    "mm", "cm", "inch",
    "Size", "Point"
]


measure_is_close = partial(isclose, abs_tol=0.001*mm)


def from_str(measure: str | int | float) -> float:
    if isinstance(measure, str):
        return eval(measure)
    return measure


@dataclass(frozen=True, order=True)
class Size:
    """Size class in any measure."""

    width: float | int
    height: float | int

    def __eq__(self, other):
        return measure_is_close(self.width, other.width) and measure_is_close(self.height, other.height)

    def __str__(self):
        return f"({self.width}, {self.height})"

    def __iter__(self):
        return (v for v in (self.width, self.height))

    @staticmethod
    def from_str(s: str) -> Size:
        try:
            size = eval(s)
            if isinstance(size, Size):
                return size
            if isinstance(size, tuple) and len(size) == 2:
                return Size(*size)
        except Exception:
            pass

        raise ValueError(f'invalid literal for Size value: \'{s}\'')

    def __mul__(self, other: float | int) -> Size:
        return self.__class__(self.width * other, self.height * other)

    def __truediv__(self, other: float | int) -> Size:
        return self.__class__(self.width / other, self.height / other)


@dataclass(frozen=True, order=True)
class Point:
    """Point class in any measure."""

    x: float | int
    y: float | int

    def __eq__(self, other):
        return measure_is_close(self.x, other.x) and measure_is_close(self.y, other.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __iter__(self):
        return (v for v in (self.x, self.y))


@dataclass(frozen=True, order=True)
class Line:
    """Line class."""

    a: Point
    b: Point

    def __eq__(self, other):
        return ((self.a == other.a) and (self.b == other.b) or
                (self.a == other.b) and (self.b == other.a))

    def __str__(self):
        return f"{self.a} <-> {self.b}"

    def __iter__(self):
        return (v for v in (self.a.x, self.a.y, self.b.x, self.b.y))


class Coordinates(Point):
    pass


A1: Final[Size] = Size(*pagesizes.A1)
A2: Final[Size] = Size(*pagesizes.A2)
A3: Final[Size] = Size(*pagesizes.A3)
A4: Final[Size] = Size(*pagesizes.A4)
A5: Final[Size] = Size(*pagesizes.A5)
LETTER: Final[Size] = Size(*pagesizes.LETTER)
HALF_LETTER: Final[Size] = Size(*pagesizes.HALF_LETTER)
LEGAL: Final[Size] = Size(*pagesizes.LEGAL)
JUNIOR_LEGAL: Final[Size] = Size(*pagesizes.JUNIOR_LEGAL)
TABLOID: Final[Size] = Size(*pagesizes.TABLOID)

MINI_USA: Final[Size] = Size(41*mm, 63*mm)        # Eldritch Horror
MINI_CHIMERA: Final[Size] = Size(43*mm, 65*mm)    # Arkharm Horror
MINI_EURO: Final[Size] = Size(45*mm, 68*mm)       # Viticulture
STANDARD_USA: Final[Size] = Size(56*mm, 87*mm)    # Munchkin
CHIMERA: Final[Size] = Size(57.5*mm, 89*mm)       # Fantasi Flight games
EURO: Final[Size] = Size(59*mm, 92*mm)            # Dominion
STANDARD: Final[Size] = Size(63.5*mm, 88*mm)      # Magic
MAGNUM_COPPER: Final[Size] = Size(65*mm, 100*mm)  # 7 Wonders
MAGNUM_SPACE: Final[Size] = Size(61*mm, 103*mm)   # Space Alert
SMALL_SQUARE: Final[Size] = Size(70*mm, 70*mm)    # Alta Tensión
SQUARE: Final[Size] = Size(80*mm, 80*mm)          # Jungle Speed
MAGNUM_SILVER: Final[Size] = Size(70*mm, 110*mm)  # Scythe Encuentros
MAGNUM_GOLD: Final[Size] = Size(80*mm, 120*mm)    # Dixit
TAROT: Final[Size] = Size(70*mm, 120*mm)
