from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from leaf_qt.workspace_runtime_core import build_sorting_health_dashboard_model

SCHEMA = "LEAF_QT_SORTING_HEALTH_DASHBOARD_PHASE_21E_V1"



class SortingHealthDashboard(QFrame):
    """Read-only Qt dashboard for sorting health.

    This widget consumes the Phase 20E sorting dashboard model. It does not
    classify, plan, approve, execute, move, delete, archive, or import files.
    """

    refresh_requested = Signal()

    def __init__(self, project_root: str | Path | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project_root = Path(project_root) if project_root is not None else Path.cwd()
        self.model: dict[str, Any] = {}

        self.setObjectName("SortingHealthDashboard")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self.title_label = QLabel("Sorting Health Dashboard")
        self.title_label.setObjectName("SortingHealthDashboardTitle")

        self.status_label = QLabel("")
        self.status_label.setObjectName("SortingHealthDashboardStatus")
        self.status_label.setWordWrap(True)

        self.metrics_table = QTableWidget()
        self.metrics_table.setObjectName("SortingHealthDashboardMetricsTable")
        self.metrics_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.metrics_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.details = QTextEdit()
        self.details.setObjectName("SortingHealthDashboardDetails")
        self.details.setReadOnly(True)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("SortingHealthDashboardRefreshButton")
        self.refresh_button.clicked.connect(self.refresh)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.metrics_table)
        layout.addWidget(self.details)
        layout.addWidget(self.refresh_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.refresh()

    def refresh(self) -> None:
        self.model = build_sorting_health_dashboard_model(self.project_root)
        self._populate()
        self.refresh_requested.emit()

    def _populate(self) -> None:
        summary = self.model.get("summary", {})
        status = self.model.get("status", {})
        health = self.model.get("health", {})
        metrics = self.model.get("metrics", {})

        self.status_label.setText(
            "Sorting dashboard is read-only. "
            f"Automatic import active: {status.get('automatic_import_active', health.get('automatic_import_active', False))}. "
            f"Execution allowed: {status.get('execution_allowed', health.get('execution_allowed', False))}."
        )

        rows: list[tuple[str, Any]] = []

        for section_name, section in (
            ("summary", summary),
            ("status", status),
            ("health", health),
            ("metrics", metrics),
        ):
            if isinstance(section, dict):
                for key, value in section.items():
                    rows.append((f"{section_name}.{key}", value))

        if not rows:
            for key, value in self.model.items():
                if not isinstance(value, (dict, list)):
                    rows.append((key, value))

        self.metrics_table.clear()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.metrics_table.setRowCount(len(rows))

        for row, (metric, value) in enumerate(rows):
            self.metrics_table.setItem(row, 0, QTableWidgetItem(str(metric)))
            self.metrics_table.setItem(row, 1, QTableWidgetItem(str(value)))

        self.metrics_table.resizeColumnsToContents()

        self.details.setPlainText(
            "\n".join([
                "Safety Meaning",
                "--------------",
                "This dashboard displays the sorting system state only.",
                "It does not perform classification, approval, import execution, movement, deletion, or archival.",
                "The sorting intelligence remains owned by the completed Phase 19 and Phase 20 models.",
                "",
                "Qt Binding Rule",
                "---------------",
                "Qt consumes the model. Qt does not own sorting logic.",
            ])
        )


def build_sorting_health_dashboard_snapshot(project_root: str | Path = ".") -> dict[str, Any]:
    model = build_sorting_health_dashboard_model(project_root)

    summary = model.get("summary", {})
    status = model.get("status", {})
    health = model.get("health", {})
    metrics = model.get("metrics", {})

    combined = {}
    for section in (summary, status, health, metrics):
        if isinstance(section, dict):
            combined.update(section)

    return {
        "schema": SCHEMA,
        "phase": "21E",
        "feature": "QT_SORTING_HEALTH_DASHBOARD",
        "source_sorting_dashboard_model_schema": model.get("schema"),
        "summary": {
            "dashboard_class": "SortingHealthDashboard",
            "presentation_only": True,
            "consumes_phase_20e_dashboard_model": True,
            "qt_owns_sorting_logic": False,
            "read_only_dashboard": True,
            "automatic_import_active": bool(combined.get("automatic_import_active", False)),
            "execution_allowed": bool(combined.get("execution_allowed", False)),
            "imports_files": False,
            "copies_files": False,
            "moves_files": False,
            "deletes_files": False,
            "archives_files": False,
            "model_sections_available": sum(
                1 for section in (summary, status, health, metrics) if isinstance(section, dict) and section
            ),
            "model_keys_available": len(model),
        },
    }
