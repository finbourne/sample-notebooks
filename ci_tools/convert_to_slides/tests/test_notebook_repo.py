from convert_to_slides.notebook_repo import NotebookRepo


class TestNotebookRepo:
    repo = NotebookRepo(force_slide_metadata=False)

    def test_filter_files_empty_list_returns_empty_generator(self):
        res = list(self.repo.filter_files([]))
        assert [] == res
