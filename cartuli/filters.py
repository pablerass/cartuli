import logging

from abc import ABC, abstractmethod
from dataclasses import dataclass
# from pathlib import Path

from .card import CardImage
from .measure import mm, from_str
from .processing import inpaint, straighten


class Filter(ABC):
    @abstractmethod
    def apply(self, card_image: CardImage) -> CardImage:
        pass


@dataclass(frozen=True)
class NullFilter(Filter):
    def apply(self, card_image: CardImage) -> CardImage:
        return CardImage(card_image.image, card_image.size, card_image.bleed)


class MultipleFilter(Filter):
    def __init__(self, *filters: Filter):
        self._filters = tuple(filters)

    def apply(self, card_image: CardImage) -> CardImage:
        for f in self._filters:
            card_image = f.apply(card_image)

        return card_image

    def __eq__(self, other) -> bool:
        return self._filters == other._filters


@dataclass(frozen=True)
class InpaintFilter(Filter):
    inpaint_size: float = 3*mm
    image_crop: float = 0.8*mm
    corner_radius: float = 3*mm
    inpaint_radius: float = 1*mm

    def apply(self, card_image: CardImage) -> CardImage:
        logger = logging.getLogger('InpaintFilter')
        logger.debug(f'Applying to {card_image}')

        return CardImage(
            inpaint(
                card_image.image,
                inpaint_size=card_image.resolution * self.inpaint_size,
                image_crop=card_image.resolution * self.image_crop,
                corner_radius=card_image.resolution * self.corner_radius,
                inpaint_radius=max(card_image.resolution) * self.inpaint_radius,
                # debug_dir=f'.debug/filters/inpaint/{card_image}'
            ),
            size=card_image.size,
            bleed=card_image.bleed + self.inpaint_size,
            name=card_image.name
        )


@dataclass(frozen=True)
class StraightenFilter(Filter):
    def apply(self, card_image: CardImage) -> CardImage:
        logger = logging.getLogger('StraightenFilter')
        logger.debug(f'Applying to {card_image}')

        return CardImage(
            straighten(
                card_image.image,
                debug_dir=f'.debug/filters/straighten/{card_image}'
            ),
            size=card_image.size,
            bleed=card_image.bleed,
            name=card_image.name
        )


def snake_to_class(snake_case_str):
    words = snake_case_str.split('_')
    camel_case_str = ''.join(word.capitalize() for word in words)
    return camel_case_str


def from_dict(filter_dict: dict) -> Filter:
    if not filter_dict:
        return NullFilter()
    elif len(filter_dict) == 1:
        filter_name = list(filter_dict)[0]
        filter_class = globals()[snake_to_class(filter_name) + 'Filter']
        filter_args = {}
        if filter_dict[filter_name] is not None:
            filter_args = {k: from_str(v) for k, v in filter_dict[filter_name].items()}
        return filter_class(**filter_args)
    else:
        return MultipleFilter(
            *(from_dict({i[0]: i[1]}) for i in filter_dict.items())
        )
