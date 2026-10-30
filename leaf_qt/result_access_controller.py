from PySide6.QtWidgets import QMessageBox


class ResultAccessController:
    """
    Shared result access and result validation gate.

    Used by report export, window launching, report viewing,
    and future controller systems.
    """

    def __init__(self, get_results_callback, get_main_outputs_callback=None):
        self.get_results = get_results_callback
        self.get_main_outputs = get_main_outputs_callback

    def current_results(self):
        results = self.get_results()

        if isinstance(results, dict):
            return results

        return {}

    def current_main_outputs(self):
        if self.get_main_outputs is None:
            return {}

        results = self.get_main_outputs()

        if isinstance(results, dict):
            return results

        return {}

    def require_results(self, parent=None, message="Run a calculation first."):
        results = self.current_results()

        if not results:
            QMessageBox.warning(
                parent,
                "No Results",
                message,
            )
            return None

        return results

    def require_main_outputs(self, parent=None):
        results = self.current_main_outputs()

        if not results:
            QMessageBox.warning(
                parent,
                "No Results",
                "No scalar output results are available.",
            )
            return None

        return results