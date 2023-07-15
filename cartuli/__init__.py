"""Package to create printable sheets for print and play games."""
from .measure import A1, A2, A3, A4, A5, LETTER, HALF_LETTER, LEGAL, JUNIOR_LEGAL, TABLOID
from .measure import MINI_USA, MINI_CHIMERA, MINI_EURO, STANDARD_USA, CHIMERA, EURO,  STANDARD, MAGNUM_COPPER
from .measure import MAGNUM_SPACE, SMALL_SQUARE,  SQUARE, MAGNUM_SILVER, MAGNUM_GOLD, TAROT
from .measure import Coordinates, Point, Size, mm, cm, inch
from .card import Card, CardImage
from .deck import Deck
from .sheet import Sheet


__version__ = "v0.1.0b0"


__all__ = [
    A1, A2, A3, A4, A5, LETTER, HALF_LETTER, LEGAL, JUNIOR_LEGAL, TABLOID,
    MINI_USA, MINI_CHIMERA, MINI_EURO, STANDARD_USA, CHIMERA, EURO,  STANDARD, MAGNUM_COPPER,
    MAGNUM_SPACE, SMALL_SQUARE,  SQUARE, MAGNUM_SILVER, MAGNUM_GOLD, TAROT,
    Coordinates, Point, Size, mm, cm, inch,
    Card, CardImage, Sheet, Deck
]
