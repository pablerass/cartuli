import pytest

from math import isclose

from cartuli.card import Card, CardSize
from cartuli.measure import Coordinates, Point, Size, Line, mm, A4
from cartuli.sheet import Sheet


def test_sheet_cards_per_page():
    sheet_standard = Sheet(card_size=CardSize.STANDARD_SIZE)
    assert sheet_standard.cards_per_page == Size(3, 3)
    assert sheet_standard.num_cards_per_page == 9

    sheet_chimera = Sheet(card_size=CardSize.MINI_CHIMERA_SIZE)
    assert sheet_chimera.cards_per_page == Size(4, 4)
    assert sheet_chimera.num_cards_per_page == 16

    sheet_mini_usa = Sheet(card_size=CardSize.MINI_USA_SIZE,
                           margin=2*mm, padding=0*mm)
    assert sheet_mini_usa.cards_per_page == Size(5, 4)
    assert sheet_mini_usa.num_cards_per_page == 20

    sheet_tarot = Sheet(card_size=CardSize.TAROT_SIZE)
    assert sheet_tarot.cards_per_page == Size(2, 2)
    assert sheet_tarot.num_cards_per_page == 4


def test_sheet_card_page():
    card_sheet = Sheet(card_size=CardSize.STANDARD_SIZE,
                       margin=5*mm, padding=4*mm, size=A4)
    assert card_sheet.card_page(4) == 1
    assert card_sheet.card_page(10) == 2
    assert card_sheet.card_page(30) == 4


def test_sheet_card_coordinates():
    card_sheet = Sheet(card_size=CardSize.STANDARD_SIZE,
                       margin=5*mm, padding=4*mm, size=A4)
    assert card_sheet.card_coordinates(1) == Coordinates(0, 0)
    assert card_sheet.card_coordinates(2) == Coordinates(1, 0)
    assert card_sheet.card_coordinates(3) == Coordinates(2, 0)
    assert card_sheet.card_coordinates(4) == Coordinates(0, 1)
    assert card_sheet.card_coordinates(5) == Coordinates(1, 1)
    assert card_sheet.card_coordinates(6) == Coordinates(2, 1)
    assert card_sheet.card_coordinates(7) == Coordinates(0, 2)
    assert card_sheet.card_coordinates(8) == Coordinates(1, 2)
    assert card_sheet.card_coordinates(9) == Coordinates(2, 2)
    assert card_sheet.card_coordinates(10) == Coordinates(0, 0)
    assert card_sheet.card_coordinates(18) == Coordinates(2, 2)


def test_sheet_card_position():
    card_sheet = Sheet(card_size=CardSize.STANDARD_SIZE,
                       margin=5*mm, padding=4*mm, size=A4)
    assert card_sheet.card_position(Coordinates(0, 0)) == Point(5.75*mm,
                                                                A4.height - CardSize.STANDARD_SIZE.height - 12.5*mm)
    assert card_sheet.card_position(Coordinates(2, 0)) == Point(140.75*mm,
                                                                A4.height - CardSize.STANDARD_SIZE.height - 12.5*mm)
    assert card_sheet.card_position(Coordinates(1, 2)) == Point(73.25*mm,
                                                                A4.height - CardSize.STANDARD_SIZE.height - 196.5*mm)
    with pytest.raises(ValueError):
        assert card_sheet.card_position(Coordinates(4, 2))


def test_sheet_margins():
    card_sheet = Sheet(card_size=CardSize.STANDARD_SIZE,
                       margin=5*mm, padding=4*mm, size=A4)
    assert isclose(card_sheet.horizontal_margin, 5.75*mm)
    assert isclose(card_sheet.vertical_margin, 12.5*mm)


def test_sheet_page_cards():
    cards_set_1 = [
        Card(CardSize.STANDARD_SIZE, "f01"),
        Card(CardSize.STANDARD_SIZE, "f02"),
        Card(CardSize.STANDARD_SIZE, "f03"),
        Card(CardSize.STANDARD_SIZE, "f04"),
        Card(CardSize.STANDARD_SIZE, "f05"),
        Card(CardSize.STANDARD_SIZE, "f06"),
        Card(CardSize.STANDARD_SIZE, "f07")
    ]
    cards_set_2 = [
        # Card(CardSize.STANDARD_SIZE, "f08", "b08"),
        Card(CardSize.STANDARD_SIZE, "f08"),
        Card(CardSize.STANDARD_SIZE, "f09"),
        # Card(CardSize.STANDARD_SIZE"f10", "b10"),
        Card(CardSize.STANDARD_SIZE, "f10"),
        Card(CardSize.STANDARD_SIZE, "f11")
    ]
    sheet = Sheet(card_size=CardSize.STANDARD_SIZE)
    num_cards_per_page = sheet.num_cards_per_page

    assert sheet.pages == 0
    # assert not sheet.two_sided
    assert sheet.page_cards(1) == []

    sheet.add_cards(cards_set_1)
    assert sheet.pages == 1
    # assert not sheet.two_sided
    assert sheet.page_cards(1) == cards_set_1
    assert sheet.page_cards(2) == []

    sheet.add_cards(cards_set_2)
    assert sheet.pages == 2
    # assert sheet.two_sided
    assert sheet.page_cards(1) == (cards_set_1 + cards_set_2)[:num_cards_per_page]
    assert sheet.page_cards(2) == (cards_set_1 + cards_set_2)[num_cards_per_page:]

    sheet.add_cards(cards_set_1)
    assert sheet.pages == 2
    # assert sheet.two_sided
    assert sheet.page_cards(1) == (cards_set_1 + cards_set_2)[:num_cards_per_page]
    assert sheet.page_cards(2) == (cards_set_1 + cards_set_2 + cards_set_1)[num_cards_per_page:]

    sheet.add_cards(cards_set_1)
    assert sheet.pages == 3
    # assert sheet.two_sided


def test_sheet_crop_marks():
    card_sheet = Sheet(card_size=CardSize.STANDARD_SIZE,
                       margin=5*mm, padding=4*mm, size=A4)

    assert sorted(card_sheet.crop_marks) == sorted([
        Line(Point(5.75*mm, A4.height), Point(5.75*mm, 0*mm)),
        Line(Point(69.25*mm, A4.height), Point(69.25*mm, 0*mm)),
        Line(Point(73.25*mm, A4.height), Point(73.25*mm, 0*mm)),
        Line(Point(136.75*mm, A4.height), Point(136.75*mm, 0*mm)),
        Line(Point(140.75*mm, A4.height), Point(140.75*mm, 0*mm)),
        Line(Point(204.25*mm, A4.height), Point(204.25*mm, 0*mm)),
        Line(Point(0*mm, A4.height - 12.5*mm), Point(card_sheet.size.width, A4.height - 12.5*mm)),
        Line(Point(0*mm, A4.height - 100.5*mm), Point(card_sheet.size.width, A4.height - 100.5*mm)),
        Line(Point(0*mm, A4.height - 104.5*mm), Point(card_sheet.size.width, A4.height - 104.5*mm)),
        Line(Point(0*mm, A4.height - 192.5*mm), Point(card_sheet.size.width, A4.height - 192.5*mm)),
        Line(Point(0*mm, A4.height - 196.5*mm), Point(card_sheet.size.width, A4.height - 196.5*mm)),
        Line(Point(0*mm, A4.height - 284.5*mm), Point(card_sheet.size.width, A4.height - 284.5*mm)),
    ])
