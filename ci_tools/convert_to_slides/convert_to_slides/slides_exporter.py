from typing import Iterable, Generator
from convert_to_slides.notebook import Notebook
from nbconvert import SlidesExporter
from traitlets.config import Config


class SlidesExporterProcessor:
    def __init__(self, execute_notebooks: bool):
        c = Config()
        if execute_notebooks:
            c.ExecutePreprocessor.enabled = False
            c.ClearOutputPreprocessor.enabled = False
        c.SlidesExporter.reveal_scroll = True
        self.__slides_exporter = SlidesExporter(config=c)

    def generate_slides_for_notebook(self, notebook: Notebook) -> Notebook:
        slides_source, slides_resources = self.__slides_exporter.from_notebook_node(
            notebook.source
        )
        notebook.slides_source = slides_source
        notebook.slides_resources = slides_resources
        return notebook

    def generate_slides(
        self, notebooks: Iterable[Notebook]
    ) -> Generator[Notebook, None, None]:
        return (self.generate_slides_for_notebook(notebook) for notebook in notebooks)
