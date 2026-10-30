from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

SCHEMA = "LEAF_DESIGN_MANIFEST_PHASE_25C_V1"
DESIGN_MANIFEST_FILENAME = "design.leaf_design.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_design_id() -> str:
    return f"design_{uuid4().hex[:16]}"


@dataclass
class DesignManifest:
    design_id: str
    design_name: str
    parent_project_id: str
    created_at: str
    modified_at: str
    engine_type: str = "liquid_rocket_engine"
    solver_profile: str = ""
    materials_profile: str = ""
    geometry_profile: str = ""
    validation_refs: list[str] = field(default_factory=list)
    report_refs: list[str] = field(default_factory=list)
    export_refs: list[str] = field(default_factory=list)
    dirty_state: str = "saved"
    runtime_last_opened: str = ""
    storage_schema_version: str = SCHEMA
    engineering_state_ref: str = ""

    @classmethod
    def create(
        cls,
        design_name: str,
        parent_project_id: str,
        engine_type: str = "liquid_rocket_engine",
    ) -> "DesignManifest":
        now = utc_now()
        return cls(
            design_id=new_design_id(),
            design_name=design_name,
            parent_project_id=parent_project_id,
            created_at=now,
            modified_at=now,
            engine_type=engine_type,
        )

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any],
    ) -> "DesignManifest":
        data = dict(payload)

        data.pop("schema", None)
        data.pop("manifest_filename", None)

        return cls(
            design_id=str(data["design_id"]),
            design_name=str(data["design_name"]),
            parent_project_id=str(data["parent_project_id"]),
            created_at=str(data["created_at"]),
            modified_at=str(data["modified_at"]),
            engine_type=str(
                data.get(
                    "engine_type",
                    "liquid_rocket_engine",
                )
            ),
            solver_profile=str(
                data.get(
                    "solver_profile",
                    "",
                )
            ),
            materials_profile=str(
                data.get(
                    "materials_profile",
                    "",
                )
            ),
            geometry_profile=str(
                data.get(
                    "geometry_profile",
                    "",
                )
            ),
            validation_refs=list(
                data.get(
                    "validation_refs",
                    [],
                )
            ),
            report_refs=list(
                data.get(
                    "report_refs",
                    [],
                )
            ),
            export_refs=list(
                data.get(
                    "export_refs",
                    [],
                )
            ),
            dirty_state=str(
                data.get(
                    "dirty_state",
                    "saved",
                )
            ),
            runtime_last_opened=str(
                data.get(
                    "runtime_last_opened",
                    "",
                )
            ),
            storage_schema_version=str(
                data.get(
                    "storage_schema_version",
                    SCHEMA,
                )
            ),
            engineering_state_ref=str(
                data.get(
                    "engineering_state_ref",
                    "",
                )
            ),
        )

    def touch(self) -> None:
        self.modified_at = utc_now()

    def mark_opened(self) -> None:
        self.runtime_last_opened = utc_now()

    def set_profiles(
        self,
        solver_profile: str | None = None,
        materials_profile: str | None = None,
        geometry_profile: str | None = None,
    ) -> None:
        if solver_profile is not None:
            self.solver_profile = solver_profile
        if materials_profile is not None:
            self.materials_profile = materials_profile
        if geometry_profile is not None:
            self.geometry_profile = geometry_profile
        self.touch()

    def add_validation(self, validation_ref: str) -> None:
        if validation_ref not in self.validation_refs:
            self.validation_refs.append(validation_ref)
            self.touch()

    def add_report(self, report_ref: str) -> None:
        if report_ref not in self.report_refs:
            self.report_refs.append(report_ref)
            self.touch()

    def add_export(self, export_ref: str) -> None:
        if export_ref not in self.export_refs:
            self.export_refs.append(export_ref)
            self.touch()

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = SCHEMA
        payload["manifest_filename"] = DESIGN_MANIFEST_FILENAME
        payload["owns_solver_payloads"] = False
        payload["owns_material_payloads"] = False
        payload["owns_geometry_payloads"] = False
        payload["owns_report_payloads"] = False
        payload["owns_validation_payloads"] = False
        payload["qt_owns_design_manifest"] = False
        return payload


class DesignManifestValidator:
    REQUIRED_FIELDS = {
        "design_id",
        "design_name",
        "parent_project_id",
        "created_at",
        "modified_at",
        "engine_type",
        "solver_profile",
        "materials_profile",
        "geometry_profile",
        "validation_refs",
        "report_refs",
        "export_refs",
        "dirty_state",
        "runtime_last_opened",
        "storage_schema_version",
    }

    VALID_DIRTY_STATES = {
        "saved",
        "modified",
        "unsaved",
    }

    def validate(self, manifest: DesignManifest) -> dict[str, Any]:
        failures: list[str] = []
        snapshot = manifest.snapshot()

        for field_name in self.REQUIRED_FIELDS:
            if field_name not in snapshot:
                failures.append(f"missing_field:{field_name}")

        if not manifest.design_id.startswith("design_"):
            failures.append("design_id_invalid")

        if not manifest.design_name.strip():
            failures.append("design_name_required")

        if not manifest.parent_project_id.startswith("project_"):
            failures.append("parent_project_id_invalid")

        if not manifest.engine_type.strip():
            failures.append("engine_type_required")

        if manifest.dirty_state not in self.VALID_DIRTY_STATES:
            failures.append("dirty_state_invalid")

        if manifest.storage_schema_version != SCHEMA:
            failures.append("storage_schema_version_mismatch")

        for list_name in ["validation_refs", "report_refs", "export_refs"]:
            if not isinstance(getattr(manifest, list_name), list):
                failures.append(f"{list_name}_not_list")

        return {
            "schema": "LEAF_DESIGN_MANIFEST_VALIDATION_PHASE_25C_V1",
            "passed": not failures,
            "failures": failures,
            "design_id": manifest.design_id,
            "design_name": manifest.design_name,
            "parent_project_id": manifest.parent_project_id,
        }


design_manifest_validator = DesignManifestValidator()
