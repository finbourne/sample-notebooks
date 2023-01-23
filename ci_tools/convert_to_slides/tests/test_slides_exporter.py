from convert_to_slides.notebook import Notebook
from convert_to_slides.slides_exporter import SlidesExporterProcessor
from nbformat import read


class TestSlidesExporterProcessor:
    def test_generate_slides_generates_slides_html_string(self):
        exporter = SlidesExporterProcessor(execute_notebooks=False)
        notebook = Notebook(
            "", read("tests/notebooks/test_with_slide_metadata.ipynb", as_version=4)
        )
        with open(
            "tests/notebooks/test_with_slide_metadata_no_execute.slides.html",
            "r",
        ) as f:
            expected_content = f.read()

        result = list(exporter.generate_slides([notebook]))
        assert expected_content == result[0].slides_source

    def test_generate_slides_executes_and_generates_slides_html_string(self):
        exporter = SlidesExporterProcessor(execute_notebooks=True)
        notebook = Notebook(
            "", read("tests/notebooks/test_with_slide_metadata.ipynb", as_version=4)
        )
        with open(
            "tests/notebooks/test_with_slide_metadata_executed.slides.html",
            "r",
        ) as f:
            expected_content = f.read()

        result = list(exporter.generate_slides([notebook]))
        assert expected_content == result[0].slides_source
