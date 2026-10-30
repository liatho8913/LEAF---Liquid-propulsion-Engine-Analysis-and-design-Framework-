"""
Programme 28E Completion Gate.

Validates the Engineering Module Validation Contract.
"""

from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORT_DIR = ROOT / "LEAF_Reports" / "module_interface_architecture"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

from leaf_qt.module_interface.interface_model import (
    EngineeringModuleDependency,
    EngineeringModuleInterfaceStatus,
    build_engineering_module_interface,
)
from leaf_qt.module_interface.validation_contract import (
    EngineeringModuleValidationFinding,
    EngineeringModuleValidationMode,
    EngineeringModuleValidationSeverity,
    build_engineering_module_validation_contract,
)


def main() -> None:
    for rel in [
        "leaf_qt/module_interface/__init__.py",
        "leaf_qt/module_interface/interface_model.py",
        "leaf_qt/module_interface/module_registry.py",
        "leaf_qt/module_interface/dependency_graph.py",
        "leaf_qt/module_interface/adapter_contract.py",
        "leaf_qt/module_interface/validation_contract.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    interface = build_engineering_module_interface(
        module_id="regen_demonstration_module",
        title="Regenerative Cooling Demonstration Module",
        status=EngineeringModuleInterfaceStatus.READY,
        dependencies=(
            EngineeringModuleDependency(
                dependency_id="regen_platform_dependencies",
                provides=("regen.workflow", "regen.report", "regen.validation"),
                requires=("workflow.platform", "runtime.platform", "storage.platform"),
                optional=("notification.platform",),
                reason="Regen module validation plugs into shared platform services.",
            ),
        ),
    )

    sourced_contract = build_engineering_module_validation_contract(
        interface=interface,
        validation_mode=EngineeringModuleValidationMode.SOURCED_VALIDATION_MODE,
        required_fields=("inputs", "solver_outputs", "validation_rules", "report_owner"),
        metadata={"gate": "28E"},
    )

    pass_report = sourced_contract.report(
        provided_fields=("inputs", "solver_outputs", "validation_rules", "report_owner")
    )

    missing_report = sourced_contract.report(
        provided_fields=("inputs", "solver_outputs")
    )

    warning_report = sourced_contract.report(
        provided_fields=("inputs", "solver_outputs", "validation_rules", "report_owner"),
        external_findings=(
            EngineeringModuleValidationFinding(
                finding_id="warning_probe",
                severity=EngineeringModuleValidationSeverity.WARNING,
                message="Gate warning probe.",
            ),
        ),
    )

    placeholder_contract = build_engineering_module_validation_contract(
        interface=interface,
        validation_mode=EngineeringModuleValidationMode.PLACEHOLDER_MODE,
        required_fields=("inputs",),
    )

    placeholder_report = placeholder_contract.report(provided_fields=("inputs",))

    failures = []

    if pass_report["result"]["verdict"] != "PASS":
        failures.append(f"sourced pass verdict mismatch: {pass_report['result']['verdict']}")

    if pass_report["result"]["passed"] is not True:
        failures.append("sourced validation with complete fields should pass")

    if missing_report["result"]["verdict"] != "FAIL":
        failures.append(f"missing field verdict mismatch: {missing_report['result']['verdict']}")

    if missing_report["result"]["passed"] is not False:
        failures.append("missing fields should not pass")

    if warning_report["result"]["verdict"] != "WARNING":
        failures.append(f"warning verdict mismatch: {warning_report['result']['verdict']}")

    if placeholder_report["result"]["verdict"] != "BLOCKED":
        failures.append(f"placeholder verdict mismatch: {placeholder_report['result']['verdict']}")

    if placeholder_report["result"]["passed"] is not False:
        failures.append("PLACEHOLDER_MODE must never pass")

    for label, report in [
        ("pass", pass_report),
        ("missing", missing_report),
        ("warning", warning_report),
        ("placeholder", placeholder_report),
    ]:
        if report["mutation_performed"] is not False:
            failures.append(f"{label} report mutated repository")
        if report["solver_executed"] is not False:
            failures.append(f"{label} report executed solver")
        if report["runtime_mutation_performed"] is not False:
            failures.append(f"{label} report mutated runtime")
        if report["storage_mutation_performed"] is not False:
            failures.append(f"{label} report mutated storage")

    final_report = {
        "schema": "LEAF_ENGINEERING_MODULE_VALIDATION_CONTRACT_COMPLETION_PHASE_28E_V1",
        "pass_report": pass_report,
        "missing_report": missing_report,
        "warning_report": warning_report,
        "placeholder_report": placeholder_report,
        "gate": {
            "phase": "28E",
            "programme": "28",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_28E_ENGINEERING_MODULE_VALIDATION_CONTRACT_COMPLETE"
                if not failures
                else "PROGRAMME_28E_ENGINEERING_MODULE_VALIDATION_CONTRACT_FAILED"
            ),
            "next_phase": "28F Engineering Module Report Contract",
        },
    }

    txt_path = REPORT_DIR / "engineering_module_validation_contract_gate_phase_28e.txt"
    json_path = REPORT_DIR / "engineering_module_validation_contract_gate_phase_28e.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 28E Engineering Module Validation Contract Gate",
                "=============================================================",
                f"passed={not failures}",
                f"module_id={interface.module_id}",
                f"sourced_verdict={pass_report['result']['verdict']}",
                f"missing_verdict={missing_report['result']['verdict']}",
                f"warning_verdict={warning_report['result']['verdict']}",
                f"placeholder_verdict={placeholder_report['result']['verdict']}",
                f"placeholder_passed={placeholder_report['result']['passed']}",
                f"mutation_performed={pass_report['mutation_performed']}",
                f"solver_executed={pass_report['solver_executed']}",
                f"runtime_mutation_performed={pass_report['runtime_mutation_performed']}",
                f"storage_mutation_performed={pass_report['storage_mutation_performed']}",
                f"failures={len(failures)}",
                f"completion_notice={final_report['gate']['completion_notice']}",
                f"next_phase={final_report['gate']['next_phase']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    json_path.write_text(json.dumps(final_report, indent=2), encoding="utf-8")

    if failures:
        print("FAIL_PHASE_28E_ENGINEERING_MODULE_VALIDATION_CONTRACT")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_28E_ENGINEERING_MODULE_VALIDATION_CONTRACT")
    print("schema=LEAF_ENGINEERING_MODULE_VALIDATION_CONTRACT_PHASE_28E_V1")
    print(f"module_id={interface.module_id}")
    print(f"sourced_verdict={pass_report['result']['verdict']}")
    print(f"missing_verdict={missing_report['result']['verdict']}")
    print(f"warning_verdict={warning_report['result']['verdict']}")
    print(f"placeholder_verdict={placeholder_report['result']['verdict']}")
    print(f"placeholder_passed={placeholder_report['result']['passed']}")
    print(f"mutation_performed={pass_report['mutation_performed']}")
    print(f"solver_executed={pass_report['solver_executed']}")
    print(f"runtime_mutation_performed={pass_report['runtime_mutation_performed']}")
    print(f"storage_mutation_performed={pass_report['storage_mutation_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_28E_ENGINEERING_MODULE_VALIDATION_CONTRACT_COMPLETE")
    print("next_phase=28F Engineering Module Report Contract")


if __name__ == "__main__":
    main()
