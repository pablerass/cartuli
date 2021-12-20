"""Measures package."""
from dataclasses import dataclass
from math import isclose
from reportlab.lib import pagesizes
from reportlab.lib.units import mm, cm, inch


__all__ = [
    "A1", "A2", "A3", "A4", "A5",
    "LETTER", "HALF_LETTER", "LEGAL", "JUNIOR_LEGAL", "TABLOID",
    "mm", "cm", "inch",
    "Size", "Point"
]


@dataclass(frozen=True, order=True)
class Size:
    """Size class in any measure."""

    width: float
    height: float

    def __eq__(self, other):
        return isclose(self.width, other.width) and isclose(self.height, other.height)

    def __str__(self):
        return f"({self.width}, {self.height})"

    def __iter__(self):
        return (v for v in (self.width, self.height))


@dataclass(frozen=True, order=True)
class Point:
    """Point class in any measure."""

    x: float
    y: float

    def __eq__(self, other):
        return isclose(self.x, other.x) and isclose(self.y, other.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __iter__(self):
        return (v for v in (self.x, self.y))


@dataclass(frozen=True, order=True)
class Line:
    """Line class."""

    a: Point
    b: Point

    def __str__(self):
        return f"{self.a} <-> {self.b}"

    def __iter__(self):
        return (v for v in (self.a.x, self.a.y, self.b.x, self.b.y))


class Coordinates(Point):
    pass


A1 = Size(*pagesizes.A1)
A2 = Size(*pagesizes.A2)
A3 = Size(*pagesizes.A3)
A4 = Size(*pagesizes.A4)
A5 = Size(*pagesizes.A5)
LETTER = Size(*pagesizes.LETTER)
HALF_LETTER = Size(*pagesizes.HALF_LETTER)
LEGAL = Size(*pagesizes.LEGAL)
JUNIOR_LEGAL = Size(*pagesizes.JUNIOR_LEGAL)
TABLOID = Size(*pagesizes.TABLOID)
