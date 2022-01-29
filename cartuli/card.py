"""Card module."""
import cv2 as cv
import numpy as np

from dataclasses import dataclass
from PIL import Image, ImageOps, ImageDraw

from . import Size


def inpaint_card_image(image: Image, inpaint_size: int = 16, image_crop: int = 2, corner_radius: int = 12) -> Image:
    # TODO; Convert inpaint_size and image_crop in mm
    # TUNE: Manage properly off inpaint size values
    expanded_image = ImageOps.expand(image, border=inpaint_size//2, fill='white')

    mask_image = Image.new('L', tuple(s + inpaint_size for s in image.size), color='white')
    mask_image_draw = ImageDraw.Draw(mask_image)
    mask_image_draw.rounded_rectangle(
        (inpaint_size + image_crop, inpaint_size + image_crop,
         image.size[0] - image_crop, image.size[1] - image_crop),
        fill='black', width=0, radius=corner_radius)

    inpaint_image_cv = cv.inpaint(
        cv.cvtColor(np.array(expanded_image), cv.COLOR_RGB2BGR), np.array(mask_image), 15, cv.INPAINT_NS)

    return Image.fromarray(cv.cvtColor(inpaint_image_cv, cv.COLOR_BGR2RGB))


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
