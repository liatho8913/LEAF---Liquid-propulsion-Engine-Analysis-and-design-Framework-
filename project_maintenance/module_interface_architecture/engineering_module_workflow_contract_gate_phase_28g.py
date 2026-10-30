"""
Programme 28G Completion Gate.

Validates the Engineering Module Workflow Contract.
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
from leaf_qt.module_interface.workflow_contract import (
    EngineeringModuleWorkflowStepDefinition,
    build_engineering_module_workflow_contract,
)
from leaf_qt.workflow import WorkflowStepStatus


def main() -> None:
    for rel in [
        "leaf_qt/module_interface/__init__.py",
        "leaf_qt/module_interface/interface_model.py",
        "leaf_qt/module_interface/module_registry.py",
        "leaf_qt/module_interface/dependency_graph.py",
        "leaf_qt/module_interface/adapter_contract.py",
        "leaf_qt/module_interface/validation_contract.py",
        "leaf_qt/module_interface/report_contract.py",
        "leaf_qt/module_interface/workflow_contract.py",
        "leaf_qt/workflow/model.py",
        "leaf_qt/workflow/progress_tracker.py",
        "leaf_qt/workflow/readiness_gate.py",
        "leaf_qt/workflow/recommendation_engine.py",
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
                reason="Regen workflow contract plugs into completed Programme 26 workflow platform.",
            ),
        ),
    )

    contract = build_engineering_module_workflow_contract(
        interface=interface,
        metadata={"gate": "28G"},
    )

    statuses = {
        "define_inputs": WorkflowStepStatus.COMPLETE,
        "run_module_solver": WorkflowStepStatus.READY,
        "validate_module_outputs": WorkflowStepStatus.NOT_STARTED,
        "produce_module_report": WorkflowStepStatus.NOT_STARTED,
        "store_module_design": WorkflowStepStatus.NOT_STARTED,
    }

    report = contract.report(
        current_step_id="run_module_solver",
        statuses=statuses,
    )

    failures = list(report["contract_validation_failures"])
    failures.extend(report["workflow"]["validation_failures"])

    if report["schema"] != "LEAF_ENGINEERING_MODULE_WORKFLOW_CONTRACT_PHASE_28G_V1":
        failures.append(f"schema mismatch: {report['schema']}")

    if report["progress"]["total_steps"] != 5:
        failures.append(f"expected total_steps=5, actual={report['progress']['total_steps']}")

    if report["progress"]["current_ready_step"] != "run_module_solver":
        failures.append(
            f"current_ready_step mismatch: {report['progress']['current_ready_step']}"
        )

    if report["readiness"]["verdict"] != "READY":
        failures.append(f"readiness verdict mismatch: {report['readiness']['verdict']}")

    if report["recommendation"]["kind"] != "PROCEED_CURRENT_STEP":
        failures.append(f"recommendation kind mismatch: {report['recommendation']['kind']}")

    for flag in [
        "mutation_performed",
        "solver_executed",
        "runtime_mutation_performed",
        "storage_mutation_performed",
    ]:
        if report[flag] is not False:
            failures.append(f"{flag} must remain False")

    bad_contract = build_engineering_module_workflow_contract(
        interface=interface,
        step_definitions=(
            EngineeringModuleWorkflowStepDefinition(
                step_id="a",
                title="A",
                description="A",
                dependencies=("missing",),
            ),
        ),
    )

    bad_failures = bad_contract.validate_contract()
    if not any("depends on missing step" in failure for failure in bad_failures):
        failures.append("bad workflow contract did not detect missing dependency")

    final_report = {
        "schema": "LEAF_ENGINEERING_MODULE_WORKFLOW_CONTRACT_COMPLETION_PHASE_28G_V1",
        "workflow_contract_report": report,
        "bad_contract_failures": list(bad_failures),
        "gate": {
            "phase": "28G",
            "programme": "28",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_28G_ENGINEERING_MODULE_WORKFLOW_CONTRACT_COMPLETE"
                if not failures
                else "PROGRAMME_28G_ENGINEERING_MODULE_WORKFLOW_CONTRACT_FAILED"
            ),
            "next_phase": "28H Engineering Module Runtime Contract",
        },
    }

    txt_path = REPORT_DIR / "engineering_module_workflow_contract_gate_phase_28g.txt"
    json_path = REPORT_DIR / "engineering_module_workflow_contract_gate_phase_28g.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 28G Engineering Module Workflow Contract Gate",
                "==========================================================",
                f"passed={not failures}",
                f"module_id={report['module_id']}",
                f"workflow_id={report['workflow_id']}",
                f"total_steps={report['progress']['total_steps']}",
                f"current_ready_step={report['progress']['current_ready_step']}",
                f"readiness_verdict={report['readiness']['verdict']}",
                f"recommendation_kind={report['recommendation']['kind']}",
                f"mutation_performed={report['mutation_performed']}",
                f"solver_executed={report['solver_executed']}",
                f"runtime_mutation_performed={report['runtime_mutation_performed']}",
                f"storage_mutation_performed={report['storage_mutation_performed']}",
                f"bad_contract_failures={len(bad_failures)}",
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
        print("FAIL_PHASE_28G_ENGINEERING_MODULE_WORKFLOW_CONTRACT")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_28G_ENGINEERING_MODULE_WORKFLOW_CONTRACT")
    print("schema=LEAF_ENGINEERING_MODULE_WORKFLOW_CONTRACT_PHASE_28G_V1")
    print(f"module_id={report['module_id']}")
    print(f"workflow_id={report['workflow_id']}")
    print(f"total_steps={report['progress']['total_steps']}")
    print(f"current_ready_step={report['progress']['current_ready_step']}")
    print(f"readiness_verdict={report['readiness']['verdict']}")
    print(f"recommendation_kind={report['recommendation']['kind']}")
    print(f"mutation_performed={report['mutation_performed']}")
    print(f"solver_executed={report['solver_executed']}")
    print(f"runtime_mutation_performed={report['runtime_mutation_performed']}")
    print(f"storage_mutation_performed={report['storage_mutation_performed']}")
    print(f"bad_contract_failures={len(bad_failures)}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_28G_ENGINEERING_MODULE_WORKFLOW_CONTRACT_COMPLETE")
    print("next_phase=28H Engineering Module Runtime Contract")


if __name__ == "__main__":
    main()
