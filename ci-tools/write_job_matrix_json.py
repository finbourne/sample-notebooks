import os
import json
from pathlib import Path

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

    nbs_dirs = []

    for root, dirs, files in os.walk(nb_root, topdown=False):
        if ".ipynb_checkpoints" not in root:
            for name in files:
                if name.lower().endswith(".ipynb"):
                    nbs_dirs.append(os.path.join(root))
    
    return set(nbs_dirs)

def construct_matrix_json(nb_dirs):

    matrix_json = []
    for notebook_dir in nb_dirs:

        notebook_dir_short =  notebook_dir[notebook_dir.rfind("sample-notebooks")+26:]

        matrix_json.append({"notebookDir": notebook_dir, "notebookDirShort": notebook_dir_short})
    
    return matrix_json

def main():

    root_nb_path = Path(__file__).absolute().parent.parent.joinpath("examples")

    nb_dirs = find_nbs(root_nb_path)

    matrix_json = construct_matrix_json(nb_dirs)

    matrix_json_path = Path(__file__).absolute().parent.parent.joinpath("ci-tools").joinpath("job_matrix.json")

    print(matrix_json_path)

    with open(matrix_json_path, "w") as file:
        json.dump(matrix_json, file)

if __name__ == "__main__":
    main()
