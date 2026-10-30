from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.engineering_panel_contract_phase_22c import (
    SCHEMA,
    write_engineering_panel_contracts,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22c"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_tool_registry_phase_22b.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_panel_contract_phase_22c.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_panel_contract_gate_phase_22c.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    written = write_engineering_panel_contracts(ROOT)
    contracts_payload = written["contracts"]
    summary = contracts_payload["summary"]

    if contracts_payload.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if contracts_payload.get("source_registry_schema") != "LEAF_ENGINEERING_TOOL_REGISTRY_PHASE_22B_V1":
        failures.append("source_registry_schema_invalid")

    if summary.get("contract_count") != 7:
        failures.append("contract_count_invalid")

    if summary.get("registered_tool_count") != 7:
        failures.append("registered_tool_count_invalid")

    for key in [
        "all_registered_tools_have_panel_contracts",
        "contracts_are_metadata_only",
        "ready_for_22d_design_session_manager",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true:{key}")

    for key in [
        "qt_executes_solver_count",
        "qt_owns_validation_count",
        "qt_owns_reports_count",
        "filesystem_mutation_count",
    ]:
        if summary.get(key) != 0:
            failures.append(f"unsafe_count_nonzero:{key}")

    for key, value in contracts_payload.get("safety_boundaries", {}).items():
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

    actual_tools = {contract.get("tool_id") for contract in contracts_payload.get("contracts", [])}

    if actual_tools != expected_tools:
        failures.append("contract_tool_set_invalid")

    for contract in contracts_payload.get("contracts", []):
        tool_id = contract.get("tool_id")

        for required_key in [
            "panel_id",
            "panel_label",
            "required_model_contract",
            "required_controller_contract",
            "required_validation_contract",
            "required_report_contract",
            "workspace_adapter",
            "qt_binding_state",
        ]:
            if contract.get(required_key) in ("", None):
                failures.append(f"contract_missing_required_key:{tool_id}:{required_key}")

        for unsafe_key in [
            "qt_executes_solver",
            "qt_owns_validation",
            "qt_owns_reports",
            "filesystem_mutation",
        ]:
            if contract.get(unsafe_key) is not False:
                failures.append(f"contract_unsafe_flag_not_false:{tool_id}:{unsafe_key}")

    result = {
        "phase": "22C",
        "feature": "ENGINEERING_PANEL_CONTRACT",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "source_registry_schema": contracts_payload.get("source_registry_schema"),
        "summary": summary,
        "contracted_tools": sorted(actual_tools),
        "failures": failures,
        "contracts_json": written["json_path"],
        "contracts_report": written["txt_path"],
        "completion_notice": "PHASE_22C_COMPLETE_ENGINEERING_PANEL_CONTRACT_ESTABLISHED" if not failures else "PHASE_22C_BLOCKED",
        "next_phase": "22D_DESIGN_SESSION_MANAGER",
    }

    gate_json = OUT / "engineering_panel_contract_gate_phase_22c.json"
    gate_txt = OUT / "engineering_panel_contract_gate_phase_22c.txt"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 22C ENGINEERING PANEL CONTRACT GATE",
        "===============================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_registry_schema={result['source_registry_schema']}",
        f"contract_count={summary.get('contract_count')}",
        f"registered_tool_count={summary.get('registered_tool_count')}",
        f"all_registered_tools_have_panel_contracts={summary.get('all_registered_tools_have_panel_contracts')}",
        f"qt_executes_solver_count={summary.get('qt_executes_solver_count')}",
        f"qt_owns_validation_count={summary.get('qt_owns_validation_count')}",
        f"qt_owns_reports_count={summary.get('qt_owns_reports_count')}",
        f"filesystem_mutation_count={summary.get('filesystem_mutation_count')}",
        f"contracts_are_metadata_only={summary.get('contracts_are_metadata_only')}",
        f"ready_for_22d_design_session_manager={summary.get('ready_for_22d_design_session_manager')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"contracts_json={result['contracts_json']}",
        f"contracts_report={result['contracts_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_22C_ENGINEERING_PANEL_CONTRACT" if result["passed"] else "FAIL_PHASE_22C_ENGINEERING_PANEL_CONTRACT")
    print(f"schema={result['schema']}")
    print(f"source_registry_schema={result['source_registry_schema']}")
    print(f"contract_count={summary.get('contract_count')}")
    print(f"registered_tool_count={summary.get('registered_tool_count')}")
    print(f"all_registered_tools_have_panel_contracts={summary.get('all_registered_tools_have_panel_contracts')}")
    print(f"qt_executes_solver_count={summary.get('qt_executes_solver_count')}")
    print(f"qt_owns_validation_count={summary.get('qt_owns_validation_count')}")
    print(f"qt_owns_reports_count={summary.get('qt_owns_reports_count')}")
    print(f"filesystem_mutation_count={summary.get('filesystem_mutation_count')}")
    print(f"contracts_are_metadata_only={summary.get('contracts_are_metadata_only')}")
    print(f"ready_for_22d_design_session_manager={summary.get('ready_for_22d_design_session_manager')}")
    print(f"contracted_tools={','.join(result['contracted_tools'])}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"contracts_json={result['contracts_json']}")
    print(f"contracts_report={result['contracts_report']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
