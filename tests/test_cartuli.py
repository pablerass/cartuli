import pytest

from math import isclose

from cartuli import Card, Coordinates, Position, Sheet, Size, A4, mm


def test_card():
    card1 = Card("c1.jpg")
    card2 = Card("f1.jpg", "b1.jpg")

    assert not card1.two_sided
    assert card2.two_sided


def test_card_sheet():
    sheet = Sheet("test", card_size=Card.STANDARD_SIZE)
    assert sheet.card_size == Card.STANDARD_SIZE
    assert sheet.size == A4

    with pytest.raises(ValueError):
        sheet.add_cards(Card("f1.jpg", size=Card.CHIMERA_SIZE))

def test_sheet_calculations():
    assert Sheet("t", card_size=Card.STANDARD_SIZE).cards_per_sheet == Size(3, 3)
    assert Sheet("t", card_size=Card.MINI_CHIMERA_SIZE).cards_per_sheet == Size(4, 4)
    assert Sheet("t", card_size=Card.MINI_USA_SIZE,
                 margin=2*mm, padding=0*mm).cards_per_sheet == Size(5, 4)
    assert Sheet("t", card_size=Card.TAROT_SIZE).cards_per_sheet == Size(2, 2)

    card_sheet = Sheet("t", card_size=Card.STANDARD_SIZE,
                       margin=5*mm, padding=4*mm)
    assert card_sheet.card_position(Coordinates(0, 0)) == Position(5*mm, 5*mm)
    assert card_sheet.card_position(Coordinates(2, 0)) == Position(140*mm, 5*mm)
    assert card_sheet.card_position(Coordinates(1, 2)) == Position(72.5*mm, 189*mm)
    with pytest.raises(ValueError):
        assert card_sheet.card_position(Coordinates(3, 1))


def test_sheet_pages():
    cards_set_1 = [
        Card("f"),
        Card("f"),
        Card("f"),
        Card("f"),
        Card("f"),
        Card("f"),
        Card("f")
    ]
    cards_set_2 = [
        Card("f", "b"),
        Card("f"),
        Card("f", "b"),
        Card("f")
    ]
    sheet = Sheet("t", card_size=Card.STANDARD_SIZE)

    assert sheet.pages == 0
    assert not sheet.two_sided

    sheet.add_cards(cards_set_1)
    assert sheet.pages == 1
    assert not sheet.two_sided

    sheet.add_cards(cards_set_2)
    assert sheet.pages == 2
    assert sheet.two_sided

    sheet.add_cards(cards_set_1)
    assert sheet.pages == 2
    assert sheet.two_sided

    sheet.add_cards(cards_set_1)
    assert sheet.pages == 3
    assert sheet.two_sided