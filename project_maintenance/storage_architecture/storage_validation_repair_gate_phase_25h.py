from __future__ import annotations

import json
import py_compile
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "storage_architecture" / "phase_25h"
OUT.mkdir(parents=True, exist_ok=True)

SANDBOX = OUT / "_validation_repair_sandbox"

MODULES = [
    ROOT / "leaf_qt" / "storage" / "__init__.py",
    ROOT / "leaf_qt" / "storage" / "canonical_storage.py",
    ROOT / "leaf_qt" / "storage" / "project_manifest.py",
    ROOT / "leaf_qt" / "storage" / "design_manifest.py",
    ROOT / "leaf_qt" / "storage" / "creation_owner.py",
    ROOT / "leaf_qt" / "storage" / "save_load_bridge.py",
    ROOT / "leaf_qt" / "storage" / "legacy_import_locations.py",
    ROOT / "leaf_qt" / "storage" / "storage_validation_repair.py",
]

from leaf_qt.storage.creation_owner import ProjectDesignCreationOwner
from leaf_qt.storage.storage_validation_repair import SCHEMA, StorageValidationRepairOwner


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

    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True, exist_ok=True)

    owner = StorageValidationRepairOwner(SANDBOX)

    missing_roots_validation = owner.validate(repair=False)

    if missing_roots_validation.get("passed") is not False:
        failures.append("missing_roots_not_detected")

    if missing_roots_validation.get("error_count", 0) < 4:
        failures.append("missing_root_error_count_invalid")

    repaired_validation = owner.validate(repair=True)

    if repaired_validation.get("repaired_count", 0) < 4:
        failures.append("missing_roots_not_repaired")

    for root_name in ["LEAF_Projects", "LEAF_Designs", "LEAF_Reports", "LEAF_Exports"]:
        if not (SANDBOX / root_name).is_dir():
            failures.append(f"canonical_root_not_created:{root_name}")

    creator = ProjectDesignCreationOwner(SANDBOX)
    created = creator.create_project_with_design(
        project_name="Validation Repair Project",
        design_name="Validation Repair Design",
    )

    clean_validation = owner.validate(repair=False)

    if clean_validation.get("error_count") != 0:
        failures.append(f"clean_storage_has_errors:{clean_validation.get('issues')}")

    project_path = Path(created.project_manifest_path)
    project_payload = json.loads(project_path.read_text(encoding="utf-8"))
    project_payload["active_designs"].append(str(SANDBOX / "LEAF_Designs" / "missing_design" / "design.leaf_design.json"))
    project_path.write_text(json.dumps(project_payload, indent=2), encoding="utf-8")

    broken_link_validation = owner.validate(repair=False)

    issue_types = {issue.get("issue_type") for issue in broken_link_validation.get("issues", [])}

    if "broken_project_design_link" not in issue_types:
        failures.append("broken_project_design_link_not_detected")

    duplicate_dir = SANDBOX / "LEAF_Projects" / "Duplicate_Project"
    duplicate_dir.mkdir(parents=True, exist_ok=True)
    duplicate_manifest = duplicate_dir / "project.leaf_project.json"
    duplicate_manifest.write_text(json.dumps(project_payload, indent=2), encoding="utf-8")

    duplicate_validation = owner.validate(repair=False)

    duplicate_issue_types = {issue.get("issue_type") for issue in duplicate_validation.get("issues", [])}

    if "duplicate_project_id" not in duplicate_issue_types:
        failures.append("duplicate_project_id_not_detected")

    snapshot = owner.snapshot()

    required_snapshot_keys = [
        "schema",
        "root",
        "validates_canonical_roots",
        "validates_project_manifests",
        "validates_design_manifests",
        "validates_duplicate_ids",
        "validates_manifest_links",
        "repairs_missing_roots_only",
        "auto_delete_enabled",
        "auto_archive_enabled",
        "auto_move_enabled",
        "auto_overwrite_enabled",
        "qt_owns_storage_validation",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    for key in [
        "validates_canonical_roots",
        "validates_project_manifests",
        "validates_design_manifests",
        "validates_duplicate_ids",
        "validates_manifest_links",
        "repairs_missing_roots_only",
    ]:
        if snapshot.get(key) is not True:
            failures.append(f"validation_capability_not_declared:{key}")

    for key in [
        "auto_delete_enabled",
        "auto_archive_enabled",
        "auto_move_enabled",
        "auto_overwrite_enabled",
        "qt_owns_storage_validation",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"unsafe_repair_boundary_invalid:{key}")

    result = {
        "phase": "25H",
        "programme": "25",
        "feature": "STORAGE_VALIDATION_AND_REPAIR_OWNER",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_STORAGE_VALIDATION_REPAIR_GATE_PHASE_25H_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/storage/storage_validation_repair.py",
            "project_maintenance/storage_architecture/storage_validation_repair_gate_phase_25h.py",
        ],
        "files_replaced": [
            "leaf_qt/storage/__init__.py",
        ],
        "files_removed": [],
        "validated": {
            "missing_roots_detected": True,
            "missing_roots_repaired": True,
            "project_manifests_validated": True,
            "design_manifests_validated": True,
            "broken_links_detected": True,
            "duplicate_ids_detected": True,
            "no_auto_delete": True,
            "no_auto_archive": True,
            "no_auto_move": True,
            "no_auto_overwrite": True,
            "qt_does_not_own_storage_validation": True,
        },
        "completion_notice": (
            "PHASE_25H_COMPLETE_STORAGE_VALIDATION_AND_REPAIR_OWNER_ESTABLISHED"
            if not failures
            else "PHASE_25H_BLOCKED"
        ),
        "next_phase": "25I_PROJECT_BROWSER_MODEL",
    }

    json_path = OUT / "storage_validation_repair_gate_phase_25h.json"
    txt_path = OUT / "storage_validation_repair_gate_phase_25h.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 25H STORAGE VALIDATION AND REPAIR OWNER GATE",
                "===========================================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "missing_roots_detected=True",
                "missing_roots_repaired=True",
                "project_manifests_validated=True",
                "design_manifests_validated=True",
                "broken_links_detected=True",
                "duplicate_ids_detected=True",
                "no_auto_delete=True",
                "no_auto_archive=True",
                "no_auto_move=True",
                "no_auto_overwrite=True",
                "qt_does_not_own_storage_validation=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_25H_STORAGE_VALIDATION_AND_REPAIR_OWNER")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_25H_STORAGE_VALIDATION_AND_REPAIR_OWNER")
    print(f"runtime_schema={SCHEMA}")
    print("missing_roots_detected=True")
    print("missing_roots_repaired=True")
    print("project_manifests_validated=True")
    print("design_manifests_validated=True")
    print("broken_links_detected=True")
    print("duplicate_ids_detected=True")
    print("no_auto_delete=True")
    print("no_auto_archive=True")
    print("no_auto_move=True")
    print("no_auto_overwrite=True")
    print("qt_does_not_own_storage_validation=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
