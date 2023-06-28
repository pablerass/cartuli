import pytest

from cartuli.card import Card, CardImage
from cartuli.measure import STANDARD, CHIMERA, Size


def test_card_image_resolution(fixture_file):
    assert CardImage(fixture_file("card.png"), STANDARD).resolution == Size(6.666, 6.815)
    assert CardImage(fixture_file("card.png"), STANDARD*2).resolution == Size(6.666, 6.815)/2


def test_card_from_path():
    card1 = Card("c1.jpg", size=STANDARD)
    card2 = Card("f1.jpg", "b1.jpg", size=STANDARD)

    assert not card1.two_sided
    assert card2.two_sided

    with pytest.raises(ValueError):
        Card("c1.jpg")


def test_card_from_card_image():
    with pytest.raises(ValueError):
        Card(CardImage("c1.jpg", size=STANDARD), size=CHIMERA)

    with pytest.raises(ValueError):
        Card(CardImage("c1.jpg", size=STANDARD), CardImage("b1.jpg", size=CHIMERA))


def test_missmatch_sizes():
    with pytest.raises(ValueError):
        Card(CardImage("c1.jpg", CHIMERA), size=STANDARD)
