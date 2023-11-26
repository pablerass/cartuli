import pytest

from cartuli.measure import Line, Point, Size, mm, A4, MINI_USA


def test_size():
    assert Size.from_str("(3*mm, 4*mm)") == Size(3*mm, 4*mm)
    assert Size.from_str("A4") == A4
    assert Size.from_str("MINI_USA") == MINI_USA
    assert Size(3*mm, 4*mm) * 4 == Size(12*mm, 16*mm)

    with pytest.raises(ValueError):
        Size.from_str("[3*mm, 4*mm]") == Size(3*mm, 4*mm)
    with pytest.raises(ValueError):
        Size.from_str("Size")


def test_line():
    a = Point(0, 0)
    b = Point(1, 1)

    assert Line(a, b) == Line(b, a)
