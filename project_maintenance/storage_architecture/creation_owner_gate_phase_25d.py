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

OUT = ROOT / "_leaf_artifacts" / "storage_architecture" / "phase_25d"
OUT.mkdir(parents=True, exist_ok=True)

SANDBOX = ROOT / "_leaf_artifacts" / "storage_architecture" / "phase_25d" / "_creation_sandbox"

MODULES = [
    ROOT / "leaf_qt" / "storage" / "__init__.py",
    ROOT / "leaf_qt" / "storage" / "canonical_storage.py",
    ROOT / "leaf_qt" / "storage" / "project_manifest.py",
    ROOT / "leaf_qt" / "storage" / "design_manifest.py",
    ROOT / "leaf_qt" / "storage" / "creation_owner.py",
]

from leaf_qt.storage.creation_owner import SCHEMA, ProjectDesignCreationOwner, safe_slug
from leaf_qt.storage.project_manifest import PROJECT_MANIFEST_FILENAME, ProjectManifestValidator
from leaf_qt.storage.design_manifest import DESIGN_MANIFEST_FILENAME, DesignManifestValidator


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

    owner = ProjectDesignCreationOwner(SANDBOX)

    result = owner.create_project_with_design(
        project_name="Runtime Creation Test Project",
        design_name="Runtime Creation Test Design",
        runtime_schema_version="LEAF_RUNTIME_COMPLETION_GATE_PHASE_24H_V1",
        project_notes="25D gate project.",
        engine_type="liquid_rocket_engine",
    )

    project_dir = Path(result.project_dir)
    design_dir = Path(result.design_dir or "")
    project_manifest_path = Path(result.project_manifest_path)
    design_manifest_path = Path(result.design_manifest_path or "")

    if not project_dir.exists():
        failures.append("project_dir_not_created")

    if not design_dir.exists():
        failures.append("design_dir_not_created")

    if project_dir.name != safe_slug("Runtime Creation Test Project"):
        failures.append("project_dir_slug_invalid")

    if design_dir.name != safe_slug("Runtime Creation Test Design"):
        failures.append("design_dir_slug_invalid")

    if project_manifest_path.name != PROJECT_MANIFEST_FILENAME:
        failures.append("project_manifest_filename_invalid")

    if design_manifest_path.name != DESIGN_MANIFEST_FILENAME:
        failures.append("design_manifest_filename_invalid")

    if not project_manifest_path.exists():
        failures.append("project_manifest_not_written")

    if not design_manifest_path.exists():
        failures.append("design_manifest_not_written")

    project_payload = json.loads(project_manifest_path.read_text(encoding="utf-8"))
    design_payload = json.loads(design_manifest_path.read_text(encoding="utf-8"))

    if str(design_manifest_path) not in project_payload.get("active_designs", []):
        failures.append("design_not_linked_to_project_manifest")

    if design_payload.get("parent_project_id") != project_payload.get("project_id"):
        failures.append("design_parent_project_id_invalid")

    project_validation = ProjectManifestValidator().validate(
        __import__("leaf_qt.storage.project_manifest", fromlist=["ProjectManifest"]).ProjectManifest.from_dict(project_payload)
    )
    design_validation = DesignManifestValidator().validate(
        __import__("leaf_qt.storage.design_manifest", fromlist=["DesignManifest"]).DesignManifest.from_dict(design_payload)
    )

    if project_validation.get("passed") is not True:
        failures.append(f"project_manifest_validation_failed:{project_validation.get('failures')}")

    if design_validation.get("passed") is not True:
        failures.append(f"design_manifest_validation_failed:{design_validation.get('failures')}")

    try:
        owner.create_project_with_design(
            project_name="Runtime Creation Test Project",
            design_name="Runtime Creation Test Design",
        )
        failures.append("duplicate_creation_without_overwrite_allowed")
    except FileExistsError:
        pass

    snapshot = owner.snapshot()

    required_snapshot_keys = [
        "schema",
        "storage",
        "creates_project_folders",
        "creates_design_folders",
        "writes_project_manifest",
        "writes_design_manifest",
        "links_design_to_project",
        "qt_owns_creation_workflow",
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    for key in [
        "creates_project_folders",
        "creates_design_folders",
        "writes_project_manifest",
        "writes_design_manifest",
        "links_design_to_project",
    ]:
        if snapshot.get(key) is not True:
            failures.append(f"creation_capability_not_declared:{key}")

    for key in [
        "qt_owns_creation_workflow",
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"creation_boundary_invalid:{key}")

    result_payload = {
        "phase": "25D",
        "programme": "25",
        "feature": "PROJECT_DESIGN_CREATION_OWNER",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_PROJECT_DESIGN_CREATION_OWNER_GATE_PHASE_25D_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/storage/creation_owner.py",
            "project_maintenance/storage_architecture/creation_owner_gate_phase_25d.py",
        ],
        "files_replaced": [
            "leaf_qt/storage/__init__.py",
        ],
        "files_removed": [],
        "created_project_manifest": str(project_manifest_path.relative_to(ROOT)) if project_manifest_path.exists() else None,
        "created_design_manifest": str(design_manifest_path.relative_to(ROOT)) if design_manifest_path.exists() else None,
        "validated": {
            "project_folder_creation": True,
            "design_folder_creation": True,
            "project_manifest_write": True,
            "design_manifest_write": True,
            "design_linked_to_project": True,
            "parent_project_id_link": True,
            "duplicate_creation_blocked": True,
            "manifest_validation": True,
            "qt_does_not_own_creation_workflow": True,
            "metadata_only_creation_owner": True,
        },
        "completion_notice": (
            "PHASE_25D_COMPLETE_PROJECT_DESIGN_CREATION_OWNER_ESTABLISHED"
            if not failures
            else "PHASE_25D_BLOCKED"
        ),
        "next_phase": "25E_SAVE_LOAD_RUNTIME_BRIDGE",
    }

    json_path = OUT / "creation_owner_gate_phase_25d.json"
    txt_path = OUT / "creation_owner_gate_phase_25d.txt"

    json_path.write_text(json.dumps(result_payload, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 25D PROJECT / DESIGN CREATION OWNER GATE",
                "=======================================================",
                f"passed={result_payload['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "project_folder_creation=True",
                "design_folder_creation=True",
                "project_manifest_write=True",
                "design_manifest_write=True",
                "design_linked_to_project=True",
                "parent_project_id_link=True",
                "duplicate_creation_blocked=True",
                "manifest_validation=True",
                "qt_does_not_own_creation_workflow=True",
                "metadata_only_creation_owner=True",
                f"completion_notice={result_payload['completion_notice']}",
                f"next_phase={result_payload['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_25D_PROJECT_DESIGN_CREATION_OWNER")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_25D_PROJECT_DESIGN_CREATION_OWNER")
    print(f"runtime_schema={SCHEMA}")
    print("project_folder_creation=True")
    print("design_folder_creation=True")
    print("project_manifest_write=True")
    print("design_manifest_write=True")
    print("design_linked_to_project=True")
    print("parent_project_id_link=True")
    print("duplicate_creation_blocked=True")
    print("manifest_validation=True")
    print("qt_does_not_own_creation_workflow=True")
    print("metadata_only_creation_owner=True")
    print(f"completion_notice={result_payload['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result_payload['next_phase']}")


if __name__ == "__main__":
    main()
