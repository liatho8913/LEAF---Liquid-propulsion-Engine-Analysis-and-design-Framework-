from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.engineering_workspace_integration_plan_phase_22a import (
    SCHEMA,
    write_engineering_workspace_integration_plan,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22a"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_workspace_integration_plan_phase_22a.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_workspace_integration_plan_gate_phase_22a.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    written = write_engineering_workspace_integration_plan(ROOT)
    plan = written["plan"]

    if plan.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if len(plan.get("programme_22_steps", [])) != 7:
        failures.append("programme_22_step_count_invalid")

    expected_phases = {"22B", "22C", "22D", "22E", "22F", "22G", "22H"}
    actual_phases = {step.get("phase") for step in plan.get("programme_22_steps", [])}

    if actual_phases != expected_phases:
        failures.append("programme_22_phase_set_invalid")

    for key, value in plan.get("non_negotiable_principles", {}).items():
        if key == "canonical_user_storage":
            if value != "LEAF_Designs":
                failures.append("canonical_user_storage_invalid")
        elif value is not True:
            failures.append(f"principle_not_true:{key}")

    for key, value in plan.get("safety_boundaries", {}).items():
        if value is not False:
            failures.append(f"safety_boundary_not_false:{key}")

    for key, value in plan.get("completion_criteria", {}).items():
        if value is not True:
            failures.append(f"completion_criterion_not_true:{key}")

    required_contracts = plan.get("required_contracts", {})
    for contract_name in [
        "engineering_tool_registry",
        "panel_contract",
        "design_session_contract",
        "report_export_contract",
        "activation_contract",
    ]:
        if required_contracts.get(contract_name, {}).get("required") is not True:
            failures.append(f"required_contract_missing:{contract_name}")

    result = {
        "phase": "22A",
        "feature": "ENGINEERING_WORKSPACE_INTEGRATION_PLANNING",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "programme_22_steps": len(plan.get("programme_22_steps", [])),
        "required_contracts": len(required_contracts),
        "safety_boundaries": plan.get("safety_boundaries", {}),
        "completion_criteria": plan.get("completion_criteria", {}),
        "failures": failures,
        "plan_json": written["json_path"],
        "plan_report": written["txt_path"],
        "completion_notice": "PHASE_22A_COMPLETE_ENGINEERING_WORKSPACE_INTEGRATION_PLAN_ESTABLISHED" if not failures else "PHASE_22A_BLOCKED",
        "next_phase": "22B_ENGINEERING_TOOL_REGISTRY",
    }

    gate_json = OUT / "engineering_workspace_integration_plan_gate_phase_22a.json"
    gate_txt = OUT / "engineering_workspace_integration_plan_gate_phase_22a.txt"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 22A ENGINEERING WORKSPACE INTEGRATION PLAN GATE",
        "==========================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"programme_22_steps={result['programme_22_steps']}",
        f"required_contracts={result['required_contracts']}",
        f"qt_owns_solver_logic={result['safety_boundaries'].get('qt_owns_solver_logic')}",
        f"qt_owns_validation_logic={result['safety_boundaries'].get('qt_owns_validation_logic')}",
        f"qt_owns_report_logic={result['safety_boundaries'].get('qt_owns_report_logic')}",
        f"qt_owns_sorting_logic={result['safety_boundaries'].get('qt_owns_sorting_logic')}",
        f"automatic_sorting_activation={result['safety_boundaries'].get('automatic_sorting_activation')}",
        f"filesystem_mutation={result['safety_boundaries'].get('filesystem_mutation')}",
        f"engineering_calculation_execution={result['safety_boundaries'].get('engineering_calculation_execution')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"plan_json={result['plan_json']}",
        f"plan_report={result['plan_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_22A_ENGINEERING_WORKSPACE_INTEGRATION_PLAN" if result["passed"] else "FAIL_PHASE_22A_ENGINEERING_WORKSPACE_INTEGRATION_PLAN")
    print(f"schema={result['schema']}")
    print(f"programme_22_steps={result['programme_22_steps']}")
    print(f"required_contracts={result['required_contracts']}")
    print(f"qt_owns_solver_logic={result['safety_boundaries'].get('qt_owns_solver_logic')}")
    print(f"qt_owns_validation_logic={result['safety_boundaries'].get('qt_owns_validation_logic')}")
    print(f"qt_owns_report_logic={result['safety_boundaries'].get('qt_owns_report_logic')}")
    print(f"qt_owns_sorting_logic={result['safety_boundaries'].get('qt_owns_sorting_logic')}")
    print(f"automatic_sorting_activation={result['safety_boundaries'].get('automatic_sorting_activation')}")
    print(f"filesystem_mutation={result['safety_boundaries'].get('filesystem_mutation')}")
    print(f"engineering_calculation_execution={result['safety_boundaries'].get('engineering_calculation_execution')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"plan_json={result['plan_json']}")
    print(f"plan_report={result['plan_report']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
