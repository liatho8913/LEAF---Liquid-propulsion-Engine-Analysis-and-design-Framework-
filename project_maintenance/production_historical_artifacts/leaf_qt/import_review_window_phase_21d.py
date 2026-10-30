from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from leaf_qt.workspace_runtime_core import build_import_review_ui_model

SCHEMA = "LEAF_QT_IMPORT_REVIEW_WINDOW_PHASE_21D_V1"


class ImportReviewWindow(QDialog):
    """Presentation-only Qt window for import review.

    This window consumes the Phase 20D Import Review UI Model. It does not
    approve records, execute imports, copy files, move files, delete files,
    archive files, or perform repository sorting.
    """

    review_selected = Signal(str)
    refresh_requested = Signal()

    def __init__(self, project_root: str | Path | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project_root = Path(project_root) if project_root is not None else Path.cwd()
        self.model: dict[str, Any] = {}
        self.row_review_ids: list[str] = []

        self.setObjectName("ImportReviewWindow")
        self.setWindowTitle("LEAF Import Review")
        self.resize(1250, 720)

        self.title_label = QLabel("Import Review")
        self.title_label.setObjectName("ImportReviewWindowTitle")

        self.status_label = QLabel("")
        self.status_label.setObjectName("ImportReviewWindowStatus")
        self.status_label.setWordWrap(True)

        self.table = QTableWidget()
        self.table.setObjectName("ImportReviewWindowTable")
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.details = QTextEdit()
        self.details.setObjectName("ImportReviewWindowDetails")
        self.details.setReadOnly(True)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("ImportReviewWindowRefreshButton")
        self.refresh_button.clicked.connect(self.refresh)

        self.approve_button = QPushButton("Approve Import")
        self.approve_button.setObjectName("ImportReviewWindowApproveButton")
        self.approve_button.setEnabled(False)

        self.execute_button = QPushButton("Execute Approved Import")
        self.execute_button.setObjectName("ImportReviewWindowExecuteButton")
        self.execute_button.setEnabled(False)

        button_row = QHBoxLayout()
        button_row.addWidget(self.refresh_button)
        button_row.addStretch(1)
        button_row.addWidget(self.approve_button)
        button_row.addWidget(self.execute_button)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.table)
        splitter.addWidget(self.details)
        splitter.setSizes([820, 430])

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.status_label)
        layout.addWidget(splitter)
        layout.addLayout(button_row)

        self.table.itemSelectionChanged.connect(self._selection_changed)

        self.refresh()

    def refresh(self) -> None:
        self.model = build_import_review_ui_model(self.project_root)
        self._populate()
        self.refresh_requested.emit()

    def _populate(self) -> None:
        columns = self.model.get("table_columns", [])
        rows = self.model.get("rows", [])
        summary = self.model.get("summary", {})
        execution_policy = self.model.get("execution_policy", {})

        self.status_label.setText(
            "Review rows: "
            f"{summary.get('review_rows', 0)} | "
            "Approval writeback: "
            f"{summary.get('approval_writeback_enabled', False)} | "
            "Execution buttons: "
            f"{summary.get('execution_buttons_enabled', False)} | "
            "Automatic import: "
            f"{self.model.get('activation_status', {}).get('automatic_import_active', False)}"
        )

        self.row_review_ids = []
        self.table.clear()
        self.table.setColumnCount(len(columns))
        self.table.setRowCount(len(rows))
        self.table.setHorizontalHeaderLabels([str(column.get("label", column.get("id", ""))) for column in columns])

        for col, column in enumerate(columns):
            width = int(column.get("width", 120))
            self.table.setColumnWidth(col, width)

        for row_index, row in enumerate(rows):
            review_id = str(row.get("review_id", ""))
            self.row_review_ids.append(review_id)

            for col_index, column in enumerate(columns):
                key = column.get("id")
                value = row.get(key, "")
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setData(Qt.ItemDataRole.UserRole, review_id)
                self.table.setItem(row_index, col_index, item)

        approval_enabled = bool(execution_policy.get("approval_writeback_enabled", False))
        execution_enabled = bool(execution_policy.get("execution_buttons_enabled", False))

        self.approve_button.setEnabled(approval_enabled)
        self.execute_button.setEnabled(execution_enabled)

        if rows:
            self.table.selectRow(0)
        else:
            self.details.setPlainText("No import review records are currently available.")

    def _selection_changed(self) -> None:
        selected = self.table.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        if row < 0 or row >= len(self.row_review_ids):
            return

        review_id = self.row_review_ids[row]
        self.show_review_details(review_id)

    def show_review_details(self, review_id: str) -> bool:
        details = self.model.get("details", {}).get(review_id)

        if details is None:
            return False

        lines = [
            f"Review ID: {review_id}",
            "",
            "Safety Meaning",
            "--------------",
            "This window displays import review state only.",
            "Approval writeback is disabled unless the Phase 20D model explicitly enables it.",
            "Execution remains disabled unless the Phase 20D model explicitly enables it.",
            "",
            "Record Details",
            "--------------",
        ]

        for key, value in details.items():
            lines.append(f"{key}: {value}")

        self.details.setPlainText("\n".join(lines))
        self.review_selected.emit(review_id)
        return True


def build_import_review_window_snapshot(project_root: str | Path = ".") -> dict[str, Any]:
    model = build_import_review_ui_model(project_root)
    summary = model.get("summary", {})
    activation = model.get("activation_status", {})
    policy = model.get("execution_policy", {})

    return {
        "schema": SCHEMA,
        "phase": "21D",
        "feature": "QT_IMPORT_REVIEW_WINDOW",
        "source_import_review_ui_model_schema": model.get("schema"),
        "summary": {
            "window_class": "ImportReviewWindow",
            "table_columns_bound": summary.get("table_columns", 0),
            "review_rows_bound": summary.get("review_rows", 0),
            "detail_records_bound": summary.get("detail_records", 0),
            "review_actions_visible": summary.get("review_actions", 0),
            "presentation_only": True,
            "consumes_phase_20d_import_review_ui_model": True,
            "qt_owns_review_logic": False,
            "table_editable": False,
            "approval_writeback_enabled": policy.get("approval_writeback_enabled", False),
            "execution_buttons_enabled": policy.get("execution_buttons_enabled", False),
            "automatic_import_active": activation.get("automatic_import_active", False),
            "imports_files": policy.get("imports_files", False),
            "copies_files": policy.get("copies_files", False),
            "moves_files": policy.get("moves_files", False),
            "deletes_files": policy.get("deletes_files", False),
            "archives_files": policy.get("archives_files", False),
            "developer_internal_fields_exposed": summary.get("developer_internal_fields_exposed", 0),
            "ready_for_qt_binding": summary.get("ready_for_qt_binding", False),
        },
    }
