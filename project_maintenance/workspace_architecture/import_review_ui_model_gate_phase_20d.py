from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from leaf_qt.workspace_runtime_core import (
    IMPORT_REVIEW_UI_SCHEMA as SCHEMA,
    build_import_review_ui_model,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_20d"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "import_review_ui_model_gate_phase_20d.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    model = build_import_review_ui_model(ROOT)
    summary = model["summary"]
    policy = model["execution_policy"]
    activation = model["activation_status"]

    expected_schemas = {
        "source_review_registry_schema": "LEAF_IMPORT_REVIEW_REGISTRY_PHASE_19B_V1",
        "source_safe_import_plan_schema": "LEAF_SAFE_IMPORT_PLAN_GENERATOR_PHASE_19C_V1",
        "source_action_model_schema": "LEAF_WORKSPACE_ACTION_MODEL_PHASE_20C_V1",
    }

    if model.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    for key, expected in expected_schemas.items():
        if model.get(key) != expected:
            failures.append(f"{key}_invalid")

    if activation.get("import_review_ui_model_ready") is not True:
        failures.append("import_review_ui_model_not_ready")

    if activation.get("ready_for_qt_table_binding") is not True:
        failures.append("not_ready_for_qt_table_binding")

    for key in [
        "approval_writeback_active",
        "controlled_import_execution_active",
        "automatic_import_active",
    ]:
        if activation.get(key) is not False:
            failures.append(f"activation_not_false={key}")

    for key in ["ui_model_only"]:
        if policy.get(key) is not True:
            failures.append(f"policy_not_true={key}")

    for key in [
        "qt_widgets_created",
        "approval_writeback_enabled",
        "execution_buttons_enabled",
        "imports_files",
        "copies_files",
        "moves_files",
        "deletes_files",
        "archives_files",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false={key}")

    if summary.get("review_rows") != summary.get("detail_records"):
        failures.append("row_detail_count_mismatch")

    if summary.get("approval_writeback_enabled") is not False:
        failures.append("approval_writeback_enabled")

    if summary.get("execution_buttons_enabled") is not False:
        failures.append("execution_buttons_enabled")

    if summary.get("developer_internal_fields_exposed") != 0:
        failures.append("developer_internal_fields_exposed")

    model_path = OUT / "import_review_ui_model_phase_20d.json"
    gate_json = OUT / "import_review_ui_model_gate_phase_20d.json"
    gate_txt = OUT / "import_review_ui_model_gate_phase_20d.txt"

    model_path.write_text(json.dumps(model, indent=2), encoding="utf-8")

    result = {
        "phase": "20D",
        "feature": "IMPORT_REVIEW_UI_MODEL",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": model.get("schema"),
        "summary": summary,
        "activation_status": activation,
        "failures": failures,
        "ui_model_json": model_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_20D_COMPLETE_IMPORT_REVIEW_UI_MODEL_ESTABLISHED" if not failures else "PHASE_20D_BLOCKED",
        "next_phase": "20E_SORTING_HEALTH_DASHBOARD_MODEL",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 20D IMPORT REVIEW UI MODEL",
        "======================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"table_columns={summary.get('table_columns')}",
        f"review_rows={summary.get('review_rows')}",
        f"detail_records={summary.get('detail_records')}",
        f"review_actions={summary.get('review_actions')}",
        f"approval_writeback_enabled={summary.get('approval_writeback_enabled')}",
        f"execution_buttons_enabled={summary.get('execution_buttons_enabled')}",
        f"ready_for_qt_binding={summary.get('ready_for_qt_binding')}",
        f"developer_internal_fields_exposed={summary.get('developer_internal_fields_exposed')}",
        f"automatic_import_active={activation.get('automatic_import_active')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"ui_model_json={result['ui_model_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_20D_IMPORT_REVIEW_UI_MODEL" if result["passed"] else "FAIL_PHASE_20D_IMPORT_REVIEW_UI_MODEL")
    print(f"schema={result['schema']}")
    print(f"table_columns={summary.get('table_columns')}")
    print(f"review_rows={summary.get('review_rows')}")
    print(f"detail_records={summary.get('detail_records')}")
    print(f"review_actions={summary.get('review_actions')}")
    print(f"approval_writeback_enabled={summary.get('approval_writeback_enabled')}")
    print(f"execution_buttons_enabled={summary.get('execution_buttons_enabled')}")
    print(f"ready_for_qt_binding={summary.get('ready_for_qt_binding')}")
    print(f"developer_internal_fields_exposed={summary.get('developer_internal_fields_exposed')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"ui_model_json={result['ui_model_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
