from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from leaf_qt.workspace_runtime_core import build_workspace_panel_data_providers

SCHEMA = "LEAF_QT_WORKSPACE_PANEL_SHELL_PHASE_21B_V1"

SECTION_ID_TO_PANEL_LABEL = {
    "design": "Designs",
    "project": "Projects",
    "report": "Reports",
    "export": "Exports",
    "import_review": "Import Review",
    "sorting_health": "Sorting Health",
}


class WorkspacePanelShell(QFrame):
    """Presentation-only Qt shell for LEAF workspace panels.

    This widget consumes Phase 20B panel providers. It does not crawl folders,
    execute imports, move files, delete files, archive files, or own repository
    intelligence.
    """

    panel_selected = Signal(str)

    def __init__(self, project_root: str | Path | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project_root = Path(project_root) if project_root is not None else Path.cwd()
        self.providers: dict[str, Any] = {}
        self.panel_widgets: dict[str, QWidget] = {}

        self.setObjectName("WorkspacePanelShell")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self.title_label = QLabel("Workspace Panel")
        self.title_label.setObjectName("WorkspacePanelTitle")

        self.description_label = QLabel("")
        self.description_label.setObjectName("WorkspacePanelDescription")
        self.description_label.setWordWrap(True)

        self.stack = QStackedWidget()
        self.stack.setObjectName("WorkspacePanelStack")

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.description_label)
        layout.addWidget(self.stack)

        self.refresh()

    def refresh(self) -> None:
        self.providers = build_workspace_panel_data_providers(self.project_root)
        self.stack.clear()
        self.panel_widgets.clear()

        for panel_label, panel in self.providers.get("panels", {}).items():
            widget = self._build_panel_widget(panel_label, panel)
            self.panel_widgets[panel_label] = widget
            self.stack.addWidget(widget)

        first_panel = next(iter(self.panel_widgets), "")
        if first_panel:
            self.show_panel(first_panel)

    def show_panel(self, panel_label_or_section_id: str) -> bool:
        panel_label = SECTION_ID_TO_PANEL_LABEL.get(panel_label_or_section_id, panel_label_or_section_id)

        widget = self.panel_widgets.get(panel_label)
        panel = self.providers.get("panels", {}).get(panel_label)

        if widget is None or panel is None:
            return False

        self.stack.setCurrentWidget(widget)
        self.title_label.setText(str(panel.get("title", panel_label)))
        self.description_label.setText(str(panel.get("description", "")))
        self.panel_selected.emit(panel_label)
        return True

    def available_panels(self) -> list[str]:
        return list(self.panel_widgets)

    def _build_panel_widget(self, panel_label: str, panel: dict[str, Any]) -> QWidget:
        panel_type = panel.get("panel_type")

        if panel_type == "workspace_resource_panel":
            return self._build_resource_panel(panel)
        if panel_type == "import_review_panel":
            return self._build_import_review_panel(panel)
        if panel_type == "sorting_health_panel":
            return self._build_sorting_health_panel(panel)

        return self._build_unknown_panel(panel_label, panel)

    def _build_resource_panel(self, panel: dict[str, Any]) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        summary = QLabel(
            f"{panel.get('resource_type', 'resource').title()} items: {panel.get('item_count', 0)}"
        )
        summary.setObjectName("WorkspaceResourcePanelSummary")
        layout.addWidget(summary)

        items = panel.get("items", [])
        if not items:
            empty = QLabel(str(panel.get("empty_state_message", "No items available.")))
            empty.setObjectName("WorkspaceResourcePanelEmptyState")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(empty)
            return widget

        table = QTableWidget()
        table.setObjectName("WorkspaceResourcePanelTable")
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Name", "Type", "Location"])
        table.setRowCount(len(items))

        for row, item in enumerate(items):
            table.setItem(row, 0, QTableWidgetItem(str(item.get("name", ""))))
            table.setItem(row, 1, QTableWidgetItem(str(item.get("kind", item.get("type", "")))))
            table.setItem(row, 2, QTableWidgetItem(str(item.get("relative_path", item.get("path", "")))))

        table.resizeColumnsToContents()
        layout.addWidget(table)
        return widget

    def _build_import_review_panel(self, panel: dict[str, Any]) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        metrics = [
            ("Pending Review", panel.get("pending_review", 0)),
            ("Duplicate Groups", panel.get("duplicate_groups", 0)),
            ("Destination Conflicts", panel.get("destination_conflict_groups", 0)),
            ("High Priority", panel.get("high_review", 0)),
            ("Normal Priority", panel.get("normal_review", 0)),
            ("Low Confidence", panel.get("low_confidence_review", 0)),
            ("Execution Allowed", panel.get("execution_allowed", False)),
        ]

        table = QTableWidget()
        table.setObjectName("WorkspaceImportReviewPanelTable")
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Metric", "Value"])
        table.setRowCount(len(metrics))

        for row, (name, value) in enumerate(metrics):
            table.setItem(row, 0, QTableWidgetItem(str(name)))
            table.setItem(row, 1, QTableWidgetItem(str(value)))

        table.resizeColumnsToContents()
        layout.addWidget(table)

        note = QLabel("Import execution remains locked. This panel is review-only.")
        note.setObjectName("WorkspaceImportReviewSafetyNote")
        layout.addWidget(note)

        return widget

    def _build_sorting_health_panel(self, panel: dict[str, Any]) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        metrics = [
            ("Programme Completed", panel.get("programme_completed")),
            ("Ready For GUI Activation", panel.get("ready_for_gui_activation")),
            ("Automatic Import Active", panel.get("automatic_import_active")),
            ("GUI Activation Active", panel.get("gui_activation_active")),
            ("Import Candidates", panel.get("import_candidates")),
            ("Review Records", panel.get("review_records")),
            ("Plans Ready", panel.get("plans_ready")),
            ("Plans Blocked", panel.get("plans_blocked")),
            ("Approved Records", panel.get("approved_records")),
            ("Executed Records", panel.get("executed_records")),
            ("Safe No-Op State", panel.get("safe_no_op_state")),
        ]

        table = QTableWidget()
        table.setObjectName("WorkspaceSortingHealthPanelTable")
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Metric", "Value"])
        table.setRowCount(len(metrics))

        for row, (name, value) in enumerate(metrics):
            table.setItem(row, 0, QTableWidgetItem(str(name)))
            table.setItem(row, 1, QTableWidgetItem(str(value)))

        table.resizeColumnsToContents()
        layout.addWidget(table)

        return widget

    def _build_unknown_panel(self, panel_label: str, panel: dict[str, Any]) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        text = QTextEdit()
        text.setObjectName("WorkspaceUnknownPanelPayload")
        text.setReadOnly(True)
        text.setPlainText(f"Panel '{panel_label}' has no Qt renderer yet.\n\n{panel}")
        layout.addWidget(text)
        return widget


