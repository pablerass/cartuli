"""Card module."""
from pathlib import Path

from PIL import Image

from .measure import Size


class CardImage:
    """Card image."""

    DEFAULT_BLEED = 0.0

    # TUNE: Size is duplicated between image and card
    def __init__(self, image: Path | str | Image.Image, /, size: Size, bleed: float = DEFAULT_BLEED):
        self.__image_path = None
        self.__image = None
        self.__resolution = None

        if isinstance(image, str):
            image = Path(image)
        if isinstance(image, Path):
            self.__image_path = image
            self.__image = Image.open(self.__image_path)
        elif isinstance(image, Image.Image):
            self.__image = image
        else:
            raise TypeError(f"{type(image)} is not a valid image")

        self.__size = size
        self.__bleed = bleed

    @property
    def image(self) -> Image.Image:
        return self.__image

    @property
    def size(self) -> Size:
        return self.__size

    @property
    def bleed(self) -> float:
        return self.__bleed

    @property
    def resolution(self) -> Size:
        if self.__resolution is None:
            self.__resolution = Size(
                self.image.width / self.size.width,
                self.image.height / self.size.height)

        return self.__resolution

    @property
    def image_size(self) -> Size:
        return Size(self.size.width + 2*self.bleed, self.size.height + 2*self.bleed)

    def __eq__(self, other) -> bool:
        return (self.image == other.image and
                self.size == self.size and
                self.bleed == self.bleed)


class Card:
    """One or two sided card representation."""

    def __init__(self, front: Path | str | CardImage, back: Path | str | CardImage = None, /,
                 size: Size = None, name: str = ''):

        if isinstance(front, Path) or isinstance(front, str):
            if size is None:
                raise ValueError("size must be specified when not using a CardImage as front")
            front = CardImage(front, size)
        elif isinstance(front, CardImage):
            if size is None:
                size = front.size
            elif size != front.size:
                raise ValueError("front image is not of the same size as the card")
        else:
            raise TypeError(f"{type(front)} is not a valid image")

        if back is not None:
            if isinstance(back, Path) or isinstance(back, str):
                back = CardImage(back, size)
            elif isinstance(back, CardImage):
                if size != back.size:
                    raise ValueError("back image is not of the same size as the card")
            else:
                raise TypeError(f"{type(back)} is not a valid image")

        self.__size = size
        self.__front = front
        self.__back = back
        self.__name = name

    @property
    def size(self) -> Size:
        return self.__size

    @property
    def front(self) -> CardImage:
        return self.__front

    @property
    def back(self) -> CardImage:
        return self.__back

    @back.setter
    def back(self, back: Path | str | CardImage):
        if self.__back is not None:
            raise AttributeError("can't set attribute 'back' if already set")

        if isinstance(back, Path) or isinstance(back, str):
            back = CardImage(back, self.__size)
        elif isinstance(back, CardImage):
            if self.__size != back.size:
                raise ValueError("back is not of the same size as the card")
        else:
            raise TypeError(f"{type(back)} is not a valid image")
        self.__back = back

    @property
    def name(self) -> str:
        return self.__name

    @property
    def two_sided(self) -> bool:
        return self.back is not None

    def __eq__(self, other) -> bool:
        return (self.front == other.front and
                self.back == self.back and
                self.size == self.size and
                self.name == self.name)

    def __str__(self) -> str:
        if self.name:
            return self.name
        return super().__str__()
