from leaf_qt.status_presentation import LegacyCompatibilityProducer
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QApplication,
)

from foundation_regression_tests import run_foundation_regression_tests


class FoundationTestRunnerWindow(QDialog):
    def __init__(self, parent=None, results=None):
        super().__init__(parent)

        self.results = results or {}
        self.regression = {}

        self.setWindowTitle("LEAF Foundation Test Runner")
        self.resize(1000, 700)

        self.create_layout()
        self.run_tests()

    def create_layout(self):
        layout = QVBoxLayout(self)

        self.status_label = QLabel("Foundation regression status: NOT RUN")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #444;
            }
        """)
        layout.addWidget(self.status_label)

        button_bar = QHBoxLayout()

        self.run_button = QPushButton("Run Tests")
        self.run_button.clicked.connect(self.run_tests)

        self.copy_button = QPushButton("Copy Report")
        self.copy_button.clicked.connect(self.copy_report)

        self.export_button = QPushButton("Export TXT")
        self.export_button.clicked.connect(self.export_report)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        button_bar.addWidget(self.run_button)
        button_bar.addWidget(self.copy_button)
        button_bar.addWidget(self.export_button)
        button_bar.addWidget(self.close_button)

        layout.addLayout(button_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "Status",
            "Test",
            "Detail",
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(32)

        layout.addWidget(self.table)

    def run_tests(self):
        self.regression = run_foundation_regression_tests(self.results)

        status = self.regression.get("foundation_regression_status", "UNKNOWN")
        passed = self.regression.get("foundation_regression_passed_count", 0)
        failed = self.regression.get("foundation_regression_failed_count", 0)

        self.status_label.setText(
            f"Foundation regression status: {status} | Passed: {passed} | Failed: {failed}"
        )

        tests = self.regression.get("foundation_regression_tests", [])
        self.populate_table(tests)

    def populate_table(self, tests):
        self.table.setRowCount(len(tests))

        for row_index, test in enumerate(tests):
            passed = bool(test.get("passed"))
            status_text = LegacyCompatibilityProducer.marker_from_bool(passed)

            items = [
                QTableWidgetItem(status_text),
                QTableWidgetItem(str(test.get("name", ""))),
                QTableWidgetItem(str(test.get("detail", ""))),
            ]

            for item in items:
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)

            for column_index, item in enumerate(items):
                self.table.setItem(row_index, column_index, item)

        self.table.resizeColumnsToContents()

    def copy_report(self):
        text = self.regression.get("foundation_regression_text", "")

        if not text:
            QMessageBox.warning(self, "No Report", "No regression report is available.")
            return

        QApplication.clipboard().setText(text)

    def export_report(self):
        text = self.regression.get("foundation_regression_text", "")

        if not text:
            QMessageBox.warning(self, "No Report", "No regression report is available.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Foundation Regression Report",
            "leaf_foundation_regression_report.txt",
            "Text File (*.txt)",
        )

        if not path:
            return

        if not path.endswith(".txt"):
            path += ".txt"

        with open(path, "w", encoding="utf-8") as file:
            file.write(text)

        QMessageBox.information(
            self,
            "Export Complete",
            "Foundation regression report exported successfully.",
        )