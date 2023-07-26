from cartuli.filters import from_dict, InpaintFilter, NullFilter, MultipleFilter, StraightenFilter, snake_to_class
from cartuli.measure import mm


def test_filter_from_dict():
    assert from_dict({}) == NullFilter()
    assert from_dict({'inpaint': {}}) == InpaintFilter()
    assert from_dict({
        'inpaint': {
            'inpaint_size': "2*mm",
            'corner_radius': 2*mm
        }
    }) == InpaintFilter(inpaint_size=2*mm, corner_radius=2*mm)
    assert from_dict({
        'inpaint': {
        },
        'straighten': {}
    }) == MultipleFilter(
        InpaintFilter(),
        StraightenFilter()
    )
    assert from_dict({
        'inpaint': {
            'image_crop': 2*mm
        },
        'straighten': {}
    }) == MultipleFilter(
        InpaintFilter(image_crop=2*mm),
        StraightenFilter()
    )


def test_snake_to_class():
    assert snake_to_class('filter') == 'Filter'
    assert snake_to_class('inpaint_filter') == 'InpaintFilter'
