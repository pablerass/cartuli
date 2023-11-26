import pytest

from math import isclose

from cartuli.card import Card
from cartuli.measure import Coordinates, Point, Size, Line, mm, inch, A4, STANDARD, MINI_CHIMERA, MINI_USA, TAROT
from cartuli.sheet import Sheet


def test_sheet_cards_per_page(random_card_image):
    sheet_standard = Sheet(
        Card(random_card_image(size=STANDARD)), size=A4, print_margin=1*inch, padding=4*mm)
    assert sheet_standard.cards_per_page == Size(2, 2)
    assert sheet_standard.num_cards_per_page == 4

    sheet_standard = Sheet(Card(random_card_image(size=STANDARD)), size=A4, print_margin=2*mm, padding=4*mm)
    assert sheet_standard.cards_per_page == Size(3, 3)
    assert sheet_standard.num_cards_per_page == 9

    sheet_chimera = Sheet(
        Card(random_card_image(size=MINI_CHIMERA)), size=A4, print_margin=2*mm, padding=4*mm)
    assert sheet_chimera.cards_per_page == Size(4, 4)
    assert sheet_chimera.num_cards_per_page == 16

    sheet_mini_usa = Sheet(Card(random_card_image(size=MINI_USA)), size=A4, print_margin=2*mm, padding=0)
    assert sheet_mini_usa.cards_per_page == Size(5, 4)
    assert sheet_mini_usa.num_cards_per_page == 20

    sheet_tarot = Sheet(Card(random_card_image(size=TAROT)), size=A4, print_margin=2*mm, padding=4*mm)
    assert sheet_tarot.cards_per_page == Size(2, 2)
    assert sheet_tarot.num_cards_per_page == 4


def test_sheet_card_page(random_card_image):
    card_sheet = Sheet(Card(random_card_image(size=STANDARD)), size=A4, print_margin=5*mm, padding=4*mm)
    assert card_sheet.card_page(4) == 1
    assert card_sheet.card_page(10) == 2
    assert card_sheet.card_page(30) == 4


def test_sheet_card_coordinates(random_card_image):
    card_sheet = Sheet(Card(random_card_image(size=STANDARD)), size=A4, print_margin=5*mm, padding=4*mm)
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
    card_sheet = Sheet(Card(random_card_image(size=STANDARD)), size=A4, print_margin=5*mm, padding=4*mm)
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
    card_sheet = Sheet(Card(random_card_image(size=STANDARD)), size=A4, print_margin=5*mm, padding=4*mm)
    assert (card_sheet.card_position(Coordinates(0, 0)) ==
            Point(5.75*mm, A4.height - STANDARD.height - 12.5*mm))
    assert (card_sheet.card_position(Coordinates(2, 0)) ==
            Point(140.75*mm, A4.height - STANDARD.height - 12.5*mm))
    assert (card_sheet.card_position(Coordinates(1, 2)) ==
            Point(73.25*mm, A4.height - STANDARD.height - 196.5*mm))
    with pytest.raises(ValueError):
        assert card_sheet.card_position(Coordinates(4, 2))


def test_sheet_margins(random_card_image):
    card_sheet = Sheet(Card(random_card_image(size=STANDARD)), size=A4, print_margin=5*mm, padding=4*mm)
    assert isclose(card_sheet.margin.height, 12.5*mm)
    assert isclose(card_sheet.margin.width, 5.75*mm)


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
    sheet = Sheet(size=A4, print_margin=2*mm, padding=4*mm)

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


def test_sheet_single_card_crop_marks(random_card_image):
    sheet = Sheet(Card(random_card_image(size=A4/2)), size=A4, print_margin=3*mm, padding=4*mm,
                  crop_marks_padding=1*mm)

    print_margin = sheet.print_margin
    crop_marks_padding = sheet.crop_marks_padding
    sheet_size = sheet.size
    card_size = sheet.card_size
    margin = sheet.margin

    #   V1    V2
    #    |    |
    # H1- ---- -H3
    #    |    |
    #    |Card|
    #    |    |
    # H2- ---- -H4
    #    |    |
    #   V3    V4
    assert sorted(sheet._calculate_border_horizontal_crop_marks()) == sorted([
        # H1
        Line(Point(print_margin, margin.height),
             Point(margin.width - crop_marks_padding, margin.height)),
        # H2
        Line(Point(print_margin, margin.height + card_size.height),
             Point(margin.width - crop_marks_padding, margin.height + card_size.height)),
        # H3
        Line(Point(sheet_size.width - margin.width + crop_marks_padding, margin.height),
             Point(sheet_size.width - print_margin, sheet.margin.height)),
        # H4
        Line(Point(sheet_size.width - margin.width + crop_marks_padding, margin.height + card_size.height),
             Point(sheet_size.width - print_margin, margin.height + card_size.height)),
    ])
    assert sheet._calculate_middle_horizontal_crop_marks() == []
    assert sorted(sheet._calculate_border_vertical_crop_marks()) == sorted([
        # V1
        Line(Point(margin.width, print_margin),
             Point(margin.width, margin.height - crop_marks_padding)),
        # V2
        Line(Point(margin.width + card_size.width, print_margin),
             Point(margin.width + card_size.width, margin.height - crop_marks_padding)),
        # V3
        Line(Point(margin.width, sheet_size.height - margin.height + crop_marks_padding),
             Point(margin.width, sheet_size.height - print_margin)),
        # V4
        Line(Point(margin.width + card_size.width, sheet_size.height - margin.height + crop_marks_padding),
             Point(margin.width + card_size.width, sheet_size.height - print_margin)),
    ])
    assert sheet._calculate_middle_vertical_crop_marks() == []


