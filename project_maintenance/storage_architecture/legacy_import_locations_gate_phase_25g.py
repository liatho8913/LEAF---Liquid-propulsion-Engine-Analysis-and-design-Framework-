from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "storage_architecture" / "phase_25g"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "storage" / "__init__.py",
    ROOT / "leaf_qt" / "storage" / "canonical_storage.py",
    ROOT / "leaf_qt" / "storage" / "project_manifest.py",
    ROOT / "leaf_qt" / "storage" / "design_manifest.py",
    ROOT / "leaf_qt" / "storage" / "creation_owner.py",
    ROOT / "leaf_qt" / "storage" / "save_load_bridge.py",
    ROOT / "leaf_qt" / "storage" / "legacy_import_locations.py",
]

from leaf_qt.storage.legacy_import_locations import (
    DEFAULT_LEGACY_SEARCH_ROOTS,
    SCHEMA,
    LegacyImportSearchLocations,
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

    owner = LegacyImportSearchLocations(ROOT)
    locations = owner.locations()

    if len(locations) != len(DEFAULT_LEGACY_SEARCH_ROOTS):
        failures.append("legacy_location_count_invalid")

    for location in locations:
        if location.import_only is not True:
            failures.append(f"legacy_location_not_import_only:{location.root_name}")

        if location.authoritative is not False:
            failures.append(f"legacy_location_marked_authoritative:{location.root_name}")

        if location.auto_delete_enabled is not False:
            failures.append(f"legacy_location_auto_delete_enabled:{location.root_name}")

        if location.auto_archive_enabled is not False:
            failures.append(f"legacy_location_auto_archive_enabled:{location.root_name}")

        if not owner.is_legacy_import_only(f"{location.root_name}/example.py"):
            failures.append(f"legacy_path_not_recognised:{location.root_name}")

    canonical_design = owner.classify_path("LEAF_Designs/test_design/design.leaf_design.json")

    if canonical_design.get("authoritative_storage") is not True:
        failures.append("canonical_design_not_authoritative")

    if canonical_design.get("legacy_import_only") is not False:
        failures.append("canonical_design_marked_legacy")

    legacy_leaf_qt = owner.classify_path("leaf_qt/saved_designs/old_design.json")

    if legacy_leaf_qt.get("legacy_import_only") is not True:
        failures.append("legacy_leaf_qt_not_import_only")

    if legacy_leaf_qt.get("authoritative_storage") is not False:
        failures.append("legacy_leaf_qt_marked_authoritative")

    quarantine = owner.classify_path("_external_repository_quarantine/old_repo/file.py")

    if quarantine.get("legacy_import_only") is not True:
        failures.append("quarantine_not_import_only")

    if quarantine.get("safe_for_auto_delete") is not False:
        failures.append("quarantine_auto_delete_enabled")

    unknown = owner.classify_path("random_unknown_folder/file.py")

    if unknown.get("authoritative_storage") is not False:
        failures.append("unknown_marked_authoritative")

    if unknown.get("legacy_import_only") is not False:
        failures.append("unknown_marked_legacy")

    snapshot = owner.snapshot()

    required_snapshot_keys = [
        "schema",
        "legacy_locations",
        "canonical_roots",
        "legacy_import_only_roots",
        "legacy_storage_authoritative",
        "quarantine_storage_authoritative",
        "leaf_qt_storage_authoritative",
        "project_evidence_authoritative",
        "auto_delete_enabled",
        "auto_archive_enabled",
        "moves_files",
        "deletes_files",
        "archives_files",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    for key in [
        "legacy_storage_authoritative",
        "quarantine_storage_authoritative",
        "leaf_qt_storage_authoritative",
        "project_evidence_authoritative",
        "auto_delete_enabled",
        "auto_archive_enabled",
        "moves_files",
        "deletes_files",
        "archives_files",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"legacy_boundary_invalid:{key}")

    result = {
        "phase": "25G",
        "programme": "25",
        "feature": "LEGACY_IMPORT_SEARCH_LOCATIONS",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_LEGACY_IMPORT_SEARCH_LOCATIONS_GATE_PHASE_25G_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/storage/legacy_import_locations.py",
            "project_maintenance/storage_architecture/legacy_import_locations_gate_phase_25g.py",
        ],
        "files_replaced": [
            "leaf_qt/storage/__init__.py",
        ],
        "files_removed": [],
        "validated": {
            "leaf_qt_import_only": True,
            "project_evidence_import_only": True,
            "cleanup_candidates_import_only": True,
            "external_quarantine_import_only": True,
            "canonical_storage_authoritative": True,
            "legacy_storage_not_authoritative": True,
            "auto_delete_disabled": True,
            "auto_archive_disabled": True,
            "no_file_moves": True,
            "no_file_deletes": True,
            "no_file_archives": True,
        },
        "completion_notice": (
            "PHASE_25G_COMPLETE_LEGACY_IMPORT_SEARCH_LOCATIONS_ESTABLISHED"
            if not failures
            else "PHASE_25G_BLOCKED"
        ),
        "next_phase": "25H_STORAGE_VALIDATION_AND_REPAIR_OWNER",
    }

    json_path = OUT / "legacy_import_locations_gate_phase_25g.json"
    txt_path = OUT / "legacy_import_locations_gate_phase_25g.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 25G LEGACY IMPORT SEARCH LOCATIONS GATE",
                "======================================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "leaf_qt_import_only=True",
                "project_evidence_import_only=True",
                "cleanup_candidates_import_only=True",
                "external_quarantine_import_only=True",
                "canonical_storage_authoritative=True",
                "legacy_storage_not_authoritative=True",
                "auto_delete_disabled=True",
                "auto_archive_disabled=True",
                "no_file_moves=True",
                "no_file_deletes=True",
                "no_file_archives=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_25G_LEGACY_IMPORT_SEARCH_LOCATIONS")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_25G_LEGACY_IMPORT_SEARCH_LOCATIONS")
    print(f"runtime_schema={SCHEMA}")
    print("leaf_qt_import_only=True")
    print("project_evidence_import_only=True")
    print("cleanup_candidates_import_only=True")
    print("external_quarantine_import_only=True")
    print("canonical_storage_authoritative=True")
    print("legacy_storage_not_authoritative=True")
    print("auto_delete_disabled=True")
    print("auto_archive_disabled=True")
    print("no_file_moves=True")
    print("no_file_deletes=True")
    print("no_file_archives=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
