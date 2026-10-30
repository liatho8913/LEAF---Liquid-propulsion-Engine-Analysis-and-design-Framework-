from __future__ import annotations
import math
import time

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from leaf_qt.storage.canonical_storage import paths_match

SCHEMA = "LEAF_RUNTIME_SESSION_LIFECYCLE_S1M9_V4"

RUNTIME_SECURITY_LOCKED = "LOCKED"
RUNTIME_SECURITY_UNLOCKED = "UNLOCKED"

VALID_RUNTIME_SECURITY_STATES = frozenset({
    RUNTIME_SECURITY_LOCKED,
    RUNTIME_SECURITY_UNLOCKED,
})

DEFAULT_RUNTIME_SECURITY_STATE = (
    RUNTIME_SECURITY_UNLOCKED
)

CANONICAL_PROJECT_ROOT = "LEAF_Projects"
CANONICAL_DESIGN_ROOT = "LEAF_Designs"
CANONICAL_REPORT_ROOT = "LEAF_Reports"
CANONICAL_EXPORT_ROOT = "LEAF_Exports"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class RuntimeOpenDocument:
    document_id: str
    path: str
    document_type: str
    opened_at: str = field(default_factory=utc_now)


def _coerce_security_activity_monotonic(
    value: float | None,
) -> float:
    try:
        timestamp = (
            time.monotonic()
            if value is None
            else float(value)
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "runtime_security_activity_time_invalid"
        ) from exc

    if (
        not math.isfinite(timestamp)
        or
        timestamp < 0.0
    ):
        raise ValueError(
            "runtime_security_activity_time_invalid"
        )

    return timestamp


@dataclass
class RuntimeSessionState:
    session_id: str
    created_at: str
    active_project: str | None = None
    active_design: str | None = None
    active_workspace: str | None = None
    active_tool: str | None = None
    active_report: str | None = None
    open_documents: dict[str, RuntimeOpenDocument] = field(default_factory=dict)
    closed_at: str | None = None
    security_state: str = DEFAULT_RUNTIME_SECURITY_STATE
    authenticated_principal_id: str | None = None
    last_security_activity_monotonic: float | None = None

    @property
    def is_open(self) -> bool:
        return self.closed_at is None

    def __post_init__(self) -> None:
        if (
            self.security_state
            not in
            VALID_RUNTIME_SECURITY_STATES
        ):
            raise ValueError(
                "runtime_security_state_invalid"
            )

        if (
            self.authenticated_principal_id
            is not None
        ):
            principal_id = str(
                self.authenticated_principal_id
            ).strip()

            if not principal_id:
                raise ValueError(
                    "runtime_authenticated_"
                    "principal_id_invalid"
                )

            self.authenticated_principal_id = (
                principal_id
            )

        if (
            self.security_state
            ==
            RUNTIME_SECURITY_LOCKED
        ):
            if (
                self.authenticated_principal_id
                is not None
            ):
                raise ValueError(
                    "runtime_locked_session_has_"
                    "authenticated_principal"
                )

            if (
                self.last_security_activity_monotonic
                is not None
            ):
                raise ValueError(
                    "runtime_locked_session_has_"
                    "security_activity"
                )

            return

        self.last_security_activity_monotonic = (
            _coerce_security_activity_monotonic(
                self.last_security_activity_monotonic
            )
        )



    @property
    def is_security_locked(self) -> bool:
        return (
            self.security_state
            ==
            RUNTIME_SECURITY_LOCKED
        )

    @property
    def is_security_unlocked(self) -> bool:
        return (
            self.security_state
            ==
            RUNTIME_SECURITY_UNLOCKED
        )

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = SCHEMA
        payload["is_open"] = self.is_open
        payload["qt_owns_runtime_state"] = False
        payload["stores_solver_payloads"] = False
        payload["stores_report_payloads"] = False
        payload["stores_validation_payloads"] = False
        payload["canonical_user_roots"] = {
            "projects": CANONICAL_PROJECT_ROOT,
            "designs": CANONICAL_DESIGN_ROOT,
            "reports": CANONICAL_REPORT_ROOT,
            "exports": CANONICAL_EXPORT_ROOT,
        }
        return payload


