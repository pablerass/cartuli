from cartuli.card import Card
from cartuli.measure import STANDARD


def test_card():
    card1 = Card(STANDARD, "c1.jpg")
    card2 = Card(STANDARD, "f1.jpg", "b1.jpg")

    assert not card1.two_sided
    assert card2.two_sided
