import os
import unittest
from pathlib import Path

from docgen import (
    NbMeta,
    build_doc,
    process_nb,
    nb_relative_path)

from parameterized import parameterized


class DocGenTests(unittest.TestCase):

    @parameterized.expand(
        [
            ["notebooks/no_features.ipynb", "Notebook title", "Longer description of notebook"],
            ["notebooks/no_description.ipynb", "Notebook title", None, ["derived portfolios",
                                                                        "properties",
                                                                        "transaction config",]],
            ["notebooks/valid.ipynb", "Notebook title", "Longer description of notebook", ["derived portfolios",
                                                                                           "properties",
                                                                                           "transaction config",]]
        ]
    )
    def test_parse_metadata(self, nb, title=None, description=None, features=[]):
        meta = process_nb(nb)

        self.assertEqual(meta.title, title)
        self.assertEqual(meta.description, description)
        self.assertListEqual(meta.features, features)

    @parameterized.expand(
        [
            "notebooks/markdown_cell.ipynb",
            "notebooks/no_docstring.ipynb"
        ]
    )
    def test_invalid_metadata(self, nb):
        meta = process_nb(nb)
        self.assertIsNone(meta)

    def test_build_doc(self):
        meta = [
            NbMeta("a/b", "b.ipynb", "title ab", "des ab", ["a", "b"]),
            NbMeta("c", "c.ipynb", "title c", "des c", ["c"]),
            NbMeta("a", "a.ipynb", "title a", "des a", ["a"]),
        ]

        template = Path(__file__).parent.parent.joinpath("README.mustache")

        doc = build_doc(meta, template)

        self.assertIn("| a.ipynb | title a | des a | a |", doc)
        self.assertIn("| b.ipynb | title ab | des ab | a, b |", doc)
        self.assertIn("| c.ipynb | title c | des c | c |",  doc)

        print(doc)

    def test_nb_relative_path_with_relative_path(self):

        nb_root = Path(__file__).parent.parent.joinpath("examples").joinpath("use-cases").joinpath("ibor").joinpath("notebook.ipynb")
        rel_path = nb_relative_path(nb_root)

        self.assertEqual("examples/use-cases/ibor", rel_path)

    def test_nb_relative_path_with_absolute_path(self):
        nb_root = Path(__file__).parent.parent.joinpath("examples").joinpath("use-cases").joinpath("ibor").joinpath("notebook.ipynb").absolute()
        rel_path = nb_relative_path(nb_root)

        self.assertEqual("examples/use-cases/ibor", rel_path)


if __name__ == '__main__':
    unittest.main()
