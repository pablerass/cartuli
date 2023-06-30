import pytest

from cartuli.card import Card, CardImage
from cartuli.measure import STANDARD, CHIMERA, Size


def test_card_image(fixture_file):
    with pytest.raises(FileNotFoundError):
        CardImage("unexistent_image.png", size=STANDARD)

    assert CardImage(fixture_file("card.png"), STANDARD).resolution == Size(6.666, 6.815)
    assert CardImage(fixture_file("card.png"), STANDARD*2).resolution == Size(6.666, 6.815)/2


def test_card_from_path(random_image):
    card1 = Card(random_image, size=STANDARD)
    card2 = Card(random_image, random_image, size=STANDARD)

    assert not card1.two_sided
    assert card2.two_sided

    with pytest.raises(FileNotFoundError):
        Card("unexistent_image.png", size=STANDARD)
    with pytest.raises(ValueError):
        Card(random_image)


def test_card_from_card_image(random_image):
    with pytest.raises(ValueError):
        Card(CardImage(random_image, size=STANDARD), size=CHIMERA)

    with pytest.raises(ValueError):
        Card(CardImage(random_image, size=STANDARD), CardImage(random_image, size=CHIMERA))


def test_card_add_back(random_image):
    card1 = Card(random_image, size=STANDARD)
    card1.back = random_image
    with pytest.raises(AttributeError):
        card1.back = random_image

    card2 = Card(random_image, random_image, size=STANDARD)
    with pytest.raises(AttributeError):
        card2.back = random_image


def test_missmatch_sizes(random_image):
    with pytest.raises(ValueError):
        Card(CardImage(random_image, CHIMERA), size=STANDARD)
