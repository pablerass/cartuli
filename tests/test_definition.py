import pytest

from cartuli.definition import Definition


def test_not_exists(fixture_file):
    with pytest.raises(FileNotFoundError):
        Definition.from_file(fixture_file("non_exitent_file"))


def test_directory(fixture_file):
    with pytest.raises(IsADirectoryError):
        Definition.from_file(fixture_file(".."))


def test_file(fixture_file):
    assert Definition.from_file(fixture_file("simple-cartulifile.yml")).values == {}


def test_definition():
    pass