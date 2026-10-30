import csv
import json

from PySide6.QtWidgets import QFileDialog, QMessageBox

from variable_registry import get_label, get_unit
from report_formatting import report_text_to_html, build_html_report_bundle
from station_report_builder import build_station_table_csv_text
from report_ownership import (
    build_main_output_report,
    build_validation_report,
    build_diagnostics_report,
    build_recommendation_report,
    build_axial_report,
    build_foundation_bundle_report,
    build_development_evidence_report,
    build_report_viewer_bundle,
    build_output_ownership_audit_report,
    build_foundation_attachment_audit_report,
    build_result_key_audit_report,
    build_benchmark_report,
    build_engine_reproduction_report,
)


class ReportExportController:
    """
    Owns all report/file export actions.

    Important:
    - Main output exports use scalar-only result access.
    - Report exports use full results.
    - Exported report content is routed through report_ownership.py.
    - This prevents Report Viewer and exported reports from drifting apart.
    """

    def __init__(self, parent, result_access_controller):
        self.parent = parent
        self.result_access_controller = result_access_controller

    def require_results(self):
        return self.result_access_controller.require_results(
            parent=self.parent,
            message="No calculation results to export.",
        )

    def require_main_outputs(self):
        return self.result_access_controller.require_main_outputs(
            parent=self.parent,
        )

    def export_text_report(self, title, report_text, default_name):
        if not report_text:
            QMessageBox.warning(
                self.parent,
                "No Report",
                "No report text was generated.",
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self.parent,
            title,
            default_name,
            "Text File (*.txt)",
        )

        if not path:
            return

        if not path.endswith(".txt"):
            path += ".txt"

        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write(str(report_text))
        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Export Failed",
                f"Could not export report:\n\n{exc}",
            )
            return

        QMessageBox.information(
            self.parent,
            "Export Complete",
            f"{title} exported successfully.",
        )

    def export_html_report(self, title, report_text, default_name):
        if not report_text:
            QMessageBox.warning(
                self.parent,
                "No Report",
                "No report text was generated.",
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self.parent,
            title,
            default_name,
            "HTML File (*.html)",
        )

        if not path:
            return

        if not path.endswith(".html"):
            path += ".html"

        try:
            html_text = report_text_to_html(title, str(report_text))

            with open(path, "w", encoding="utf-8") as file:
                file.write(html_text)
        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Export Failed",
                f"Could not export HTML report:\n\n{exc}",
            )
            return

        QMessageBox.information(
            self.parent,
            "Export Complete",
            f"{title} exported successfully.",
        )

    def export_outputs_json(self):
        results = self.require_main_outputs()

        if results is None:
            return

        path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Export Main Outputs as JSON",
            "leaf_main_outputs.json",
            "JSON File (*.json)",
        )

        if not path:
            return

        if not path.endswith(".json"):
            path += ".json"

        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(results, file, indent=4)
        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Export Failed",
                f"Could not export JSON:\n\n{exc}",
            )
            return

        QMessageBox.information(
            self.parent,
            "Export Complete",
            "Main outputs exported as JSON.",
        )

    def export_outputs_csv(self):
        results = self.require_main_outputs()

        if results is None:
            return

        path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Export Main Outputs as CSV",
            "leaf_main_outputs.csv",
            "CSV File (*.csv)",
        )

        if not path:
            return

        if not path.endswith(".csv"):
            path += ".csv"

        try:
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Variable", "Internal Name", "Value", "Unit"])

                for key, value in results.items():
                    writer.writerow([
                        get_label(key),
                        key,
                        value,
                        get_unit(key),
                    ])
        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Export Failed",
                f"Could not export CSV:\n\n{exc}",
            )
            return

        QMessageBox.information(
            self.parent,
            "Export Complete",
            "Main outputs exported as CSV.",
        )

    def export_report_bundle_html(self):
        results = self.require_results()

        if results is None:
            return

        reports = build_report_viewer_bundle(results)

        path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Export LEAF Report Bundle HTML",
            "leaf_report_bundle.html",
            "HTML File (*.html)",
        )

        if not path:
            return

        if not path.endswith(".html"):
            path += ".html"

        try:
            html_text = build_html_report_bundle(reports)

            with open(path, "w", encoding="utf-8") as file:
                file.write(html_text)
        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Export Failed",
                f"Could not export report bundle:\n\n{exc}",
            )
            return

        QMessageBox.information(
            self.parent,
            "Export Complete",
            "Report bundle exported successfully.",
        )

    def export_station_table_csv(self):
        results = self.require_results()

        if results is None:
            return

        csv_text = build_station_table_csv_text(results)

        if not csv_text:
            QMessageBox.warning(
                self.parent,
                "No Station Data",
                "No station-by-station data was found in the current results.",
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Export Station Table CSV",
            "leaf_station_table.csv",
            "CSV File (*.csv)",
        )

        if not path:
            return

        if not path.endswith(".csv"):
            path += ".csv"

        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write(csv_text)
        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Export Failed",
                f"Could not export station table:\n\n{exc}",
            )
            return

        QMessageBox.information(
            self.parent,
            "Export Complete",
            "Station table exported successfully.",
        )

    def _export_owned_text_report(self, title, builder, default_name):
        results = self.require_results()

        if results is None:
            return

        self.export_text_report(
            title,
            builder(results),
            default_name,
        )

    def _export_owned_html_report(self, title, builder, default_name):
        results = self.require_results()

        if results is None:
            return

        self.export_html_report(
            title,
            builder(results),
            default_name,
        )

    def export_main_output_report_txt(self):
        self._export_owned_text_report(
            "Export Main Output Report",
            build_main_output_report,
            "leaf_main_output_report.txt",
        )

    def export_validation_report_txt(self):
        self._export_owned_text_report(
            "Export Validation Report",
            build_validation_report,
            "leaf_validation_report.txt",
        )

    def export_diagnostics_report_txt(self):
        self._export_owned_text_report(
            "Export Diagnostics Report",
            build_diagnostics_report,
            "leaf_diagnostics_report.txt",
        )

    def export_recommendation_report_txt(self):
        self._export_owned_text_report(
            "Export Recommended Design Report",
            build_recommendation_report,
            "leaf_recommended_design_report.txt",
        )

    def export_axial_report_txt(self):
        self._export_owned_text_report(
            "Export Axial Report",
            build_axial_report,
            "leaf_axial_report.txt",
        )

    def export_foundation_bundle_report_txt(self):
        self._export_owned_text_report(
            "Export Foundation Bundle Report",
            build_foundation_bundle_report,
            "leaf_foundation_bundle_report.txt",
        )

    def export_development_evidence_report_txt(self):
        self._export_owned_text_report(
            "Export Development Evidence Report",
            build_development_evidence_report,
            "leaf_development_evidence_report.txt",
        )

    def export_development_evidence_report_html(self):
        self._export_owned_html_report(
            "LEAF Development Evidence Report",
            build_development_evidence_report,
            "leaf_development_evidence_report.html",
        )

    def export_output_ownership_audit_txt(self):
        self._export_owned_text_report(
            "Export Output Ownership Audit",
            build_output_ownership_audit_report,
            "leaf_output_ownership_audit.txt",
        )

    def export_foundation_attachment_audit_txt(self):
        self._export_owned_text_report(
            "Export Foundation Attachment Audit",
            build_foundation_attachment_audit_report,
            "leaf_foundation_attachment_audit.txt",
        )

    def export_result_key_audit_txt(self):
        self._export_owned_text_report(
            "Export Foundation Result Key Audit",
            build_result_key_audit_report,
            "leaf_foundation_result_key_audit.txt",
        )

    def export_benchmark_report_txt(self):
        self._export_owned_text_report(
            "Export Benchmark Comparison Report",
            build_benchmark_report,
            "leaf_benchmark_comparison_report.txt",
        )

    def export_engine_reproduction_report_txt(self):
        self._export_owned_text_report(
            "Export Engine Reproduction Report",
            build_engine_reproduction_report,
            "leaf_engine_reproduction_report.txt",
        )