import pytest

from cartuli.definition import Definition
from cartuli.measure import Size, STANDARD, mm


def test_defintion_invalid_file():
    with pytest.raises(FileNotFoundError):
        Definition.from_file("non_exitent_file")
    with pytest.raises(IsADirectoryError):
        Definition.from_file("..")


def test_file(fixture_file):
    pass
    # assert Definition.from_file(fixture_file("simple-cartulifile.yml")).values == {}


def test_empty_definition():
    empty_definition = {
        'decks': {
            'cards': {
                'size': 'STANDARD'
            },
            'tokens': {
                'size': '(44*mm,75*mm)'
            }
        }
    }
    definition = Definition(empty_definition)
    assert definition.decks[0].name == 'cards'
    assert definition.decks[1].name == 'tokens'
    assert definition.decks[0].size == STANDARD
    assert definition.decks[1].size == Size(44*mm,75*mm)