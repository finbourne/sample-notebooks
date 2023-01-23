from argparse import ArgumentParser
from convert_to_slides.notebook_repo import NotebookRepo
from convert_to_slides.slides_exporter import SlidesExporterProcessor
from typing import NamedTuple, List, Iterable
from sys import argv, exit
import logging

logging.basicConfig()
logger = logging.getLogger()


class Args(NamedTuple):
    filepaths: str
    delimiter: str
    execute: bool
    force_slides: bool


def parse_args(args: List[str]) -> Args:
    parser = ArgumentParser(
        prog="convert_to_slides",
        description="Takes a list of mixed files and converts to revealjs slides.",
    )
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
    parsed_args = parser.parse_args(args)

    return Args(
        filepaths=parsed_args.filepaths,
        delimiter=parsed_args.delimiter,
        execute=parsed_args.execute,
        force_slides=parsed_args.force_slides,
    )


def split_filepaths(filepaths: str, delimiter: str) -> List[str]:
    return filepaths.split(delimiter)


def process_notebooks(
    notebook_repo: NotebookRepo,
    slides_exporter: SlidesExporterProcessor,
    filepaths: Iterable[str],
):
    notebooks = notebook_repo.read_files(filepaths=filepaths)
    notebooks_with_slides = slides_exporter.generate_slides(notebooks)
    notebook_repo.write_files(notebooks_with_slides)


def main() -> int:
    try:
        args = parse_args(argv[1:])
        notebook_repo = NotebookRepo(force_slide_metadata=args.force_slides)
        slides_exporter = SlidesExporterProcessor(execute_notebooks=args.execute)
        filepaths = split_filepaths(args.filepaths, args.delimiter)
        process_notebooks(notebook_repo, slides_exporter, filepaths)

    except Exception:
        logger.exception("failed to generate slides for all notebooks")
        return -1
    return 0


if __name__ == "__main__":
    exit(main())  # pragma: no cover
