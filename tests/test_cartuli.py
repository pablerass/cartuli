import pytest

from cartuli import Card, Sheet, A4


def test_card():
    card1 = Card("c1.jpg")
    card2 = Card("f1.jpg", "b1.jpg")

    assert not card1.two_sides
    assert card2.two_sides


def test_card_sheet():
    sheet = Sheet("test", card_size=Card.STANDARD_SIZE)
    assert sheet.card_size == Card.STANDARD_SIZE
    assert sheet.size == A4

    with pytest.raises(ValueError):
        sheet.add_cards(Card("f1.jpg", size=Card.CHIMERA_SIZE))