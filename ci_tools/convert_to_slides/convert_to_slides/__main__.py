from argparse import ArgumentParser
from convert_to_slides.notebook_repo import NotebookRepo
from convert_to_slides.slides_exporter import SlidesExporterProcessor

if __name__ == "__main__":
    parser = ArgumentParser(
        prog="convert_to_slides",
        description="Takes a list of mixed files and converts to revealjs slides.",
    )
    parser.add_argument(
        "-f",
        "--filepaths",
        type=str,
        required=True,
        help="delimiter seperated list of paths to notebooks",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        action="store",
        nargs="?",
        default=",",
        help="delimiter to use for splitting filepath list",
    )
    parser.add_argument(
        "-e",
        "--execute",
        action="store_true",
        default=False,
        help="execute notebook when generating slides",
    )
    parser.add_argument(
        "-s",
        "--force-slides",
        default=False,
        action="store_true",
        help="throw error if notebooks don't have any slideshow metadata saved",
    )
    args = parser.parse_args()
    notebook_repo = NotebookRepo(force_slide_metadata=args.force_slides)
    slides_exporter = SlidesExporterProcessor(execute_notebooks=args.execute)

    filepaths = args.filepaths.split(args.delimiter)
    notebooks = notebook_repo.read_files(filepaths=filepaths)
    notebooks_with_slides = slides_exporter.generate_slides(notebooks)
    notebook_repo.write_files(notebooks_with_slides)
