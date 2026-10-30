from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from leaf_qt.workspace_runtime_core import build_workspace_sidebar_model


class WorkspaceSidebarShell(QFrame):
    """Qt shell for LEAF workspace navigation.

    This widget is presentation-only. It consumes the reusable workspace sidebar
    model and does not own sorting, import, registry, or filesystem logic.
    """

    section_selected = Signal(str)

    def __init__(self, project_root: str | Path | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project_root = Path(project_root) if project_root is not None else Path.cwd()
        self.sidebar_model: dict[str, Any] = {}

        self.setObjectName("WorkspaceSidebarShell")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self.title_label = QLabel("LEAF Workspace")
        self.title_label.setObjectName("WorkspaceSidebarTitle")

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("WorkspaceSidebarList")
        self.list_widget.currentItemChanged.connect(self._on_current_item_changed)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.list_widget)

        self.refresh()

    def refresh(self) -> None:
        self.sidebar_model = build_workspace_sidebar_model(self.project_root)
        self.list_widget.clear()

        for item in self.sidebar_model.get("sidebar_items", []):
            list_item = QListWidgetItem(f"{item['label']} ({item['item_count']})")
            list_item.setData(256, item["id"])
            list_item.setToolTip(item.get("description", ""))
            list_item.setHidden(not bool(item.get("visible", True)))
            list_item.setFlags(list_item.flags() if item.get("enabled", True) else list_item.flags() & ~list_item.flags().ItemIsEnabled)
            self.list_widget.addItem(list_item)

        if self.list_widget.count() and self.list_widget.currentRow() < 0:
            self.list_widget.setCurrentRow(0)

    def selected_section_id(self) -> str:
        item = self.list_widget.currentItem()
        return str(item.data(256)) if item else ""

    def _on_current_item_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        if current is None:
            return
        section_id = str(current.data(256))
        self.section_selected.emit(section_id)


def build_workspace_sidebar_shell_snapshot(project_root: str | Path = ".") -> dict[str, Any]:
    model = build_workspace_sidebar_model(project_root)
    items = model.get("sidebar_items", [])

    return {
        "schema": "LEAF_QT_WORKSPACE_SIDEBAR_SHELL_PHASE_21A_V1",
        "phase": "21A",
        "feature": "QT_WORKSPACE_SIDEBAR_SHELL",
        "source_sidebar_schema": model.get("schema"),
        "summary": {
            "sidebar_items": len(items),
            "visible_items": sum(1 for item in items if item.get("visible")),
            "enabled_items": sum(1 for item in items if item.get("enabled")),
            "developer_internal_items_exposed": sum(1 for item in items if item.get("developer_internal")),
            "items_requiring_internal_path_knowledge": sum(1 for item in items if item.get("requires_internal_path_knowledge")),
            "qt_widget_class": "WorkspaceSidebarShell",
            "presentation_only": True,
        },
    }
