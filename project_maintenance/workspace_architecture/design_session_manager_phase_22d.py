from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_DESIGN_SESSION_MANAGER_PHASE_22D_V1"

USER_DESIGN_ROOT = "LEAF_Designs"
SESSION_STATE_DIR = "_leaf_artifacts/workspace_architecture/design_sessions"
SESSION_STATE_FILE = "design_session_state_phase_22d.json"


@dataclass(frozen=True)
class DesignSessionRecord:
    session_id: str
    design_id: str
    design_label: str
    design_path: str
    active_tool_id: str | None
    dirty: bool
    saved: bool
    user_visible_storage: bool
    internal_storage: bool
    qt_owns_design_logic: bool


class DesignSessionManager:
    """Owns workspace design session state.

    This manager stores session metadata only. Canonical user designs belong in
    LEAF_Designs, while internal artifacts only store lightweight active-session
    state.
    """

    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.user_design_root = self.project_root / USER_DESIGN_ROOT
        self.state_dir = self.project_root / SESSION_STATE_DIR
        self.state_path = self.state_dir / SESSION_STATE_FILE

    def ensure_user_design_root(self) -> Path:
        self.user_design_root.mkdir(parents=True, exist_ok=True)
        return self.user_design_root

    def create_session(
        self,
        *,
        design_label: str = "Untitled Design",
        active_tool_id: str | None = None,
    ) -> DesignSessionRecord:
        self.ensure_user_design_root()

        design_id = self._safe_design_id(design_label)
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        design_path = f"{USER_DESIGN_ROOT}/{design_id}.leaf_design.json"

        return DesignSessionRecord(
            session_id=session_id,
            design_id=design_id,
            design_label=design_label,
            design_path=design_path,
            active_tool_id=active_tool_id,
            dirty=False,
            saved=False,
            user_visible_storage=True,
            internal_storage=False,
            qt_owns_design_logic=False,
        )

    def save_state(self, session: DesignSessionRecord) -> dict[str, Any]:
        self.state_dir.mkdir(parents=True, exist_ok=True)

        payload = {
            "schema": SCHEMA,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "session": asdict(session),
            "state_type": "session_metadata_only",
            "stores_engineering_calculation_data": False,
            "stores_solver_state": False,
            "stores_validation_state": False,
            "stores_report_payloads": False,
            "canonical_user_design_root": USER_DESIGN_ROOT,
        }

        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {
                "schema": SCHEMA,
                "exists": False,
                "valid": False,
                "reason": "session_state_missing",
            }

        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {
                "schema": SCHEMA,
                "exists": True,
                "valid": False,
                "reason": f"session_state_unreadable:{exc!r}",
            }

        if payload.get("schema") != SCHEMA:
            return {
                "schema": SCHEMA,
                "exists": True,
                "valid": False,
                "reason": "schema_mismatch",
            }

        unsafe_keys = [
            "stores_engineering_calculation_data",
            "stores_solver_state",
            "stores_validation_state",
            "stores_report_payloads",
        ]

        for key in unsafe_keys:
            if payload.get(key) is not False:
                return {
                    "schema": SCHEMA,
                    "exists": True,
                    "valid": False,
                    "reason": f"unsafe_session_payload:{key}",
                }

        session = payload.get("session", {})
        if session.get("user_visible_storage") is not True:
            return {
                "schema": SCHEMA,
                "exists": True,
                "valid": False,
                "reason": "session_not_user_visible_storage",
            }

        if session.get("internal_storage") is not False:
            return {
                "schema": SCHEMA,
                "exists": True,
                "valid": False,
                "reason": "session_uses_internal_storage",
            }

        return {
            **payload,
            "exists": True,
            "valid": True,
        }

    @staticmethod
    def _safe_design_id(label: str) -> str:
        cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in label).strip("_")
        cleaned = "_".join(part for part in cleaned.split("_") if part)
        return cleaned or "untitled_design"


def build_design_session_manager_snapshot(project_root: str | Path = ".") -> dict[str, Any]:
    manager = DesignSessionManager(project_root)
    sample_session = manager.create_session(design_label="Untitled Design", active_tool_id="regen")
    manager.save_state(sample_session)
    loaded = manager.load_state()

    return {
        "schema": SCHEMA,
        "phase": "22D",
        "feature": "DESIGN_SESSION_MANAGER",
        "summary": {
            "manager_class": "DesignSessionManager",
            "canonical_user_design_root": USER_DESIGN_ROOT,
            "session_state_path": manager.state_path.relative_to(manager.project_root).as_posix(),
            "sample_session_id": sample_session.session_id,
            "sample_design_id": sample_session.design_id,
            "sample_design_path": sample_session.design_path,
            "session_state_exists": manager.state_path.exists(),
            "session_state_valid": loaded.get("valid", False),
            "user_visible_storage": sample_session.user_visible_storage,
            "internal_storage": sample_session.internal_storage,
            "qt_owns_design_logic": sample_session.qt_owns_design_logic,
            "stores_engineering_calculation_data": False,
            "stores_solver_state": False,
            "stores_validation_state": False,
            "stores_report_payloads": False,
            "filesystem_mutation_limited_to_session_metadata": True,
            "ready_for_22e_engineering_document_model": True,
        },
    }