def test_sheet_crop_marks(random_card_image):
    sheet = Sheet(Card(random_card_image(size=STANDARD)), size=A4, print_margin=3*mm, padding=4*mm,
                  crop_marks_padding=1*mm)

    # print_margin = sheet.print_margin
    # padding = sheet.padding
    # crop_marks_padding = sheet.crop_marks_padding
    sheet_size = sheet.size
    # card_size = sheet.card_size
    # margin = sheet.margin

    #    V1    V2     V3    V4     V5    V6
    #    |      |     |      |     |      |
    # H1- ------ -H7-- ------ -H13- ------ -H19
    #    |      |     |      |     |      |
    #    | C1x1 |     | C2x1 |     | C3x1 |
    #    |      |     |      |     |      |
    # H2- ------ -H8-- ------ -H14- ------ -H20
    #    |      |     |      |     |      |
    #    V7    V8     V9   V10     V11  V12
    #    |      |     |      |     |      |
    # H3- ------ -H9-- ------ -H15- ------ -H21
    #    |      |     |      |     |      |
    #    | C1x2 |     | C2x2 |     | C3x2 |
    #    |      |     |      |     |      |
    # H4- ------ -H10- ------ -H16- ------ -H22
    #    |      |     |      |     |      |
    #    V13  V14     V15  V16     V17  V18
    #    |      |     |      |     |      |
    # H5- ------ -H11- ------ -H17- ------ -H23
    #    |      |     |      |     |      |
    #    | C1x3 |     | C2x3 |     | C3x3 |
    #    |      |     |      |     |      |
    # H6- ------ -H12- ------ -H18- ------ -H24
    #    |      |     |      |     |      |
    #    V19  V20     V21  V22     V23  V24
    #
    # Horizontal margin = 5.75
    # Vertical margin = 12.5
    assert sorted(sheet._calculate_border_horizontal_crop_marks()) == sorted([
        # H1
        Line(Point(3*mm, 12.5*mm), Point(4.75*mm, 12.5*mm)),
        # H2
        Line(Point(3*mm, 100.5*mm), Point(4.75*mm, 100.5*mm)),
        # H3
        Line(Point(3*mm, 104.5*mm), Point(4.75*mm, 104.5*mm)),
        # H4
        Line(Point(3*mm, 192.5*mm), Point(4.75*mm, 192.5*mm)),
        # H5
        Line(Point(3*mm, 196.5*mm), Point(4.75*mm, 196.5*mm)),
        # H6
        Line(Point(3*mm, 284.5*mm), Point(4.75*mm, 284.5*mm)),
        # H19
        Line(Point(sheet_size.width - 4.75*mm, 12.5*mm), Point(sheet_size.width - 3*mm, 12.5*mm)),
        # H20
        Line(Point(sheet_size.width - 4.75*mm, 100.5*mm), Point(sheet_size.width - 3*mm, 100.5*mm)),
        # H21
        Line(Point(sheet_size.width - 4.75*mm, 104.5*mm), Point(sheet_size.width - 3*mm, 104.5*mm)),
        # H22
        Line(Point(sheet_size.width - 4.75*mm, 192.5*mm), Point(sheet_size.width - 3*mm, 192.5*mm)),
        # H23
        Line(Point(sheet_size.width - 4.75*mm, 196.5*mm), Point(sheet_size.width - 3*mm, 196.5*mm)),
        # H24
        Line(Point(sheet_size.width - 4.75*mm, 284.5*mm), Point(sheet_size.width - 3*mm, 284.5*mm))
    ])
    assert sorted(sheet._calculate_middle_horizontal_crop_marks()) == sorted([
        # H7
        Line(Point(70.25*mm, 12.5*mm), Point(72.25*mm, 12.5*mm)),
        # H8
        Line(Point(70.25*mm, 100.5*mm), Point(72.25*mm, 100.5*mm)),
        # H9
        Line(Point(70.25*mm, 104.5*mm), Point(72.25*mm, 104.5*mm)),
        # H10
        Line(Point(70.25*mm, 192.5*mm), Point(72.25*mm, 192.5*mm)),
        # H11
        Line(Point(70.25*mm, 196.5*mm), Point(72.25*mm, 196.5*mm)),
        # H12
        Line(Point(70.25*mm, 284.5*mm), Point(72.25*mm, 284.5*mm)),
        # H13
        Line(Point(137.75*mm, 12.5*mm), Point(139.75*mm, 12.5*mm)),
        # H14
        Line(Point(137.75*mm, 100.5*mm), Point(139.75*mm, 100.5*mm)),
        # H15
        Line(Point(137.75*mm, 104.5*mm), Point(139.75*mm, 104.5*mm)),
        # H16
        Line(Point(137.75*mm, 192.5*mm), Point(139.75*mm, 192.5*mm)),
        # H17
        Line(Point(137.75*mm, 196.5*mm), Point(139.75*mm, 196.5*mm)),
        # H18
        Line(Point(137.75*mm, 284.5*mm), Point(139.75*mm, 284.5*mm)),
    ])
    assert sorted(sheet._calculate_border_vertical_crop_marks()) == sorted([
        # V1
        Line(Point(5.75*mm, 3*mm), Point(5.75*mm, 11.5*mm)),
        # V2
        Line(Point(69.25*mm, 3*mm), Point(69.25*mm, 11.5*mm)),
        # V3
        Line(Point(73.25*mm, 3*mm), Point(73.25*mm, 11.5*mm)),
        # V4
        Line(Point(136.75*mm, 3*mm), Point(136.75*mm, 11.5*mm)),
        # V5
        Line(Point(140.75*mm, 3*mm), Point(140.75*mm, 11.5*mm)),
        # V6
        Line(Point(204.25*mm, 3*mm), Point(204.25*mm, 11.5*mm)),
        # V19
        Line(Point(5.75*mm, sheet_size.height - 11.5*mm), Point(5.75*mm, sheet_size.height - 3*mm)),
        # V20
        Line(Point(69.25*mm, sheet_size.height - 11.5*mm), Point(69.25*mm, sheet_size.height - 3*mm)),
        # V21
        Line(Point(73.25*mm, sheet_size.height - 11.5*mm), Point(73.25*mm, sheet_size.height - 3*mm)),
        # V22
        Line(Point(136.75*mm, sheet_size.height - 11.5*mm), Point(136.75*mm, sheet_size.height - 3*mm)),
        # V23
        Line(Point(140.75*mm, sheet_size.height - 11.5*mm), Point(140.75*mm, sheet_size.height - 3*mm)),
        # V24
        Line(Point(204.25*mm, sheet_size.height - 11.5*mm), Point(204.25*mm, sheet_size.height - 3*mm)),
    ])
    assert sorted(sheet._calculate_middle_vertical_crop_marks()) == sorted([
        # V7
        Line(Point(5.75*mm, 101.5*mm), Point(5.75*mm, 103.5*mm)),
        # V8
        Line(Point(69.25*mm, 101.5*mm), Point(69.25*mm, 103.5*mm)),
        # V9
        Line(Point(73.25*mm, 101.5*mm), Point(73.25*mm, 103.5*mm)),
        # V10
        Line(Point(136.75*mm, 101.5*mm), Point(136.75*mm, 103.5*mm)),
        # V11
        Line(Point(140.75*mm, 101.5*mm), Point(140.75*mm, 103.5*mm)),
        # V12
        Line(Point(204.25*mm, 101.5*mm), Point(204.25*mm, 103.5*mm)),
        # V13
        Line(Point(5.75*mm, 193.5*mm), Point(5.75*mm, 195.5*mm)),
        # V14
        Line(Point(69.25*mm, 193.5*mm), Point(69.25*mm, 195.5*mm)),
        # V15
        Line(Point(73.25*mm, 193.5*mm), Point(73.25*mm, 195.5*mm)),
        # V16
        Line(Point(136.75*mm, 193.5*mm), Point(136.75*mm, 195.5*mm)),
        # V17
        Line(Point(140.75*mm, 193.5*mm), Point(140.75*mm, 195.5*mm)),
        # V18
        Line(Point(204.25*mm, 193.5*mm), Point(204.25*mm, 195.5*mm)),
    ])


def test_sheet_two_sides(random_card_image):
    sheet = Sheet(
        Card(random_card_image(size=STANDARD), random_card_image(size=STANDARD)),
        size=A4
    )
    assert sheet.two_sided
