import urllib.parse

class NbMeta:
    """
    Metadata associated with a notebook.

    Attributes
    ----------

    path : str
        Relative folder path of the location of the notebook from the root of the repository
    filename : str
        Notebook filename
    title : str
        notebook title
    description : str
        Notebook description, taken from the short description of the docstring
    features : [str]
        List of notebook features, taken from the attributes of the docstring
    formatted_features : str
        Comma separated formatted string based on features

    """

    def __init__(self, path: str, filename: str, title: str, description: str, features: [str]):
        """
        Parameters
        ----------
        path : str
            Relative folder path of the location of the notebook from the root of the repository
        filename : str
            Notebook filename
        title : str
            Notebook title
        description : str
            Notebook description, taken from the short description of the docstring
        features : [str]
            List of notebook features, taken from the attributes of the docstring
        """

        self.path = path
        self.filename = filename
        self.url_filename = urllib.parse.quote(filename)
        self.title = title
        self.description = description.replace("\n", "<br>") if description else description
        self.features = features
        self.formatted_features = ", ".join(self.features)

    def __str__(self):
        return self.filename

    def __repr__(self):
        return self.filename
