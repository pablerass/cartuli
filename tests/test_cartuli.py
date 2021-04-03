import pytest

from math import isclose

from cartuli import Card, Coordinates, Position, Sheet, Size, A4, mm


def test_card():
    card1 = Card("c1.jpg")
    card2 = Card("f1.jpg", "b1.jpg")

    assert not card1.two_sided
    assert card2.two_sided


def test_sheet_add_card():
    sheet = Sheet("test", card_size=Card.STANDARD_SIZE)
    assert sheet.card_size == Card.STANDARD_SIZE
    assert sheet.size == A4

    with pytest.raises(ValueError):
        sheet.add_cards(Card("f1.jpg", size=Card.CHIMERA_SIZE))


def test_sheet_cards_per_page():
    sheet_standard = Sheet("t", card_size=Card.STANDARD_SIZE)
    assert sheet_standard.cards_per_page == Size(3, 3)
    assert sheet_standard.num_cards_per_page == 9

    sheet_chimera = Sheet("t", card_size=Card.MINI_CHIMERA_SIZE)
    assert sheet_chimera.cards_per_page == Size(4, 4)
    assert sheet_chimera.num_cards_per_page == 16

    sheet_mini_usa = Sheet("t", card_size=Card.MINI_USA_SIZE,
                           margin=2*mm, padding=0*mm)
    assert sheet_mini_usa.cards_per_page == Size(5, 4)
    assert sheet_mini_usa.num_cards_per_page == 20

    sheet_tarot = Sheet("t", card_size=Card.TAROT_SIZE)
    assert sheet_tarot.cards_per_page == Size(2, 2)
    assert sheet_tarot.num_cards_per_page == 4


def test_sheet_card_page():
    card_sheet = Sheet("t", card_size=Card.STANDARD_SIZE,
                       margin=5*mm, padding=4*mm)
    assert card_sheet.card_page(4) == 1
    assert card_sheet.card_page(10) == 2
    assert card_sheet.card_page(30) == 4


def test_sheet_card_coordinates():
    card_sheet = Sheet("t", card_size=Card.STANDARD_SIZE,
                       margin=5*mm, padding=4*mm)
    assert card_sheet.card_coordinates(1) == Coordinates(1, 1)
    assert card_sheet.card_coordinates(4) == Coordinates(1, 2)
    assert card_sheet.card_coordinates(7) == Coordinates(1, 3)


def test_sheet_card_position():
    card_sheet = Sheet("t", card_size=Card.STANDARD_SIZE,
                       margin=5*mm, padding=4*mm)
    assert card_sheet.card_position(Coordinates(1, 1)) == Position(5*mm, 5*mm)
    assert card_sheet.card_position(Coordinates(3, 1)) == Position(140*mm, 5*mm)
    assert card_sheet.card_position(Coordinates(2, 3)) == Position(72.5*mm, 189*mm)
    with pytest.raises(ValueError):
        assert card_sheet.card_position(Coordinates(4, 2))


def test_sheet_page_cards():
    cards_set_1 = [
        Card("f01"),
        Card("f02"),
        Card("f03"),
        Card("f04"),
        Card("f05"),
        Card("f06"),
        Card("f07")
    ]
    cards_set_2 = [
        Card("f08", "b08"),
        Card("f09"),
        Card("f10", "b10"),
        Card("f11")
    ]
    sheet = Sheet("t", card_size=Card.STANDARD_SIZE)
    num_cards_per_page = sheet.num_cards_per_page

    assert sheet.pages == 0
    assert not sheet.two_sided
    assert sheet.page_cards(1) == []

    sheet.add_cards(cards_set_1)
    assert sheet.pages == 1
    assert not sheet.two_sided
    assert sheet.page_cards(1) == cards_set_1
    assert sheet.page_cards(2) == []

    sheet.add_cards(cards_set_2)
    assert sheet.pages == 2
    assert sheet.two_sided
    assert sheet.page_cards(1) == (cards_set_1 + cards_set_2)[:num_cards_per_page]
    assert sheet.page_cards(2) == (cards_set_1 + cards_set_2)[num_cards_per_page:]

    sheet.add_cards(cards_set_1)
    assert sheet.pages == 2
    assert sheet.two_sided
    assert sheet.page_cards(1) == (cards_set_1 + cards_set_2)[:num_cards_per_page]
    assert sheet.page_cards(2) == (cards_set_1 + cards_set_2 + cards_set_1)[num_cards_per_page:]

    sheet.add_cards(cards_set_1)
    assert sheet.pages == 3
    assert sheet.two_sided