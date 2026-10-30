
try:
    from regen_station_live_feed_validator_phase_16n5 import (
        RegenStationLiveFeedValidatorPhase16N5,
    )
except Exception:
    RegenStationLiveFeedValidatorPhase16N5 = None

import csv

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QApplication,
    QMessageBox,
    QTabWidget,
)

from station_report_builder import (
    build_station_view_rows,
    get_station_column_label,
    build_station_table_csv_text,
)


STATION_VIEWS = [
    "Thermal",
    "Validation",
    "Diagnostics",
    "Full",
]


class StationTableWindow(QDialog):
    def refresh_station_live_feed_validation_phase_16n5(self):
        """
        Phase 16N.5B
        Record whether station-viewer live-feed payloads are present.
        """
        if not isinstance(getattr(self, "results", None), dict):
            return

        if RegenStationLiveFeedValidatorPhase16N5 is None:
            self.results["phase_16n5_station_live_feed_status"] = (
                "WARN_STATION_LIVE_FEED_VALIDATOR_IMPORT_FAILED_PHASE_16N5"
            )
            return

        validator = RegenStationLiveFeedValidatorPhase16N5()
        result = validator.validate(self.results)

        self.results["phase_16n5_station_live_feed_status"] = result.status
        self.results["phase_16n5_station_payload_present"] = result.station_payload_present
        self.results["phase_16n5_station_count"] = result.station_count
        self.results["phase_16n5_station_automatic_geometry_present"] = (
            result.automatic_geometry_present
        )
        self.results["phase_16n5_station_recommendation_present"] = (
            result.recommendation_present
        )
        self.results["phase_16n5_station_live_feed_notes"] = list(result.notes)


    def __init__(self, parent=None, results=None):
        super().__init__(parent)

        self.results = results
        self.refresh_station_live_feed_validation_phase_16n5() or {}
        self.tables = {}

        self.setWindowTitle("LEAF Station Table")
        self.resize(1100, 750)

        self.create_layout()
        self.populate_all_tables()

    def create_layout(self):
        layout = QVBoxLayout(self)

        title = QLabel("LEAF Station Table Viewer")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 6px;
            }
        """)
        layout.addWidget(title)

        button_bar = QHBoxLayout()

        self.copy_button = QPushButton("Copy Current Table")
        self.copy_button.clicked.connect(self.copy_current_table)

        self.export_button = QPushButton("Export Current CSV")
        self.export_button.clicked.connect(self.export_current_csv)

        self.export_full_button = QPushButton("Export Full CSV")
        self.export_full_button.clicked.connect(self.export_full_csv)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        button_bar.addWidget(self.copy_button)
        button_bar.addWidget(self.export_button)
        button_bar.addWidget(self.export_full_button)
        button_bar.addWidget(self.close_button)

        layout.addLayout(button_bar)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        for view_name in STATION_VIEWS:
            table = QTableWidget()
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.ExtendedSelection)
            table.verticalHeader().setVisible(False)
            table.verticalHeader().setDefaultSectionSize(30)
            table.setSortingEnabled(True)

            self.tables[view_name] = table
            self.tabs.addTab(table, view_name)

    def populate_all_tables(self):
        for view_name, table in self.tables.items():
            self.populate_table(view_name, table)

    def populate_table(self, view_name, table):
        rows, columns = build_station_view_rows(self.results, view_name)

        table.setSortingEnabled(False)
        table.clear()

        if not rows or not columns:
            table.setColumnCount(1)
            table.setRowCount(1)
            table.setHorizontalHeaderLabels(["Status"])
            table.setItem(
                0,
                0,
                QTableWidgetItem("No station rows or columns available for this view."),
            )
            table.setSortingEnabled(True)
            return

        table.setColumnCount(len(columns))
        table.setRowCount(len(rows))

        table.setHorizontalHeaderLabels([
            get_station_column_label(key)
            for key in columns
        ])

        for row_index, row_data in enumerate(rows):
            if not isinstance(row_data, dict):
                continue

            for column_index, key in enumerate(columns):
                value = row_data.get(key)
                item = QTableWidgetItem(self.format_value(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                table.setItem(row_index, column_index, item)

        table.resizeColumnsToContents()
        table.setSortingEnabled(True)

    def current_view_name(self):
        return self.tabs.tabText(self.tabs.currentIndex())

    def current_table(self):
        return self.tabs.currentWidget()

    def copy_current_table(self):
        table = self.current_table()

        if table is None:
            return

        text = self.build_table_text(table)
        QApplication.clipboard().setText(text)

    def export_current_csv(self):
        view_name = self.current_view_name()
        rows, columns = build_station_view_rows(self.results, view_name)

        if not rows or not columns:
            QMessageBox.warning(
                self,
                "No Station Data",
                "No station data is available for this view.",
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export {view_name} Station Table",
            f"leaf_station_table_{view_name.lower()}.csv",
            "CSV File (*.csv)",
        )

        if not path:
            return

        if not path.endswith(".csv"):
            path += ".csv"

        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow([
                get_station_column_label(key)
                for key in columns
            ])

            for row in rows:
                if not isinstance(row, dict):
                    continue

                writer.writerow([
                    self.format_value(row.get(key))
                    for key in columns
                ])

        QMessageBox.information(
            self,
            "Export Complete",
            f"{view_name} station table exported.",
        )

    def export_full_csv(self):
        csv_text = build_station_table_csv_text(self.results)

        if not csv_text:
            QMessageBox.warning(
                self,
                "No Station Data",
                "No full station table data is available.",
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Full Station Table",
            "leaf_station_table_full.csv",
            "CSV File (*.csv)",
        )

        if not path:
            return

        if not path.endswith(".csv"):
            path += ".csv"

        with open(path, "w", encoding="utf-8") as file:
            file.write(csv_text)

        QMessageBox.information(
            self,
            "Export Complete",
            "Full station table exported.",
        )

    def build_table_text(self, table):
        if table is None:
            return ""

        lines = []

        headers = []

        for column in range(table.columnCount()):
            item = table.horizontalHeaderItem(column)
            headers.append(item.text() if item else "")

        lines.append("\t".join(headers))

        for row in range(table.rowCount()):
            values = []

            for column in range(table.columnCount()):
                item = table.item(row, column)
                values.append(item.text() if item else "")

            lines.append("\t".join(values))

        return "\n".join(lines)

    def format_value(self, value):
        if value in (None, "", "N/A", "None"):
            return "N/A"

        if isinstance(value, float):
            return f"{value:.6g}"

        return str(value)