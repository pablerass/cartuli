from cartuli import Card


def test_card():
    card1 = Card("c1.jpg")
    card2 = Card("f1.jpg", "b1.jpg")

    assert not card1.two_sided
    assert card2.two_sided
