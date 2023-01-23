from convert_to_slides.__main__ import (
    parse_args,
    split_filepaths,
    process_notebooks,
    Args,
    main,
)
import pytest
from convert_to_slides.notebook_repo import NotebookRepo
from convert_to_slides.slides_exporter import SlidesExporterProcessor
from unittest.mock import MagicMock, create_autospec, patch
from convert_to_slides.notebook import Notebook


@pytest.fixture
def test_filepath_name():
    return "test_filepath"


@pytest.fixture
def args_array(test_filepath_name):
    return ["-f", test_filepath_name]


def raise_ValueError():
    raise ValueError()


class TestMain:
    def test_parse_args_returns_filepaths(self, args_array, test_filepath_name):

        result = parse_args(args_array)
        assert test_filepath_name == result.filepaths
        assert not result.execute
        assert not result.force_slides

    def test_parse_args_returns_delimiter(self, args_array):
        test_delimiter = "/f"
        extra_args = ["-d", test_delimiter]
        result = parse_args(args_array + extra_args)
        assert test_delimiter == result.delimiter
        assert not result.execute
        assert not result.force_slides

    def test_parse_args_returns_True_for_slides_and_execute_if_set(self, args_array):
        extra_args = ["-e", "-s"]
        result = parse_args(args_array + extra_args)
        assert result.execute
        assert result.force_slides

    @pytest.mark.parametrize(
        "filepaths, delimiter, expected",
        [
            ("ooh,la,la", ",", ["ooh", "la", "la"]),
            (
                "ooh\nla\nla",
                "\n",
                ["ooh", "la", "la"],
            ),
            ("ooh", ",", ["ooh"]),
            ("", ",", [""]),
        ],
    )
    def test_split_filepaths_returns_correctly_split_list(
        self, filepaths, delimiter, expected
    ):
        assert expected == split_filepaths(filepaths, delimiter)

    def test_process_notebooks(self):
        filepaths = ["fvbhksfhbv"]
        notebook = Notebook(
            filepath="f",
            source=MagicMock(),
            slides_resources=MagicMock(),
            slides_source=MagicMock(),
        )

        repo_mock = create_autospec(NotebookRepo)
        fake_file_array = [notebook]
        repo_mock.read_files.return_value = fake_file_array
        slides_exporter_mock = create_autospec(SlidesExporterProcessor)
        slides_exporter_mock.generate_slides.return_value = [notebook]
        process_notebooks(repo_mock, slides_exporter_mock, filepaths)

        repo_mock.read_files.assert_called_once_with(filepaths)
        slides_exporter_mock.generate_slides.assert_called_once_with([notebook])
        repo_mock.write_files.assert_called_once_with([notebook])

    @patch(
        "convert_to_slides.notebook_repo.NotebookRepo",
    )
    @patch(
        "convert_to_slides.slides_exporter.SlidesExporterProcessor",
    )
    @patch(
        "convert_to_slides.__main__.parse_args",
        return_value=Args(
            filepaths="hello world", delimiter=" ", execute=True, force_slides=True
        ),
    )
    @patch("convert_to_slides.__main__.process_notebooks", side_effect=raise_ValueError)
    def test_main_exception_thrown_returns_non_zero_value(
        self,
        process_notebooks_func,
        parse_args_func,
        exporter,
        repo,
    ):
        result = main()
        parse_args_func.assert_called()
        process_notebooks_func.assert_called()
        assert 0 != result

    @patch("convert_to_slides.notebook_repo.NotebookRepo")
    @patch("convert_to_slides.slides_exporter.SlidesExporterProcessor")
    @patch(
        "convert_to_slides.__main__.parse_args",
        return_value=Args(
            filepaths="hello world", delimiter=" ", execute=True, force_slides=True
        ),
    )
    @patch("convert_to_slides.__main__.process_notebooks")
    def test_main_no_exception_thrown_returns_0(
        self,
        process_notebooks_func,
        parse_args_func,
        exporter,
        repo,
    ):
        result = main()
        parse_args_func.assert_called()
        process_notebooks_func.assert_called()
        # assert
        assert 0 == result
