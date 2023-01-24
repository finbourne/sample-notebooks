from convert_to_slides.notebook import Notebook
from nbformat import NotebookNode


class SlideMetadataChecker:
    def check_notebook_has_slide_metadata(self, notebook: Notebook) -> bool:
        return any(
            self.__check_cell_has_slide_metadata(cell) for cell in notebook.source.cells
        )

    def __check_cell_has_slide_metadata(self, cell: NotebookNode) -> bool:
        if hasattr(cell, "metadata") and hasattr(cell.metadata, "slideshow"):
            return True
        return False
