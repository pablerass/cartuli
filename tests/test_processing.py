from cartuli.processing import _get_rotation_angle, _discard_outliers


def test_rotation_angle():
    assert _get_rotation_angle([0, 0, 1, 0]) == 0.0     # Horizontal
    assert _get_rotation_angle([0, 0, 0, 1]) == 0.0     # Vertical
    assert _get_rotation_angle([1, 0, 0, 0]) == 0.0     # Horizontal
    assert _get_rotation_angle([0, 1, 0, 0]) == 0.0     # Vertical
    assert _get_rotation_angle([0, 0, 1, 1]) == 45.0
    assert _get_rotation_angle([1, 1, 0, 0]) == 45.0
    assert _get_rotation_angle([0, 1, 1, 0]) == -45.0
    assert _get_rotation_angle([1, 0, 0, 1]) == -45.0


def test_discard_outliers():
    assert _discard_outliers([0, 0, 0, 0, 10]) == [0, 0, 0, 0]
    assert _discard_outliers([0, 0, 0, 0]) == [0, 0, 0, 0]
