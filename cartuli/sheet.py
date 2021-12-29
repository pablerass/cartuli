"""Sheet module."""
import logging

from math import ceil
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from typing import List

from .card import Card, CardSize
from .measure import Coordinates, Point, Size, Line, A4, mm


class Sheet(object):
    """Sheet that contains multiple cards to be printed."""

    DEFAULT_MARGIN = 2*mm
    DEFAULT_PADDING = 6*mm
    DEFAULT_CROP_MARKS_PADDING = 1*mm
    DEFAULT_SIZE = A4

    def __init__(self, /, card_size: Size = CardSize.STANDARD_SIZE, margin: float = DEFAULT_MARGIN,
                 padding: float = DEFAULT_PADDING, crop_marks_padding=DEFAULT_CROP_MARKS_PADDING,
                 size: Size = DEFAULT_SIZE):
        """Create Sheet object."""
        self.__card_size = card_size
        self.__margin = margin
        self.__padding = padding
        self.__crop_marks_padding = crop_marks_padding
        self.__size = size

        self.__cards = []
        self.__cards_per_page = None
        self.__num_cards_per_page = None
        self.__horizontal_margin = None
        self.__vertical_margin = None
        self.__crop_marks = None

    @property
    def card_size(self) -> Size:
        """Return sheet card size."""
        return self.__card_size

    @property
    def margin(self) -> float:
        """Return sheet margins."""
        return self.__margin

    @property
    def horizontal_margin(self) -> float:
        """Return horizontal sheet margin to center content."""
        if self.__horizontal_margin is None:
            horizontal_cards = self.cards_per_page.width
            self.__horizontal_margin = (self.size.width - horizontal_cards * self.card_size.width -
                                        (horizontal_cards - 1) * self.padding) / 2

        return self.__horizontal_margin

    @property
    def vertical_margin(self) -> float:
        """Return vertical sheet margin to center content."""
        if self.__vertical_margin is None:
            vertical_cards = self.cards_per_page.height
            self.__vertical_margin = (self.size.height - vertical_cards * self.card_size.height -
                                      (vertical_cards - 1) * self.padding) / 2

        return self.__vertical_margin

    @property
    def padding(self) -> float:
        """Return distance between cards."""
        return self.__padding

    @property
    def crop_marks_padding(self) -> float:
        """Return distance between crop marks and cards."""
        return self.__crop_marks_padding

    @property
    def size(self) -> Size:
        """Return sheet size."""
        return self.__size

    @property
    def cards(self) -> list[Card]:
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
        return Coordinates((card_number_in_page - 1) % self.cards_per_page.width,
                           (card_number_in_page - 1) // self.cards_per_page.width)

    def card_position(self, coordinates: Coordinates) -> Point:
        """Return the card position based on a coordinates."""
        if (self.cards_per_page.width < coordinates.x or
                self.cards_per_page.height < coordinates.y):
            raise ValueError(f"Invalid position, maximun position is {Point(*self.cards_per_page)}")
        x = self.horizontal_margin + coordinates.x * self.card_size.width + coordinates.x * self.padding
        y = (self.size.height - self.vertical_margin - (coordinates.y + 1) * self.card_size.height -
             coordinates.y * self.padding)
        return Point(x, y)

    @property
    def crop_marks(self) -> List[Line]:
        """Return the crop marks to be drawn in each page."""
        if self.__crop_marks is None:
            crop_marks = []

            for x in range(self.cards_per_page.width):
                start_x_point = self.horizontal_margin + x * (self.card_size.width + self.padding)
                end_x_point = start_x_point + self.card_size.width

                crop_marks.append(Line(
                    Point(start_x_point, 0),
                    Point(start_x_point, self.vertical_margin - self.crop_marks_padding)))
                crop_marks.append(Line(
                    Point(end_x_point, 0),
                    Point(end_x_point, self.vertical_margin - self.crop_marks_padding)))
                if 2 * self.crop_marks_padding < self.padding:
                    for y in range(self.cards_per_page.height - 1):
                        crop_marks.append(Line(
                            Point(start_x_point, self.vertical_margin + (y + 1) * self.card_size.height
                                  + y * self.padding + self.crop_marks_padding),
                            Point(start_x_point, self.vertical_margin +
                                  (y + 1) * (self.card_size.height + self.padding) - self.crop_marks_padding)))
                        crop_marks.append(Line(
                            Point(end_x_point, self.vertical_margin + (y + 1) * self.card_size.height
                                  + y * self.padding + self.crop_marks_padding),
                            Point(end_x_point, self.vertical_margin + (y + 1) * (self.card_size.height + self.padding)
                                  - self.crop_marks_padding)))
                crop_marks.append(Line(
                    Point(start_x_point, self.size.height - self.vertical_margin + self.crop_marks_padding),
                    Point(start_x_point, self.size.height)))
                crop_marks.append(Line(
                    Point(end_x_point, self.size.height - self.vertical_margin + self.crop_marks_padding),
                    Point(end_x_point, self.size.height)))

            for y in range(self.cards_per_page.height):
                start_y_point = self.vertical_margin + y * (self.card_size.height + self.padding)
                end_y_point = start_y_point + self.card_size.height

                crop_marks.append(Line(
                    Point(0, start_y_point),
                    Point(self.horizontal_margin - self.crop_marks_padding, start_y_point)))
                crop_marks.append(Line(
                    Point(0, end_y_point),
                    Point(self.horizontal_margin - self.crop_marks_padding, end_y_point)))
                if 2 * self.crop_marks_padding < self.padding:
                    for x in range(self.cards_per_page.width - 1):
                        crop_marks.append(Line(
                            Point(self.horizontal_margin + (x + 1) * self.card_size.width + x * self.padding
                                  + self.crop_marks_padding, start_y_point),
                            Point(self.horizontal_margin + (x + 1) * (self.card_size.width + self.padding)
                                  - self.crop_marks_padding, start_y_point)))
                        crop_marks.append(Line(
                            Point(self.horizontal_margin + (x + 1) * self.card_size.width + x * self.padding
                                  + self.crop_marks_padding, end_y_point),
                            Point(self.horizontal_margin + (x + 1) * (self.card_size.width + self.padding)
                                  - self.crop_marks_padding, end_y_point)))
                crop_marks.append(Line(
                    Point(self.size.width - self.horizontal_margin + self.crop_marks_padding, start_y_point),
                    Point(self.size.width, start_y_point)))
                crop_marks.append(Line(
                    Point(self.size.width - self.horizontal_margin + self.crop_marks_padding, end_y_point),
                    Point(self.size.width, end_y_point)))

            self.__crop_marks = crop_marks

        return self.__crop_marks

    @property
    def pages(self) -> int:
        """Return the current number of pages."""
        return ceil(len(self.__cards) / self.num_cards_per_page)

    # @property
    # def two_sided(self) -> bool:
    #     """Return if the card has two sides."""
    #     return any([card.back_image is not None for card in self.cards])

    def add_cards(self, cards: Card | list[Card]) -> None:
        """Add cards to sheet."""
        if isinstance(cards, Card):
            cards = (cards,)

        for i, card in enumerate(cards):
            if card.size is not None and card.size != self.__card_size:
                raise ValueError(f"{card.size} does not fit in sheet")
            if card.back_image is not None:
                raise ValueError("Only one side cards are supported")

            self.__cards.append(card)

    def page_cards(self, page: int) -> list[Card]:
        """Return the cards that belong to a page."""
        return self.cards[(page - 1)*self.num_cards_per_page:page*self.num_cards_per_page]

    def create_pdf(self, base_name: str) -> None:
        """Create the sheet PDF with all added cards."""
        logger = logging.getLogger('cartuli.Sheet.create_pdf')

        c = canvas.Canvas(f"{base_name}", pagesize=tuple(self.size))
        for page in range(1, self.pages + 1):
            for line in self.crop_marks:
                c.setLineWidth(0.5)
                c.line(*list(line))

            for i, card in enumerate(self.page_cards(page)):
                num_card = i + 1
                card_image = Image.open(card.front_image)
                card_coordinates = self.card_coordinates(num_card)
                card_position = self.card_position(card_coordinates)
                logger.debug(f"Adding {num_card} card {card.front_image} to page {page} at {card_coordinates} position")
                c.drawImage(ImageReader(card_image),
                            card_position.x, card_position.y,
                            self.card_size.width, self.card_size.height)
            c.showPage()

        c.save()
        logger.debug(f"Created {page}")
