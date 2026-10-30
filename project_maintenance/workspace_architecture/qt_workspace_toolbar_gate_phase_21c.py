from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.production_historical_artifacts.leaf_qt.workspace_toolbar_phase_21c import (
    SCHEMA,
    build_workspace_toolbar_snapshot,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21c"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "workspace_toolbar_phase_21c.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "qt_workspace_toolbar_gate_phase_21c.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    snapshot = build_workspace_toolbar_snapshot(ROOT)
    summary = snapshot["summary"]

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if snapshot.get("source_action_model_schema") != "LEAF_WORKSPACE_ACTION_MODEL_PHASE_20C_V1":
        failures.append("source_action_model_schema_invalid")

    if summary.get("actions_bound") != 9:
        failures.append("actions_bound_invalid")

    if summary.get("enabled_actions") != 7:
        failures.append("enabled_actions_invalid")

    if summary.get("disabled_actions") != 2:
        failures.append("disabled_actions_invalid")

    if summary.get("panels_with_actions") != 6:
        failures.append("panels_with_actions_invalid")

    if summary.get("unsafe_enabled_actions") != 0:
        failures.append("unsafe_enabled_actions_detected")

    for key in [
        "presentation_only",
        "consumes_phase_20c_action_model",
        "disabled_actions_remain_disabled",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true={key}")

    for key in [
        "qt_owns_action_logic",
        "imports_files",
        "moves_files",
        "deletes_files",
        "archives_files",
        "automatic_import_allowed",
    ]:
        if summary.get(key) is not False:
            failures.append(f"unsafe_summary_not_false={key}")

    expected_actions = {
        "open_design",
        "save_design",
        "open_project",
        "open_report",
        "export_resource",
        "review_import_candidate",
        "approve_import_candidate",
        "execute_approved_import",
        "refresh_workspace",
    }

    if set(snapshot.get("action_ids", [])) != expected_actions:
        failures.append("action_ids_invalid")

    snapshot_path = OUT / "qt_workspace_toolbar_snapshot_phase_21c.json"
    gate_json = OUT / "qt_workspace_toolbar_gate_phase_21c.json"
    gate_txt = OUT / "qt_workspace_toolbar_gate_phase_21c.txt"

    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    result = {
        "phase": "21C",
        "feature": "QT_WORKSPACE_TOOLBAR",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": snapshot.get("schema"),
        "source_action_model_schema": snapshot.get("source_action_model_schema"),
        "summary": summary,
        "action_ids": snapshot.get("action_ids", []),
        "failures": failures,
        "snapshot_json": snapshot_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_21C_COMPLETE_QT_WORKSPACE_TOOLBAR_ESTABLISHED" if not failures else "PHASE_21C_BLOCKED",
        "next_phase": "21D_IMPORT_REVIEW_WINDOW",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 21C QT WORKSPACE TOOLBAR",
        "====================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_action_model_schema={result['source_action_model_schema']}",
        f"actions_bound={summary.get('actions_bound')}",
        f"enabled_actions={summary.get('enabled_actions')}",
        f"disabled_actions={summary.get('disabled_actions')}",
        f"panels_with_actions={summary.get('panels_with_actions')}",
        f"unsafe_enabled_actions={summary.get('unsafe_enabled_actions')}",
        f"presentation_only={summary.get('presentation_only')}",
        f"consumes_phase_20c_action_model={summary.get('consumes_phase_20c_action_model')}",
        f"qt_owns_action_logic={summary.get('qt_owns_action_logic')}",
        f"imports_files={summary.get('imports_files')}",
        f"moves_files={summary.get('moves_files')}",
        f"deletes_files={summary.get('deletes_files')}",
        f"archives_files={summary.get('archives_files')}",
        f"automatic_import_allowed={summary.get('automatic_import_allowed')}",
        f"disabled_actions_remain_disabled={summary.get('disabled_actions_remain_disabled')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"snapshot_json={result['snapshot_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_21C_QT_WORKSPACE_TOOLBAR" if result["passed"] else "FAIL_PHASE_21C_QT_WORKSPACE_TOOLBAR")
    print(f"schema={result['schema']}")
    print(f"source_action_model_schema={result['source_action_model_schema']}")
    print(f"actions_bound={summary.get('actions_bound')}")
    print(f"enabled_actions={summary.get('enabled_actions')}")
    print(f"disabled_actions={summary.get('disabled_actions')}")
    print(f"panels_with_actions={summary.get('panels_with_actions')}")
    print(f"unsafe_enabled_actions={summary.get('unsafe_enabled_actions')}")
    print(f"presentation_only={summary.get('presentation_only')}")
    print(f"consumes_phase_20c_action_model={summary.get('consumes_phase_20c_action_model')}")
    print(f"qt_owns_action_logic={summary.get('qt_owns_action_logic')}")
    print(f"disabled_actions_remain_disabled={summary.get('disabled_actions_remain_disabled')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"snapshot_json={result['snapshot_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
