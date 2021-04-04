"""Sheet module."""
import logging

from math import ceil
from typing import List, Union

from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from . import Card, Coordinates, Position, Size, A4, mm


class Sheet(object):
    """Sheet that contains multiple cards to be printed."""

    DEFAULT_MARGIN = 5*mm
    DEFAULT_PADDING = 4*mm
    DEFAULT_SIZE = A4

    def __init__(self, name: str, /, card_size: Size = Card.STANDARD_SIZE, margin: float = DEFAULT_MARGIN,
                 padding: float = DEFAULT_PADDING, size: Size = DEFAULT_SIZE):
        """Create Sheet object."""
        self.__name = name
        self.__card_size = card_size
        self.__margin = margin
        self.__padding = padding
        self.__size = size

        self.__cards = []
        self.__cards_per_page = None
        self.__num_cards_per_page = None

    @property
    def name(self) -> str:
        """Return sheet name."""
        return self.__name

    @property
    def margin(self) -> float:
        """Return sheet margins."""
        return self.__margin

    @property
    def padding(self) -> float:
        """Return distance between cards."""
        return self.__padding

    @property
    def size(self) -> Size:
        """Return sheet size."""
        return self.__size

    @property
    def card_size(self) -> Size:
        """Return sheet card size."""
        return self.__card_size

    @property
    def cards(self) -> List[Card]:
        """Return current sheet cards."""
        return self.__cards

    @property
    def cards_per_page(self) -> Size:
        """Return the amount of cards that fits in each page."""
        if self.__cards_per_page is None:
            width = (self.size.width - 2*self.margin + self.padding) / (self.card_size.width + self.padding)
            height = (self.size.height - 2*self.margin + self.padding) / (self.card_size.height + self.padding)
            self.__cards_per_page = Size(int(width), int(height))
        return self.__cards_per_page

    @property
    def num_cards_per_page(self) -> Size:
        """Return the amount of cards that fits in each page."""
        if self.__num_cards_per_page is None:
            self.__num_cards_per_page = self.cards_per_page.width * self.cards_per_page.height
        return self.__num_cards_per_page

    def card_page(self, card_number: int) -> int:
        """Return the card page based on its sequence number."""
        return card_number // (self.cards_per_page.width * self.cards_per_page.height) + 1

    def card_coordinates(self, card_number: int) -> Coordinates:
        """Return the card coordinates based on its sequence number."""
        card_number_in_page = (card_number - 1) % (self.cards_per_page.width * self.cards_per_page.height) + 1
        return Coordinates((card_number_in_page - 1) % self.cards_per_page.width + 1,
                           (card_number_in_page - 1) // self.cards_per_page.width + 1)

    def card_position(self, coordinates: Coordinates) -> Position:
        """Return the card position based on a coordinates."""
        if (self.cards_per_page.width < coordinates.x or
                self.cards_per_page.height < coordinates.y):
            raise ValueError(f"Invalid position, maximun position is {Position(*self.cards_per_page)}")
        x = self.margin + (coordinates.x - 1)*(self.card_size.width + self.padding)
        y = self.margin + (coordinates.y - 1)*(self.card_size.height + self.padding)
        return Position(x, y)

    def __report_card_position(self, coordinates: Coordinates) -> Position:
        card_position = self.card_position(coordinates)
        x = card_position.x
        y = self.size.height - card_position.y - self.card_size.height
        return Position(x, y)

    @property
    def pages(self) -> int:
        """Return the current number of pages."""
        return ceil(len(self.__cards) / self.num_cards_per_page)

    # @property
    # def two_sided(self) -> bool:
    #     """Return if the card has two sides."""
    #     return any([card.back_image is not None for card in self.cards])

    def add_cards(self, cards: Union[Card, List[Card]]) -> None:
        """Add cards to sheet."""
        if isinstance(cards, Card):
            cards = (cards,)

        for i, card in enumerate(cards):
            if card.size is not None and card.size != self.__card_size:
                raise ValueError(f"{card.size} does not fit in sheet")
            if card.back_image is not None:
                raise ValueError("Only one side cards are supported")

            self.__cards.append(card)

    def page_cards(self, page: int) -> List[Card]:
        """Return the cards that belong to a page."""
        return self.cards[(page - 1)*self.num_cards_per_page:page*self.num_cards_per_page]

    def create_pdf(self) -> None:
        """Create the sheet PDF with all added cards."""
        logger = logging.getLogger('cartuli.Sheet.create_pdf')

        for page in range(1, self.pages + 1):
            page_canvas = canvas.Canvas(f"{self.name}-{page}.pdf", pagesize=tuple(self.size))
            for i, card in enumerate(self.page_cards(page)):
                num_card = i + 1
                card_image = Image.open(card.front_image)
                card_coordinates = self.card_coordinates(num_card)
                card_position = self.__report_card_position(card_coordinates)
                logger.debug(f"Adding {num_card} card {card.front_image} to page {page} at {card_coordinates} position")
                page_canvas.drawImage(ImageReader(card_image),
                                      card_position.x, card_position.y,
                                      self.card_size.width, self.card_size.height)
            page_canvas.save()
            logger.debug(f"Created {page} PDF")
