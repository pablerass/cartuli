import pytest
from math import pi, sqrt

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


def test_point():
    # Basic operations
    assert Point(9, 0) + Point(1, 10) == Point(10, 10)
    assert Point(3, -1) - Point(6, -2) == Point(-3, 1)
    assert Point(5, 0) * 3 == Point(15, 0)
    assert Point(5, 1) / 5 == Point(1, 0.2)

    # Rotation
    assert Point(1, 0).rotate(pi) == Point(-1, 0)
    assert Point(1, 0).rotate(pi/2, Point(1, 1)) == Point(2, 1)
    assert Point(1, 0).rotate(pi, Point(1, 1)) == Point(1, 2)
    assert Point(1, 0).rotate(pi/2) == Point(0, 1)
    assert Point(1, 0).rotate(pi/4) == Point(1/sqrt(2), 1/sqrt(2))
    assert Point(1, 0).rotate(3*pi/4) == Point(-1/sqrt(2), 1/sqrt(2))
