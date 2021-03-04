"""Measures package."""
from collections import namedtuple

from reportlab.lib import pagesizes
from reportlab.lib.units import mm, cm, inch


__all__ = [
    "A1", "A2", "A3", "A4", "A5",
    "LETTER", "HALF_LETTER", "LEGAL", "JUNIOR_LEGAL", "TABLOID",
    "mm", "cm", "inch",
    "Size", "Position"
]


Size = namedtuple('Size', ('width', 'height'))


Position = namedtuple('Position', ('x', 'y'))


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
