from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.engineering_tool_registry_phase_22b import (
    SCHEMA,
    write_engineering_tool_registry,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22b"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_tool_registry_phase_22b.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_tool_registry_gate_phase_22b.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    written = write_engineering_tool_registry(ROOT)
    registry = written["registry"]
    summary = registry["summary"]

    if registry.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    expected_tools = {
        "regen",
        "materials",
        "coatings",
        "graph_explorer",
        "station_viewer",
        "reports",
        "exports",
    }

    actual_tools = {tool.get("tool_id") for tool in registry.get("tools", [])}

    if actual_tools != expected_tools:
        failures.append("registered_tool_set_invalid")

    if summary.get("tool_count") != 7:
        failures.append("tool_count_invalid")

    if summary.get("user_visible_tools") != 7:
        failures.append("user_visible_tool_count_invalid")

    if summary.get("planned_tools") != 7:
        failures.append("planned_tool_count_invalid")

    if summary.get("qt_executes_solver_count") != 0:
        failures.append("qt_executes_solver_count_nonzero")

    if summary.get("qt_owns_logic_count") != 0:
        failures.append("qt_owns_logic_count_nonzero")

    for key in [
        "registry_is_metadata_only",
        "ready_for_22c_panel_contract",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true:{key}")

    for key, value in registry.get("safety_boundaries", {}).items():
        if value is not False:
            failures.append(f"safety_boundary_not_false:{key}")

    for tool in registry.get("tools", []):
        for required_key in [
            "tool_id",
            "label",
            "category",
            "owner_layer",
            "model_source",
            "controller_source",
            "validation_owner",
            "report_owner",
            "workspace_panel_adapter",
            "activation_state",
        ]:
            if required_key not in tool or tool.get(required_key) in ("", None):
                failures.append(f"tool_missing_required_key:{tool.get('tool_id')}:{required_key}")

        if tool.get("qt_executes_solver") is not False:
            failures.append(f"tool_qt_executes_solver_not_false:{tool.get('tool_id')}")

        if tool.get("qt_owns_logic") is not False:
            failures.append(f"tool_qt_owns_logic_not_false:{tool.get('tool_id')}")

    result = {
        "phase": "22B",
        "feature": "ENGINEERING_TOOL_REGISTRY",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "summary": summary,
        "registered_tools": sorted(actual_tools),
        "failures": failures,
        "registry_json": written["json_path"],
        "registry_report": written["txt_path"],
        "completion_notice": "PHASE_22B_COMPLETE_ENGINEERING_TOOL_REGISTRY_ESTABLISHED" if not failures else "PHASE_22B_BLOCKED",
        "next_phase": "22C_ENGINEERING_PANEL_CONTRACT",
    }

    gate_json = OUT / "engineering_tool_registry_gate_phase_22b.json"
    gate_txt = OUT / "engineering_tool_registry_gate_phase_22b.txt"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 22B ENGINEERING TOOL REGISTRY GATE",
        "==============================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"tool_count={summary.get('tool_count')}",
        f"user_visible_tools={summary.get('user_visible_tools')}",
        f"planned_tools={summary.get('planned_tools')}",
        f"qt_executes_solver_count={summary.get('qt_executes_solver_count')}",
        f"qt_owns_logic_count={summary.get('qt_owns_logic_count')}",
        f"registry_is_metadata_only={summary.get('registry_is_metadata_only')}",
        f"ready_for_22c_panel_contract={summary.get('ready_for_22c_panel_contract')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"registry_json={result['registry_json']}",
        f"registry_report={result['registry_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_22B_ENGINEERING_TOOL_REGISTRY" if result["passed"] else "FAIL_PHASE_22B_ENGINEERING_TOOL_REGISTRY")
    print(f"schema={result['schema']}")
    print(f"tool_count={summary.get('tool_count')}")
    print(f"user_visible_tools={summary.get('user_visible_tools')}")
    print(f"planned_tools={summary.get('planned_tools')}")
    print(f"qt_executes_solver_count={summary.get('qt_executes_solver_count')}")
    print(f"qt_owns_logic_count={summary.get('qt_owns_logic_count')}")
    print(f"registry_is_metadata_only={summary.get('registry_is_metadata_only')}")
    print(f"ready_for_22c_panel_contract={summary.get('ready_for_22c_panel_contract')}")
    print(f"registered_tools={','.join(result['registered_tools'])}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"registry_json={result['registry_json']}")
    print(f"registry_report={result['registry_report']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
