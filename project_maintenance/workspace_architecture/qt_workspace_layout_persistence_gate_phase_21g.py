from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.production_historical_artifacts.leaf_qt.workspace_main_window_phase_21f import build_workspace_main_window_snapshot
from leaf_qt.workspace_layout_persistence import (
    SCHEMA,
    WorkspaceLayoutPersistence,
    build_workspace_layout_persistence_snapshot,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21g"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_layout_persistence.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "workspace_main_window_phase_21f.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "qt_workspace_layout_persistence_gate_phase_21g.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    owner = WorkspaceLayoutPersistence(ROOT)

    save_result = owner.save_layout(
        geometry_bytes=b"phase_21g_geometry_test",
        window_state_bytes=b"phase_21g_state_test",
        splitter_sizes=[310, 1140],
        selected_panel="Designs",
    )

    loaded = owner.load_layout()
    persistence_snapshot = build_workspace_layout_persistence_snapshot(ROOT)
    main_window_snapshot = build_workspace_main_window_snapshot(ROOT)

    persistence_summary = persistence_snapshot["summary"]
    main_summary = main_window_snapshot["summary"]

    if persistence_snapshot.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if not save_result.saved:
        failures.append("save_result_not_saved")

    if loaded.get("valid") is not True:
        failures.append("saved_layout_not_valid")

    if loaded.get("geometry_bytes") != b"phase_21g_geometry_test":
        failures.append("geometry_roundtrip_failed")

    if loaded.get("window_state_bytes") != b"phase_21g_state_test":
        failures.append("window_state_roundtrip_failed")

    if loaded.get("splitter_sizes") != [310, 1140]:
        failures.append("splitter_sizes_roundtrip_failed")

    for key in [
        "presentation_state_only",
    ]:
        if persistence_summary.get(key) is not True:
            failures.append(f"persistence_summary_not_true={key}")

    for key in [
        "stores_engineering_data",
        "stores_repository_intelligence",
        "stores_sorting_execution_state",
        "stores_import_approval_state",
        "imports_files",
        "copies_files",
        "moves_files",
        "deletes_files",
        "archives_files",
        "automatic_import_allowed",
    ]:
        if persistence_summary.get(key) is not False:
            failures.append(f"unsafe_persistence_summary_not_false={key}")

    for key in [
        "integrates_phase_21g_layout_persistence",
        "layout_persistence_presentation_only",
    ]:
        if main_summary.get(key) is not True:
            failures.append(f"main_window_summary_not_true={key}")

    snapshot = {
        "schema": SCHEMA,
        "phase": "21G",
        "feature": "WORKSPACE_LAYOUT_PERSISTENCE",
        "persistence_snapshot": persistence_snapshot,
        "main_window_snapshot": main_window_snapshot,
        "loaded_layout_valid": loaded.get("valid"),
    }

    snapshot_path = OUT / "workspace_layout_persistence_snapshot_phase_21g.json"
    gate_json = OUT / "workspace_layout_persistence_gate_phase_21g.json"
    gate_txt = OUT / "workspace_layout_persistence_gate_phase_21g.txt"

    snapshot_path.write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")

    result = {
        "phase": "21G",
        "feature": "WORKSPACE_LAYOUT_PERSISTENCE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "summary": {
            **persistence_summary,
            "integrates_phase_21g_layout_persistence": main_summary.get("integrates_phase_21g_layout_persistence"),
            "layout_persistence_presentation_only": main_summary.get("layout_persistence_presentation_only"),
        },
        "failures": failures,
        "snapshot_json": snapshot_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_21G_COMPLETE_WORKSPACE_LAYOUT_PERSISTENCE_ESTABLISHED" if not failures else "PHASE_21G_BLOCKED",
        "next_phase": "21H_WORKSPACE_COMPLETION_GATE",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    s = result["summary"]

    gate_txt.write_text("\n".join([
        "LEAF PHASE 21G WORKSPACE LAYOUT PERSISTENCE",
        "===========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"owner_class={s.get('owner_class')}",
        f"layout_path={s.get('layout_path')}",
        f"layout_file_exists={s.get('layout_file_exists')}",
        f"loaded_layout_valid={s.get('loaded_layout_valid')}",
        f"presentation_state_only={s.get('presentation_state_only')}",
        f"stores_engineering_data={s.get('stores_engineering_data')}",
        f"stores_repository_intelligence={s.get('stores_repository_intelligence')}",
        f"stores_sorting_execution_state={s.get('stores_sorting_execution_state')}",
        f"stores_import_approval_state={s.get('stores_import_approval_state')}",
        f"integrates_phase_21g_layout_persistence={s.get('integrates_phase_21g_layout_persistence')}",
        f"layout_persistence_presentation_only={s.get('layout_persistence_presentation_only')}",
        f"imports_files={s.get('imports_files')}",
        f"moves_files={s.get('moves_files')}",
        f"deletes_files={s.get('deletes_files')}",
        f"archives_files={s.get('archives_files')}",
        f"automatic_import_allowed={s.get('automatic_import_allowed')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"snapshot_json={result['snapshot_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_21G_WORKSPACE_LAYOUT_PERSISTENCE" if result["passed"] else "FAIL_PHASE_21G_WORKSPACE_LAYOUT_PERSISTENCE")
    print(f"schema={result['schema']}")
    print(f"owner_class={s.get('owner_class')}")
    print(f"layout_path={s.get('layout_path')}")
    print(f"layout_file_exists={s.get('layout_file_exists')}")
    print(f"loaded_layout_valid={s.get('loaded_layout_valid')}")
    print(f"presentation_state_only={s.get('presentation_state_only')}")
    print(f"stores_engineering_data={s.get('stores_engineering_data')}")
    print(f"stores_repository_intelligence={s.get('stores_repository_intelligence')}")
    print(f"stores_sorting_execution_state={s.get('stores_sorting_execution_state')}")
    print(f"stores_import_approval_state={s.get('stores_import_approval_state')}")
    print(f"integrates_phase_21g_layout_persistence={s.get('integrates_phase_21g_layout_persistence')}")
    print(f"layout_persistence_presentation_only={s.get('layout_persistence_presentation_only')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"snapshot_json={result['snapshot_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
