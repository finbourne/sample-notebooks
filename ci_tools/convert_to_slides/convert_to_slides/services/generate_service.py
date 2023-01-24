from convert_to_slides.notebook_repo import NotebookRepo
from convert_to_slides.slides_exporter import SlidesExporterProcessor
from convert_to_slides.slide_metadata_checker import SlideMetadataChecker
from typing import Iterable, List
from argparse import Namespace
from logging import getLogger

logger = getLogger(__name__)


def generate(args: Namespace):
    notebook_repo = NotebookRepo(
        slide_metadata_checker=SlideMetadataChecker(),
        force_slide_metadata=args.force_slides,
    )
    try:
        slides_exporter = SlidesExporterProcessor(execute_notebooks=args.execute)
        filepaths = split_filepaths(args.filepaths, args.delimiter)
        process_notebooks(notebook_repo, slides_exporter, filepaths)
    except Exception:
        logger.exception("failed to generate slides for all notebooks")
        raise


def process_notebooks(
    notebook_repo: NotebookRepo,
    slides_exporter: SlidesExporterProcessor,
    filepaths: Iterable[str],
):
    notebooks = notebook_repo.read_files(filepaths=filepaths)
    notebooks_with_slides = slides_exporter.generate_slides(notebooks)
    notebook_repo.write_files(notebooks_with_slides)


def split_filepaths(filepaths: str, delimiter: str) -> List[str]:
    return filepaths.split(delimiter)
