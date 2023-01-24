from argparse import ArgumentParser
from convert_to_slides.commands import setup_generate_args, setup_validate_args
from typing import NamedTuple, List
from sys import argv, exit
import logging

logging.basicConfig()
logger = logging.getLogger()


class Args(NamedTuple):
    filepaths: str
    delimiter: str
    execute: bool
    force_slides: bool


def parse_args(args: List[str]):
    parser = ArgumentParser(
        description="Takes a list of mixed files and converts to revealjs slides.",
    )
    subparsers = parser.add_subparsers()
    setup_generate_args(
        subparsers.add_parser(
            "generate",
            description="Takes a list of mixed files and converts to revealjs slides.",
        )
    )
    setup_validate_args(
        subparsers.add_parser(
            "validate",
            description="Takes a directory and checks that all generated slides are correct",
        )
    )
    args = parser.parse_args()
    args.func(args)


def main() -> int:
    try:
        parse_args(argv[1:])
    except Exception:
        logger.exception("something went wrong, terminating")
        return -1
    return 0


if __name__ == "__main__":
    exit(main())  # pragma: no cover
