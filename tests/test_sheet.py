import pytest

from math import isclose

from cartuli.card import Card
from cartuli.measure import Coordinates, Point, Size, Line, mm, inch, A4, STANDARD, MINI_CHIMERA, MINI_USA, TAROT
from cartuli.sheet import Sheet


def test_sheet_cards_per_page(random_card_image):
    sheet_standard = Sheet(
        Card(random_card_image(size=STANDARD)), size=A4, margin=2*mm, padding=4*mm, print_margin=1*inch)
    assert sheet_standard.cards_per_page == Size(2, 2)
    assert sheet_standard.num_cards_per_page == 4

    sheet_standard = Sheet(Card(random_card_image(size=STANDARD)), size=A4, margin=2*mm, padding=4*mm, print_margin=0)
    assert sheet_standard.cards_per_page == Size(3, 3)
    assert sheet_standard.num_cards_per_page == 9

    sheet_chimera = Sheet(
        Card(random_card_image(size=MINI_CHIMERA)), size=A4, margin=2*mm, padding=4*mm, print_margin=0)
    assert sheet_chimera.cards_per_page == Size(4, 4)
    assert sheet_chimera.num_cards_per_page == 16

    sheet_mini_usa = Sheet(Card(random_card_image(size=MINI_USA)), size=A4, margin=2*mm, padding=0, print_margin=0)
    assert sheet_mini_usa.cards_per_page == Size(5, 4)
    assert sheet_mini_usa.num_cards_per_page == 20

    sheet_tarot = Sheet(Card(random_card_image(size=TAROT)), size=A4, margin=2*mm, padding=4*mm, print_margin=0)
    assert sheet_tarot.cards_per_page == Size(2, 2)
    assert sheet_tarot.num_cards_per_page == 4


def test_sheet_card_page(random_card_image):
    card_sheet = Sheet(Card(random_card_image(size=STANDARD)), size=A4, margin=5*mm, padding=4*mm, print_margin=0)
    assert card_sheet.card_page(4) == 1
    assert card_sheet.card_page(10) == 2
    assert card_sheet.card_page(30) == 4


def test_sheet_card_coordinates(random_card_image):
    card_sheet = Sheet(Card(random_card_image(size=STANDARD)), size=A4, margin=5*mm, padding=4*mm, print_margin=0)
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


def test_sheet_card_coordinates_back(random_card_image):
    card_sheet = Sheet(Card(random_card_image(size=STANDARD)), size=A4, margin=5*mm, padding=4*mm, print_margin=0)
    assert card_sheet.card_coordinates(1, back=True) == Coordinates(2, 0)
    assert card_sheet.card_coordinates(2, back=True) == Coordinates(1, 0)
    assert card_sheet.card_coordinates(3, back=True) == Coordinates(0, 0)
    assert card_sheet.card_coordinates(4, back=True) == Coordinates(2, 1)
    assert card_sheet.card_coordinates(5, back=True) == Coordinates(1, 1)
    assert card_sheet.card_coordinates(6, back=True) == Coordinates(0, 1)
    assert card_sheet.card_coordinates(7, back=True) == Coordinates(2, 2)
    assert card_sheet.card_coordinates(8, back=True) == Coordinates(1, 2)
    assert card_sheet.card_coordinates(9, back=True) == Coordinates(0, 2)
    assert card_sheet.card_coordinates(10, back=True) == Coordinates(2, 0)
    assert card_sheet.card_coordinates(18, back=True) == Coordinates(0, 2)


def test_sheet_card_position(random_card_image):
    card_sheet = Sheet(Card(random_card_image(size=STANDARD)), size=A4, margin=5*mm, padding=4*mm, print_margin=0)
    assert (card_sheet.card_position(Coordinates(0, 0)) ==
            Point(5.75*mm, A4.height - STANDARD.height - 12.5*mm))
    assert (card_sheet.card_position(Coordinates(2, 0)) ==
            Point(140.75*mm, A4.height - STANDARD.height - 12.5*mm))
    assert (card_sheet.card_position(Coordinates(1, 2)) ==
            Point(73.25*mm, A4.height - STANDARD.height - 196.5*mm))
    with pytest.raises(ValueError):
        assert card_sheet.card_position(Coordinates(4, 2))


