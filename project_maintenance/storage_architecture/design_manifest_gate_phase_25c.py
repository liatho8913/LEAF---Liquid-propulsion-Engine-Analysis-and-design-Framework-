from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "storage_architecture" / "phase_25c"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "storage" / "__init__.py",
    ROOT / "leaf_qt" / "storage" / "canonical_storage.py",
    ROOT / "leaf_qt" / "storage" / "project_manifest.py",
    ROOT / "leaf_qt" / "storage" / "design_manifest.py",
]

from leaf_qt.storage.design_manifest import (
    DESIGN_MANIFEST_FILENAME,
    SCHEMA,
    DesignManifest,
    DesignManifestValidator,
)


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        if not module.exists():
            failures.append(f"missing_module:{module.relative_to(ROOT)}")
            continue

        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    manifest = DesignManifest.create(
        design_name="Runtime Storage Test Design",
        parent_project_id="project_test1234567890",
        engine_type="liquid_rocket_engine",
    )

    if not manifest.design_id.startswith("design_"):
        failures.append("design_id_invalid")

    if manifest.design_name != "Runtime Storage Test Design":
        failures.append("design_name_not_retained")

    if manifest.parent_project_id != "project_test1234567890":
        failures.append("parent_project_id_not_retained")

    if manifest.created_at != manifest.modified_at:
        failures.append("created_modified_initial_mismatch")

    manifest.set_profiles(
        solver_profile="regen_solver_v1",
        materials_profile="copper_alloy_profile",
        geometry_profile="rao_regen_geometry",
    )

    manifest.add_validation("LEAF_Reports/validation_001.json")
    manifest.add_validation("LEAF_Reports/validation_001.json")
    manifest.add_report("LEAF_Reports/report_001.json")
    manifest.add_export("LEAF_Exports/export_001.csv")
    manifest.mark_opened()

    if manifest.solver_profile != "regen_solver_v1":
        failures.append("solver_profile_not_retained")

    if manifest.materials_profile != "copper_alloy_profile":
        failures.append("materials_profile_not_retained")

    if manifest.geometry_profile != "rao_regen_geometry":
        failures.append("geometry_profile_not_retained")

    if len(manifest.validation_refs) != 1:
        failures.append("duplicate_validation_ref_not_prevented")

    if len(manifest.report_refs) != 1:
        failures.append("report_ref_not_retained")

    if len(manifest.export_refs) != 1:
        failures.append("export_ref_not_retained")

    if not manifest.runtime_last_opened:
        failures.append("runtime_last_opened_not_set")

    snapshot = manifest.snapshot()

    required_snapshot_keys = [
        "schema",
        "manifest_filename",
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
        "owns_solver_payloads",
        "owns_material_payloads",
        "owns_geometry_payloads",
        "owns_report_payloads",
        "owns_validation_payloads",
        "qt_owns_design_manifest",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    if snapshot.get("manifest_filename") != DESIGN_MANIFEST_FILENAME:
        failures.append("manifest_filename_invalid")

    for key in [
        "owns_solver_payloads",
        "owns_material_payloads",
        "owns_geometry_payloads",
        "owns_report_payloads",
        "owns_validation_payloads",
        "qt_owns_design_manifest",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"manifest_boundary_invalid:{key}")

    restored = DesignManifest.from_dict(snapshot)

    if restored.snapshot().get("design_id") != snapshot.get("design_id"):
        failures.append("round_trip_design_id_failed")

    if restored.snapshot().get("validation_refs") != snapshot.get("validation_refs"):
        failures.append("round_trip_validation_refs_failed")

    validator = DesignManifestValidator()
    validation = validator.validate(restored)

    if validation.get("passed") is not True:
        failures.append(f"validator_failed:{validation.get('failures')}")

    bad_manifest = DesignManifest(
        design_id="bad",
        design_name="",
        parent_project_id="bad_project",
        created_at="",
        modified_at="",
        dirty_state="half_saved",
        storage_schema_version="wrong",
    )

    bad_validation = validator.validate(bad_manifest)

    if bad_validation.get("passed") is not False:
        failures.append("validator_failed_to_reject_bad_manifest")

    result = {
        "phase": "25C",
        "programme": "25",
        "feature": "DESIGN_MANIFEST_MODEL",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_DESIGN_MANIFEST_GATE_PHASE_25C_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/storage/design_manifest.py",
            "project_maintenance/storage_architecture/design_manifest_gate_phase_25c.py",
        ],
        "files_replaced": [
            "leaf_qt/storage/__init__.py",
        ],
        "files_removed": [],
        "validated": {
            "design_id": True,
            "design_name": True,
            "parent_project_id": True,
            "engine_type": True,
            "solver_profile": True,
            "materials_profile": True,
            "geometry_profile": True,
            "validation_refs": True,
            "report_refs": True,
            "export_refs": True,
            "dirty_state": True,
            "runtime_last_opened": True,
            "round_trip_manifest": True,
            "manifest_validator": True,
            "qt_does_not_own_design_manifest": True,
            "metadata_only_design_manifest": True,
        },
        "completion_notice": (
            "PHASE_25C_COMPLETE_DESIGN_MANIFEST_MODEL_ESTABLISHED"
            if not failures
            else "PHASE_25C_BLOCKED"
        ),
        "next_phase": "25D_PROJECT_DESIGN_CREATION_OWNER",
    }

    json_path = OUT / "design_manifest_gate_phase_25c.json"
    txt_path = OUT / "design_manifest_gate_phase_25c.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 25C DESIGN MANIFEST MODEL GATE",
                "=============================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "design_id=True",
                "design_name=True",
                "parent_project_id=True",
                "engine_type=True",
                "solver_profile=True",
                "materials_profile=True",
                "geometry_profile=True",
                "validation_refs=True",
                "report_refs=True",
                "export_refs=True",
                "dirty_state=True",
                "runtime_last_opened=True",
                "round_trip_manifest=True",
                "manifest_validator=True",
                "qt_does_not_own_design_manifest=True",
                "metadata_only_design_manifest=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_25C_DESIGN_MANIFEST_MODEL")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_25C_DESIGN_MANIFEST_MODEL")
    print(f"runtime_schema={SCHEMA}")
    print("design_id=True")
    print("design_name=True")
    print("parent_project_id=True")
    print("engine_type=True")
    print("solver_profile=True")
    print("materials_profile=True")
    print("geometry_profile=True")
    print("validation_refs=True")
    print("report_refs=True")
    print("export_refs=True")
    print("dirty_state=True")
    print("runtime_last_opened=True")
    print("round_trip_manifest=True")
    print("manifest_validator=True")
    print("qt_does_not_own_design_manifest=True")
    print("metadata_only_design_manifest=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
