from IPython.core.display import display


class StopExecution(Exception):
    def __init__(self, message):
        self.message = message

    def _render_traceback_(self):
        display(self.message)
        pass