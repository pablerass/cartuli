from cartuli.card import Card, CardSize


def test_card():
    card1 = Card(CardSize.STANDARD_SIZE, "c1.jpg")
    card2 = Card(CardSize.STANDARD_SIZE, "f1.jpg", "b1.jpg")

    assert not card1.two_sided
    assert card2.two_sided
