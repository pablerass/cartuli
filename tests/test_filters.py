from cartuli.filters import Filter, InpaintFilter, NullFilter, MultipleFilter, StraightenFilter, snake_to_class
from cartuli.measure import mm


def test_filter_from_dict():
    assert Filter.from_dict({}) == NullFilter()
    assert Filter.from_dict({'inpaint': {}}) == InpaintFilter()
    assert Filter.from_dict({
        'inpaint': {
            'inpaint_size': "2*mm",
            'corner_radius': 2*mm
        }
    }) == InpaintFilter(inpaint_size=2*mm, corner_radius=2*mm)
    assert Filter.from_dict({
        'inpaint': {
        },
        'straighten': {}
    }) == MultipleFilter(
        InpaintFilter(),
        StraightenFilter()
    )
    assert Filter.from_dict({
        'inpaint': {
            'image_crop': 2*mm
        },
        'straighten': None
    }) == MultipleFilter(
        InpaintFilter(image_crop=2*mm),
        StraightenFilter()
    )


def test_snake_to_class():
    assert snake_to_class('filter') == 'Filter'
    assert snake_to_class('inpaint_filter') == 'InpaintFilter'
