import pytest

from cartuli.card import Card
from cartuli.deck import Deck
from cartuli.measure import STANDARD, CHIMERA


def test_deck(random_image):
    with pytest.raises(ValueError):
        Deck(Card(random_image, size=STANDARD), size=CHIMERA)

    deck = Deck(Card(random_image, size=STANDARD))
    assert len(deck) == 1
    assert not deck.two_sided

    with pytest.raises(ValueError):
        deck.add(Card(random_image, size=CHIMERA))


def test_deck_with_back(card_image):
    deck = Deck(Card(card_image), back=card_image)
    assert deck.two_sided
    with pytest.raises(ValueError):
        deck.add(Card(card_image, card_image, size=STANDARD))
