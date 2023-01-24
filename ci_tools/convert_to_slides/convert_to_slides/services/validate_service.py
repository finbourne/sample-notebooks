from os import walk
import os
from argparse import Namespace
from convert_to_slides.notebook import Notebook
from convert_to_slides.notebook_repo import NotebookRepo
from convert_to_slides.slide_metadata_checker import SlideMetadataChecker
from convert_to_slides.slides_exporter import SlidesExporterProcessor
from typing import Generator
from logging import getLogger

logger = getLogger(__name__)


def get_all_notebooks_with_metadata(root: str) -> Generator[Notebook, None, None]:
    notebook_repo = NotebookRepo(
        slide_metadata_checker=SlideMetadataChecker(), force_slide_metadata=True
    )
    filepaths = (
        os.path.join(dirpath, filename)
        for dirpath, dirnames, filenames in walk(root)
        for filename in filenames
    )
    filtered_filepaths = notebook_repo.filter_files(filepaths)
    for filepath in filtered_filepaths:
        try:
            notebook = notebook_repo.read_file(filepath)
            yield notebook
        except ValueError as exc:
            logger.warning(f"File could not be processed: {exc}")


def validate(args: Namespace):
    try:
        logger.info("validating")
        SLIDES_EXT = ".slides.html"
        slides_exporter = SlidesExporterProcessor(execute_notebooks=False)
        notebooks = get_all_notebooks_with_metadata(args.notebooks)
        logger.info(f"fetched notebooks:{notebooks}")
        for notebook in notebooks:
            expected_slide_data = slides_exporter.generate_slides_for_notebook(
                notebook
            ).slides_source
            notebook_filepath_without_ext = notebook.filepath[:-6]
            slides_filepath = f"{notebook_filepath_without_ext}{SLIDES_EXT}"
            with open(slides_filepath, "r") as slides_file:
                assert expected_slide_data == slides_file.read()
    except AssertionError:
        logger.exception(f"notebook: {notebook.filepath} does not have correct slides")
        raise
    except Exception:
        logger.exception("Could not verify that all slides are correct")
        raise
