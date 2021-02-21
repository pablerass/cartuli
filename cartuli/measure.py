"""Measures package."""
from collections import namedtuple

from reportlab.lib.pagesizes import A1, A2, A3, A4, A5, LETTER, HALF_LETTER, LEGAL, JUNIOR_LEGAL, TABLOID
from reportlab.lib.units import mm, cm, inch


__all__ = [
    "A1", "A2", "A3", "A4", "A5",
    "LETTER", "HALF_LETTER", "LEGAL", "JUNIOR_LEGAL", "TABLOID",
    "mm", "cm", "inch",
    "Size", "Position"
]


Size = namedtuple('Size', ('height', 'width'))


Position = namedtuple('Position', ('x', 'y'))
