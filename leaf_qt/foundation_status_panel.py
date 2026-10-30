from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)


class FoundationStatusPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.latest_results = {}
        self.startup_health_report = {}

        self.create_layout()

    def create_layout(self):
        layout = QVBoxLayout(self)

        title = QLabel("Foundation Status")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 6px;
            }
        """)
        layout.addWidget(title)

        self.summary_label = QLabel("No calculation has been run yet.")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                border: 1px solid #444;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.summary_label)

        button_bar = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh)

        button_bar.addWidget(self.refresh_button)
        layout.addLayout(button_bar)

        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        layout.addWidget(self.text_box)

    def update_status(self, results=None, startup_health_report=None):
        if isinstance(results, dict):
            self.latest_results = results

        if isinstance(startup_health_report, dict):
            self.startup_health_report = startup_health_report

        self.refresh()

    def refresh(self):
        results = self.latest_results or {}
        startup = self.startup_health_report or {}

        startup_status = startup.get(
            "startup_health_status",
            results.get("startup_health_status", "UNKNOWN"),
        )

        attachment_summary = self.get_attachment_summary(results)
        attachment_failures = self.get_non_blocking_attachment_failures(results)
        skipped_layers = self.get_skipped_attachment_layers(results)

        pipeline_status = results.get(
            "foundation_attachment_pipeline_status",
            "NOT_RUN",
        )

        regression_status = results.get("foundation_regression_status", "NOT_RUN")
        benchmark_status = results.get("benchmark_status", "NOT_RUN")
        reproduction_status = results.get("engine_reproduction_status", "NOT_RUN")

        result_key_audit_status = results.get(
            "foundation_result_key_audit_status",
            "NOT_RUN",
        )

        self.summary_label.setText(
            f"Startup: {startup_status} | "
            f"Pipeline: {pipeline_status} | "
            f"Regression: {regression_status} | "
            f"Benchmark: {benchmark_status} | "
            f"Reproduction: {reproduction_status} | "
            f"Non-blocking failures: {len(attachment_failures)} | "
            f"Skipped: {len(skipped_layers)} | "
            f"Key audit: {result_key_audit_status}"
        )

        self.text_box.setPlainText(
            self.build_status_text(
                results=results,
                startup=startup,
                attachment_summary=attachment_summary,
                attachment_failures=attachment_failures,
                skipped_layers=skipped_layers,
            )
        )

    def get_attachment_summary(self, results):
        summary = results.get("foundation_attachment_summary", {})

        if isinstance(summary, dict):
            return summary

        return {}

    def get_attachment_audit_rows(self, results):
        rows = results.get("foundation_attachment_audit", [])

        if isinstance(rows, list):
            return rows

        return []

    def get_non_blocking_attachment_failures(self, results):
        rows = self.get_attachment_audit_rows(results)

        return [
            row for row in rows
            if isinstance(row, dict)
            and row.get("status") == "FAILED_NON_BLOCKING"
        ]

    def get_skipped_attachment_layers(self, results):
        rows = self.get_attachment_audit_rows(results)

        return [
            row for row in rows
            if isinstance(row, dict)
            and row.get("status") == "SKIPPED"
        ]

    def build_status_text(
            self,
            results,
            startup,
            attachment_summary,
            attachment_failures,
            skipped_layers,
    ):
        lines = []
        lines.append("LEAF FOUNDATION STATUS")
        lines.append("======================")
        lines.append("")

        self._append_startup_health(lines, results, startup)
        self._append_attachment_pipeline(
            lines,
            results,
            attachment_summary,
            attachment_failures,
            skipped_layers,
        )
        self._append_foundation_regression(lines, results)
        self._append_result_key_audit(lines, results)
        self._append_benchmark_status(lines, results)
        self._append_design_evidence(lines, results)
        self._append_validation_source_status(lines, results)
        self._append_interpretation(lines, attachment_failures)

        return "\n".join(lines)

    def _append_startup_health(self, lines, results, startup):
        lines.append("Startup Health")
        lines.append("--------------")
        lines.append(
            f"Status: {startup.get('startup_health_status', results.get('startup_health_status', 'UNKNOWN'))}"
        )
        lines.append(
            f"Required failures: {startup.get('startup_health_required_failure_count', results.get('startup_health_required_failure_count', 'UNKNOWN'))}"
        )
        lines.append(
            f"Optional warnings: {startup.get('startup_health_optional_warning_count', results.get('startup_health_optional_warning_count', 'UNKNOWN'))}"
        )
        lines.append("")

    def _append_attachment_pipeline(
            self,
            lines,
            results,
            attachment_summary,
            attachment_failures,
            skipped_layers,
    ):
        lines.append("Foundation Attachment Pipeline")
        lines.append("------------------------------")
        lines.append(
            f"Status: {results.get('foundation_attachment_pipeline_status', 'NOT_RUN')}"
        )
        lines.append(
            f"Benchmark case: {results.get('foundation_attachment_benchmark_case', 'N/A')}"
        )
        lines.append(
            f"Started: {results.get('foundation_attachment_pipeline_started_at', 'N/A')}"
        )
        lines.append(
            f"Completed: {results.get('foundation_attachment_pipeline_completed_at', 'N/A')}"
        )
        lines.append("")

        lines.append("Attachment Summary:")
        lines.append(f"- Total: {attachment_summary.get('total', 0)}")
        lines.append(f"- Passed: {attachment_summary.get('passed', 0)}")
        lines.append(f"- Skipped: {attachment_summary.get('skipped', 0)}")
        lines.append(f"- Returned None: {attachment_summary.get('returned_none', 0)}")
        lines.append(
            f"- Failed non-blocking: {attachment_summary.get('failed_non_blocking', 0)}"
        )
        lines.append("")

        if attachment_failures:
            lines.append("Non-Blocking Attachment Failures:")

            for row in attachment_failures:
                lines.append(f"- {row.get('layer', 'unknown')}: {row.get('message', '')}")

                if row.get("error_type"):
                    lines.append(f"  Error type: {row.get('error_type')}")

            lines.append("")
        else:
            lines.append("Non-Blocking Attachment Failures: none")
            lines.append("")

        if skipped_layers:
            lines.append("Skipped Optional Layers:")

            for row in skipped_layers:
                lines.append(f"- {row.get('layer', 'unknown')}: {row.get('message', '')}")

            lines.append("")
        else:
            lines.append("Skipped Optional Layers: none")
            lines.append("")

    def _append_foundation_regression(self, lines, results):
        lines.append("Foundation Regression")
        lines.append("---------------------")
        lines.append(f"Status: {results.get('foundation_regression_status', 'NOT_RUN')}")
        lines.append(f"Passed: {results.get('foundation_regression_passed_count', 'N/A')}")
        lines.append(f"Failed: {results.get('foundation_regression_failed_count', 'N/A')}")
        lines.append("")

    def _append_result_key_audit(self, lines, results):
        lines.append("Result Key Audit")
        lines.append("----------------")
        lines.append(
            f"Status: {results.get('foundation_result_key_audit_status', 'NOT_RUN')}"
        )
        lines.append(
            f"Registered keys: {results.get('foundation_result_key_audit_registered_count', 'N/A')}"
        )
        lines.append(
            f"Unregistered keys: {results.get('foundation_result_key_audit_unregistered_count', 'N/A')}"
        )
        lines.append("")

    def _append_benchmark_status(self, lines, results):
        lines.append("Benchmark / Reproduction")
        lines.append("------------------------")
        lines.append(
            f"Benchmark case: {results.get('benchmark_selected_case', results.get('foundation_attachment_benchmark_case', 'N/A'))}"
        )
        lines.append(f"Benchmark status: {results.get('benchmark_status', 'NOT_RUN')}")
        lines.append(f"Benchmark failed count: {results.get('benchmark_failed_count', 'N/A')}")
        lines.append(
            f"Engine reproduction status: {results.get('engine_reproduction_status', 'NOT_RUN')}"
        )
        lines.append(
            f"Engine reproduction confidence: {results.get('engine_reproduction_confidence', 'N/A')}"
        )
        lines.append("")

    def _append_design_evidence(self, lines, results):
        lines.append("Design Evidence")
        lines.append("---------------")
        lines.append(
            f"Design narrative: {results.get('design_iteration_narrative_status', results.get('design_iteration_narrative_attachment_status', 'N/A'))}"
        )
        lines.append(
            f"Optimisation proof: {results.get('regen_optimisation_proof_status', results.get('regen_optimisation_proof_attachment_status', 'N/A'))}"
        )
        lines.append(
            f"Root cause: {results.get('failure_root_cause_status', results.get('failure_root_cause_attachment_status', 'N/A'))}"
        )
        lines.append(
            f"Recommendations: {results.get('recommendation_explanation_status', results.get('recommendation_explanation_attachment_status', 'N/A'))}"
        )
        lines.append(
            f"Before/after: {results.get('before_after_comparison_status', results.get('before_after_comparison_attachment_status', 'N/A'))}"
        )
        lines.append("")

    def _append_validation_source_status(self, lines, results):
        lines.append("Validation / Source Status")
        lines.append("--------------------------")
        lines.append(f"Validation status: {results.get('validation_status', 'N/A')}")
        lines.append(f"Regen validation status: {results.get('regen_validation_status', 'N/A')}")
        lines.append(f"Material source mode: {results.get('material_source_mode', 'N/A')}")
        lines.append(f"Coating source mode: {results.get('coating_source_mode', 'N/A')}")
        lines.append(f"Validation mode: {results.get('validation_mode', 'N/A')}")
        lines.append("")

    def _append_interpretation(self, lines, attachment_failures):
        lines.append("Interpretation")
        lines.append("--------------")
        lines.append("- This panel checks foundation health, not engine correctness by itself.")
        lines.append("- Benchmark/reproduction failure must not block the main calculation.")
        lines.append("- Skipped optional layers mean that evidence/report modules were unavailable.")
        lines.append("- FAILED_NON_BLOCKING means LEAF protected the core calculation from a report-layer failure.")

        if attachment_failures:
            lines.append("- Treat affected reports as incomplete until failed attachment layers are repaired.")

        lines.append("- Core solver results should still be inspected in Main Outputs and reports.")