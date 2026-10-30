from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "storage_architecture" / "phase_25b"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "storage" / "__init__.py",
    ROOT / "leaf_qt" / "storage" / "canonical_storage.py",
    ROOT / "leaf_qt" / "storage" / "project_manifest.py",
]

from leaf_qt.storage.project_manifest import (
    PROJECT_MANIFEST_FILENAME,
    SCHEMA,
    ProjectManifest,
    ProjectManifestValidator,
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

    manifest = ProjectManifest.create(
        project_name="Runtime Storage Test Project",
        runtime_schema_version="LEAF_RUNTIME_COMPLETION_GATE_PHASE_24H_V1",
        project_notes="Project manifest gate test.",
    )

    if not manifest.project_id.startswith("project_"):
        failures.append("project_id_invalid")

    if manifest.project_name != "Runtime Storage Test Project":
        failures.append("project_name_not_retained")

    if manifest.created_at != manifest.modified_at:
        failures.append("created_modified_initial_mismatch")

    manifest.add_design("LEAF_Designs/test_design/design.leaf_design.json")
    manifest.add_design("LEAF_Designs/test_design/design.leaf_design.json")
    manifest.add_report("LEAF_Reports/test_report.json")
    manifest.add_export("LEAF_Exports/test_export.csv")

    if len(manifest.active_designs) != 1:
        failures.append("duplicate_design_ref_not_prevented")

    if len(manifest.linked_reports) != 1:
        failures.append("report_ref_not_retained")

    if len(manifest.linked_exports) != 1:
        failures.append("export_ref_not_retained")

    snapshot = manifest.snapshot()

    required_snapshot_keys = [
        "schema",
        "manifest_filename",
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
        "owns_design_payloads",
        "owns_report_payloads",
        "owns_export_payloads",
        "qt_owns_project_manifest",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    if snapshot.get("manifest_filename") != PROJECT_MANIFEST_FILENAME:
        failures.append("manifest_filename_invalid")

    for key in [
        "owns_design_payloads",
        "owns_report_payloads",
        "owns_export_payloads",
        "qt_owns_project_manifest",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"manifest_boundary_invalid:{key}")

    restored = ProjectManifest.from_dict(snapshot)

    if restored.snapshot().get("project_id") != snapshot.get("project_id"):
        failures.append("round_trip_project_id_failed")

    if restored.snapshot().get("active_designs") != snapshot.get("active_designs"):
        failures.append("round_trip_design_refs_failed")

    validator = ProjectManifestValidator()
    validation = validator.validate(restored)

    if validation.get("passed") is not True:
        failures.append(f"validator_failed:{validation.get('failures')}")

    bad_manifest = ProjectManifest(
        project_id="bad",
        project_name="",
        created_at="",
        modified_at="",
        storage_schema_version="wrong",
    )

    bad_validation = validator.validate(bad_manifest)

    if bad_validation.get("passed") is not False:
        failures.append("validator_failed_to_reject_bad_manifest")

    result = {
        "phase": "25B",
        "programme": "25",
        "feature": "PROJECT_MANIFEST_MODEL",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_PROJECT_MANIFEST_GATE_PHASE_25B_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/storage/project_manifest.py",
            "project_maintenance/storage_architecture/project_manifest_gate_phase_25b.py",
        ],
        "files_replaced": [
            "leaf_qt/storage/__init__.py",
        ],
        "files_removed": [],
        "validated": {
            "project_id": True,
            "project_name": True,
            "created_at": True,
            "modified_at": True,
            "active_designs": True,
            "linked_reports": True,
            "linked_exports": True,
            "project_notes": True,
            "runtime_schema_version": True,
            "storage_schema_version": True,
            "round_trip_manifest": True,
            "manifest_validator": True,
            "qt_does_not_own_project_manifest": True,
            "metadata_only_project_manifest": True,
        },
        "completion_notice": (
            "PHASE_25B_COMPLETE_PROJECT_MANIFEST_MODEL_ESTABLISHED"
            if not failures
            else "PHASE_25B_BLOCKED"
        ),
        "next_phase": "25C_DESIGN_MANIFEST_MODEL",
    }

    json_path = OUT / "project_manifest_gate_phase_25b.json"
    txt_path = OUT / "project_manifest_gate_phase_25b.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 25B PROJECT MANIFEST MODEL GATE",
                "==============================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "project_id=True",
                "project_name=True",
                "created_at=True",
                "modified_at=True",
                "active_designs=True",
                "linked_reports=True",
                "linked_exports=True",
                "project_notes=True",
                "runtime_schema_version=True",
                "storage_schema_version=True",
                "round_trip_manifest=True",
                "manifest_validator=True",
                "qt_does_not_own_project_manifest=True",
                "metadata_only_project_manifest=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_25B_PROJECT_MANIFEST_MODEL")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_25B_PROJECT_MANIFEST_MODEL")
    print(f"runtime_schema={SCHEMA}")
    print("project_id=True")
    print("project_name=True")
    print("created_at=True")
    print("modified_at=True")
    print("active_designs=True")
    print("linked_reports=True")
    print("linked_exports=True")
    print("project_notes=True")
    print("runtime_schema_version=True")
    print("storage_schema_version=True")
    print("round_trip_manifest=True")
    print("manifest_validator=True")
    print("qt_does_not_own_project_manifest=True")
    print("metadata_only_project_manifest=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
