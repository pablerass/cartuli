import pytest

from PIL import ImageChops

from cartuli.templater import SVGTemplate


def test_templater(fixture_content, random_image):
    template_content = fixture_content("template.svg")

    with pytest.raises(ValueError):
        SVGTemplate(template_content, [])

    with pytest.raises(ValueError):
        SVGTemplate(template_content, ('name', 'image'))

    template = SVGTemplate(template_content, ('image', 'text'))

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