class RuntimeSessionLifecycle:
    """
    Central owner for LEAF engineering runtime session metadata.

    This is intentionally metadata-only.

    It owns:
    - active project reference
    - active design reference
    - active workspace reference
    - active tool reference
    - active report reference
    - open document references
    - ephemeral runtime security state

    It does not own:
    - credentials or credential verification
    - Qt widgets
    - solver state
    - validation payloads
    - report payloads
    - repository sorting execution
    """

    def __init__(self) -> None:
        self._session: RuntimeSessionState | None = None

    def create_session(self) -> RuntimeSessionState:
        if self._session is not None and self._session.is_open:
            raise RuntimeError("runtime_session_already_open")

        self._session = RuntimeSessionState(
            session_id=f"runtime_{uuid4().hex[:16]}",
            created_at=utc_now(),
        )
        return self._session

    def require_session(self) -> RuntimeSessionState:
        if self._session is None or not self._session.is_open:
            raise RuntimeError("runtime_session_not_open")
        return self._session

    def close_session(self) -> RuntimeSessionState:
        session = self.require_session()
        session.closed_at = utc_now()
        return session

    def set_active_project(self, path: str | Path) -> RuntimeSessionState:
        session = self.require_session()
        session.active_project = str(path)
        return session

    def set_active_design(self, path: str | Path) -> RuntimeSessionState:
        session = self.require_session()
        session.active_design = str(path)
        return session

    def set_active_workspace(self, workspace_id: str) -> RuntimeSessionState:
        session = self.require_session()
        session.active_workspace = workspace_id
        return session

    def set_active_tool(self, tool_id: str) -> RuntimeSessionState:
        session = self.require_session()
        session.active_tool = tool_id
        return session

    def set_active_report(self, report_id: str | None) -> RuntimeSessionState:
        session = self.require_session()
        session.active_report = report_id
        return session

    def open_document(
        self,
        path: str | Path,
        document_type: str,
        document_id: str | None = None,
    ) -> RuntimeOpenDocument:
        session = self.require_session()
        document = RuntimeOpenDocument(
            document_id=document_id or f"doc_{uuid4().hex[:16]}",
            path=str(path),
            document_type=document_type,
        )
        session.open_documents[document.document_id] = document
        return document

    def close_document(self, document_id: str) -> RuntimeSessionState:
        session = self.require_session()
        session.open_documents.pop(document_id, None)
        return session

    def replace_path_reference(
        self,
        old_path: str | Path,
        new_path: str | Path,
    ) -> dict[str, Any]:
        """
        Replace live session path references while preserving
        open-document identity and original opened_at time.
        """
        session = self.require_session()

        new_path_text = str(
            new_path
        )

        active_project_changed = (
            paths_match(
                session.active_project,
                old_path,
            )
        )

        active_design_changed = (
            paths_match(
                session.active_design,
                old_path,
            )
        )

        if active_project_changed:
            session.active_project = (
                new_path_text
            )

        if active_design_changed:
            session.active_design = (
                new_path_text
            )

        open_documents_changed = 0

        for (
            document_id,
            document,
        ) in list(
            session.open_documents.items()
        ):
            if not paths_match(
                document.path,
                old_path,
            ):
                continue

            session.open_documents[
                document_id
            ] = RuntimeOpenDocument(
                document_id=
                    document.document_id,

                path=
                    new_path_text,

                document_type=
                    document.document_type,

                opened_at=
                    document.opened_at,
            )

            open_documents_changed += 1

        return {
            "active_project_changed":
                active_project_changed,

            "active_design_changed":
                active_design_changed,

            "open_documents_changed":
                open_documents_changed,
        }

    def _lock_for_authentication(self) -> bool:
        """
        Enter the fail-closed runtime authentication state.

        This operation does not inspect or receive credentials.
        """
        session = self.require_session()

        changed = (
            not session.is_security_locked
            or
            session.authenticated_principal_id
            is not None
            or
            session.last_security_activity_monotonic
            is not None
        )

        session.security_state = (
            RUNTIME_SECURITY_LOCKED
        )

        session.authenticated_principal_id = (
            None
        )

        session.last_security_activity_monotonic = (
            None
        )

        return changed


    def _complete_authenticated_unlock(
        self,
        principal_id: str,
    ) -> bool:
        """
        Commit an unlock only after an external authentication
        owner has successfully proved the principal.
        """
        principal_id = str(
            principal_id
        ).strip()

        if not principal_id:
            raise ValueError(
                "runtime_authenticated_"
                "principal_id_invalid"
            )

        session = self.require_session()

        if not session.is_security_locked:
            raise RuntimeError(
                "runtime_security_session_not_locked"
            )

        session.security_state = (
            RUNTIME_SECURITY_UNLOCKED
        )

        session.authenticated_principal_id = (
            principal_id
        )

        session.last_security_activity_monotonic = (
            _coerce_security_activity_monotonic(
                None
            )
        )

        return True


    def record_security_activity(self) -> bool:
        """
        Record trusted application activity for an unlocked
        runtime security session.

        Activity cannot unlock a locked session.
        """
        session = self.require_session()

        if session.is_security_locked:
            return False

        session.last_security_activity_monotonic = (
            _coerce_security_activity_monotonic(
                None
            )
        )

        return True

    def security_inactivity_elapsed_seconds(
        self,
    ) -> float | None:
        """
        Return elapsed inactivity for an unlocked session.

        Locked sessions return None because no additional
        restrictive transition is necessary.
        """
        session = self.require_session()

        if session.is_security_locked:
            return None

        activity = (
            session.last_security_activity_monotonic
        )

        if activity is None:
            raise RuntimeError(
                "runtime_security_activity_missing"
            )

        return max(
            0.0,
            time.monotonic()
            -
            activity,
        )

    def security_inactivity_expired(
        self,
        timeout_seconds: float,
    ) -> bool:
        """
        Evaluate whether the supplied inactivity policy has
        expired without performing any security transition.
        """
        try:
            timeout = float(
                timeout_seconds
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "runtime_security_inactivity_"
                "timeout_invalid"
            ) from exc

        if (
            not math.isfinite(timeout)
            or
            timeout <= 0.0
        ):
            raise ValueError(
                "runtime_security_inactivity_"
                "timeout_invalid"
            )

        elapsed = (
            self
            .security_inactivity_elapsed_seconds()
        )

        return (
            elapsed is not None
            and
            elapsed >= timeout
        )

    def snapshot(self) -> dict[str, Any]:
        return self.require_session().snapshot()


runtime_session_lifecycle = RuntimeSessionLifecycle()