def test_sheet_margins(random_card_image):
    card_sheet = Sheet(Card(random_card_image(size=STANDARD)), size=A4, margin=5*mm, padding=4*mm, print_margin=0)
    assert isclose(card_sheet.horizontal_margin, 5.75*mm)
    assert isclose(card_sheet.vertical_margin, 12.5*mm)


def test_sheet_page_cards(random_image, random_card_image):
    cards_set_1 = (
        Card(random_image(), size=STANDARD),
        Card(random_image(), size=STANDARD),
        Card(random_image(), size=STANDARD),
        Card(random_image(), size=STANDARD),
        Card(random_image(), size=STANDARD),
        Card(random_image(), size=STANDARD),
        Card(random_image(), size=STANDARD)
    )
    cards_set_2 = (
        Card(random_image(), size=STANDARD),
        Card(random_image(), size=STANDARD),
        Card(random_image(), size=STANDARD),
        Card(random_image(), size=STANDARD)
    )
    sheet = Sheet(size=A4, margin=2*mm, padding=4*mm, print_margin=0)

    assert sheet.pages == 0
    with pytest.raises(AttributeError):
        sheet.two_sided
    assert sheet.page_cards(1) == ()

    sheet.add(cards_set_1)
    assert sheet.pages == 1
    assert not sheet.two_sided
    assert sheet.page_cards(1) == cards_set_1
    assert sheet.page_cards(2) == ()

    sheet.add(cards_set_2)
    assert sheet.pages == 2
    assert not sheet.two_sided
    assert sheet.page_cards(1) == (cards_set_1 + cards_set_2)[:sheet.num_cards_per_page]
    assert sheet.page_cards(2) == (cards_set_1 + cards_set_2)[sheet.num_cards_per_page:]

    sheet.add(cards_set_1)
    assert sheet.pages == 2
    assert not sheet.two_sided
    assert sheet.page_cards(1) == (cards_set_1 + cards_set_2)[:sheet.num_cards_per_page]
    assert sheet.page_cards(2) == (cards_set_1 + cards_set_2 + cards_set_1)[sheet.num_cards_per_page:]

    sheet.add(cards_set_1)
    assert sheet.pages == 3
    assert not sheet.two_sided


