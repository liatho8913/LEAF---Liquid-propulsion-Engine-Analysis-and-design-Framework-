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
    SIDEBAR_SCHEMA as SCHEMA,
    build_workspace_sidebar_model,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_20a"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_integration_completion_phase_19g.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_sidebar_model_gate_phase_20a.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    model = build_workspace_sidebar_model(ROOT)
    summary = model["summary"]
    policy = model["execution_policy"]
    activation = model["activation_status"]

    if model.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if model.get("source_navigation_schema") != "LEAF_WORKSPACE_NAVIGATION_MODEL_PHASE_18D_V1":
        failures.append("source_navigation_schema_invalid")

    if model.get("source_sorting_completion_schema") != "LEAF_SORTING_INTEGRATION_COMPLETION_PHASE_19G_V1":
        failures.append("source_sorting_completion_schema_invalid")

    if activation.get("ready_for_gui_activation") is not True:
        failures.append("not_ready_for_gui_activation")

    if activation.get("workspace_sidebar_model_ready") is not True:
        failures.append("workspace_sidebar_model_not_ready")

    if activation.get("automatic_import_active") is not False:
        failures.append("automatic_import_active_not_false")

    if activation.get("gui_execution_active") is not False:
        failures.append("gui_execution_active_not_false")

    if summary.get("sidebar_items", 0) < 6:
        failures.append("sidebar_item_count_too_low")

    if summary.get("developer_internal_items_exposed") != 0:
        failures.append("developer_internal_items_exposed")

    if summary.get("items_requiring_internal_path_knowledge") != 0:
        failures.append("items_require_internal_path_knowledge")

    for key in [
        "model_only",
    ]:
        if policy.get(key) is not True:
            failures.append(f"policy_not_true={key}")

    for key in [
        "qt_widgets_created",
        "imports_files",
        "moves_files",
        "deletes_files",
        "archives_files",
        "automatic_import_allowed",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false={key}")

    model_path = OUT / "workspace_sidebar_model_phase_20a.json"
    gate_json = OUT / "workspace_sidebar_model_gate_phase_20a.json"
    gate_txt = OUT / "workspace_sidebar_model_gate_phase_20a.txt"

    model_path.write_text(json.dumps(model, indent=2), encoding="utf-8")

    result = {
        "phase": "20A",
        "feature": "WORKSPACE_SIDEBAR_MODEL",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": model.get("schema"),
        "source_navigation_schema": model.get("source_navigation_schema"),
        "source_sorting_completion_schema": model.get("source_sorting_completion_schema"),
        "summary": summary,
        "activation_status": activation,
        "failures": failures,
        "sidebar_json": model_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_20A_COMPLETE_WORKSPACE_SIDEBAR_MODEL_ESTABLISHED" if not failures else "PHASE_20A_BLOCKED",
        "next_phase": "20B_WORKSPACE_PANEL_DATA_PROVIDERS",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 20A WORKSPACE SIDEBAR MODEL",
        "=======================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_navigation_schema={result['source_navigation_schema']}",
        f"source_sorting_completion_schema={result['source_sorting_completion_schema']}",
        f"sidebar_items={summary.get('sidebar_items')}",
        f"visible_items={summary.get('visible_items')}",
        f"enabled_items={summary.get('enabled_items')}",
        f"developer_internal_items_exposed={summary.get('developer_internal_items_exposed')}",
        f"items_requiring_internal_path_knowledge={summary.get('items_requiring_internal_path_knowledge')}",
        f"workspace_sidebar_model_ready={summary.get('workspace_sidebar_model_ready')}",
        f"ready_for_qt_binding={summary.get('ready_for_qt_binding')}",
        f"automatic_import_active={activation.get('automatic_import_active')}",
        f"gui_execution_active={activation.get('gui_execution_active')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"sidebar_json={result['sidebar_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_20A_WORKSPACE_SIDEBAR_MODEL" if result["passed"] else "FAIL_PHASE_20A_WORKSPACE_SIDEBAR_MODEL")
    print(f"schema={result['schema']}")
    print(f"source_navigation_schema={result['source_navigation_schema']}")
    print(f"source_sorting_completion_schema={result['source_sorting_completion_schema']}")
    print(f"sidebar_items={summary.get('sidebar_items')}")
    print(f"visible_items={summary.get('visible_items')}")
    print(f"enabled_items={summary.get('enabled_items')}")
    print(f"developer_internal_items_exposed={summary.get('developer_internal_items_exposed')}")
    print(f"items_requiring_internal_path_knowledge={summary.get('items_requiring_internal_path_knowledge')}")
    print(f"workspace_sidebar_model_ready={summary.get('workspace_sidebar_model_ready')}")
    print(f"ready_for_qt_binding={summary.get('ready_for_qt_binding')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"sidebar_json={result['sidebar_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
