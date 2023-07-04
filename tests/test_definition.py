import pytest

from cartuli.definition import Definition
from cartuli.measure import Size, STANDARD, A4, mm


def test_defintion_invalid_file():
    with pytest.raises(FileNotFoundError):
        Definition.from_file("non_exitent_file")
    with pytest.raises(FileNotFoundError):
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
    assert definition.decks[1].size == Size(44*mm, 75*mm)


def test_definition(random_image):
    random_image_dir = random_image("front").parent
    for _ in range(0, 4):
        random_image("front")
    simple_definition = {
        'decks': {
            'cards': {
                'size': 'STANDARD',
                'front': {
                    'images': str(random_image_dir / "*.png"),
                    'bleed': '2*mm'
                },
                'back': {
                    'image': str(random_image("back"))
                }
            }
        },
        'outputs': {
            'sheet': {
                'size': 'A4',
                'print_margin': '3*mm'
            }
        }
    }
    definition = Definition(simple_definition)
    assert definition.decks[0].name == 'cards'
    assert definition.decks[0].size == STANDARD
    assert len(definition.decks[0]) == 5
    assert definition.decks[0].two_sided
    assert definition.decks[0].cards[0].front.bleed == 2*mm
    assert definition.sheets[0].deck == definition.decks[0]
    assert definition.sheets[0].size == A4
    assert definition.sheets[0].print_margin == 3*mm
