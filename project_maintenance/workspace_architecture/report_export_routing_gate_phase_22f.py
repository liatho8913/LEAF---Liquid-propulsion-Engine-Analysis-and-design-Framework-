from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.report_export_routing_phase_22f import (
    SCHEMA,
    write_report_export_routing_model,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22f"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_tool_registry_phase_22b.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_document_model_phase_22e.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "report_export_routing_phase_22f.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "report_export_routing_gate_phase_22f.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    written = write_report_export_routing_model(ROOT)
    model = written["model"]
    summary = model["summary"]

    if model.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if model.get("source_tool_registry_schema") != "LEAF_ENGINEERING_TOOL_REGISTRY_PHASE_22B_V1":
        failures.append("source_tool_registry_schema_invalid")

    if model.get("source_document_model_schema") != "LEAF_ENGINEERING_DOCUMENT_MODEL_PHASE_22E_V1":
        failures.append("source_document_model_schema_invalid")

    if summary.get("source_engineering_tools") != 5:
        failures.append("source_engineering_tools_invalid")

    if summary.get("route_count") != 10:
        failures.append("route_count_invalid")

    if summary.get("report_routes") != 5:
        failures.append("report_routes_invalid")

    if summary.get("export_routes") != 5:
        failures.append("export_routes_invalid")

    if summary.get("qt_generates_output_count") != 0:
        failures.append("qt_generates_output_count_nonzero")

    if summary.get("qt_owns_report_logic_count") != 0:
        failures.append("qt_owns_report_logic_count_nonzero")

    if summary.get("qt_owns_export_logic_count") != 0:
        failures.append("qt_owns_export_logic_count_nonzero")

    if summary.get("filesystem_mutation_requires_user_action_count") != 10:
        failures.append("filesystem_mutation_requires_user_action_count_invalid")

    for key in [
        "routes_are_metadata_only",
        "ready_for_22g_workspace_tool_activation_binding",
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
    }

    actual_tools = {route.get("source_tool_id") for route in model.get("routes", [])}
    if actual_tools != expected_tools:
        failures.append("route_source_tool_set_invalid")

    for route in model.get("routes", []):
        route_id = route.get("route_id")

        if route.get("output_type") == "report" and route.get("canonical_root") != "LEAF_Reports":
            failures.append(f"report_route_root_invalid:{route_id}")

        if route.get("output_type") == "export" and route.get("canonical_root") != "LEAF_Exports":
            failures.append(f"export_route_root_invalid:{route_id}")

        for unsafe_key in [
            "qt_generates_output",
            "qt_owns_report_logic",
            "qt_owns_export_logic",
        ]:
            if route.get(unsafe_key) is not False:
                failures.append(f"route_unsafe_flag_not_false:{route_id}:{unsafe_key}")

        if route.get("filesystem_mutation_requires_user_action") is not True:
            failures.append(f"route_user_action_required_not_true:{route_id}")

    result = {
        "phase": "22F",
        "feature": "REPORT_AND_EXPORT_ROUTING",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "summary": summary,
        "routed_tools": sorted(actual_tools),
        "failures": failures,
        "model_json": written["json_path"],
        "model_report": written["txt_path"],
        "completion_notice": "PHASE_22F_COMPLETE_REPORT_EXPORT_ROUTING_ESTABLISHED" if not failures else "PHASE_22F_BLOCKED",
        "next_phase": "22G_WORKSPACE_TOOL_ACTIVATION_BINDING",
    }

    gate_json = OUT / "report_export_routing_gate_phase_22f.json"
    gate_txt = OUT / "report_export_routing_gate_phase_22f.txt"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 22F REPORT AND EXPORT ROUTING GATE",
        "=============================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"route_count={summary.get('route_count')}",
        f"report_routes={summary.get('report_routes')}",
        f"export_routes={summary.get('export_routes')}",
        f"source_engineering_tools={summary.get('source_engineering_tools')}",
        f"report_root={summary.get('report_root')}",
        f"export_root={summary.get('export_root')}",
        f"qt_generates_output_count={summary.get('qt_generates_output_count')}",
        f"qt_owns_report_logic_count={summary.get('qt_owns_report_logic_count')}",
        f"qt_owns_export_logic_count={summary.get('qt_owns_export_logic_count')}",
        f"filesystem_mutation_requires_user_action_count={summary.get('filesystem_mutation_requires_user_action_count')}",
        f"routes_are_metadata_only={summary.get('routes_are_metadata_only')}",
        f"ready_for_22g_workspace_tool_activation_binding={summary.get('ready_for_22g_workspace_tool_activation_binding')}",
        f"routed_tools={','.join(result['routed_tools'])}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"model_json={result['model_json']}",
        f"model_report={result['model_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_22F_REPORT_EXPORT_ROUTING" if result["passed"] else "FAIL_PHASE_22F_REPORT_EXPORT_ROUTING")
    print(f"schema={result['schema']}")
    print(f"route_count={summary.get('route_count')}")
    print(f"report_routes={summary.get('report_routes')}")
    print(f"export_routes={summary.get('export_routes')}")
    print(f"source_engineering_tools={summary.get('source_engineering_tools')}")
    print(f"report_root={summary.get('report_root')}")
    print(f"export_root={summary.get('export_root')}")
    print(f"qt_generates_output_count={summary.get('qt_generates_output_count')}")
    print(f"qt_owns_report_logic_count={summary.get('qt_owns_report_logic_count')}")
    print(f"qt_owns_export_logic_count={summary.get('qt_owns_export_logic_count')}")
    print(f"filesystem_mutation_requires_user_action_count={summary.get('filesystem_mutation_requires_user_action_count')}")
    print(f"routes_are_metadata_only={summary.get('routes_are_metadata_only')}")
    print(f"ready_for_22g_workspace_tool_activation_binding={summary.get('ready_for_22g_workspace_tool_activation_binding')}")
    print(f"routed_tools={','.join(result['routed_tools'])}")
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
