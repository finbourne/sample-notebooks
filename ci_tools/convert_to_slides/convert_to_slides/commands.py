from argparse import ArgumentParser
from convert_to_slides.services.generate_service import generate
from convert_to_slides.services.validate_service import validate


def setup_generate_args(parser: ArgumentParser):
    parser.add_argument(
        "-f",
        "--filepaths",
        type=str,
        required=True,
        help="delimiter separated list of paths to notebooks",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        action="store",
        nargs="?",
        default=",",
        help="delimiter to use for splitting filepath list",
    )
    parser.add_argument(
        "-e",
        "--execute",
        action="store_true",
        default=False,
        help="execute notebook when generating slides",
    )
    parser.add_argument(
        "-s",
        "--force-slides",
        default=False,
        action="store_true",
        help="throw error if notebooks don't have any slideshow metadata saved",
    )
    parser.set_defaults(func=generate)


def setup_validate_args(parser: ArgumentParser):
    parser.add_argument(
        "-n",
        "--notebooks",
        type=str,
        help="notebook source directory",
    )
    parser.set_defaults(func=validate)
