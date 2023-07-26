from cartuli.card import CardImage, Card
from cartuli.deck import Deck
from cartuli.measure import STANDARD


def test_card_image_name(random_image):
    card_image = CardImage(random_image(), size=STANDARD)
    assert not card_image.name
    Card(card_image, name='card')
    assert card_image.name == 'card_front'

    card_image = CardImage(random_image(), name='card_image', size=STANDARD)
    assert card_image.name == 'card_image'
    Card(card_image, name='card')
    assert card_image.name == 'card_image'


def test_card_name(random_card_image):
    cards = [Card(random_card_image()) for _ in range(5)]
    cards[1].name = 'c2'
    Deck(cards)
    assert not cards[0].name
    assert cards[1].name == 'c2'
    assert all(not c.name for c in cards[2:])

    assert not cards[0].front.name
    assert cards[1].front.name == 'c2_front'

    Deck(cards, name='deck')
    assert cards[0].name == 'deck_1'
    assert cards[1].name == 'c2'
    assert [c.name for c in cards[2:]] == ['deck_3', 'deck_4', 'deck_5']

    assert cards[0].front.name == 'deck_1_front'
    assert cards[1].front.name == 'c2_front'
