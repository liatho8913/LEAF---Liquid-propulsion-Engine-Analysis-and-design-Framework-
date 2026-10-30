from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.workspace_tool_activation_binding_phase_22g import (
    SCHEMA,
    write_workspace_tool_activation_binding,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22g"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_tool_registry_phase_22b.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_panel_contract_phase_22c.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "design_session_manager_phase_22d.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "report_export_routing_phase_22f.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_tool_activation_binding_phase_22g.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_tool_activation_binding_gate_phase_22g.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    written = write_workspace_tool_activation_binding(ROOT)
    model = written["model"]
    summary = model["summary"]

    if model.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if model.get("source_registry_schema") != "LEAF_ENGINEERING_TOOL_REGISTRY_PHASE_22B_V1":
        failures.append("source_registry_schema_invalid")

    if model.get("source_panel_contract_schema") != "LEAF_ENGINEERING_PANEL_CONTRACT_PHASE_22C_V1":
        failures.append("source_panel_contract_schema_invalid")

    if model.get("source_routing_schema") != "LEAF_REPORT_EXPORT_ROUTING_PHASE_22F_V1":
        failures.append("source_routing_schema_invalid")

    if summary.get("binding_count") != 7:
        failures.append("binding_count_invalid")

    if summary.get("workspace_visible_tools") != 7:
        failures.append("workspace_visible_tools_invalid")

    if summary.get("workspace_enabled_tools") != 7:
        failures.append("workspace_enabled_tools_invalid")

    if summary.get("session_required_tools") != 5:
        failures.append("session_required_tools_invalid")

    if summary.get("tools_with_report_routes") != 5:
        failures.append("tools_with_report_routes_invalid")

    if summary.get("tools_with_export_routes") != 5:
        failures.append("tools_with_export_routes_invalid")

    if summary.get("blocked_tools") != 0:
        failures.append("blocked_tools_nonzero")

    for key in [
        "qt_executes_solver_count",
        "qt_generates_reports_count",
        "qt_generates_exports_count",
        "filesystem_mutation_count",
    ]:
        if summary.get(key) != 0:
            failures.append(f"unsafe_count_nonzero:{key}")

    for key in [
        "activation_binding_is_metadata_only",
        "ready_for_22h_engineering_workspace_completion_gate",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true:{key}")

    for key, value in model.get("safety_boundaries", {}).items():
        if value is not False:
            failures.append(f"safety_boundary_not_false:{key}")

    expected_tools = {
        "regen",
        "materials",
        "coatings",
        "graph_explorer",
        "station_viewer",
        "reports",
        "exports",
    }

    actual_tools = {binding.get("tool_id") for binding in model.get("bindings", [])}
    if actual_tools != expected_tools:
        failures.append("binding_tool_set_invalid")

    for binding in model.get("bindings", []):
        tool_id = binding.get("tool_id")

        if not binding.get("panel_id"):
            failures.append(f"missing_panel_id:{tool_id}")

        if binding.get("workspace_visible") is not True:
            failures.append(f"workspace_visible_not_true:{tool_id}")

        if binding.get("workspace_enabled") is not True:
            failures.append(f"workspace_enabled_not_true:{tool_id}")

        if binding.get("blocked_reason"):
            failures.append(f"binding_blocked:{tool_id}:{binding.get('blocked_reason')}")

        for unsafe_key in [
            "qt_executes_solver",
            "qt_generates_reports",
            "qt_generates_exports",
            "filesystem_mutation",
        ]:
            if binding.get(unsafe_key) is not False:
                failures.append(f"binding_unsafe_flag_not_false:{tool_id}:{unsafe_key}")

    result = {
        "phase": "22G",
        "feature": "WORKSPACE_TOOL_ACTIVATION_BINDING",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "summary": summary,
        "bound_tools": sorted(actual_tools),
        "failures": failures,
        "model_json": written["json_path"],
        "model_report": written["txt_path"],
        "completion_notice": "PHASE_22G_COMPLETE_WORKSPACE_TOOL_ACTIVATION_BINDING_ESTABLISHED" if not failures else "PHASE_22G_BLOCKED",
        "next_phase": "22H_ENGINEERING_WORKSPACE_COMPLETION_GATE",
    }

    gate_json = OUT / "workspace_tool_activation_binding_gate_phase_22g.json"
    gate_txt = OUT / "workspace_tool_activation_binding_gate_phase_22g.txt"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 22G WORKSPACE TOOL ACTIVATION BINDING GATE",
        "=====================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"binding_count={summary.get('binding_count')}",
        f"workspace_visible_tools={summary.get('workspace_visible_tools')}",
        f"workspace_enabled_tools={summary.get('workspace_enabled_tools')}",
        f"session_required_tools={summary.get('session_required_tools')}",
        f"tools_with_report_routes={summary.get('tools_with_report_routes')}",
        f"tools_with_export_routes={summary.get('tools_with_export_routes')}",
        f"blocked_tools={summary.get('blocked_tools')}",
        f"qt_executes_solver_count={summary.get('qt_executes_solver_count')}",
        f"qt_generates_reports_count={summary.get('qt_generates_reports_count')}",
        f"qt_generates_exports_count={summary.get('qt_generates_exports_count')}",
        f"filesystem_mutation_count={summary.get('filesystem_mutation_count')}",
        f"activation_binding_is_metadata_only={summary.get('activation_binding_is_metadata_only')}",
        f"ready_for_22h_engineering_workspace_completion_gate={summary.get('ready_for_22h_engineering_workspace_completion_gate')}",
        f"bound_tools={','.join(result['bound_tools'])}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"model_json={result['model_json']}",
        f"model_report={result['model_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_22G_WORKSPACE_TOOL_ACTIVATION_BINDING" if result["passed"] else "FAIL_PHASE_22G_WORKSPACE_TOOL_ACTIVATION_BINDING")
    print(f"schema={result['schema']}")
    print(f"binding_count={summary.get('binding_count')}")
    print(f"workspace_visible_tools={summary.get('workspace_visible_tools')}")
    print(f"workspace_enabled_tools={summary.get('workspace_enabled_tools')}")
    print(f"session_required_tools={summary.get('session_required_tools')}")
    print(f"tools_with_report_routes={summary.get('tools_with_report_routes')}")
    print(f"tools_with_export_routes={summary.get('tools_with_export_routes')}")
    print(f"blocked_tools={summary.get('blocked_tools')}")
    print(f"qt_executes_solver_count={summary.get('qt_executes_solver_count')}")
    print(f"qt_generates_reports_count={summary.get('qt_generates_reports_count')}")
    print(f"qt_generates_exports_count={summary.get('qt_generates_exports_count')}")
    print(f"filesystem_mutation_count={summary.get('filesystem_mutation_count')}")
    print(f"activation_binding_is_metadata_only={summary.get('activation_binding_is_metadata_only')}")
    print(f"ready_for_22h_engineering_workspace_completion_gate={summary.get('ready_for_22h_engineering_workspace_completion_gate')}")
    print(f"bound_tools={','.join(result['bound_tools'])}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"model_json={result['model_json']}")
    print(f"model_report={result['model_report']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
