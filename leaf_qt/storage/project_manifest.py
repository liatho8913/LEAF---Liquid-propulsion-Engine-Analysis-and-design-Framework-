from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from leaf_qt.security_context import (
    DEFAULT_PROJECT_SECURITY_CLASSIFICATION,
    VALID_SECURITY_CLASSIFICATIONS,
)

SCHEMA = "LEAF_PROJECT_MANIFEST_PHASE_25B_V1"
PROJECT_MANIFEST_FILENAME = "project.leaf_project.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_project_id() -> str:
    return f"project_{uuid4().hex[:16]}"


@dataclass
class ProjectManifest:
    project_id: str
    project_name: str
    created_at: str
    modified_at: str
    active_designs: list[str] = field(default_factory=list)
    linked_reports: list[str] = field(default_factory=list)
    linked_exports: list[str] = field(default_factory=list)
    project_notes: str = ""
    runtime_schema_version: str = ""
    storage_schema_version: str = SCHEMA
    owner_principal_id: str = ""
    security_classification: str = DEFAULT_PROJECT_SECURITY_CLASSIFICATION

    @classmethod
    def create(
        cls,
        project_name: str,
        runtime_schema_version: str = "",
        project_notes: str = "",
    ) -> "ProjectManifest":
        now = utc_now()
        return cls(
            project_id=new_project_id(),
            project_name=project_name,
            created_at=now,
            modified_at=now,
            project_notes=project_notes,
            runtime_schema_version=runtime_schema_version,
            storage_schema_version=SCHEMA,
        )

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ProjectManifest":
        data = dict(payload)

        if data.get("schema"):
            data.pop("schema")

        return cls(
            project_id=str(data["project_id"]),
            project_name=str(data["project_name"]),
            created_at=str(data["created_at"]),
            modified_at=str(data["modified_at"]),
            active_designs=list(data.get("active_designs", [])),
            linked_reports=list(data.get("linked_reports", [])),
            linked_exports=list(data.get("linked_exports", [])),
            project_notes=str(data.get("project_notes", "")),
            runtime_schema_version=str(data.get("runtime_schema_version", "")),
            storage_schema_version=str(data.get("storage_schema_version", SCHEMA)),
            owner_principal_id=str(
                data.get(
                    "owner_principal_id",
                    "",
                )
            ).strip(),
            security_classification=(
                str(
                    data.get(
                        "security_classification",
                        DEFAULT_PROJECT_SECURITY_CLASSIFICATION,
                    )
                    or DEFAULT_PROJECT_SECURITY_CLASSIFICATION
                ).strip()
                or DEFAULT_PROJECT_SECURITY_CLASSIFICATION
            ),
        )

    def touch(self) -> None:
        self.modified_at = utc_now()

    def add_design(self, design_ref: str) -> None:
        if design_ref not in self.active_designs:
            self.active_designs.append(design_ref)
            self.touch()

    def add_report(self, report_ref: str) -> None:
        if report_ref not in self.linked_reports:
            self.linked_reports.append(report_ref)
            self.touch()

    def add_export(self, export_ref: str) -> None:
        if export_ref not in self.linked_exports:
            self.linked_exports.append(export_ref)
            self.touch()

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = SCHEMA
        payload["manifest_filename"] = PROJECT_MANIFEST_FILENAME
        payload["owns_design_payloads"] = False
        payload["owns_report_payloads"] = False
        payload["owns_export_payloads"] = False
        payload["qt_owns_project_manifest"] = False
        return payload


class ProjectManifestValidator:
    REQUIRED_FIELDS = {
        "project_id",
        "project_name",
        "created_at",
        "modified_at",
        "active_designs",
        "linked_reports",
        "linked_exports",
        "project_notes",
        "runtime_schema_version",
        "storage_schema_version",
    }

    def validate(self, manifest: ProjectManifest) -> dict[str, Any]:
        failures: list[str] = []
        snapshot = manifest.snapshot()

        for field_name in self.REQUIRED_FIELDS:
            if field_name not in snapshot:
                failures.append(f"missing_field:{field_name}")

        if not manifest.project_id.startswith("project_"):
            failures.append("project_id_invalid")

        if not manifest.project_name.strip():
            failures.append("project_name_required")

        if not isinstance(manifest.active_designs, list):
            failures.append("active_designs_not_list")

        if not isinstance(manifest.linked_reports, list):
            failures.append("linked_reports_not_list")

        if not isinstance(manifest.linked_exports, list):
            failures.append("linked_exports_not_list")

        if manifest.storage_schema_version != SCHEMA:
            failures.append("storage_schema_version_mismatch")

        if (
            manifest.owner_principal_id
            and
            not manifest.owner_principal_id.startswith("principal_")
        ):
            failures.append("owner_principal_id_invalid")
        
        if (
            manifest.security_classification
            not in VALID_SECURITY_CLASSIFICATIONS
        ):
            failures.append("security_classification_invalid")

        return {
            "schema": "LEAF_PROJECT_MANIFEST_VALIDATION_PHASE_25B_V1",
            "passed": not failures,
            "failures": failures,
            "project_id": manifest.project_id,
            "project_name": manifest.project_name,
        }


project_manifest_validator = ProjectManifestValidator()