def build_workspace_panel_shell_snapshot(project_root: str | Path = ".") -> dict[str, Any]:
    providers = build_workspace_panel_data_providers(project_root)
    panels = providers.get("panels", {})

    return {
        "schema": SCHEMA,
        "phase": "21B",
        "feature": "QT_WORKSPACE_PANEL_SHELL",
        "source_panel_provider_schema": providers.get("schema"),
        "summary": {
            "panel_shell_class": "WorkspacePanelShell",
            "panel_providers": len(panels),
            "resource_panels": sum(1 for p in panels.values() if p.get("panel_type") == "workspace_resource_panel"),
            "import_review_panels": sum(1 for p in panels.values() if p.get("panel_type") == "import_review_panel"),
            "sorting_health_panels": sum(1 for p in panels.values() if p.get("panel_type") == "sorting_health_panel"),
            "developer_internal_panels_exposed": sum(1 for p in panels.values() if p.get("developer_internal")),
            "panels_requiring_internal_path_knowledge": 0,
            "presentation_only": True,
            "consumes_phase_20b_providers": True,
            "imports_files": False,
            "moves_files": False,
            "deletes_files": False,
            "archives_files": False,
            "automatic_import_allowed": False,
            "sidebar_section_mapping_complete": set(SECTION_ID_TO_PANEL_LABEL.values()) == set(panels),
        },
        "available_panels": list(panels),
    }
