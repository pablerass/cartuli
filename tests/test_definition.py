import pytest

from cartuli.definition import Definition, _convert_dict_of_lists_to_list_of_dicts
from cartuli.filters import NullFilter, InpaintFilter
from cartuli.measure import Size, STANDARD, A4, mm


def test_defintion_invalid_file():
    with pytest.raises(FileNotFoundError):
        Definition.from_file("non_exitent_file")
    with pytest.raises(FileNotFoundError):
        Definition.from_file("..")


def test_file(fixture_file):
    assert Definition.from_file(fixture_file("simple-cartulifile.yml"))._values == {
        'decks': {
            'cards': {
                'size': 'STANDARD',
                'front': {
                    'images': "cards/*.png"
                },
                'default_back': {
                    'image': "card-back.png"
                }
            }
        },
        'outputs': {
            'sheet': {
                'size': "A4",
            }
        }
    }


def test_decks_definition():
    definition_dict = {
        'decks': {
            'cards': {
                'size': 'STANDARD'
            },
            'tokens': {
                'size': '(44*mm,75*mm)'
            }
        }
    }
    definition = Definition(definition_dict)
    assert definition.decks[0].name == 'cards'
    assert definition.decks[1].name == 'tokens'
    assert definition.decks[0].size == STANDARD
    assert definition.decks[1].size == Size(44*mm, 75*mm)


def test_template_parameters_definition():
    definition_dict = {
        'template_parameters': {
            'name': {
                'key1': "value1",
                'key2': "value2"
            }
        }
    }
    definition = Definition(definition_dict)
    assert definition._template_parameters['name'] == {
        'key1': "value1",
        'key2': "value2"
    }


def test_filters_definition():
    definition_dict = {
        'filters': {
            'front': {
                'inpaint': {}
            }
        }
    }
    definition = Definition(definition_dict)
    assert definition._filters['front'] == InpaintFilter()
    assert definition._filters['back'] == NullFilter()


def test_definition(random_image_file):
    num_cards = 5

    random_image_dir = random_image_file("front").parent
    for _ in range(0, num_cards - 1):
        random_image_file("front")

    definition_dict = {
        'decks': {
            'cards': {
                'size': 'STANDARD',
                'front': {
                    'images': str(random_image_dir / "*.png"),
                    'bleed': '2*mm',
                },
                'default_back': {
                    'image': str(random_image_file("back"))
                },
                'copies': 2
            }
        },
        'outputs': {
            'sheet': {
                'size': 'A4',
                'print_margin': '3*mm'
            }
        }
    }

    definition = Definition(definition_dict)
    assert definition.decks[0].name == 'cards'
    assert definition.decks[0].size == STANDARD
    assert len(definition.decks[0]) == 2 * num_cards
    assert definition.decks[0].two_sided
    assert definition.decks[0].cards[0].front.bleed == 2*mm
    assert definition.sheets['cards', ].cards == definition.decks[0].cards
    assert definition.sheets['cards', ].size == A4
    assert definition.sheets['cards', ].print_margin == 3*mm


def test_filters(random_image_file):
    # TODO: Implement filters testing
    pass


def test_convert_dict_of_lists_to_list_of_dicts():
    assert _convert_dict_of_lists_to_list_of_dicts({
        'a': [1, 2, 3, 4],
        'b': [5, 6, 7, 8]
    }) == [
        {'a': 1, 'b': 5},
        {'a': 2, 'b': 6},
        {'a': 3, 'b': 7},
        {'a': 4, 'b': 8},
    ]
