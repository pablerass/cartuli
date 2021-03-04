"""Sheet module."""
from typing import List, Union

# from PIL import Image
# from reportlab.lib.utils import ImageReader
# from reportlab.pdfgen import canvas

from . import Card, Position, Size, A4, mm


class Sheet(object):
    """Sheet that contains multiple cards to be printed."""

    DEFAULT_MARGIN = 5*mm
    DEFAULT_PADDING = 4*mm
    DEFAULT_SIZE = A4

    def __init__(self, name: str, /, card_size: Size = Card.STANDARD_SIZE, margin: int = DEFAULT_MARGIN,
                 padding: int = DEFAULT_PADDING, size: Size = DEFAULT_SIZE):
        """Create Sheet object."""
        self.__name = name
        self.__card_size = card_size
        self.__margin = margin
        self.__padding = padding
        self.__size = size

        self.__front_canvas = []
        self.__back_canvas = []

    @property
    def margin(self):
        """Return sheet margins."""
        return self.__margin

    @property
    def padding(self):
        """Return distance between cards."""
        return self.__padding

    @property
    def size(self):
        """Return sheet size."""
        return self.__size

    @property
    def card_size(self):
        """Return sheet card size."""
        return self.__card_size

    def cards_per_sheet(self) -> Size:
        """Return the amount of cards that fits in each sheet."""
        width = (self.size.width - 2*self.margin + self.padding) / (self.card_size.width + self.padding)
        height = (self.size.height - 2*self.margin + self.padding) / (self.card_size.height + self.padding)
        return Size(int(width), int(height))

    def __card_location(self, position: Position) -> Position:
        """Return the card location based on a position."""
        pass

    def add_cards(self, cards: Union[Card, List[Card]]):
        """Add cards to sheet."""
        if isinstance(cards, Card):
            cards = (cards,)

        for i, card in enumerate(cards):
            if card.size is not None and card.size != self.__card_size:
                raise ValueError(f"{card.size} does not fit in sheet")

    def create_pdf(self):
        """Create the sheet PDF with all added cards."""
        pass


# Working example
# c = canvas.Canvas(f"{name}.pdf", pagesize=A4)
# card = Image.open("./000.jpg").rotate(180)
# c.drawImage(ImageReader(card), 0, c.height - 122*mm, 73*mm, 122*mm)
# c.drawImage('001.jpg', 0, 0, 73*mm, 122*mm)
# c.showPage()
# c.drawImage('back.jpg', 0, 0, 73*mm, 122*mm)
# c.save()
