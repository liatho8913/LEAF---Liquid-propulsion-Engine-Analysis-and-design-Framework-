from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar, QWidget

from leaf_qt.workspace_runtime_core import build_workspace_action_model

SCHEMA = "LEAF_QT_WORKSPACE_TOOLBAR_PHASE_21C_V1"


class WorkspaceToolbar(QToolBar):
    """Presentation-only Qt toolbar for LEAF workspace actions.

    This toolbar consumes the Phase 20C action model. It does not execute
    imports, move files, delete files, archive files, crawl folders, or own
    action intelligence.
    """

    action_requested = Signal(str)
    refresh_requested = Signal()

    def __init__(self, project_root: str | Path | None = None, parent: QWidget | None = None) -> None:
        super().__init__("Workspace", parent)
        self.project_root = Path(project_root) if project_root is not None else Path.cwd()
        self.action_model: dict[str, Any] = {}
        self.qt_actions: dict[str, QAction] = {}

        self.setObjectName("WorkspaceToolbar")
        self.setMovable(False)

        self.refresh()

    def refresh(self) -> None:
        self.clear()
        self.qt_actions.clear()

        self.action_model = build_workspace_action_model(self.project_root)

        actions = self.action_model.get("actions", {})

        for action_id, action_payload in actions.items():
            qt_action = QAction(str(action_payload.get("label", action_id)), self)
            qt_action.setObjectName(f"WorkspaceToolbarAction_{action_id}")
            qt_action.setEnabled(bool(action_payload.get("enabled", False)))
            qt_action.setToolTip(self._build_tooltip(action_id, action_payload))
            qt_action.triggered.connect(
                lambda checked=False, captured_action_id=action_id: self._emit_action(captured_action_id)
            )

            self.qt_actions[action_id] = qt_action
            self.addAction(qt_action)

        refresh_action = self.qt_actions.get("refresh_workspace")
        if refresh_action is not None:
            refresh_action.triggered.connect(self.refresh_requested.emit)

    def available_action_ids(self) -> list[str]:
        return list(self.qt_actions)

    def enabled_action_ids(self) -> list[str]:
        return [
            action_id
            for action_id, action in self.qt_actions.items()
            if action.isEnabled()
        ]

    def disabled_action_ids(self) -> list[str]:
        return [
            action_id
            for action_id, action in self.qt_actions.items()
            if not action.isEnabled()
        ]

    def set_panel_scope(self, panel_name: str) -> None:
        panel_actions = set(self.action_model.get("panel_actions", {}).get(panel_name, []))

        for action_id, qt_action in self.qt_actions.items():
            model_action = self.action_model.get("actions", {}).get(action_id, {})
            model_enabled = bool(model_action.get("enabled", False))
            visible_for_panel = action_id in panel_actions
            qt_action.setVisible(visible_for_panel)
            qt_action.setEnabled(model_enabled and visible_for_panel)

    def _emit_action(self, action_id: str) -> None:
        action_payload = self.action_model.get("actions", {}).get(action_id, {})

        if not action_payload.get("enabled", False):
            return

        self.action_requested.emit(action_id)

    @staticmethod
    def _build_tooltip(action_id: str, action_payload: dict[str, Any]) -> str:
        parts = [
            f"Action: {action_payload.get('label', action_id)}",
            f"Scope: {action_payload.get('scope', 'Unknown')}",
            f"Type: {action_payload.get('action_type', 'Unknown')}",
            f"Execution: {action_payload.get('execution_mode', 'Unknown')}",
        ]

        if action_payload.get("filesystem_write"):
            parts.append("Filesystem write: user-initiated only")
        else:
            parts.append("Filesystem write: no")

        if not action_payload.get("enabled", False):
            reason = action_payload.get("reason_disabled", "Disabled by action model.")
            parts.append(f"Disabled: {reason}")

        return "\n".join(parts)


def build_workspace_toolbar_snapshot(project_root: str | Path = ".") -> dict[str, Any]:
    model = build_workspace_action_model(project_root)
    actions = model.get("actions", {})
    panel_actions = model.get("panel_actions", {})

    unsafe_enabled = [
        action_id
        for action_id, action in actions.items()
        if action.get("enabled") and action.get("action_type") in {
            "CONTROLLED_COPY_IMPORT",
            "DELETE_RESOURCE",
            "MOVE_RESOURCE",
            "ARCHIVE_RESOURCE",
        }
    ]

    return {
        "schema": SCHEMA,
        "phase": "21C",
        "feature": "QT_WORKSPACE_TOOLBAR",
        "source_action_model_schema": model.get("schema"),
        "summary": {
            "toolbar_class": "WorkspaceToolbar",
            "actions_bound": len(actions),
            "enabled_actions": sum(1 for action in actions.values() if action.get("enabled")),
            "disabled_actions": sum(1 for action in actions.values() if not action.get("enabled")),
            "panels_with_actions": len(panel_actions),
            "unsafe_enabled_actions": len(unsafe_enabled),
            "presentation_only": True,
            "consumes_phase_20c_action_model": True,
            "qt_owns_action_logic": False,
            "imports_files": False,
            "moves_files": False,
            "deletes_files": False,
            "archives_files": False,
            "automatic_import_allowed": False,
            "disabled_actions_remain_disabled": all(
                not action.get("enabled")
                for action_id, action in actions.items()
                if action_id in {"approve_import_candidate", "execute_approved_import"}
            ),
        },
        "action_ids": list(actions),
        "panel_actions": panel_actions,
        "unsafe_enabled_actions": unsafe_enabled,
    }
