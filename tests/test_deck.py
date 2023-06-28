import pytest

from cartuli.card import Card
from cartuli.deck import Deck
from cartuli.measure import STANDARD, CHIMERA


def test_deck(fixture_file):
    deck = Deck(Card(fixture_file("card.png"), size=STANDARD))
    assert len(deck) == 1

    with pytest.raises(ValueError):
        deck.add_cards(Card(fixture_file("card.png"), size=CHIMERA))
