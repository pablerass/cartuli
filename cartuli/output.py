"""Sheet module."""
import logging
import reportlab.graphics.shapes as shapes

from functools import lru_cache, partial
from math import sin, cos, radians
from pathlib import Path
from reportlab.lib.colors import transparent
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .measure import Line, Point, Size, mm
from .sheet import Sheet


@lru_cache
def _rotate(origin: Point, point: Point, degrees: float) -> Point:
    angle = radians(degrees)
    x = origin.x + cos(angle) * (point.x - origin.x) - sin(angle) * (point.y - origin.y)
    y = origin.y + sin(angle) * (point.x - origin.x) + cos(angle) * (point.y - origin.y)
    return Point(x, y)


def draw_registration_mark(canvas: canvas.Canvas, position: Point, size: Size = Size(5*mm, 5*mm),
                           strokeWidth: float = 0.5) -> None:
    draw = shapes.Drawing(*size)

    # Main cross
    draw.add(shapes.Line(0, size.height/2, size.width, size.height/2, strokeWidth=strokeWidth))
    draw.add(shapes.Line(size.width/2, 0, size.width/2, size.height, strokeWidth=strokeWidth))

    # Main cross ends
    cross_end_length = (size.height + size.width)/2/5
    draw.add(shapes.Line(size.width/2-cross_end_length/2, size.height,
                         size.width/2+cross_end_length/2, size.height, strokeWidth=strokeWidth))
    draw.add(shapes.Line(size.width, size.height/2-cross_end_length/2,
                         size.width, size.height/2+cross_end_length/2, strokeWidth=strokeWidth))

    # Diagonal cross
    circle_center = Point(size.height/2, size.width/2)
    circle_radius = (size.width + size.height)/4
    initial_point = Point(circle_radius, 0)
    rotate = partial(_rotate, circle_center, initial_point)
    draw.add(shapes.Line(rotate(45).x, rotate(45).y, rotate(225).x, rotate(225).y,
                         strokeWidth=strokeWidth))
    draw.add(shapes.Line(rotate(135).x, rotate(135).y, rotate(315).x, rotate(315).y,
                         strokeWidth=strokeWidth))

    # Outer circle
    outer_circle_radius = circle_radius/(3/2)
    draw.add(shapes.Circle(circle_center.x, circle_center.y, outer_circle_radius, fillColor=transparent,
             strokeWidth=strokeWidth))

    # Inner circle
    inner_circle_radius = outer_circle_radius/(3/2)
    draw.add(shapes.Circle(circle_center.x, circle_center.y, inner_circle_radius, fillColor=transparent,
             strokeWidth=strokeWidth))
    draw.add(shapes.Wedge(circle_center.x, circle_center.y, inner_circle_radius, 0, 90, strokeWidth=0))
    draw.add(shapes.Wedge(circle_center.x, circle_center.y, inner_circle_radius, 180, 270, strokeWidth=0))

    draw.drawOn(canvas, position.x - size.height/2, position.y - size.width/2)


def draw_crop_mark(canvas: canvas.Canvas, line: Line, strokeWidth: float = 0.5) -> None:
    canvas.setLineWidth(strokeWidth)
    canvas.line(*list(line))


def sheet_pdf_output(sheet: Sheet, output_path: Path | str) -> None:
    """Create a PDF document containing all sheet content."""
    logger = logging.getLogger('cartuli.output.sheet_pdf_output')

    # TODO: Add title to PDF document
    c = canvas.Canvas(str(output_path), pagesize=tuple(sheet.size))
    for page in range(1, sheet.pages + 1):
        # Front
        draw_registration_mark(c, Point(10*mm, 10*mm))
        for line in sheet.crop_marks:
            draw_crop_mark(c, line)

        for i, card in enumerate(sheet.page_cards(page)):
            num_card = i + 1
            card_image = card.front.image
            card_coordinates = sheet.card_coordinates(num_card)
            card_position = sheet.card_position(card_coordinates)
            logger.debug(f"Adding card {num_card} '{card}' front image to page {page} at {card_coordinates}")
            c.drawImage(ImageReader(card_image),
                        card_position.x - card.front.bleed, card_position.y - card.front.bleed,
                        card.front.image_size.width, card.front.image_size.height)

        # Back
        if sheet.two_sided:
            c.showPage()
            for i, card in enumerate(sheet.page_cards(page)):
                num_card = i + 1
                card_image = card.back.image
                card_coordinates = sheet.card_coordinates(num_card, back=True)
                card_position = sheet.card_position(card_coordinates)
                logger.debug(f"Adding {num_card} card {card} back image to page {page} at {card_coordinates}")
                c.drawImage(ImageReader(card_image),
                            card_position.x - card.back.bleed, card_position.y - card.back.bleed,
                            card.back.image_size.width, card.back.image_size.height)

        for line in sheet.crop_marks:
            draw_crop_mark(c, line)

        c.showPage()
        logger.debug(f"Created {output_path} page {page}")

    c.save()
    logger.info(f"Created {output_path}")


def sheet_output(sheet: Sheet, output_path: Path | str):
    if isinstance(output_path, str):
        output_path = Path(output_path)

    output_path = output_path.expanduser()

    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path

    match output_path:
        case Path(suffix='.pdf'):
            sheet_pdf_output(sheet, output_path)
        case _:
            raise ValueError('Unable to identify output format in output_path')