def test_sheet_crop_marks(random_card_image):
    sheet = Sheet(Card(random_card_image(size=STANDARD)), size=A4, margin=2*mm, padding=4*mm,
                  crop_marks_padding=1*mm, print_margin=3*mm)

    # Horizontal margin = 5.75
    # Vertical margin = 12.5
    assert sorted(sheet.crop_marks) == sorted([
        Line(Point(5.75*mm, 3*mm), Point(5.75*mm, 11.5*mm)),
        Line(Point(5.75*mm, 101.5*mm), Point(5.75*mm, 103.5*mm)),
        Line(Point(5.75*mm, 193.5*mm), Point(5.75*mm, 195.5*mm)),
        Line(Point(5.75*mm, A4.height - 11.5*mm), Point(5.75*mm, A4.height - 3*mm)),
        Line(Point(69.25*mm, 3*mm), Point(69.25*mm, 11.5*mm)),
        Line(Point(69.25*mm, 101.5*mm), Point(69.25*mm, 103.5*mm)),
        Line(Point(69.25*mm, 193.5*mm), Point(69.25*mm, 195.5*mm)),
        Line(Point(69.25*mm, A4.height - 11.5*mm), Point(69.25*mm, A4.height - 3*mm)),
        Line(Point(73.25*mm, 3*mm), Point(73.25*mm, 11.5*mm)),
        Line(Point(73.25*mm, 101.5*mm), Point(73.25*mm, 103.5*mm)),
        Line(Point(73.25*mm, 193.5*mm), Point(73.25*mm, 195.5*mm)),
        Line(Point(73.25*mm, A4.height - 11.5*mm), Point(73.25*mm, A4.height - 3*mm)),
        Line(Point(136.75*mm, 3*mm), Point(136.75*mm, 11.5*mm)),
        Line(Point(136.75*mm, 101.5*mm), Point(136.75*mm, 103.5*mm)),
        Line(Point(136.75*mm, 193.5*mm), Point(136.75*mm, 195.5*mm)),
        Line(Point(136.75*mm, A4.height - 11.5*mm), Point(136.75*mm, A4.height - 3*mm)),
        Line(Point(140.75*mm, 3*mm), Point(140.75*mm, 11.5*mm)),
        Line(Point(140.75*mm, 101.5*mm), Point(140.75*mm, 103.5*mm)),
        Line(Point(140.75*mm, 193.5*mm), Point(140.75*mm, 195.5*mm)),
        Line(Point(140.75*mm, A4.height - 11.5*mm), Point(140.75*mm, A4.height - 3*mm)),
        Line(Point(204.25*mm, 3*mm), Point(204.25*mm, 11.5*mm)),
        Line(Point(204.25*mm, 101.5*mm), Point(204.25*mm, 103.5*mm)),
        Line(Point(204.25*mm, 193.5*mm), Point(204.25*mm, 195.5*mm)),
        Line(Point(204.25*mm, A4.height - 11.5*mm), Point(204.25*mm, A4.height - 3*mm)),
        Line(Point(3*mm, 12.5*mm), Point(4.75*mm, 12.5*mm)),
        Line(Point(70.25*mm, 12.5*mm), Point(72.25*mm, 12.5*mm)),
        Line(Point(137.75*mm, 12.5*mm), Point(139.75*mm, 12.5*mm)),
        Line(Point(A4.width - 4.75*mm, 12.5*mm), Point(A4.width - 3*mm, 12.5*mm)),
        Line(Point(3*mm, 100.5*mm), Point(4.75*mm, 100.5*mm)),
        Line(Point(70.25*mm, 100.5*mm), Point(72.25*mm, 100.5*mm)),
        Line(Point(137.75*mm, 100.5*mm), Point(139.75*mm, 100.5*mm)),
        Line(Point(A4.width - 4.75*mm, 100.5*mm), Point(A4.width - 3*mm, 100.5*mm)),
        Line(Point(3*mm, 104.5*mm), Point(4.75*mm, 104.5*mm)),
        Line(Point(70.25*mm, 104.5*mm), Point(72.25*mm, 104.5*mm)),
        Line(Point(137.75*mm, 104.5*mm), Point(139.75*mm, 104.5*mm)),
        Line(Point(A4.width - 4.75*mm, 104.5*mm), Point(A4.width - 3*mm, 104.5*mm)),
        Line(Point(3*mm, 192.5*mm), Point(4.75*mm, 192.5*mm)),
        Line(Point(70.25*mm, 192.5*mm), Point(72.25*mm, 192.5*mm)),
        Line(Point(137.75*mm, 192.5*mm), Point(139.75*mm, 192.5*mm)),
        Line(Point(A4.width - 4.75*mm, 192.5*mm), Point(A4.width - 3*mm, 192.5*mm)),
        Line(Point(3*mm, 196.5*mm), Point(4.75*mm, 196.5*mm)),
        Line(Point(70.25*mm, 196.5*mm), Point(72.25*mm, 196.5*mm)),
        Line(Point(137.75*mm, 196.5*mm), Point(139.75*mm, 196.5*mm)),
        Line(Point(A4.width - 4.75*mm, 196.5*mm), Point(A4.width - 3*mm, 196.5*mm)),
        Line(Point(3*mm, 284.5*mm), Point(4.75*mm, 284.5*mm)),
        Line(Point(70.25*mm, 284.5*mm), Point(72.25*mm, 284.5*mm)),
        Line(Point(137.75*mm, 284.5*mm), Point(139.75*mm, 284.5*mm)),
        Line(Point(A4.width - 4.75*mm, 284.5*mm), Point(A4.width - 3*mm, 284.5*mm))
    ])


def test_sheet_two_sides(random_card_image):
    sheet = Sheet(
        Card(random_card_image(size=STANDARD), random_card_image(size=STANDARD)),
        size=A4
    )
    assert sheet.two_sided
