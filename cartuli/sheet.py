"""Sheet module."""
from math import ceil
from typing import Iterable

from .card import Card
from .measure import Coordinates, Point, Size, Line, A4, mm, inch


class Sheet(object):
    """Sheet that contains multiple cards to be printed."""

    DEFAULT_SIZE = A4
    DEFAULT_PRINT_MARGIN = 1*inch          # Default print margin for common printers
    DEFAULT_PADDING = 4*mm
    DEFAULT_CROP_MARKS_PADDING = 1*mm

    def __init__(self, cards: Card | Iterable[Card] = None, /, size: Size = DEFAULT_SIZE,
                 print_margin: float = DEFAULT_PRINT_MARGIN, padding: float = DEFAULT_PADDING,
                 crop_marks_padding=DEFAULT_CROP_MARKS_PADDING):
        """Create Sheet object."""
        self.__card_size = None
        self.__cards = []
        if cards is not None:
            self.add(cards)

        self.__size = size
        self.__print_margin = print_margin
        self.__padding = padding
        self.__crop_marks_padding = crop_marks_padding

        self.__cards_per_page = None
        self.__num_cards_per_page = None
        self.__margin = None
        self.__crop_marks = None

    def __add_card(self, card: Card, index: int = None) -> None:
        if self.__card_size is None:
            self.__card_size = card.size

        if card.size != self.card_size:
            raise ValueError(f"Card size {card.size} distinct from sheet {self.card_size} card size")

        if index is None:
            self.__cards.append(card)
        else:
            self.__cards.insert(card)

    def add(self, cards: Card | Iterable[Card], index: int = None) -> None:
        if isinstance(cards, Card):
            cards = [cards]
        if index is None:
            for card in cards:
                self.__add_card(card)
        else:
            for n, card in enumerate(cards):
                self.__add_card(card, index + n)

    @property
    def cards(self) -> Card:
        """Return sheet card size."""
        return tuple(self.__cards)

    @property
    def card_size(self) -> Size:
        """Return sheet card size."""
        if self.__card_size is None:
            raise AttributeError('card size is not yet available as no card has been added')
        return self.__card_size

    @property
    def size(self) -> Size:
        """Return sheet size."""
        return self.__size

    @property
    def print_margin(self) -> float:
        """Return sheet print margin."""
        return self.__print_margin

    @property
    def padding(self) -> float:
        """Return distance between cards."""
        return self.__padding

    @property
    def crop_marks_padding(self) -> float:
        """Return distance between crop marks and cards."""
        return self.__crop_marks_padding

    def __len__(self):
        return len(self.__cards)

    # TODO: Add minimum crop mark length
    @property
    def margin(self) -> float:
        """Return sheet margin to center content."""
        if self.__margin is None:
            horizontal_cards = self.cards_per_page.width
            horizontal_margin = (self.size.width - horizontal_cards * self.card_size.width -
                                 (horizontal_cards - 1) * self.padding) / 2
            vertical_cards = self.cards_per_page.height
            vertical_margin = (self.size.height - vertical_cards * self.card_size.height -
                               (vertical_cards - 1) * self.padding) / 2
            self.__margin = Size(horizontal_margin, vertical_margin)

        return self.__margin

    @property
    def cards_per_page(self) -> Size:
        """Return the amount of cards in rows and columns that fits in each page."""
        if self.__cards_per_page is None:
            width = ((self.size.width - 2*self.print_margin + self.padding) /
                     (self.card_size.width + self.padding))
            height = ((self.size.height - 2*self.print_margin + self.padding) /
                      (self.card_size.height + self.padding))
            self.__cards_per_page = Size(int(width), int(height))
        return self.__cards_per_page

    @property
    def num_cards_per_page(self) -> int:
        """Return the amount of cards that fits in each page."""
        if self.__num_cards_per_page is None:
            self.__num_cards_per_page = self.cards_per_page.width * self.cards_per_page.height
        return self.__num_cards_per_page

    def card_page(self, card_number: int) -> int:
        """Return the card page based on its sequence number."""
        return card_number // (self.cards_per_page.width * self.cards_per_page.height) + 1

    def card_coordinates(self, card_number: int, back: bool = False) -> Coordinates:
        """Return the card coordinates based on its sequence number."""
        card_number_in_page = (card_number - 1) % (self.cards_per_page.width * self.cards_per_page.height) + 1
        if not back:
            return Coordinates((card_number_in_page - 1) % self.cards_per_page.width,
                               (card_number_in_page - 1) // self.cards_per_page.width)
        else:
            return Coordinates(self.cards_per_page.width - ((card_number_in_page - 1) % self.cards_per_page.width) - 1,
                               (card_number_in_page - 1) // self.cards_per_page.width)

    def card_position(self, coordinates: Coordinates) -> Point:
        """Return the card position based on a coordinates."""
        if (self.cards_per_page.width < coordinates.x or
                self.cards_per_page.height < coordinates.y):
            raise ValueError(f"Invalid position, maximun position is {Point(*self.cards_per_page)}")
        x = self.margin.width + coordinates.x * self.card_size.width + coordinates.x * self.padding
        y = (self.size.height - self.margin.height - (coordinates.y + 1) * self.card_size.height -
             coordinates.y * self.padding)
        return Point(x, y)

    def _calculate_border_horizontal_crop_marks(self) -> list[Line]:
        crop_marks = []

        for y in range(self.cards_per_page.height):
            start_y_point = self.margin.height + y * (self.card_size.height + self.padding)
            end_y_point = start_y_point + self.card_size.height

            crop_marks.append(Line(
                Point(self.print_margin, start_y_point),
                Point(self.margin.width - self.crop_marks_padding, start_y_point)))

            crop_marks.append(Line(
                Point(self.print_margin, end_y_point),
                Point(self.margin.width - self.crop_marks_padding, end_y_point)))

            crop_marks.append(Line(
                Point(self.size.width - self.margin.width + self.crop_marks_padding, start_y_point),
                Point(self.size.width - self.print_margin, start_y_point)))

            crop_marks.append(Line(
                Point(self.size.width - self.margin.width + self.crop_marks_padding, end_y_point),
                Point(self.size.width - self.print_margin, end_y_point)))

        return crop_marks

    def _calculate_middle_horizontal_crop_marks(self) -> list[Line]:
        crop_marks = []

        for y in range(self.cards_per_page.height):
            start_y_point = self.margin.height + y * (self.card_size.height + self.padding)
            end_y_point = start_y_point + self.card_size.height

            if 2 * self.crop_marks_padding < self.padding:
                for x in range(self.cards_per_page.width - 1):
                    crop_marks.append(Line(
                        Point(self.margin.width + (x + 1) * self.card_size.width + x * self.padding
                              + self.crop_marks_padding, start_y_point),
                        Point(self.margin.width + (x + 1) * (self.card_size.width + self.padding)
                              - self.crop_marks_padding, start_y_point)))

                    crop_marks.append(Line(
                        Point(self.margin.width + (x + 1) * self.card_size.width + x * self.padding
                              + self.crop_marks_padding, end_y_point),
                        Point(self.margin.width + (x + 1) * (self.card_size.width + self.padding)
                              - self.crop_marks_padding, end_y_point)))

        return crop_marks

    def _calculate_border_vertical_crop_marks(self) -> list[Line]:
        crop_marks = []
        for x in range(self.cards_per_page.width):
            start_x_point = self.margin.width + x * (self.card_size.width + self.padding)
            end_x_point = start_x_point + self.card_size.width

            crop_marks.append(Line(
                Point(start_x_point, self.print_margin),
                Point(start_x_point, self.margin.height - self.crop_marks_padding)))

            crop_marks.append(Line(
                Point(end_x_point, self.print_margin),
                Point(end_x_point, self.margin.height - self.crop_marks_padding)))

            crop_marks.append(Line(
                Point(start_x_point, self.size.height - self.margin.height + self.crop_marks_padding),
                Point(start_x_point, self.size.height - self.print_margin)))

            crop_marks.append(Line(
                Point(end_x_point, self.size.height - self.margin.height + self.crop_marks_padding),
                Point(end_x_point, self.size.height - self.print_margin)))

        return crop_marks

    def _calculate_middle_vertical_crop_marks(self) -> list[Line]:
        crop_marks = []

        for x in range(self.cards_per_page.width):
            start_x_point = self.margin.width + x * (self.card_size.width + self.padding)
            end_x_point = start_x_point + self.card_size.width

            if 2 * self.crop_marks_padding < self.padding:
                for y in range(self.cards_per_page.height - 1):
                    crop_marks.append(Line(
                        Point(start_x_point, self.margin.height + (y + 1) * self.card_size.height
                              + y * self.padding + self.crop_marks_padding),
                        Point(start_x_point, self.margin.height +
                              (y + 1) * (self.card_size.height + self.padding) - self.crop_marks_padding)))

                    crop_marks.append(Line(
                        Point(end_x_point, self.margin.height + (y + 1) * self.card_size.height
                              + y * self.padding + self.crop_marks_padding),
                        Point(end_x_point, self.margin.height + (y + 1) * (self.card_size.height + self.padding)
                              - self.crop_marks_padding)))

        return crop_marks

    # TODO: Extract crop marks calculation from sheet class,
    # think again about it in the future, maybe it is not the best idea
    @property
    def crop_marks(self) -> list[Line]:
        """Return the crop marks to be drawn in each page."""
        if self.__crop_marks is None:
            self.__crop_marks = (
                self._calculate_border_horizontal_crop_marks() +
                self._calculate_middle_horizontal_crop_marks() +
                self._calculate_border_vertical_crop_marks() +
                self._calculate_middle_vertical_crop_marks()
            )

        return self.__crop_marks

    @property
    def pages(self) -> int:
        """Return the current number of pages."""
        if not self.__cards:
            return 0
        return ceil(len(self.__cards) / self.num_cards_per_page)

    @property
    def two_sided(self) -> bool:
        """Return if sheet cards have two sides."""
        if not self.__cards:
            raise AttributeError("Deck is empty, is not yet one sided or two sided ")
        return self.__cards[0].two_sided

    def page_cards(self, page: int) -> list[Card]:
        """Return the cards that belong to a page."""
        if not self.__cards:
            return ()
        return tuple(self.__cards[(page - 1)*self.num_cards_per_page:page*self.num_cards_per_page])
