from warning_logic import analyse_warnings


class ResultUIUpdateController:
    """
    Owns UI updates after a calculation.

    Keeps main_window.py as a coordinator only.
    """

    def __init__(
            self,
            output_panel,
            diagnostics_panel,
            warning_panel,
            audit_panel,
            foundation_status_panel,
            design_history_controller,
            get_startup_health_callback,
            set_last_results_callback,
            finalize_foundation_callback=None,
    ):
        self.output_panel = output_panel
        self.diagnostics_panel = diagnostics_panel
        self.warning_panel = warning_panel
        self.audit_panel = audit_panel
        self.foundation_status_panel = foundation_status_panel
        self.design_history_controller = design_history_controller
        self.get_startup_health = get_startup_health_callback
        self.set_last_results = set_last_results_callback
        self.finalize_foundation = finalize_foundation_callback

    def update_after_calculation(self, solved, diagnostics_report, audit_rows):
        solved = solved if isinstance(solved, dict) else {}

        if self.design_history_controller is not None:
            solved = self.design_history_controller.record_iteration(
                solved=solved,
                diagnostics_report=diagnostics_report,
                audit_rows=audit_rows,
            )

        if callable(self.finalize_foundation):
            solved = self.finalize_foundation(
                solved
            )

        self.set_last_results(solved)

        self.output_panel.update_outputs(solved)

        if self.foundation_status_panel is not None:
            self.foundation_status_panel.update_status(
                results=solved,
                startup_health_report=self.get_startup_health() or {},
            )

        self.diagnostics_panel.update_diagnostics(diagnostics_report)
        self.audit_panel.update_audit(audit_rows)

        warnings = analyse_warnings(solved)
        self.warning_panel.update_warnings(warnings)

