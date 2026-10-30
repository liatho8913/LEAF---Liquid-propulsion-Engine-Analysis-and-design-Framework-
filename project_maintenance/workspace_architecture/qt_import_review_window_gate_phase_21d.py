from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.production_historical_artifacts.leaf_qt.import_review_window_phase_21d import (
    SCHEMA,
    build_import_review_window_snapshot,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21d"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "import_review_window_phase_21d.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "qt_import_review_window_gate_phase_21d.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    snapshot = build_import_review_window_snapshot(ROOT)
    summary = snapshot["summary"]

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if snapshot.get("source_import_review_ui_model_schema") != "LEAF_IMPORT_REVIEW_UI_MODEL_PHASE_20D_V1":
        failures.append("source_import_review_ui_model_schema_invalid")

    if summary.get("table_columns_bound") != 8:
        failures.append("table_columns_bound_invalid")

    if summary.get("review_rows_bound") != summary.get("detail_records_bound"):
        failures.append("review_rows_detail_records_mismatch")

    if summary.get("developer_internal_fields_exposed") != 0:
        failures.append("developer_internal_fields_exposed")

    for key in [
        "presentation_only",
        "consumes_phase_20d_import_review_ui_model",
        "ready_for_qt_binding",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true={key}")

    for key in [
        "qt_owns_review_logic",
        "table_editable",
        "approval_writeback_enabled",
        "execution_buttons_enabled",
        "automatic_import_active",
        "imports_files",
        "copies_files",
        "moves_files",
        "deletes_files",
        "archives_files",
    ]:
        if summary.get(key) is not False:
            failures.append(f"unsafe_summary_not_false={key}")

    snapshot_path = OUT / "qt_import_review_window_snapshot_phase_21d.json"
    gate_json = OUT / "qt_import_review_window_gate_phase_21d.json"
    gate_txt = OUT / "qt_import_review_window_gate_phase_21d.txt"

    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    result = {
        "phase": "21D",
        "feature": "QT_IMPORT_REVIEW_WINDOW",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": snapshot.get("schema"),
        "source_import_review_ui_model_schema": snapshot.get("source_import_review_ui_model_schema"),
        "summary": summary,
        "failures": failures,
        "snapshot_json": snapshot_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_21D_COMPLETE_IMPORT_REVIEW_WINDOW_ESTABLISHED" if not failures else "PHASE_21D_BLOCKED",
        "next_phase": "21E_SORTING_HEALTH_DASHBOARD",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 21D IMPORT REVIEW WINDOW",
        "===================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_import_review_ui_model_schema={result['source_import_review_ui_model_schema']}",
        f"table_columns_bound={summary.get('table_columns_bound')}",
        f"review_rows_bound={summary.get('review_rows_bound')}",
        f"detail_records_bound={summary.get('detail_records_bound')}",
        f"review_actions_visible={summary.get('review_actions_visible')}",
        f"presentation_only={summary.get('presentation_only')}",
        f"consumes_phase_20d_import_review_ui_model={summary.get('consumes_phase_20d_import_review_ui_model')}",
        f"qt_owns_review_logic={summary.get('qt_owns_review_logic')}",
        f"table_editable={summary.get('table_editable')}",
        f"approval_writeback_enabled={summary.get('approval_writeback_enabled')}",
        f"execution_buttons_enabled={summary.get('execution_buttons_enabled')}",
        f"automatic_import_active={summary.get('automatic_import_active')}",
        f"imports_files={summary.get('imports_files')}",
        f"copies_files={summary.get('copies_files')}",
        f"moves_files={summary.get('moves_files')}",
        f"deletes_files={summary.get('deletes_files')}",
        f"archives_files={summary.get('archives_files')}",
        f"developer_internal_fields_exposed={summary.get('developer_internal_fields_exposed')}",
        f"ready_for_qt_binding={summary.get('ready_for_qt_binding')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"snapshot_json={result['snapshot_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_21D_IMPORT_REVIEW_WINDOW" if result["passed"] else "FAIL_PHASE_21D_IMPORT_REVIEW_WINDOW")
    print(f"schema={result['schema']}")
    print(f"source_import_review_ui_model_schema={result['source_import_review_ui_model_schema']}")
    print(f"table_columns_bound={summary.get('table_columns_bound')}")
    print(f"review_rows_bound={summary.get('review_rows_bound')}")
    print(f"detail_records_bound={summary.get('detail_records_bound')}")
    print(f"review_actions_visible={summary.get('review_actions_visible')}")
    print(f"presentation_only={summary.get('presentation_only')}")
    print(f"consumes_phase_20d_import_review_ui_model={summary.get('consumes_phase_20d_import_review_ui_model')}")
    print(f"qt_owns_review_logic={summary.get('qt_owns_review_logic')}")
    print(f"approval_writeback_enabled={summary.get('approval_writeback_enabled')}")
    print(f"execution_buttons_enabled={summary.get('execution_buttons_enabled')}")
    print(f"automatic_import_active={summary.get('automatic_import_active')}")
    print(f"ready_for_qt_binding={summary.get('ready_for_qt_binding')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"snapshot_json={result['snapshot_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
