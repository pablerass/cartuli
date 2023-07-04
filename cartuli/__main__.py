#!/usr/bin/env python3
"""Main cartuli package."""
import argparse
import logging
import os
import sys

from pathlib import Path

from .definition import Definition


def parse_args(args: list[str] = None) -> argparse.Namespace:
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Create a PDF with a list of images')
    parser.add_argument('-f', '--cartulifile', type=Path, dest='definition_file',
                        default=Path(__file__).absolute().parent / Definition.DEFAULT_CARTULIFILE,
                        help='Cartulifile to be used')
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

    os.chdir(Path(args.definition_file))
    definition = Definition.from_file(args.definition_file)
    for sheet in definition.sheets:
        sheet_file = f"{sheet.deck.name}.pdf"
        logger.debug(f'Creating sheet {sheet_file}')
        sheet.create_pdf(sheet_file)
    # TODO: Add filters to definition
    # filters = CardImageMultipleFilter(
    #    CardImageInpaintFilter()
    #    CardImageNullFilter()
    # )

    return 0


if __name__ == "__main__":
    sys.exit(main())
