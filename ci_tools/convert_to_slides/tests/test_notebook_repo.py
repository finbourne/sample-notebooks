from convert_to_slides.notebook_repo import NotebookRepo
from convert_to_slides.notebook import Notebook
from pytest import raises
from nbformat import read
from unittest.mock import mock_open, patch


class TestNotebookRepo:
    repo = NotebookRepo(force_slide_metadata=False)

    def test_filter_files_empty_list_returns_empty_generator(self):
        res = list(self.repo.filter_files([]))
        assert [] == res

    def test_filter_files_list_with_ipynb_file_returns_generator_with_ipynb_file(self):
        filename = "test.ipynb"
        res = list(self.repo.filter_files([filename]))
        assert [filename] == res

    def test_read_files_with_empty_list_returns_empty_generator(
        self,
    ):

        expected_result = []

        result = list(self.repo.read_files([]))

        assert expected_result == result

    def test_read_files_without_force_slide_metadata_returns_notebook_with_path_and_source(
        self,
    ):
        filepath = "tests/notebooks/test.ipynb"
        source = read(filepath, as_version=4)

        expected_result = [Notebook(filepath=filepath, source=source)]

        result = list(self.repo.read_files([filepath]))

        assert expected_result == result

    def test_read_files_with_force_slide_metadata_and_notebook_without_metadata_throws_ValueError(
        self,
    ):
        filepath = "tests/notebooks/test.ipynb"
        repo = NotebookRepo(force_slide_metadata=True)
        with raises(ValueError):
            list(repo.read_files([filepath]))

    def test_read_files_with_force_slide_metadata_and_notebook_with_metadata_returns_notebook(
        self,
    ):
        filepath = "tests/notebooks/test_with_slide_metadata.ipynb"
        source = read(filepath, as_version=4)
        repo = NotebookRepo(force_slide_metadata=True)

        expected_result = [Notebook(filepath=filepath, source=source)]

        result = list(repo.read_files([filepath]))

        assert expected_result == result

    def test_write_files_with_slides_source_calls_filewrite(self):
        file_path = "test_value"
        file_path_with_extension = f"{file_path}.slides.html"
        slide_source = "test_source"
        notebooks = [
            Notebook(
                filepath=file_path,
                source=read("tests/notebooks/test.ipynb", as_version=4),
                slides_source=slide_source,
            )
        ]
        m = mock_open()
        with patch("builtins.open", m):
            self.repo.write_files(notebooks)
        m.assert_called_once_with(file_path_with_extension, "w")
        handle = m()
        handle.write.assert_called_once_with(slide_source)

    def test_write_files_without_slides_source_raises_ValueError(self):
        file_path = "test_value"
        notebooks = [
            Notebook(
                filepath=file_path,
                source=read("tests/notebooks/test.ipynb", as_version=4),
            )
        ]
        with raises(ValueError):
            self.repo.write_files(notebooks)
