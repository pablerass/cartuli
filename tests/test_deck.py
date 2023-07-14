import pytest

from cartuli.card import Card
from cartuli.deck import Deck
from cartuli.measure import STANDARD, CHIMERA


def test_deck(random_image):
    with pytest.raises(ValueError):
        Deck(Card(random_image(), size=STANDARD), size=CHIMERA)

    deck = Deck(Card(random_image(), size=STANDARD))
    assert len(deck) == 1
    assert not deck.two_sided

    with pytest.raises(ValueError):
        deck.add(Card(random_image(), size=CHIMERA))


def test_deck_with_default_back(random_card_image):
    default_back_image = random_card_image()
    deck = Deck(Card(random_card_image()), default_back=default_back_image)
    assert deck.two_sided
    first_card = Card(random_card_image(), size=STANDARD)
    deck.add(first_card)
    assert deck.cards[1] == first_card
    assert deck.cards[1].back == default_back_image
    second_card_back_image = random_card_image()
    second_card = Card(random_card_image(), second_card_back_image, size=STANDARD)
    deck.add(second_card)
    assert deck.cards[2] == second_card
    assert deck.cards[2].back != default_back_image
    assert deck.cards[2].back == second_card_back_image
