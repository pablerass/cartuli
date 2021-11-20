"""Card module."""
from dataclasses import dataclass

from . import Size, mm


@dataclass(frozen=True)
class Card:
    """One or two sided card representation."""

    size: Size
    front_image: str
    back_image: str = None
    name: str = None

    @property
    def two_sided(self) -> bool:
        """Return if the card in one or two sided."""
        return self.back_image is not None


class CardSize:
    __slots__ = ()

    MINI_USA_SIZE = Size(41*mm, 63*mm)        # Eldritch Horror
    MINI_CHIMERA_SIZE = Size(43*mm, 65*mm)    # Arkharm Horror
    MINI_EURO_SIZE = Size(45*mm, 68*mm)       # Viticulture
    STANDARD_USA_SIZE = Size(56*mm, 87*mm)    # Munchkin
    CHIMERA_SIZE = Size(57.5*mm, 89*mm)       # Fantasi Flight games
    EURO_SIZE = Size(59*mm, 92*mm)            # Dominion
    STANDARD_SIZE = Size(63.5*mm, 88*mm)      # Magic
    MAGNUM_COPPER_SIZE = Size(65*mm, 100*mm)  # 7 Wonders
    MAGNUM_SPACE_SIZE = Size(61*mm, 103*mm)   # Space Alert
    SMALL_SQUARE_SIZE = Size(70*mm, 70*mm)    # Alta Tensión
    SQUARE_SIZE = Size(80*mm, 80*mm)          # Jungle Speed
    MAGNUM_SILVER_SIZE = Size(70*mm, 110*mm)  # Scythe Encuentros
    MAGNUM_GOLD_SIZE = Size(80*mm, 120*mm)    # Dixit
    TAROT_SIZE = Size(70*mm, 120*mm)
