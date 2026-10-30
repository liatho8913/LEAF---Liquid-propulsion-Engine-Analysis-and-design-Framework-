from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QApplication,
    QFileDialog,
    QMessageBox,
)


class StartupHealthWindow(QDialog):
    def __init__(self, parent=None, health_report=None):
        super().__init__(parent)

        self.health_report = health_report or {}

        self.setWindowTitle("LEAF Startup Health Check")
        self.resize(1000, 650)

        self.create_layout()
        self.populate()

    def create_layout(self):
        layout = QVBoxLayout(self)

        self.status_label = QLabel("Startup health: UNKNOWN")
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

        self.copy_button = QPushButton("Copy Report")
        self.copy_button.clicked.connect(self.copy_report)

        self.export_button = QPushButton("Export TXT")
        self.export_button.clicked.connect(self.export_report)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        button_bar.addWidget(self.copy_button)
        button_bar.addWidget(self.export_button)
        button_bar.addWidget(self.close_button)

        layout.addLayout(button_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Status",
            "System",
            "Module",
            "Required",
            "Error",
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(32)

        layout.addWidget(self.table)

    def populate(self):
        status = self.health_report.get("startup_health_status", "UNKNOWN")
        required_failures = self.health_report.get(
            "startup_health_required_failure_count",
            0,
        )
        optional_warnings = self.health_report.get(
            "startup_health_optional_warning_count",
            0,
        )

        self.status_label.setText(
            f"Startup health: {status} | "
            f"Required failures: {required_failures} | "
            f"Optional warnings: {optional_warnings}"
        )

        rows = self.health_report.get("startup_health_rows", [])

        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            values = [
                row.get("status", ""),
                row.get("name", ""),
                row.get("module", ""),
                "Yes" if row.get("required") else "No",
                row.get("error", ""),
            ]

            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row_index, column_index, item)

        self.table.resizeColumnsToContents()

    def copy_report(self):
        text = self.health_report.get("startup_health_text", "")

        if not text:
            QMessageBox.warning(self, "No Report", "No startup health report available.")
            return

        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Startup health report copied to clipboard.",
        )

    def export_report(self):
        text = self.health_report.get("startup_health_text", "")

        if not text:
            QMessageBox.warning(self, "No Report", "No startup health report available.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Startup Health Report",
            "leaf_startup_health_report.txt",
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
            "Startup health report exported successfully.",
        )