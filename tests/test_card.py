import pytest

from cartuli.card import Card, CardImage
from cartuli.measure import STANDARD, CHIMERA


def test_card():
    card1 = Card(STANDARD, "c1.jpg")
    card2 = Card(STANDARD, "f1.jpg", "b1.jpg")

    assert not card1.two_sided
    assert card2.two_sided


def test_invalid_card():
    with pytest.raises(ValueError):
        Card(STANDARD, CardImage("c1.jpg", CHIMERA))
