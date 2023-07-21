from abc import ABC, abstractmethod
from dataclasses import dataclass

from .card import CardImage
from .measure import mm
from .processing import inpaint, straighten


class Filter(ABC):
    @abstractmethod
    def apply(self, card_image: CardImage) -> CardImage:
        pass


class NullFilter(Filter):
    def apply(self, card_image: CardImage) -> CardImage:
        return CardImage(card_image.image, card_image.size, card_image.bleed)


class MultipleFilter(Filter):
    def __init__(self, *filters: Filter):
        self.__filters = filters

    def apply(self, card_image: CardImage) -> CardImage:
        for f in self.__filters:
            card_image = f.apply(card_image)

        return card_image


@dataclass(frozen=True)
class InpaintFilter(Filter):
    inpaint_size: float = 4*mm
    image_crop: float = 0.4*mm
    corner_radius: float = 3*mm

    def apply(self, card_image: CardImage) -> CardImage:
        return CardImage(
            inpaint(card_image.image,
                    card_image.resolution * self.inpaint_size,
                    card_image.resolution * self.image_crop,
                    card_image.resolution * (self.corner_radius + self.image_crop)),
            card_image.size,
            card_image.bleed + self.inpaint_size
        )


@dataclass(frozen=True)
class StaightenFilter(Filter):
    def apply(self, card_image: CardImage) -> CardImage:
        return CardImage(
            straighten(card_image.image),
            card_image.size,
            card_image.bleed
        )
