from abc import ABC, abstractmethod
from dataclasses import dataclass

from .card import CardImage
from .measure import mm
from .processing import inpaint


class CardImageFilter(ABC):
    @abstractmethod
    def apply(self, card_image: CardImage) -> CardImage:
        pass


class CardImageNullFilter(CardImageFilter):
    def apply(self, card_image: CardImage) -> CardImage:
        return CardImage(card_image.image, card_image.size, card_image.bleed)


class CardImageMultipleFilter(CardImageFilter):
    def __init__(self, *filters: CardImageFilter):
        self.__filters = filters

    def apply(self, card_image) -> CardImage:
        for f in self.__filters:
            card_image = f.apply(card_image)

        return card_image


@dataclass(frozen=True)
class CardImageInpaintFilter(CardImageFilter):
    # TODO: Convert size to coeficients or percentajes based on image size
    inpaint_size: float = 3*mm
    image_crop: float = 1*mm
    corner_radius: float = 20.0

    def apply(self, card_image: CardImage) -> CardImage:
        return CardImage(
            # TODO; Convert inpaint_size, image_crop and corner_radius to mm
            inpaint(card_image.image, int(self.inpaint_size)*3, int(self.image_crop), int(self.corner_radius)),
            card_image.size,
            card_image.bleed + self.inpaint_size
        )
