"""
PHASE 11A.7
Regen Geometry Output Window

Purpose:
    User-facing Qt window for the 11A regen geometry output architecture.

This window reads:
    phase_11a6_regen_geometry_output_architecture_owner_report
    phase_11a6_regen_geometry_output_architecture_owner_text

It does not:
    - modify solver values
    - apply candidate geometry
    - change user inputs
"""

from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QPushButton,
    QHeaderView,
)


class RegenGeometryOutputWindow(QDialog):
    def __init__(self, results=None, parent=None):
        super().__init__(parent)

        self.results = results if isinstance(results, dict) else {}

        self.setWindowTitle("LEAF Regen Geometry Diagnostics")
        self.resize(1100, 760)

        self._build_ui()
        self.populate(self.results)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Regen Geometry Diagnostics")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Discovery → Validation → Explanation → Recommendation → Candidate Geometry"
        )
        layout.addWidget(subtitle)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.summary_table = self._new_table()
        self.validation_table = self._new_table()
        self.recommendation_table = self._new_table()
        self.candidate_table = self._new_table()

        self.acceptance_table = self._new_table()
        self.acceptance_patch_text = QTextEdit()
        self.acceptance_patch_text.setReadOnly(True)

        self.visual_recommendation_table = self._new_table()
        self.visual_recommendation_detail_text = QTextEdit()
        self.visual_recommendation_detail_text.setReadOnly(True)

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)

        self.tabs.addTab(self._wrap(self.summary_table), "Summary")
        self.tabs.addTab(self._wrap(self.validation_table), "Validation")
        self.tabs.addTab(self._wrap(self.recommendation_table), "Recommendations")
        self.tabs.addTab(self._wrap(self.candidate_table), "Candidate Geometry")

        acceptance_tab = QWidget()
        acceptance_layout = QVBoxLayout(acceptance_tab)

        acceptance_layout.addWidget(QLabel("Candidate Acceptance Package"))
        acceptance_layout.addWidget(self.acceptance_table)
        acceptance_layout.addWidget(QLabel("Input Patch Preview"))
        acceptance_layout.addWidget(self.acceptance_patch_text)

        patch_button_row = QHBoxLayout()

        self.copy_acceptance_patch_button = QPushButton("Copy Input Patch")
        self.copy_acceptance_patch_button.clicked.connect(
            self.copy_acceptance_patch_to_clipboard
        )
        patch_button_row.addWidget(self.copy_acceptance_patch_button)

        patch_button_row.addStretch(1)
        acceptance_layout.addLayout(patch_button_row)

        self.tabs.addTab(acceptance_tab, "Acceptance")

        visual_tab = QWidget()
        visual_layout = QVBoxLayout(visual_tab)

        visual_layout.addWidget(QLabel("Full Visual Recommendation Integration"))
        visual_layout.addWidget(self.visual_recommendation_table)
        visual_layout.addWidget(QLabel("Selected Recommendation / Candidate Detail"))
        visual_layout.addWidget(self.visual_recommendation_detail_text)

        self.tabs.addTab(visual_tab, "Visual Recommendation")

        self.tabs.addTab(self.report_text, "Full Report")

        button_row = QHBoxLayout()
        button_row.addStretch(1)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_row.addWidget(close_button)

        layout.addLayout(button_row)

    def _new_table(self):
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        return table

    def _wrap(self, widget):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.addWidget(widget)
        return wrapper

    def populate(self, results):
        report = results.get(
            "phase_11a6_regen_geometry_output_architecture_owner_report",
            {},
        )

        if not isinstance(report, dict):
            report = {}

        self._populate_summary(report.get("summary", {}))
        self._populate_validation(report.get("validation", {}))
        self._populate_recommendations(report.get("recommendations", {}))
        self._populate_candidate(report.get("candidate", {}))
        self._populate_acceptance(results)
        self._populate_visual_recommendation(results, report)

        text = results.get(
            "phase_11a6_regen_geometry_output_architecture_owner_text",
            "No regen geometry output architecture report available.",
        )
        self.report_text.setPlainText(str(text))

    def _populate_acceptance(self, results):
        record = results.get(
            "phase_11a8_regen_geometry_candidate_acceptance_owner_record",
            {},
        )

        patch = results.get(
            "phase_11a8_regen_geometry_candidate_acceptance_owner_input_patch",
            {},
        )

        ready = results.get(
            "phase_11a8_regen_geometry_candidate_acceptance_owner_ready",
            False,
        )

        status = results.get(
            "phase_11a8_regen_geometry_candidate_acceptance_owner_engineering_status",
            "UNKNOWN",
        )

        if not isinstance(record, dict):
            record = {}

        if not isinstance(patch, dict):
            patch = {}

        rows = [
            ["Acceptance Ready", ready],
            ["Engineering Status", status],
            ["Recommendation Count", record.get("recommendation_count")],
            ["Changed Keys", ", ".join(record.get("changed_keys", [])) if isinstance(record.get("changed_keys"), list) else ""],
            ["Design History Event", record.get("design_history_event_type")],
            ["Summary", record.get("design_history_summary")],
        ]

        self._set_table(
            self.acceptance_table,
            headers=["Field", "Value"],
            rows=rows,
        )

        if patch:
            lines = []
            for key, value in sorted(patch.items()):
                lines.append(f"{key} = {value}")
            self.acceptance_patch_text.setPlainText("\n".join(lines))
        else:
            self.acceptance_patch_text.setPlainText(
                "No candidate input patch is currently available."
            )

    def copy_acceptance_patch_to_clipboard(self):
        text = self.acceptance_patch_text.toPlainText()

        if not text.strip() or "No candidate input patch" in text:
            QMessageBox.information(
                self,
                "Candidate Acceptance",
                "No candidate input patch is available to copy.",
            )
            return

        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Candidate Acceptance",
            "Candidate input patch copied to clipboard.",
        )

    def _populate_summary(self, summary):
        if not isinstance(summary, dict):
            summary = {}

        rows = [(key, value) for key, value in sorted(summary.items())]
        self._set_table(
            self.summary_table,
            headers=["Metric", "Value"],
            rows=rows,
        )

    def _populate_validation(self, validation):
        if not isinstance(validation, dict):
            validation = {}

        grouped = validation.get("grouped_results", {})
        if not isinstance(grouped, dict):
            grouped = {}

        rows = []

        for state in ("FAIL", "WARN", "PASS", "NOT_AVAILABLE"):
            items = grouped.get(state, [])
            if not isinstance(items, list):
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue

                rows.append(
                    [
                        item.get("validation_state"),
                        item.get("constraint_id"),
                        item.get("label"),
                        item.get("value"),
                        item.get("unit"),
                        item.get("reason"),
                    ]
                )

        self._set_table(
            self.validation_table,
            headers=["State", "Constraint", "Label", "Value", "Unit", "Reason"],
            rows=rows,
        )

    def _populate_recommendations(self, recommendations):
        if not isinstance(recommendations, dict):
            recommendations = {}

        items = recommendations.get("recommendations", [])
        if not isinstance(items, list):
            items = []

        rows = []

        for item in items:
            if not isinstance(item, dict):
                continue

            rows.append(
                [
                    item.get("priority"),
                    item.get("recommendation_id"),
                    item.get("title"),
                    item.get("source_constraint"),
                    ", ".join(item.get("target_variables", [])),
                    item.get("proposed_direction"),
                    item.get("expected_benefit"),
                ]
            )

        self._set_table(
            self.recommendation_table,
            headers=[
                "Priority",
                "ID",
                "Title",
                "Source",
                "Targets",
                "Direction",
                "Expected Benefit",
            ],
            rows=rows,
        )

    def _populate_visual_recommendation(self, results, report):
        if not isinstance(report, dict):
            report = {}

        validation = report.get("validation", {})
        explanations = report.get("explanations", {})
        recommendations = report.get("recommendations", {})
        candidate = report.get("candidate", {})

        if not isinstance(validation, dict):
            validation = {}
        if not isinstance(explanations, dict):
            explanations = {}
        if not isinstance(recommendations, dict):
            recommendations = {}
        if not isinstance(candidate, dict):
            candidate = {}

        validation_items = []
        grouped = validation.get("grouped_results", {})
        if isinstance(grouped, dict):
            for state in ("FAIL", "WARN"):
                items = grouped.get(state, [])
                if isinstance(items, list):
                    validation_items.extend([
                        item for item in items
                        if isinstance(item, dict)
                    ])

        explanation_items = explanations.get("explanations", [])
        if not isinstance(explanation_items, list):
            explanation_items = []

        recommendation_items = recommendations.get("recommendations", [])
        if not isinstance(recommendation_items, list):
            recommendation_items = []

        comparison_rows = candidate.get("comparison_rows", [])
        if not isinstance(comparison_rows, list):
            comparison_rows = []

        explanation_by_constraint = {
            item.get("constraint_id"): item
            for item in explanation_items
            if isinstance(item, dict)
        }

        recommendations_by_constraint = {}
        for item in recommendation_items:
            if not isinstance(item, dict):
                continue
            source = item.get("source_constraint")
            recommendations_by_constraint.setdefault(source, []).append(item)

        changed_by_variable = {
            item.get("variable"): item
            for item in comparison_rows
            if isinstance(item, dict) and item.get("changed")
        }

        rows = []

        for validation_item in validation_items:
            constraint_id = validation_item.get("constraint_id")
            explanation = explanation_by_constraint.get(constraint_id, {})
            recs = recommendations_by_constraint.get(constraint_id, [])

            if recs:
                for rec in recs:
                    target_variables = rec.get("target_variables", [])
                    if not isinstance(target_variables, list):
                        target_variables = []

                    changed_targets = [
                        variable for variable in target_variables
                        if variable in changed_by_variable
                    ]

                    rows.append([
                        validation_item.get("validation_state"),
                        constraint_id,
                        rec.get("priority"),
                        rec.get("title"),
                        ", ".join(target_variables),
                        ", ".join(changed_targets),
                        rec.get("expected_benefit"),
                    ])
            else:
                rows.append([
                    validation_item.get("validation_state"),
                    constraint_id,
                    "N/A",
                    "No recommendation linked",
                    "",
                    "",
                    explanation.get("engineering_meaning", validation_item.get("reason")),
                ])

        if not rows and recommendation_items:
            for rec in recommendation_items:
                if not isinstance(rec, dict):
                    continue

                target_variables = rec.get("target_variables", [])
                if not isinstance(target_variables, list):
                    target_variables = []

                changed_targets = [
                    variable for variable in target_variables
                    if variable in changed_by_variable
                ]

                rows.append([
                    rec.get("source_state"),
                    rec.get("source_constraint"),
                    rec.get("priority"),
                    rec.get("title"),
                    ", ".join(target_variables),
                    ", ".join(changed_targets),
                    rec.get("expected_benefit"),
                ])

        self._set_table(
            self.visual_recommendation_table,
            headers=[
                "State",
                "Constraint",
                "Priority",
                "Recommendation",
                "Targets",
                "Changed Targets",
                "Expected Benefit",
            ],
            rows=rows,
        )

        self.visual_recommendation_detail_text.setPlainText(
            self._build_visual_recommendation_detail_text(
                results=results,
                validation_items=validation_items,
                explanation_items=explanation_items,
                recommendation_items=recommendation_items,
                comparison_rows=comparison_rows,
            )
        )

    def _build_visual_recommendation_detail_text(
            self,
            results,
            validation_items,
            explanation_items,
            recommendation_items,
            comparison_rows,
    ):
        lines = []
        lines.append("FULL VISUAL RECOMMENDATION INTEGRATION")
        lines.append("======================================")
        lines.append("")

        ready = results.get(
            "phase_11a8_regen_geometry_candidate_acceptance_owner_ready",
            False,
        )
        status = results.get(
            "phase_11a8_regen_geometry_candidate_acceptance_owner_engineering_status",
            "UNKNOWN",
        )

        lines.append(f"Acceptance Ready: {ready}")
        lines.append(f"Acceptance Status: {status}")
        lines.append("")

        lines.append("Validation Issues:")
        if validation_items:
            for item in validation_items:
                lines.append(
                    f"- {item.get('validation_state')} | "
                    f"{item.get('constraint_id')} | "
                    f"{item.get('reason')}"
                )
        else:
            lines.append("- No FAIL/WARN validation issues.")

        lines.append("")
        lines.append("Explanations:")
        if explanation_items:
            for item in explanation_items:
                lines.append("")
                lines.append(f"- {item.get('constraint_id')}")
                lines.append(f"  Failure Mode: {item.get('failure_mode')}")
                lines.append(f"  Meaning: {item.get('engineering_meaning')}")
        else:
            lines.append("- No explanations required.")

        lines.append("")
        lines.append("Recommendations:")
        if recommendation_items:
            for item in recommendation_items:
                lines.append("")
                lines.append(f"- {item.get('title')} [{item.get('priority')}]")
                lines.append(f"  Source: {item.get('source_constraint')}")
                lines.append(f"  Direction: {item.get('proposed_direction')}")
                lines.append(f"  Expected Benefit: {item.get('expected_benefit')}")
        else:
            lines.append("- No recommendations required.")

        lines.append("")
        lines.append("Candidate Geometry Changes:")
        changed_rows = [
            row for row in comparison_rows
            if isinstance(row, dict) and row.get("changed")
        ]

        if changed_rows:
            for row in changed_rows:
                lines.append(
                    f"- {row.get('variable')}: "
                    f"{row.get('before')} -> {row.get('after')} "
                    f"(delta={row.get('delta')})"
                )
        else:
            lines.append("- No candidate geometry changes.")

        lines.append("")
        lines.append("Input Patch:")
        patch = results.get(
            "phase_11a8_regen_geometry_candidate_acceptance_owner_input_patch",
            {},
        )
        if isinstance(patch, dict) and patch:
            for key, value in sorted(patch.items()):
                lines.append(f"- {key}: {value}")
        else:
            lines.append("- No patch available.")

        return "\n".join(lines)

    def _populate_candidate(self, candidate):
        if not isinstance(candidate, dict):
            candidate = {}

        rows = candidate.get("comparison_rows", [])
        if not isinstance(rows, list):
            rows = []

        table_rows = []

        for row in rows:
            if not isinstance(row, dict):
                continue

            table_rows.append(
                [
                    row.get("variable"),
                    row.get("before"),
                    row.get("after"),
                    row.get("delta"),
                    "YES" if row.get("changed") else "NO",
                ]
            )

        self._set_table(
            self.candidate_table,
            headers=["Variable", "Before", "Candidate", "Delta", "Changed"],
            rows=table_rows,
        )

    def _set_table(self, table, headers, rows):
        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem("" if value is None else str(value))
                table.setItem(row_index, column_index, item)

        table.resizeRowsToContents()