from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from leaf_qt.security_context import VALID_SECURITY_CLASSIFICATIONS


SCHEMA = "LEAF_SECURITY_AUDIT_S1K3_V1"
EVENT_SCHEMA = "LEAF_SECURITY_AUDIT_EVENT_S1K3_V1"
RETENTION_MODE = "PRESERVE_UNTIL_EXPLICIT_POLICY"

VALID_OUTCOMES = frozenset({
    "success",
    "failure",
    "denied",
    "rejected",
})

ALLOWED_EVENT_FIELDS = frozenset({
    "schema",
    "event_type",
    "action",
    "outcome",
    "resource_type",
    "classification",
    "timestamp",
    "principal_id",
    "project_id",
    "design_id",
})

PROHIBITED_FIELD_NAMES = frozenset({
    "recovery_key",
    "project_key",
    "key_material",
    "wrapped_project_key",
    "ciphertext",
    "password",
    "credential",
    "token",
    "project_name",
    "design_name",
    "project_notes",
    "engineering_state",
    "payload",
    "results",
})

_TOKEN = re.compile(
    r"^[a-z][a-z0-9_.-]{0,63}$"
)

_ID = {
    "principal_id":
        re.compile(
            r"^principal_[A-Za-z0-9-]{1,96}$"
        ),
    "project_id":
        re.compile(
            r"^project_[A-Za-z0-9-]{1,96}$"
        ),
    "design_id":
        re.compile(
            r"^design_[A-Za-z0-9-]{1,96}$"
        ),
}


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat(
        timespec="seconds"
    )


@dataclass(frozen=True)
class SecurityAuditEvent:
    event_type: str
    action: str
    outcome: str
    resource_type: str
    timestamp: str
    classification: str | None = None
    principal_id: str | None = None
    project_id: str | None = None
    design_id: str | None = None

    def snapshot(
        self,
    ) -> dict[str, str]:
        payload = {
            "schema":
                EVENT_SCHEMA,
            "event_type":
                self.event_type,
            "action":
                self.action,
            "outcome":
                self.outcome,
            "resource_type":
                self.resource_type,
            "timestamp":
                self.timestamp,
        }

        payload.update({
            key: value
            for key, value in {
                "classification":
                    self.classification,
                "principal_id":
                    self.principal_id,
                "project_id":
                    self.project_id,
                "design_id":
                    self.design_id,
            }.items()
            if value is not None
        })

        return payload


