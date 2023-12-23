from __future__ import annotations

import base64
import io

from cairosvg import svg2png
from copy import deepcopy
from lxml import etree
from pathlib import Path
from PIL import Image
from typing import Iterable


DEFAULT_SVG_DPI = 300

TemplateContent = str
ParameterKey = str
ParameterValue = Image.Image | str


def _image_to_uri(image: Image.Image | str | Path, encoding: str = 'UTF-8') -> str:
    if isinstance(image, str):
        image = Path(image)
    if isinstance(image, Path):
        image = Image.open(image)

    image_buffer = io.BytesIO()
    # TUNE: This should be done with JPEG but the tests are not consistent that way :/
    image.save(image_buffer, format='PNG')

    return f"data:image/png;base64,{base64.b64encode(image_buffer.getvalue()).decode(encoding)}"


def _set_template_text(text_element: etree._Element, value: str):
    text_element.getchildren()[0].text = value


def _get_template_text(text_element: etree._Element) -> str:
    return text_element.getchildren()[0].text


def _set_template_image(image_element: etree._Element, value: Image.Image, encoding: str = 'UTF-8'):
    image_element.set('{http://www.w3.org/1999/xlink}href', _image_to_uri(value))


def _get_template_image(image_element: etree._Element, encoding: str = 'UTF-8') -> Image.Image:
    # TODO: Add beter content management, there must be supported by pillow or other library
    uri_image = image_element.get('{http://www.w3.org/1999/xlink}href')
    base64_image = uri_image.split(',')[-1]
    return Image.open(io.BytesIO(base64.b64decode(base64_image)))


# TUNE: Probably this should not be implemented here
def svg_file_to_image(svg_file: str | Path, dpi: int = DEFAULT_SVG_DPI) -> Image.Image:
    if isinstance(svg_file, str):
        svg_file = Path(svg_file)

    image_data = svg2png(bytestring=svg_file.read_bytes(), dpi=dpi)

    return Image.open(io.BytesIO(image_data))


def svg_content_to_image(svg_content: str, dpi: int = DEFAULT_SVG_DPI) -> Image.Image:
    image_data = svg2png(bytestring=svg_content, dpi=dpi)

    return Image.open(io.BytesIO(image_data))


class Template:
    def __init__(self, template: TemplateContent | etree._Element, parameters: Iterable[ParameterKey],
                 dpi: int = DEFAULT_SVG_DPI):
        if not parameters:
            raise ValueError("A template withoyt parameters does not make any sense")

        if isinstance(template, etree._ElementTree):
            self.__xml_tree = template
            self.__encoding = self.__xml_tree.docinfo.encoding
        else:
            self.__xml_tree = etree.fromstring(bytes(template, 'UTF-8'))
            self.__encoding = 'UTF-8'

        for parameter in parameters:
            # TUNE: svg contents are refered with {http://www.w3.org/2000/svg} in files created with my version of
            # Inkscape. That part is being ignored to make this work in other conditions but probably should be
            # properly managed. This assumtion is repeated along all class methods.
            element = self.__xml_tree.find(f".//*[@id='{parameter}']")

            if element is None:
                raise ValueError(f"Parameter '{parameter}' not found in template")
            if not (element.tag.endswith('image') or element.tag.endswith('text')):
                raise ValueError(f"Parameter '{parameter}' element '{element.tag}' is unsupported")

        self.__parameters = tuple(parameters)
        self.__dpi = dpi

    @staticmethod
    def from_dict(definition: dict) -> Template:
        pass

    @property
    def _xml_tree(self) -> etree._ElementTree:
        return self.__xml_tree

    @property
    def parameters(self) -> dict[ParameterKey, type]:
        return deepcopy(self.__parameters)

    @property
    def dpi(self) -> int:
        return self.__dpi

    @classmethod
    def from_file(cls, template_file: str | Path, parameters: Iterable[ParameterKey]) -> Template:
        if isinstance(template_file, str):
            template_file = Path(template_file)

        return cls(etree.parse(template_file), parameters)

    def apply_parameters(self, parameters: dict[ParameterKey, ParameterValue]) -> TemplateContent:
        # TUNE: Think if an error should be raised if not all parameters are specified
        xml_tree = deepcopy(self.__xml_tree)

        for parameter, value in parameters.items():
            element = xml_tree.find(f".//*[@id='{parameter}']")

            if element is None:
                raise ValueError(f"Parameter '{parameter}' not found in template")
            if element.tag.endswith('image'):
                if isinstance(value, Image.Image):
                    _set_template_image(element, value, encoding=self.__encoding)
                else:
                    raise ValueError((f"Parameter '{parameter}' value '{value}' is invalid "
                                      f"for '{element.tag}'"))
            if element.tag.endswith('text'):
                if isinstance(value, str):
                    _set_template_text(element, value)
                else:
                    raise ValueError((f"Parameter '{parameter}' value '{value}' is invalid "
                                      f"for '{element.tag}'"))

        return etree.tostring(xml_tree, pretty_print=True)

    def create_image(self, parameters: dict[ParameterKey, ParameterValue]) -> Image.Image:
        svg_content = self.apply_parameters(parameters)

        return svg_content_to_image(svg_content, dpi=self.__dpi)

    def get_values(self, content: TemplateContent | etree._Element,
                   parameters: tuple(ParameterKey) = None) -> dict[ParameterKey, ParameterValue]:
        if parameters is None:
            parameters = tuple(self.__parameters)

        if isinstance(content, etree._ElementTree):
            content_tree = content
        else:
            content_tree = etree.fromstring(bytes(content))

        values = {}
        for parameter in parameters:
            element = content_tree.find(f".//*[@id='{parameter}']")
            if element is None:
                raise ValueError(f"parameter '{parameter}' not found in content")
            if element.tag.endswith('image'):
                value = _get_template_image(element)
            if element.tag.endswith('text'):
                value = _get_template_text(element)

            values |= {parameter: value}

        return values

    def apply_parameters_to_file(self, file: str | Path, parameters: dict[ParameterKey, ParameterValue]):
        if isinstance(file, str):
            file = Path(file)

        file.write_text(self.apply_parameters(parameters))

    def create_image_file(self, file: str | Path, parameters: dict[ParameterKey, ParameterValue]):
        self.create_image(parameters).save(file)

    def get_values_from_file(self, content_file: str | Path,
                             parameters: tuple(ParameterKey) = None) -> dict[ParameterKey, ParameterValue]:
        if isinstance(content_file, str):
            content_file = Path(content_file)

        return self.get_values(content_file.read_text(), parameters)

    def __eq__(self, other: Template) -> bool:
        return (self._xml_tree == other._xml_tree and
                self.parameters == other.parameters)
