# Convert to slides

A simple project intended to take a list of files added or modified in a PR, filter the list for just notebooks, and convert to reveal.js slides.

## Usage

Install the package, and run using `python -m convert_to_slides -h` to see runtime options.

You must provide a list of filepaths e.g: `python -m convert_to_slides -f "notebook1.ipynb,notebook2.ipynb"`

The resulting reveal.js files will be places in the same directory as the existing notebooks.

## Development

First install [poetry](https://python-poetry.org/):

    pip install poetry

Then install ALL required packages:

    poetry install

Run linting, testing and code coverage using tox (installed with poetry):

    tox
