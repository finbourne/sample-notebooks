from typing import Iterable
from notebook import Notebook
from nbformat import NotebookNode
from nbconvert import SlidesExporter
from traitlets.config import Config


class SlidesExporterProcessor:
    def __init__(self, execute_notebooks: bool):
        self.__execute_notebooks = execute_notebooks
        c = Config()
        c.HTMLExporter.preprocessors = [
            "nbconvert.preprocessors.TagRemovePreprocessor",
            "nbconvert.preprocessors.RegexRemovePreprocessor",
            "nbconvert.preprocessors.coalesce_streams",
            "nbconvert.preprocessors.SVG2PDFPreprocessor",
            "nbconvert.preprocessors.LatexPreprocessor",
            "nbconvert.preprocessors.HighlightMagicsPreprocessor",
            "nbconvert.preprocessors.ExtractOutputPreprocessor",
            "nbconvert.preprocessors.ClearMetadataPreprocessor",
        ]
        c.SlidesExporter.reveal_scroll = True
        self.__slides_exporter = SlidesExporter(config=c)

    def generate_slides(self, filepaths: Iterable[Notebook]):
        
