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
    ACTION_MODEL_SCHEMA as SCHEMA,
    build_workspace_action_model,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_20c"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_action_model_gate_phase_20c.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    model = build_workspace_action_model(ROOT)
    summary = model["summary"]
    policy = model["execution_policy"]
    activation = model["activation_status"]

    if model.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if model.get("source_panel_provider_schema") != "LEAF_WORKSPACE_PANEL_DATA_PROVIDERS_PHASE_20B_V1":
        failures.append("source_panel_provider_schema_invalid")

    if activation.get("action_model_ready") is not True:
        failures.append("action_model_not_ready")

    if activation.get("ready_for_qt_action_binding") is not True:
        failures.append("not_ready_for_qt_action_binding")

    for key in [
        "approval_writeback_active",
        "controlled_import_execution_active",
        "automatic_import_active",
    ]:
        if activation.get(key) is not False:
            failures.append(f"activation_not_false={key}")

    for key in ["model_only"]:
        if policy.get(key) is not True:
            failures.append(f"policy_not_true={key}")

    for key in [
        "qt_widgets_created",
        "automatic_import_allowed",
        "automatic_delete_allowed",
        "automatic_move_allowed",
        "automatic_archive_allowed",
        "dangerous_actions_enabled",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false={key}")

    if summary.get("actions", 0) < 8:
        failures.append("action_count_too_low")

    if summary.get("unsafe_enabled_actions") != 0:
        failures.append("unsafe_enabled_actions_nonzero")

    for action_id, action in model.get("actions", {}).items():
        if action.get("action_type") in {"CONTROLLED_COPY_IMPORT", "DELETE_RESOURCE", "MOVE_RESOURCE", "ARCHIVE_RESOURCE"}:
            if action.get("enabled") is not False:
                failures.append(f"dangerous_action_enabled={action_id}")

    model_path = OUT / "workspace_action_model_phase_20c.json"
    gate_json = OUT / "workspace_action_model_gate_phase_20c.json"
    gate_txt = OUT / "workspace_action_model_gate_phase_20c.txt"

    model_path.write_text(json.dumps(model, indent=2), encoding="utf-8")

    result = {
        "phase": "20C",
        "feature": "WORKSPACE_OPEN_SAVE_IMPORT_ACTION_MODEL",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": model.get("schema"),
        "source_panel_provider_schema": model.get("source_panel_provider_schema"),
        "summary": summary,
        "activation_status": activation,
        "failures": failures,
        "action_model_json": model_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_20C_COMPLETE_WORKSPACE_OPEN_SAVE_IMPORT_ACTION_MODEL_ESTABLISHED" if not failures else "PHASE_20C_BLOCKED",
        "next_phase": "20D_IMPORT_REVIEW_UI_MODEL",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 20C WORKSPACE OPEN SAVE IMPORT ACTION MODEL",
        "=======================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_panel_provider_schema={result['source_panel_provider_schema']}",
        f"actions={summary.get('actions')}",
        f"enabled_actions={summary.get('enabled_actions')}",
        f"disabled_actions={summary.get('disabled_actions')}",
        f"panels_with_actions={summary.get('panels_with_actions')}",
        f"unsafe_enabled_actions={summary.get('unsafe_enabled_actions')}",
        f"ready_for_qt_binding={summary.get('ready_for_qt_binding')}",
        f"approval_writeback_active={activation.get('approval_writeback_active')}",
        f"controlled_import_execution_active={activation.get('controlled_import_execution_active')}",
        f"automatic_import_active={activation.get('automatic_import_active')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"action_model_json={result['action_model_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_20C_WORKSPACE_OPEN_SAVE_IMPORT_ACTION_MODEL" if result["passed"] else "FAIL_PHASE_20C_WORKSPACE_OPEN_SAVE_IMPORT_ACTION_MODEL")
    print(f"schema={result['schema']}")
    print(f"source_panel_provider_schema={result['source_panel_provider_schema']}")
    print(f"actions={summary.get('actions')}")
    print(f"enabled_actions={summary.get('enabled_actions')}")
    print(f"disabled_actions={summary.get('disabled_actions')}")
    print(f"panels_with_actions={summary.get('panels_with_actions')}")
    print(f"unsafe_enabled_actions={summary.get('unsafe_enabled_actions')}")
    print(f"ready_for_qt_binding={summary.get('ready_for_qt_binding')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"action_model_json={result['action_model_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
