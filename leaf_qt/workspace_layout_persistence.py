from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_WORKSPACE_LAYOUT_PERSISTENCE_PHASE_21G_V1"

DEFAULT_LAYOUT_DIR = "_leaf_artifacts/workspace_architecture/layout_persistence"
DEFAULT_LAYOUT_FILE = "workspace_layout_state_phase_21g.json"


@dataclass(frozen=True)
class WorkspaceLayoutPersistenceResult:
    schema: str
    layout_path: str
    saved: bool
    restored: bool
    valid: bool
    reason: str


class WorkspaceLayoutPersistence:
    """Small persistence owner for Qt workspace layout state.

    This owner stores presentation state only. It does not store engineering
    data, design files, repository intelligence, sorting state, import approval
    state, or execution state.
    """

    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.layout_dir = self.project_root / DEFAULT_LAYOUT_DIR
        self.layout_path = self.layout_dir / DEFAULT_LAYOUT_FILE

    def save_layout(
        self,
        *,
        geometry_bytes: bytes,
        window_state_bytes: bytes,
        splitter_sizes: list[int],
        selected_panel: str | None = None,
    ) -> WorkspaceLayoutPersistenceResult:
        self.layout_dir.mkdir(parents=True, exist_ok=True)

        payload = {
            "schema": SCHEMA,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "presentation_state_only": True,
            "stores_engineering_data": False,
            "stores_repository_intelligence": False,
            "stores_sorting_execution_state": False,
            "stores_import_approval_state": False,
            "geometry_b64": base64.b64encode(geometry_bytes).decode("ascii"),
            "window_state_b64": base64.b64encode(window_state_bytes).decode("ascii"),
            "splitter_sizes": [int(value) for value in splitter_sizes],
            "selected_panel": selected_panel,
        }

        self.layout_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        return WorkspaceLayoutPersistenceResult(
            schema=SCHEMA,
            layout_path=self.layout_path.relative_to(self.project_root).as_posix(),
            saved=True,
            restored=False,
            valid=True,
            reason="layout_saved",
        )

    def load_layout(self) -> dict[str, Any]:
        if not self.layout_path.exists():
            return {
                "schema": SCHEMA,
                "exists": False,
                "valid": False,
                "reason": "layout_file_missing",
            }

        try:
            payload = json.loads(self.layout_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {
                "schema": SCHEMA,
                "exists": True,
                "valid": False,
                "reason": f"layout_file_unreadable:{exc!r}",
            }

        if payload.get("schema") != SCHEMA:
            return {
                "schema": SCHEMA,
                "exists": True,
                "valid": False,
                "reason": "schema_mismatch",
            }

        required_false = [
            "stores_engineering_data",
            "stores_repository_intelligence",
            "stores_sorting_execution_state",
            "stores_import_approval_state",
        ]

        if payload.get("presentation_state_only") is not True:
            return {
                "schema": SCHEMA,
                "exists": True,
                "valid": False,
                "reason": "not_presentation_state_only",
            }

        for key in required_false:
            if payload.get(key) is not False:
                return {
                    "schema": SCHEMA,
                    "exists": True,
                    "valid": False,
                    "reason": f"unsafe_layout_payload:{key}",
                }

        return {
            **payload,
            "exists": True,
            "valid": True,
            "geometry_bytes": base64.b64decode(payload.get("geometry_b64", "")),
            "window_state_bytes": base64.b64decode(payload.get("window_state_b64", "")),
        }

    def clear_layout(self) -> WorkspaceLayoutPersistenceResult:
        if self.layout_path.exists():
            self.layout_path.unlink()

        return WorkspaceLayoutPersistenceResult(
            schema=SCHEMA,
            layout_path=self.layout_path.relative_to(self.project_root).as_posix(),
            saved=False,
            restored=False,
            valid=True,
            reason="layout_cleared",
        )


def build_workspace_layout_persistence_snapshot(project_root: str | Path = ".") -> dict[str, Any]:
    owner = WorkspaceLayoutPersistence(project_root)
    loaded = owner.load_layout()

    return {
        "schema": SCHEMA,
        "phase": "21G",
        "feature": "WORKSPACE_LAYOUT_PERSISTENCE",
        "summary": {
            "owner_class": "WorkspaceLayoutPersistence",
            "layout_path": owner.layout_path.relative_to(owner.project_root).as_posix(),
            "layout_file_exists": owner.layout_path.exists(),
            "loaded_layout_valid": bool(loaded.get("valid", False)),
            "presentation_state_only": True,
            "stores_engineering_data": False,
            "stores_repository_intelligence": False,
            "stores_sorting_execution_state": False,
            "stores_import_approval_state": False,
            "imports_files": False,
            "copies_files": False,
            "moves_files": False,
            "deletes_files": False,
            "archives_files": False,
            "automatic_import_allowed": False,
        },
    }
