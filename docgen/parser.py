import chevron
import docstring_parser as dp
import itertools
import nbformat
import os
import urllib.parse
import jupytext

from pathlib import Path

from nbmeta import NbMeta
import re


def find_nbs(nb_root):
    """
    Traverses a folder looking for all .ipynb files and return them via a generator

    Parameters
    ----------
    nb_root : str
        Path to root folder containing notebooks to index

    Returns
    -------
    str
        Generator path to a discovered .ipynb file

    """
    for root, dirs, files in os.walk(nb_root, topdown=False):
        if ".ipynb_checkpoints" not in root and "docgen" not in root:
            for name in files:
                if name.lower().endswith(".ipynb"):
                    yield os.path.join(root, name)


def sanitize_docstring(raw_str):
    """
    Converts a formatted docstring and strips the leading and trailing triple "

    Parameters
    ----------
    raw_str : str
        Docstring containing triple "

    Returns
    -------
    str
        Docstring with leading and trailing triple " removed

    """
    stripped_str = raw_str.strip()
    if stripped_str.startswith('"""') and stripped_str.endswith('"""'):
        return stripped_str[3:-3]


def nb_relative_path(abs_path):
    """
    Converts a full path to a relative path removing leading . directory navigation.
    Used for formatting for display

    Parameters
    ----------
    abs_path : str
        Full path

    Returns
    -------
    str
        Relative path with directory navigation removed

    """
    rel_path = os.path.relpath(os.path.dirname(abs_path))

    return rel_path[3:] if rel_path.startswith("../") else rel_path


def process_nb(nb_path):
    """
    Extracts metadata from a notebook. By convention the metadata must:
        - be the first cell
        - be a code cell
        - contain a short description
        - contain an optional long description
        - contain an optional list of features specified as Attributes

    Parameters
    ----------
    nb_path : str
        Path to notebook file

    Returns
    -------
    NbMeta
        Notebook metadata or None if unable to load metadata

    """
    nb = nbformat.read(nb_path, as_version=4)

    if len(nb.cells) < 1 or nb.cells[0].cell_type != "code":
        print(nb_path, "x (cell 0 is not code)")
        return

    potential_cleaned_str = re.findall('(""".*""")', nb.cells[0].source, re.DOTALL)

    if len(potential_cleaned_str) == 0:
        print(nb_path, "x (no string)")
        return

    doc_str = sanitize_docstring(potential_cleaned_str[0])
    doc_str_obj = dp.parse(doc_str)

    if doc_str_obj.short_description is None:
        print(nb_path, "x (no short description)")
        return

    return NbMeta(
        nb_relative_path(nb_path),
        os.path.basename(nb_path),
        doc_str_obj.short_description,
        doc_str_obj.long_description,
        sorted([m.arg_name for m in doc_str_obj.meta])
    )


def parse(nb_root):
    """
    Navigates a root folder to find all notebooks and extract their metadata where possible

    Parameters
    ----------
    nb_root : str
        Root folder containing notebooks

    Returns
    -------
    [NbMeta]
        List of NbMeta for notebooks that metadata was extracted for

    """
    return [
        meta for meta in
        [process_nb(nb) for nb in find_nbs(nb_root)]
        if meta is not None
    ]


def build_doc(meta, template, generate_for_root_directory):
    """
    Generates a documentation index string given a list of metadata and mustache template

    Parameters
    ----------
    meta : [NbMeta]
        Notebook metadata
    template : str
        Path to mustache template for generating output documentation index. The template accepts
        a single variable 'path' containing a list of dictionaries of path: [NbMeta in the path]

    Returns
    -------
    str
        Generated documentation index
    """

    # 1. group the notebooks by path
    # 2. convert to a list of dictionaries for mustache
    # 3. sort the notebooks alphabetically
    # note: [*values] converts the generator to a list
    nbs = [{"k": key, "link": key if generate_for_root_directory else "../" + key, "v": sorted([*values], key=lambda m: m.filename)}
           for key, values in itertools.groupby(meta, lambda m: m.path)]


    # sort by relative path
    nbs.sort(key=lambda n: n["k"])

    with open(template, 'r') as f:
        return chevron.render(f, {'paths': nbs})


def save_index_page(path, doc):
    """
    Saves the documentation index to a file

    Parameters
    ----------
    path : str
        Path to save the documentation index to
    doc : str
        Documentation index
    """
    with open(path, "w") as file:
        file.write(doc)


def main():
    repo_root = Path(__file__).parent.parent
    doc_gen_root = repo_root.joinpath("docgen").resolve()
    nb_root = repo_root
    example_folder = repo_root.joinpath("examples").resolve()


    print(f"searching for notebooks in {nb_root}")

    meta = parse(nb_root=nb_root)
    readme_template = doc_gen_root.joinpath("README.mustache").resolve()
    #doc for root  directory
    doc_root = build_doc(meta, readme_template, True) 
    #generate doc for examples directory
    doc_examples = build_doc(meta, readme_template, False) 
    readme_root = nb_root.joinpath("Index.md")
    readmecopy_examples = example_folder.joinpath("README.md")

    print(f"saving index to {readme_root} and to {readmecopy_examples}")

    save_index_page(readme_root, doc_root)
    save_index_page(readmecopy_examples, doc_examples)

    ntbk = jupytext.read(readme_root)
    formatted_ntbk = jupytext.write(ntbk, 'Index.ipynb')


if __name__ == "__main__":
    main()
