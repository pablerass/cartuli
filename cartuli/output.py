"""Sheet module."""
import logging

from pathlib import Path
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .sheet import Sheet


def sheet_pdf_output(sheet: Sheet, output_path: Path | str) -> None:
    """Create a PDF document containing all sheet content."""
    logger = logging.getLogger('cartuli.output.sheet_pdf_output')

    # TODO: Add title to PDF document
    c = canvas.Canvas(str(output_path), pagesize=tuple(sheet.size))
    for page in range(1, sheet.pages + 1):
        # Front
        for line in sheet.crop_marks:
            c.setLineWidth(0.5)
            c.line(*list(line))

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
            c.setLineWidth(0.5)
            c.line(*list(line))

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
