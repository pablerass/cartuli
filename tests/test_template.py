import pytest

from PIL import ImageChops

from cartuli.template import Template


def test_template(fixture_content, random_image):
    template_content = fixture_content("template.svg")

    with pytest.raises(ValueError):
        Template(template_content, [])

    with pytest.raises(ValueError):
        Template(template_content, ('name', 'image'))

    template = Template(template_content, ('image', 'text'))

    parameters = {
        'text': 'otro_texto',
        'image': random_image(),
    }
    generated_content = template.apply_parameters(parameters)
    content_values = template.get_values(generated_content)

    assert parameters['text'] == content_values['text']

    rgb_parameter_image = parameters['image'].convert('RGB')
    rgb_content_image = content_values['image'].convert('RGB')
    assert not ImageChops.difference(rgb_parameter_image, rgb_content_image).getbbox()


# TODO: Make this tests work
# def test_template_from_file(fixture_content, fixture_file):
#     template_content = fixture_content("template.svg")
#     parameters = ('text', 'image')
#
#     assert Template(template_content, parameters) == Template.from_file(fixture_file("template.svg"), parameters)
