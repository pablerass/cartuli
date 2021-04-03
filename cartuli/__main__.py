#!/usr/bin/env python3
"""Main cartuli package."""
import argparse
import logging
import sys

from typing import List

from cartuli import Sheet, Card


def parse_args(args: List[str] = None) -> argparse.Namespace:
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Create a PDF with a list of images')

    parser.add_argument('-n', '--name', type=str, required=True,
                        help='Sheet name')
    parser.add_argument('-i', '--images', type=str, nargs='+',
                        help='Images to add to sheet')
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

    sheet = Sheet(args.name, card_size=Card.TAROT_SIZE)
    sheet.add_cards([Card(image) for image in args.images])
    sheet.create_pdf()
    logger.info(f'Created {args.name} sheet with {len(args.images)} images')

    return 0


if __name__ == "__main__":
    sys.exit(main())
