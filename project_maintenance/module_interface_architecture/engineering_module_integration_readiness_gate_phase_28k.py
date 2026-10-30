"""
Programme 28K Completion Gate.

Validates the Engineering Module Integration Readiness Gate.
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

from leaf_qt.module_interface.adapter_contract import build_engineering_module_adapter_contract
from leaf_qt.module_interface.integration_readiness_gate import (
    EngineeringModuleIntegrationVerdict,
    build_engineering_module_integration_readiness_gate,
)
from leaf_qt.module_interface.interface_model import (
    EngineeringModuleDependency,
    EngineeringModuleInterfaceStatus,
    build_engineering_module_interface,
)
from leaf_qt.module_interface.notification_contract import build_engineering_module_notification_contract
from leaf_qt.module_interface.report_contract import (
    EngineeringModuleReportSection,
    build_engineering_module_report_contract,
)
from leaf_qt.module_interface.runtime_contract import build_engineering_module_runtime_contract
from leaf_qt.module_interface.storage_contract import build_engineering_module_storage_contract
from leaf_qt.module_interface.validation_contract import (
    EngineeringModuleValidationMode,
    build_engineering_module_validation_contract,
)
from leaf_qt.module_interface.workflow_contract import build_engineering_module_workflow_contract


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
        "leaf_qt/module_interface/runtime_contract.py",
        "leaf_qt/module_interface/storage_contract.py",
        "leaf_qt/module_interface/notification_contract.py",
        "leaf_qt/module_interface/integration_readiness_gate.py",
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
                reason="Regen integration readiness requires all module contracts.",
            ),
        ),
    )

    adapter_contract = build_engineering_module_adapter_contract(
        adapter_id="regen_demonstration_adapter",
        interface=interface,
    )

    validation_contract = build_engineering_module_validation_contract(
        interface=interface,
        validation_mode=EngineeringModuleValidationMode.SOURCED_VALIDATION_MODE,
        required_fields=("inputs", "solver_outputs", "validation_rules", "report_owner"),
    )
    validation_result = validation_contract.evaluate(
        provided_fields=("inputs", "solver_outputs", "validation_rules", "report_owner")
    )

    report_contract = build_engineering_module_report_contract(
        interface=interface,
        report_owner="regen_demonstration_report_owner",
    )
    report_package = report_contract.build_report(
        report_id="regen_integration_readiness_report",
        title="Regen Integration Readiness Report",
        validation_result=validation_result,
        sections=(
            EngineeringModuleReportSection("summary", "Summary", {"ready": True}),
        ),
    )

    workflow_contract = build_engineering_module_workflow_contract(interface=interface)
    runtime_contract = build_engineering_module_runtime_contract(
        interface=interface,
        runtime_reference="runtime:28k",
    )
    storage_contract = build_engineering_module_storage_contract(interface=interface)
    notification_contract = build_engineering_module_notification_contract(interface=interface)

    ready_gate = build_engineering_module_integration_readiness_gate(
        interface=interface,
        adapter_contract=adapter_contract,
        validation_result=validation_result,
        report_package=report_package,
        workflow_contract=workflow_contract,
        runtime_contract=runtime_contract,
        storage_contract=storage_contract,
        notification_contract=notification_contract,
        dependency_missing_requirements=tuple(),
    )

    ready_report = ready_gate.report()
    ready_result = ready_report["result"]

    blocked_gate = build_engineering_module_integration_readiness_gate(
        interface=interface,
        adapter_contract=adapter_contract,
        validation_result=validation_result,
        report_package=report_package,
        workflow_contract=workflow_contract,
        runtime_contract=runtime_contract,
        storage_contract=storage_contract,
        notification_contract=notification_contract,
        dependency_missing_requirements=("missing.platform",),
    )

    blocked_result = blocked_gate.evaluate().as_dict()

    failures = []

    if ready_result["verdict"] != EngineeringModuleIntegrationVerdict.READY.value:
        failures.append(f"ready verdict mismatch: {ready_result['verdict']}")

    if ready_result["ready"] is not True:
        failures.append("ready integration gate should be ready")

    expected_checks = [
        "interface_valid",
        "dependencies_satisfied",
        "adapter_contract_valid",
        "validation_passed",
        "report_package_valid",
        "workflow_contract_valid",
        "runtime_contract_valid",
        "storage_contract_valid",
        "notification_contract_valid",
        "non_mutating_contracts",
    ]

    for check in expected_checks:
        if ready_result["checks"].get(check) is not True:
            failures.append(f"ready check failed: {check}")

    if ready_result["mutation_performed"] is not False:
        failures.append("integration readiness gate must not mutate")

    if ready_result["solver_executed"] is not False:
        failures.append("integration readiness gate must not execute solver")

    if ready_result["runtime_mutation_performed"] is not False:
        failures.append("integration readiness gate must not mutate runtime")

    if ready_result["storage_mutation_performed"] is not False:
        failures.append("integration readiness gate must not mutate storage")

    if blocked_result["verdict"] != EngineeringModuleIntegrationVerdict.BLOCKED.value:
        failures.append(f"blocked verdict mismatch: {blocked_result['verdict']}")

    if blocked_result["ready"] is not False:
        failures.append("blocked integration gate should not be ready")

    if not blocked_result["blockers"]:
        failures.append("blocked integration gate should include blockers")

    final_report = {
        "schema": "LEAF_ENGINEERING_MODULE_INTEGRATION_READINESS_GATE_COMPLETION_PHASE_28K_V1",
        "ready_report": ready_report,
        "blocked_result": blocked_result,
        "gate": {
            "phase": "28K",
            "programme": "28",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_28K_ENGINEERING_MODULE_INTEGRATION_READINESS_GATE_COMPLETE"
                if not failures
                else "PROGRAMME_28K_ENGINEERING_MODULE_INTEGRATION_READINESS_GATE_FAILED"
            ),
            "next_phase": "28L Programme Completion Gate",
        },
    }

    txt_path = REPORT_DIR / "engineering_module_integration_readiness_gate_phase_28k.txt"
    json_path = REPORT_DIR / "engineering_module_integration_readiness_gate_phase_28k.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 28K Engineering Module Integration Readiness Gate",
                "================================================================",
                f"passed={not failures}",
                f"module_id={ready_result['module_id']}",
                f"ready_verdict={ready_result['verdict']}",
                f"ready={ready_result['ready']}",
                f"checks_passed={sum(1 for value in ready_result['checks'].values() if value)}",
                f"checks_total={len(ready_result['checks'])}",
                f"blocked_verdict={blocked_result['verdict']}",
                f"blocked_ready={blocked_result['ready']}",
                f"blocked_blockers={len(blocked_result['blockers'])}",
                f"mutation_performed={ready_result['mutation_performed']}",
                f"solver_executed={ready_result['solver_executed']}",
                f"runtime_mutation_performed={ready_result['runtime_mutation_performed']}",
                f"storage_mutation_performed={ready_result['storage_mutation_performed']}",
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
        print("FAIL_PHASE_28K_ENGINEERING_MODULE_INTEGRATION_READINESS_GATE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_28K_ENGINEERING_MODULE_INTEGRATION_READINESS_GATE")
    print("schema=LEAF_ENGINEERING_MODULE_INTEGRATION_READINESS_GATE_PHASE_28K_V1")
    print(f"module_id={ready_result['module_id']}")
    print(f"ready_verdict={ready_result['verdict']}")
    print(f"ready={ready_result['ready']}")
    print(f"checks_passed={sum(1 for value in ready_result['checks'].values() if value)}")
    print(f"checks_total={len(ready_result['checks'])}")
    print(f"blocked_verdict={blocked_result['verdict']}")
    print(f"blocked_ready={blocked_result['ready']}")
    print(f"blocked_blockers={len(blocked_result['blockers'])}")
    print(f"mutation_performed={ready_result['mutation_performed']}")
    print(f"solver_executed={ready_result['solver_executed']}")
    print(f"runtime_mutation_performed={ready_result['runtime_mutation_performed']}")
    print(f"storage_mutation_performed={ready_result['storage_mutation_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_28K_ENGINEERING_MODULE_INTEGRATION_READINESS_GATE_COMPLETE")
    print("next_phase=28L Programme Completion Gate")


if __name__ == "__main__":
    main()
