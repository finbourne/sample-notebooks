from dataclasses import dataclass
from nbformat import NotebookNode
from typing import Dict, Optional


@dataclass
class Notebook:
    filepath: str
    source: NotebookNode
    slides_source: Optional[str] = None
    slides_resources: Optional[Dict] = None
