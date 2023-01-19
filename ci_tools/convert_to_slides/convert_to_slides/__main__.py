from nbconvert import SlidesExporter
from argparse import ArgumentParser

if __name__ == "__main__":
    parser = ArgumentParser(
        prog="convert_to_slides",
        description="Takes a list of mixed files and converts to revealjs slides.",
    )
    parser.add_argument(
        "-f",
        "--filepaths",
        type=str,
        help="delimiter seperated list of paths to notebooks",
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
        help="execute notebook when generating slides",
    )
    parser.add_argument(
        "-f",
        "--force-slides",
        action="store_true",
        help="throw error if notebooks don't have any slideshow metadata saved",
    )
