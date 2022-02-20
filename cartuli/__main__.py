#!/usr/bin/env python3
"""Main cartuli package."""
import argparse
import logging
import sys

from .card import Card, CardImage
from .measure import Size, A4, STANDARD, mm
from .sheet import Sheet
from .filters import CardImageMultipleFilter, CardImageInpaintFilter, CardImageNullFilter


def parse_args(args: list[str] = None) -> argparse.Namespace:
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Create a PDF with a list of images')

    parser.add_argument('-o', '--output-file', type=str, required=False, default='output',
                        help='Sheet name')
    parser.add_argument('-i', '--card-images', type=str, nargs='+', required=True,
                        help='Images to add to sheet')
    parser.add_argument('-p', '--page-size', type=Size.from_str, default=A4,
                        help="Page size")
    parser.add_argument('-c', '--card-size', type=Size.from_str, default=STANDARD,
                        help="Card size")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Display verbose output")
    return parser.parse_args(args)


def main(args=None):
    """Execute main package command line functionality."""
    args = parse_args()

    # Logging
    if args.verbose < 2:
        logging_format = '%(levelname)s - %(message)s'
    else:
        logging_format = '[%(asctime)s] %(levelname)s - %(name)s - %(message)s'
    logging.basicConfig(stream=sys.stderr, format=logging_format,
                        level=logging.WARN - args.verbose * 10)
    if args.verbose < 3:
        logging.getLogger('PIL').propagate = False
    logger = logging.getLogger('cartuli')

    sheet = Sheet(size=args.page_size, card_size=args.card_size, padding=10*mm)
    filters = CardImageMultipleFilter(
        CardImageInpaintFilter()
        # CardImageNullFilter()
    )
    sheet.add_cards(
        [Card(args.card_size, filters.apply(CardImage(image, args.card_size)))
         for image in args.card_images])
    sheet.create_pdf(args.output_file)
    logger.info(f'Created {args.output_file} sheet with {len(args.card_images)} card_images')

    return 0


if __name__ == "__main__":
    sys.exit(main())
