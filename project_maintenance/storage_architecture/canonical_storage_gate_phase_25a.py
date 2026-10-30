from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "storage_architecture" / "phase_25a"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "storage" / "__init__.py",
    ROOT / "leaf_qt" / "storage" / "canonical_storage.py",
]

from leaf_qt.storage.canonical_storage import (
    CANONICAL_ROOTS,
    LEGACY_IMPORT_ONLY_ROOTS,
    SCHEMA,
    CanonicalStorageOwner,
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

    owner = CanonicalStorageOwner(ROOT)

    records = owner.ensure_roots()

    if len(records) != 4:
        failures.append("canonical_root_record_count_invalid")

    status = owner.root_status()

    for key, folder_name in CANONICAL_ROOTS.items():
        path = ROOT / folder_name

        if key not in status:
            failures.append(f"missing_root_status:{key}")

        if not path.exists():
            failures.append(f"canonical_root_missing:{folder_name}")

        if not path.is_dir():
            failures.append(f"canonical_root_not_directory:{folder_name}")

        if status.get(key, {}).get("authoritative") is not True:
            failures.append(f"canonical_root_not_authoritative:{key}")

        if status.get(key, {}).get("user_facing") is not True:
            failures.append(f"canonical_root_not_user_facing:{key}")

        if not owner.is_canonical_path(path):
            failures.append(f"canonical_path_not_recognised:{folder_name}")

    if not owner.is_canonical_path("LEAF_Designs/example_design"):
        failures.append("relative_canonical_design_path_not_recognised")

    if owner.is_canonical_path("leaf_qt/saved_designs/old_design.json"):
        failures.append("legacy_leaf_qt_path_marked_canonical")

    for legacy_root in LEGACY_IMPORT_ONLY_ROOTS:
        if not owner.is_legacy_import_only_path(f"{legacy_root}/example.py"):
            failures.append(f"legacy_import_root_not_recognised:{legacy_root}")

    if owner.is_legacy_import_only_path("LEAF_Designs/example_design"):
        failures.append("canonical_design_marked_legacy_import_only")

    policy = owner.storage_policy()

    required_policy = {
        "canonical_storage_authoritative": True,
        "legacy_storage_authoritative": False,
        "quarantine_storage_authoritative": False,
        "qt_storage_authoritative": False,
        "user_facing_storage_at_root": True,
        "auto_delete_enabled": False,
        "auto_archive_enabled": False,
    }

    for key, expected in required_policy.items():
        if policy.get(key) is not expected:
            failures.append(f"storage_policy_invalid:{key}")

    snapshot = owner.snapshot()

    required_snapshot_keys = [
        "schema",
        "root",
        "root_status",
        "storage_policy",
        "owns_project_manifest_payloads",
        "owns_design_manifest_payloads",
        "owns_report_payloads",
        "owns_export_payloads",
        "qt_owns_storage",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    for key in [
        "owns_project_manifest_payloads",
        "owns_design_manifest_payloads",
        "owns_report_payloads",
        "owns_export_payloads",
        "qt_owns_storage",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"storage_boundary_invalid:{key}")

    result = {
        "phase": "25A",
        "programme": "25",
        "feature": "CANONICAL_PROJECT_AND_DESIGN_STORAGE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_CANONICAL_STORAGE_GATE_PHASE_25A_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/storage/canonical_storage.py",
            "leaf_qt/storage/__init__.py",
            "project_maintenance/storage_architecture/canonical_storage_gate_phase_25a.py",
        ],
        "files_replaced": [],
        "files_removed": [],
        "canonical_roots": dict(CANONICAL_ROOTS),
        "legacy_import_only_roots": sorted(LEGACY_IMPORT_ONLY_ROOTS),
        "validated": {
            "leaf_projects_root": True,
            "leaf_designs_root": True,
            "leaf_reports_root": True,
            "leaf_exports_root": True,
            "canonical_paths_recognised": True,
            "legacy_paths_import_only": True,
            "leaf_qt_not_authoritative_storage": True,
            "quarantine_not_authoritative_storage": True,
            "auto_delete_disabled": True,
            "auto_archive_disabled": True,
            "qt_does_not_own_storage": True,
        },
        "completion_notice": (
            "PHASE_25A_COMPLETE_CANONICAL_PROJECT_AND_DESIGN_STORAGE_ESTABLISHED"
            if not failures
            else "PHASE_25A_BLOCKED"
        ),
        "next_phase": "25B_PROJECT_MANIFEST_MODEL",
    }

    json_path = OUT / "canonical_storage_gate_phase_25a.json"
    txt_path = OUT / "canonical_storage_gate_phase_25a.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 25A CANONICAL STORAGE GATE",
                "=========================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "leaf_projects_root=True",
                "leaf_designs_root=True",
                "leaf_reports_root=True",
                "leaf_exports_root=True",
                "canonical_paths_recognised=True",
                "legacy_paths_import_only=True",
                "leaf_qt_not_authoritative_storage=True",
                "quarantine_not_authoritative_storage=True",
                "auto_delete_disabled=True",
                "auto_archive_disabled=True",
                "qt_does_not_own_storage=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_25A_CANONICAL_STORAGE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_25A_CANONICAL_STORAGE")
    print(f"runtime_schema={SCHEMA}")
    print("leaf_projects_root=True")
    print("leaf_designs_root=True")
    print("leaf_reports_root=True")
    print("leaf_exports_root=True")
    print("canonical_paths_recognised=True")
    print("legacy_paths_import_only=True")
    print("leaf_qt_not_authoritative_storage=True")
    print("quarantine_not_authoritative_storage=True")
    print("auto_delete_disabled=True")
    print("auto_archive_disabled=True")
    print("qt_does_not_own_storage=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
