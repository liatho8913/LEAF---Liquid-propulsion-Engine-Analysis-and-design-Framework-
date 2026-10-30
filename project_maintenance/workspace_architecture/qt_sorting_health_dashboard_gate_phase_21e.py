from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.production_historical_artifacts.leaf_qt.sorting_health_dashboard_phase_21e import (
    SCHEMA,
    build_sorting_health_dashboard_snapshot,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21e"
OUT.mkdir(parents=True, exist_ok=True)

WORKSPACE_ARCHITECTURE = ROOT / "project_maintenance" / "workspace_architecture"

PHASE_20E_MODEL_CANDIDATES = sorted(
    path for path in WORKSPACE_ARCHITECTURE.glob("*20e*.py")
    if "dashboard" in path.name.lower() or "sorting" in path.name.lower()
)

MODULES = [
    *PHASE_20E_MODEL_CANDIDATES,
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "sorting_health_dashboard_phase_21e.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "qt_sorting_health_dashboard_gate_phase_21e.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    snapshot = build_sorting_health_dashboard_snapshot(ROOT)
    summary = snapshot["summary"]

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if not snapshot.get("source_sorting_dashboard_model_schema"):
        failures.append("source_sorting_dashboard_model_schema_missing")

    for key in [
        "presentation_only",
        "consumes_phase_20e_dashboard_model",
        "read_only_dashboard",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true={key}")

    for key in [
        "qt_owns_sorting_logic",
        "automatic_import_active",
        "execution_allowed",
        "imports_files",
        "copies_files",
        "moves_files",
        "deletes_files",
        "archives_files",
    ]:
        if summary.get(key) is not False:
            failures.append(f"unsafe_summary_not_false={key}")

    if summary.get("model_keys_available", 0) <= 0:
        failures.append("model_keys_available_invalid")

    snapshot_path = OUT / "qt_sorting_health_dashboard_snapshot_phase_21e.json"
    gate_json = OUT / "qt_sorting_health_dashboard_gate_phase_21e.json"
    gate_txt = OUT / "qt_sorting_health_dashboard_gate_phase_21e.txt"

    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    result = {
        "phase": "21E",
        "feature": "QT_SORTING_HEALTH_DASHBOARD",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": snapshot.get("schema"),
        "source_sorting_dashboard_model_schema": snapshot.get("source_sorting_dashboard_model_schema"),
        "summary": summary,
        "failures": failures,
        "snapshot_json": snapshot_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_21E_COMPLETE_SORTING_HEALTH_DASHBOARD_ESTABLISHED" if not failures else "PHASE_21E_BLOCKED",
        "next_phase": "21F_WORKSPACE_MAIN_WINDOW_INTEGRATION",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 21E SORTING HEALTH DASHBOARD",
        "=======================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_sorting_dashboard_model_schema={result['source_sorting_dashboard_model_schema']}",
        f"presentation_only={summary.get('presentation_only')}",
        f"consumes_phase_20e_dashboard_model={summary.get('consumes_phase_20e_dashboard_model')}",
        f"qt_owns_sorting_logic={summary.get('qt_owns_sorting_logic')}",
        f"read_only_dashboard={summary.get('read_only_dashboard')}",
        f"automatic_import_active={summary.get('automatic_import_active')}",
        f"execution_allowed={summary.get('execution_allowed')}",
        f"imports_files={summary.get('imports_files')}",
        f"copies_files={summary.get('copies_files')}",
        f"moves_files={summary.get('moves_files')}",
        f"deletes_files={summary.get('deletes_files')}",
        f"archives_files={summary.get('archives_files')}",
        f"model_sections_available={summary.get('model_sections_available')}",
        f"model_keys_available={summary.get('model_keys_available')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"snapshot_json={result['snapshot_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_21E_SORTING_HEALTH_DASHBOARD" if result["passed"] else "FAIL_PHASE_21E_SORTING_HEALTH_DASHBOARD")
    print(f"schema={result['schema']}")
    print(f"source_sorting_dashboard_model_schema={result['source_sorting_dashboard_model_schema']}")
    print(f"presentation_only={summary.get('presentation_only')}")
    print(f"consumes_phase_20e_dashboard_model={summary.get('consumes_phase_20e_dashboard_model')}")
    print(f"qt_owns_sorting_logic={summary.get('qt_owns_sorting_logic')}")
    print(f"read_only_dashboard={summary.get('read_only_dashboard')}")
    print(f"automatic_import_active={summary.get('automatic_import_active')}")
    print(f"execution_allowed={summary.get('execution_allowed')}")
    print(f"model_sections_available={summary.get('model_sections_available')}")
    print(f"model_keys_available={summary.get('model_keys_available')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"snapshot_json={result['snapshot_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
