"""Card module."""
import cv2 as cv
import numpy as np

from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

from .measure import Size


class CardImage:
    """Card image."""

    def __init__(self, image: Path | str | Image.Image, size: Size):
        self.__image_path = None
        self.__image = None

        if isinstance(image, str):
            image = Path(image)
        elif isinstance(image, Path):
            self.__image_path = image
        elif isinstance(image, Image.Image):
            self.__image = image
        else:
            raise TypeError(f"{type(image)} is not a valid impage")

        self.__size = size

    @property
    def image_path(self) -> Path:
        return self.__image_path

    @property
    def image(self) -> Image.Image:
        if self.__image is None:
            self.__image = Image.open(self.__image_path)

        return self.__image

    @property
    def size(self) -> Size:
        return self.__size

    def inpainted(self, inpaint_size: int = 16, image_crop: int = 2, corner_radius: int = 12) -> Image.Image:
        # TODO; Convert inpaint_size and image_crop in mm
        # TUNE: Manage properly off inpaint size values
        expanded_image = ImageOps.expand(self.image, border=inpaint_size//2, fill='white')

        mask_image = Image.new('L', tuple(s + inpaint_size for s in self.image.size), color='white')
        mask_image_draw = ImageDraw.Draw(mask_image)
        mask_image_draw.rounded_rectangle(
            (inpaint_size + image_crop, inpaint_size + image_crop,
             self.image.size[0] - image_crop, self.image.size[1] - image_crop),
            fill='black', width=0, radius=corner_radius)

        inpaint_image_cv = cv.inpaint(
            cv.cvtColor(np.array(expanded_image), cv.COLOR_RGB2BGR), np.array(mask_image), 15, cv.INPAINT_NS)

        return Image.fromarray(cv.cvtColor(inpaint_image_cv, cv.COLOR_BGR2RGB))


class Card:
    """One or two sided card representation."""

    def __init__(self, size: Size, front_image: Path | str | CardImage,
                 back_image: Path | str | CardImage = None):
        self.__size = size

        if isinstance(front_image, Path) or isinstance(front_image, str):
            self.__front_image = CardImage(front_image, size)
        elif isinstance(front_image, CardImage):
            if size != front_image.size:
                raise ValueError("front_image is not the same size than the card")
            self.__front_image = front_image
        else:
            raise TypeError(f"{type(front_image)} is not a valid front_image")

        self.__back_image = back_image
        if back_image is not None:
            if isinstance(back_image, Path) or isinstance(back_image, str):
                self.__back_image = CardImage(back_image, size)
            elif isinstance(front_image, CardImage):
                if size != back_image.size:
                    raise ValueError("front_image is not the same size than the card")
            else:
                raise TypeError(f"{type(back_image)} is not a valid back_image")

    @property
    def size(self) -> Size:
        return self.__size

    @property
    def front_image(self) -> CardImage:
        return self.__front_image

    @property
    def back_image(self) -> CardImage:
        return self.__back_image

    @property
    def two_sided(self) -> bool:
        """Return if the card in one or two sided."""
        return self.back_image is not None
