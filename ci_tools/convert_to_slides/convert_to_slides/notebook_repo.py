import os
from typing import Generator, Iterable
from nbformat import read, NotebookNode
from convert_to_slides.notebook import Notebook


class NotebookRepo:
    def __init__(self, force_slide_metadata: bool):
        self.__force_slide_metadata = force_slide_metadata

    """Object responsible for filtering files and other file processing before slide generation"""

    def filter_files(self, filepaths: Iterable[str]) -> Generator[str, None, None]:
        NOTEBOOK_EXTENSION = ".ipynb"
        return (
            filepath
            for filepath in filepaths
            if os.path.splitext(filepath)[1] == NOTEBOOK_EXTENSION
        )

    def read_file(self, filepath: str) -> Notebook:
        notebook = Notebook(filepath=filepath, source=read(filepath, as_version=4))
        if self.__force_slide_metadata:
            self.__check_notebook_has_slide_metadata(notebook)
        return notebook

    def read_files(self, filepaths: Iterable[str]) -> Generator[Notebook, None, None]:
        return (self.read_file(filepath) for filepath in filepaths)

    def __check_notebook_has_slide_metadata(self, notebook: Notebook) -> None:
        if not any(
            self.__check_cell_has_slide_metadata(cell) for cell in notebook.source.cells
        ):
            raise ValueError(
                f"notebook {notebook.filepath} does not have any slide metadata"
            )

    def __check_cell_has_slide_metadata(self, cell: NotebookNode) -> bool:
        if hasattr(cell, "metadata") and hasattr(cell.metadata, "slideshow"):
            return True
        return False

    def write_files(self, notebooks: Iterable[Notebook]):
        for notebook in notebooks:
            self.write_file(notebook)

    def write_file(self, notebook: Notebook):
        if not notebook.slides_source:
            raise ValueError(
                f"notebook {notebook.filepath} has not got slides to write"
            )
        SLIDES_EXT = ".slides.html"
        filepath, ext = os.path.splitext(notebook.filepath)
        output_filepath = f"{filepath}{SLIDES_EXT}"
        with open(output_filepath, "w") as file:
            file.write(notebook.slides_source)