class SecurityAuditOwner:
    """
    Canonical owner of minimal local
    security-accountability evidence.
    """

    def __init__(
        self,
        audit_path: str | Path | None = None,
    ) -> None:
        self.audit_path = (
            Path(
                audit_path
            )
            if audit_path is not None
            else (
                Path.home()
                / ".leaf"
                / "security"
                / "security_audit.jsonl"
            )
        )

    def record_event(
        self,
        *,
        event_type: str,
        action: str,
        outcome: str,
        resource_type: str,
        classification: str | None = None,
        principal_id: str | None = None,
        project_id: str | None = None,
        design_id: str | None = None,
    ) -> SecurityAuditEvent:

        event = SecurityAuditEvent(
            event_type=
                self._token(
                    event_type,
                    "event_type",
                ),
            action=
                self._token(
                    action,
                    "action",
                ),
            outcome=
                self._outcome(
                    outcome
                ),
            resource_type=
                self._token(
                    resource_type,
                    "resource_type",
                ),
            classification=
                self._classification(
                    classification
                ),
            principal_id=
                self._identifier(
                    principal_id,
                    "principal_id",
                ),
            project_id=
                self._identifier(
                    project_id,
                    "project_id",
                ),
            design_id=
                self._identifier(
                    design_id,
                    "design_id",
                ),
            timestamp=
                utc_now(),
        )

        payload = (
            event.snapshot()
        )

        self._validate_payload(
            payload
        )

        self._append(
            payload
        )

        return event

    def retention_contract(
        self,
    ) -> dict[str, Any]:
        return {
            "mode":
                RETENTION_MODE,
            "owner":
                type(self).__name__,
            "automatic_deletion_enabled":
                False,
            "central_enforcement_point":
                True,
        }

    def snapshot(
        self,
    ) -> dict[str, Any]:
        return {
            "schema":
                SCHEMA,
            "owner":
                type(self).__name__,
            "audit_path":
                str(
                    self.audit_path
                ),
            "security_accountability_owner":
                True,
            "engineering_report_owner":
                False,
            "telemetry_owner":
                False,
            "analytics_owner":
                False,
            "secret_payload_persistence":
                False,
            "engineering_payload_persistence":
                False,
            "retention":
                self.retention_contract(),
        }

    @staticmethod
    def _validate_payload(
        payload: dict[str, Any],
    ) -> None:

        fields = set(
            payload
        )

        prohibited = (
            fields
            &
            PROHIBITED_FIELD_NAMES
        )

        if prohibited:
            raise PermissionError(
                "security_audit_prohibited_fields:"
                +
                ",".join(
                    sorted(
                        prohibited
                    )
                )
            )

        unknown = (
            fields
            -
            ALLOWED_EVENT_FIELDS
        )

        if unknown:
            raise ValueError(
                "security_audit_fields_not_allowlisted:"
                +
                ",".join(
                    sorted(
                        unknown
                    )
                )
            )

        required = {
            "schema",
            "event_type",
            "action",
            "outcome",
            "resource_type",
            "timestamp",
        }

        if required - fields:
            raise ValueError(
                "security_audit_required_fields_missing"
            )

        if (
            payload["schema"]
            !=
            EVENT_SCHEMA
        ):
            raise ValueError(
                "security_audit_event_schema_invalid"
            )

    @staticmethod
    def _token(
        value: str,
        label: str,
    ) -> str:

        value = str(
            value
            or ""
        ).strip()

        if not _TOKEN.fullmatch(
            value
        ):
            raise ValueError(
                f"security_audit_{label}_invalid"
            )

        return value

    @staticmethod
    def _outcome(
        value: str,
    ) -> str:

        value = str(
            value
            or ""
        ).strip().lower()

        if (
            value
            not in
            VALID_OUTCOMES
        ):
            raise ValueError(
                "security_audit_outcome_invalid"
            )

        return value

    @staticmethod
    def _classification(
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = str(
            value
        ).strip()

        if (
            value
            not in
            VALID_SECURITY_CLASSIFICATIONS
        ):
            raise ValueError(
                "security_audit_classification_invalid"
            )

        return value

    @staticmethod
    def _identifier(
        value: str | None,
        label: str,
    ) -> str | None:

        if value is None:
            return None

        value = str(
            value
        ).strip()

        if not _ID[
            label
        ].fullmatch(
            value
        ):
            raise ValueError(
                f"security_audit_{label}_invalid"
            )

        return value

    def _append(
        self,
        payload: dict[str, Any],
    ) -> None:

        path = (
            self.audit_path
        )

        if (
            path.exists()
            and
            (
                path.is_symlink()
                or
                not path.is_file()
            )
        ):
            raise RuntimeError(
                "security_audit_path_invalid"
            )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            os.chmod(
                path.parent,
                0o700,
            )
        except OSError:
            pass

        data = (
            json.dumps(
                payload,
                sort_keys=True,
                separators=(
                    ",",
                    ":",
                ),
            )
            +
            "\n"
        ).encode(
            "utf-8"
        )

        flags = (
            os.O_WRONLY
            |
            os.O_CREAT
            |
            os.O_APPEND
        )

        if hasattr(
            os,
            "O_NOFOLLOW",
        ):
            flags |= (
                os.O_NOFOLLOW
            )

        descriptor = (
            os.open(
                path,
                flags,
                0o600,
            )
        )

        try:
            while data:

                written = (
                    os.write(
                        descriptor,
                        data,
                    )
                )

                if written <= 0:
                    raise OSError(
                        "security_audit_write_incomplete"
                    )

                data = (
                    data[
                        written:
                    ]
                )

            os.fsync(
                descriptor
            )

        finally:
            os.close(
                descriptor
            )

        try:
            os.chmod(
                path,
                0o600,
            )
        except OSError:
            pass
