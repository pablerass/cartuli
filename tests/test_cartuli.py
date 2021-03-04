import pytest

from cartuli import Card, Sheet, Size, A4, mm


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

def test_card_calculations():
    #assert Sheet("t", card_size=Card.STANDARD_SIZE).cards_per_sheet() == Size(3, 3)
    #assert Sheet("t", card_size=Card.MINI_CHIMERA_SIZE).cards_per_sheet() == Size(4, 4)
    #assert Sheet("t", card_size=Card.MINI_USA_SIZE,
                 #margin=2*mm, padding=0*mm).cards_per_sheet() == Size(5, 4)
    assert Sheet("t", card_size=Card.TAROT_SIZE).cards_per_sheet() == Size(2, 2)