from dataclasses import dataclass
from nbformat import NotebookNode
from typing import Dict


@dataclass
class Notebook:
    filepath: str
    source: NotebookNode
    slides_source: str
    slides_resources: Dict
