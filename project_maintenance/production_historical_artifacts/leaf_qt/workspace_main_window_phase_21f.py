from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QMainWindow,
    QSplitter,
    QWidget,
)

from project_maintenance.production_historical_artifacts.leaf_qt.workspace_panel_shell_phase_21b import WorkspacePanelShell
from project_maintenance.production_historical_artifacts.leaf_qt.workspace_toolbar_phase_21c import WorkspaceToolbar
from project_maintenance.production_historical_artifacts.leaf_qt.import_review_window_phase_21d import ImportReviewWindow
from project_maintenance.production_historical_artifacts.leaf_qt.sorting_health_dashboard_phase_21e import SortingHealthDashboard
from leaf_qt.workspace_layout_persistence import WorkspaceLayoutPersistence

SCHEMA = "LEAF_QT_WORKSPACE_MAIN_WINDOW_PHASE_21F_V1"


def _load_sidebar_shell_class() -> type[QWidget]:
    candidate_modules = [
        "project_maintenance.production_historical_artifacts.leaf_qt.workspace_sidebar_shell_phase_21a",
        "leaf_qt.qt_workspace_sidebar_shell_phase_21a",
    ]

    candidate_classes = [
        "WorkspaceSidebarShell",
        "QtWorkspaceSidebarShell",
        "WorkspaceSidebar",
    ]

    for module_name in candidate_modules:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue

        for class_name in candidate_classes:
            cls = getattr(module, class_name, None)
            if isinstance(cls, type):
                return cls

    raise AttributeError("No recognised Phase 21A workspace sidebar shell class was found.")


class WorkspaceMainWindow(QMainWindow):
    """Integrated LEAF workspace window.

    This class wires the completed Phase 21A-21E Qt shells together.
    It does not own repository intelligence, workspace intelligence, sorting
    intelligence, action logic, import execution, or filesystem mutation.
    """

    def __init__(self, project_root: str | Path | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project_root = Path(project_root) if project_root is not None else Path.cwd()

        self.setObjectName("WorkspaceMainWindow")
        self.setWindowTitle("LEAF Workspace")
        self.resize(1450, 850)
        self.layout_persistence = WorkspaceLayoutPersistence(self.project_root)

        sidebar_cls = _load_sidebar_shell_class()

        self.sidebar_shell = sidebar_cls(self.project_root, self)
        self.panel_shell = WorkspacePanelShell(self.project_root, self)
        self.toolbar_shell = WorkspaceToolbar(self.project_root, self)

        self.import_review_window = ImportReviewWindow(self.project_root, self)
        self.sorting_health_dashboard = SortingHealthDashboard(self.project_root, self)

        self.addToolBar(self.toolbar_shell)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setObjectName("WorkspaceMainWindowSplitter")
        self.splitter.addWidget(self.sidebar_shell)
        self.splitter.addWidget(self.panel_shell)
        self.splitter.setSizes([310, 1140])

        central = QWidget()
        self.setCentralWidget(self.splitter)

        self.sorting_health_dock = QDockWidget("Sorting Health", self)
        self.sorting_health_dock.setObjectName("WorkspaceSortingHealthDock")
        self.sorting_health_dock.setWidget(self.sorting_health_dashboard)
        self.sorting_health_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.sorting_health_dock)
        self.sorting_health_dock.hide()

        self._connect_signals()
        self.restore_workspace_layout()

    def _connect_signals(self) -> None:
        for signal_name in ("section_selected", "panel_selected", "item_selected"):
            signal = getattr(self.sidebar_shell, signal_name, None)
            if signal is not None and hasattr(signal, "connect"):
                signal.connect(self._show_workspace_panel)
                break

        if hasattr(self.toolbar_shell, "action_requested"):
            self.toolbar_shell.action_requested.connect(self._handle_toolbar_action)

        if hasattr(self.panel_shell, "panel_selected"):
            self.panel_shell.panel_selected.connect(self._sync_toolbar_scope)

    def _show_workspace_panel(self, section_or_panel_id: str) -> None:
        shown = self.panel_shell.show_panel(section_or_panel_id)
        if shown:
            self._sync_toolbar_scope(section_or_panel_id)

    def _sync_toolbar_scope(self, section_or_panel_id: str) -> None:
        if hasattr(self.toolbar_shell, "set_panel_scope"):
            self.toolbar_shell.set_panel_scope(section_or_panel_id)

    def _handle_toolbar_action(self, action_id: str) -> None:
        if action_id == "review_import_candidate":
            self.import_review_window.refresh()
            self.import_review_window.show()
            self.import_review_window.raise_()
            self.import_review_window.activateWindow()
            return

        if action_id == "refresh_workspace":
            self.refresh_workspace()
            return

        if action_id in {"approve_import_candidate", "execute_approved_import"}:
            return

    def refresh_workspace(self) -> None:
        for widget in (
            self.sidebar_shell,
            self.panel_shell,
            self.toolbar_shell,
            self.sorting_health_dashboard,
        ):
            refresh = getattr(widget, "refresh", None)
            if callable(refresh):
                refresh()

    def save_workspace_layout(self) -> None:
        self.layout_persistence.save_layout(
            geometry_bytes=bytes(self.saveGeometry()),
            window_state_bytes=bytes(self.saveState()),
            splitter_sizes=self.splitter.sizes(),
            selected_panel=getattr(self.panel_shell, "title_label", None).text()
            if getattr(self.panel_shell, "title_label", None) is not None
            else None,
        )

    def restore_workspace_layout(self) -> bool:
        payload = self.layout_persistence.load_layout()
        if not payload.get("valid"):
            return False

        geometry = payload.get("geometry_bytes")
        window_state = payload.get("window_state_bytes")
        splitter_sizes = payload.get("splitter_sizes")

        if geometry:
            self.restoreGeometry(geometry)
        if window_state:
            self.restoreState(window_state)
        if isinstance(splitter_sizes, list) and splitter_sizes:
            self.splitter.setSizes([int(value) for value in splitter_sizes])

        return True

    def closeEvent(self, event) -> None:
        self.save_workspace_layout()
        super().closeEvent(event)


def build_workspace_main_window_snapshot(project_root: str | Path = ".") -> dict[str, Any]:
    sidebar_class = _load_sidebar_shell_class()

    return {
        "schema": SCHEMA,
        "phase": "21F",
        "feature": "QT_WORKSPACE_MAIN_WINDOW_INTEGRATION",
        "summary": {
            "main_window_class": "WorkspaceMainWindow",
            "sidebar_shell_class": sidebar_class.__name__,
            "panel_shell_class": "WorkspacePanelShell",
            "toolbar_class": "WorkspaceToolbar",
            "import_review_window_class": "ImportReviewWindow",
            "sorting_health_dashboard_class": "SortingHealthDashboard",
            "presentation_only": True,
            "integrates_phase_21a_sidebar": True,
            "integrates_phase_21b_panel_shell": True,
            "integrates_phase_21c_toolbar": True,
            "integrates_phase_21d_import_review_window": True,
            "integrates_phase_21e_sorting_health_dashboard": True,
            "qt_owns_repository_logic": False,
            "qt_owns_sorting_logic": False,
            "qt_owns_action_logic": False,
            "imports_files": False,
            "copies_files": False,
            "moves_files": False,
            "deletes_files": False,
            "archives_files": False,
            "automatic_import_allowed": False,
            "unsafe_toolbar_actions_execute": False,
            "integrates_phase_21g_layout_persistence": True,
            "layout_persistence_presentation_only": True,
        },
    }
