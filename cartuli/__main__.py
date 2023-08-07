#!/usr/bin/env python3
"""Main cartuli package."""
import argparse
import logging
import os
import re
import sys

from pathlib import Path

from .definition import Definition


def parse_args(args: list[str] = None) -> argparse.Namespace:
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Create a PDF with a list of images')
    parser.add_argument('definition_file', type=Path, default=Definition.DEFAULT_CARTULIFILE,
                        nargs='?', help='Cartulifile to be used')
    parser.add_argument('-c', '--cards', type=str, nargs='*', default=(),
                        help="Cards to include supporting shell patterns")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Display verbose output")
    return parser.parse_args(args)


def main(args=None):
    """Execute main package command line functionality."""
    args = parse_args()

    # Logging
    if args.verbose < 3:
        logging_format = '%(levelname)s - %(message)s'
    else:
        logging_format = '[%(asctime)s] %(levelname)s - %(name)s - %(message)s'
    logging.basicConfig(stream=sys.stderr, format=logging_format,
                        level=logging.WARN - args.verbose * 10)
    if args.verbose < 4:
        logging.getLogger('PIL').propagate = False
    logger = logging.getLogger('cartuli')

    # Definition paths are relative to definition file
    definition_dir = Path(args.definition_file)
    if not definition_dir.is_dir():
        definition_dir = definition_dir.parent
    # TODO: Find a better way to manage definition relative paths
    os.chdir(definition_dir)

    cards_filter = None
    if args.cards is not None:
        cards_regex = re.compile(r'^.*(' + '|'.join(args.cards) + r').*$')
        cards_filter = lambda x: cards_regex.match(x)

    definition = Definition.from_file(args.definition_file, cards_filter=cards_filter)
    logger.info(f"Loaded {args.definition_file} with {len(definition.decks)} decks")
    sheet_dir = definition_dir / 'sheets'
    for deck_names, sheet in definition.sheets.items():
        sheet_dir.mkdir(exist_ok=True)
        sheet_file = sheet_dir / f"{'_'.join(deck_names)}.pdf"
        logger.debug(f'Creating sheet {sheet_file}')
        sheet.create_pdf(sheet_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
