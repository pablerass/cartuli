"""Sheet module."""
import logging
import reportlab.graphics.shapes as shapes

from functools import lru_cache, partial
from math import radians
from pathlib import Path
from reportlab.lib.colors import transparent, white
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .measure import Line, Point, mm
from .sheet import Sheet


DEFAULT_REGISTRATION_MARK_SIZE = 5*mm
DEFAULT_REGISTRATION_MARK_MARGIN = 0.5*mm
DEFAULT_MARK_WIDTH = 0.5


@lru_cache
def _rotate(point: Point, origin: Point, degrees: float) -> Point:
    angle = radians(degrees)
    return origin.rotate(angle, origin)


def draw_registration_mark(c: canvas.Canvas, center: Point,
                           size: float = DEFAULT_REGISTRATION_MARK_SIZE,
                           stroke_width: float = DEFAULT_MARK_WIDTH,
                           margin: float = DEFAULT_REGISTRATION_MARK_MARGIN) -> None:
    # TODO: Add magin to white background
    draw = shapes.Drawing(size, size)

    draw.add(shapes.Rect(-margin, -margin, size + 2*margin, size + 2*margin, strokeColor=transparent, fillColor=white))

    # Main cross
    draw.add(shapes.Line(0, size/2, size, size/2, strokeWidth=stroke_width))
    draw.add(shapes.Line(size/2, 0, size/2, size, strokeWidth=stroke_width))

    # Main cross ends
    cross_end_length = size/5
    draw.add(shapes.Line(size/2-cross_end_length/2, size,
                         size/2+cross_end_length/2, size, strokeWidth=stroke_width))
    draw.add(shapes.Line(size, size/2-cross_end_length/2,
                         size, size/2+cross_end_length/2, strokeWidth=stroke_width))

    # Diagonal cross
    circle_center = Point(size/2, size/2)
    circle_radius = size/2
    initial_point = Point(circle_radius, 0)
    rotate = partial(_rotate, circle_center, initial_point)
    draw.add(shapes.Line(rotate(45).x, rotate(45).y, rotate(225).x, rotate(225).y,
                         strokeWidth=stroke_width))
    draw.add(shapes.Line(rotate(135).x, rotate(135).y, rotate(315).x, rotate(315).y,
                         strokeWidth=stroke_width))

    # Outer circle
    outer_circle_radius = circle_radius/1.6
    draw.add(shapes.Circle(circle_center.x, circle_center.y, outer_circle_radius, fillColor=transparent,
             strokeWidth=stroke_width))

    # Inner circle
    inner_circle_radius = outer_circle_radius/1.6
    draw.add(shapes.Circle(circle_center.x, circle_center.y, inner_circle_radius, fillColor=transparent,
             strokeWidth=stroke_width))
    draw.add(shapes.Wedge(circle_center.x, circle_center.y, inner_circle_radius, 0, 90, strokeWidth=0))
    draw.add(shapes.Wedge(circle_center.x, circle_center.y, inner_circle_radius, 180, 270, strokeWidth=0))

    draw.drawOn(c, center.x - size/2, center.y - size/2)


def draw_crop_mark(c: canvas.Canvas, line: Line, stroke_width: float = DEFAULT_MARK_WIDTH) -> None:
    c.setLineWidth(stroke_width)
    c.line(*list(line))


def _draw_marks(c: canvas.Canvas, sheet: Sheet, registration_size: float = DEFAULT_REGISTRATION_MARK_SIZE,
                stroke_width: float = DEFAULT_MARK_WIDTH) -> None:
    # Crop marks
    draw_crop = partial(draw_crop_mark, c, stroke_width=stroke_width)
    for line in sheet.crop_marks:
        draw_crop(line)

    # Registration marks
    draw_register = partial(draw_registration_mark, c, size=registration_size, stroke_width=stroke_width)

    # TUNE: Probably there is a better way to set this value
    if sheet.print_margin:
        to_border = sheet.print_margin + registration_size/2
    else:
        to_border = (sheet.margin.width + sheet.margin.height)/2 - registration_size/2

    draw_register(Point(sheet.size.width - to_border, to_border))
    draw_register(Point(sheet.size.width - to_border, sheet.size.height - to_border))
    draw_register(Point(to_border, to_border))
    draw_register(Point(to_border, sheet.size.height - to_border))


def sheet_pdf_output(sheet: Sheet, output_path: Path | str) -> None:
    """Create a PDF document containing all sheet content."""
    logger = logging.getLogger('cartuli.output.sheet_pdf_output')
    # TODO: Add title to PDF document
    c = canvas.Canvas(str(output_path), pagesize=tuple(sheet.size))

    for page in range(1, sheet.pages + 1):
        # Front
        _draw_marks(c, sheet)

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

        _draw_marks(c, sheet)

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
