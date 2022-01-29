"""Card module."""
from dataclasses import dataclass

from . import Size


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
