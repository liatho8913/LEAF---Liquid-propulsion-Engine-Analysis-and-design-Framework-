class BenchmarkSelectionController:
    """
    Owns benchmark case selection.

    This prevents main_window.py from directly managing benchmark panel logic.
    """

    DEFAULT_CASE_KEY = None

    def __init__(self, benchmark_panel=None):
        self.benchmark_panel = benchmark_panel

    def get_selected_case(self):
        if self.benchmark_panel is None:
            return self.DEFAULT_CASE_KEY

        selected_case = self.benchmark_panel.get_selected_case_key()

        if selected_case:
            return selected_case

        return self.DEFAULT_CASE_KEY

    def set_selected_case(self, case_key):
        if self.benchmark_panel is None:
            return

        self.benchmark_panel.set_selected_case_key(case_key)