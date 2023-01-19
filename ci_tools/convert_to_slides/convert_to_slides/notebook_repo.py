import os
from typing import Generator, Iterable, List
from nbformat import read, NotebookNode
from notebook import Notebook


class NotebookRepo:
    def __init__(self, force_slide_metadata: bool):
        self.__force_slide_metadata = force_slide_metadata

    """Object responsible for filtering files and other file processing before slide generation"""

    def filter_files(self, filepaths: Iterable[str]) -> Generator[str, None, None]:
        NOTEBOOK_EXTENSION = ".ipynb"
        return (
            filepath
            for filepath in filepaths
            if os.path.splitext(filepath)[0] == NOTEBOOK_EXTENSION
        )

    def split_string_to_files(self, filepaths: str, delimiter: str) -> List[str]:
        return filepaths.split(delimiter)

    def read_files(self, filepaths: Iterable[str]) -> List[Notebook]:
        notebooks = [
            Notebook(filepath=filepath, source=read(filepath, as_version=4))
            for filepath in filepaths
        ]
        if self.__force_slide_metadata:
            for notebook in notebooks:
                self.__check_notebook_has_slide_metadata(notebook)
        return notebooks

    def __check_notebook_has_slide_metadata(self, notebook: Notebook) -> None:
        if not any(
            self.__check_cell_has_slide_metadata(cell) for cell in notebook.cells
        ):
            raise ValueError(
                f"notebook {notebook.filepath} does not have any slide metadata"
            )

    def __check_cell_has_slide_metadata(self, cell: NotebookNode) -> bool:
        if cell.metadata is None:
            return False
        if cell.metadata.slideshow is None:
            return False
        return True
