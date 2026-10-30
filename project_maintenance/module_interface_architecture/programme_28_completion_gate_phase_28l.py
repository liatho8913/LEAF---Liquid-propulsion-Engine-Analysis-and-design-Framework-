"""
Programme 28L Completion Gate.

Signs off Programme 28: Modular Engineering Interface Platform.
"""

from __future__ import annotations

import importlib
import json
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORT_DIR = ROOT / "LEAF_Reports" / "module_interface_architecture"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

REQUIRED_FILES = [
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
]

REQUIRED_EXPORTS = [
    "EngineeringModuleCapability",
    "EngineeringModuleDependency",
    "EngineeringModuleInterface",
    "EngineeringModuleInterfaceStatus",
    "EngineeringModuleSurface",
    "build_engineering_module_interface",
    "EngineeringModuleRegistry",
    "build_engineering_module_registry",
    "EngineeringModuleDependencyGraph",
    "EngineeringModuleDependencyGraphReport",
    "build_engineering_module_dependency_graph",
    "EngineeringModuleAdapterCapability",
    "EngineeringModuleAdapterContract",
    "EngineeringModuleAdapterProtocol",
    "EngineeringModuleAdapterResult",
    "EngineeringModuleAdapterStatus",
    "build_engineering_module_adapter_contract",
    "default_adapter_capability_map",
    "EngineeringModuleValidationContract",
    "EngineeringModuleValidationFinding",
    "EngineeringModuleValidationMode",
    "EngineeringModuleValidationResult",
    "EngineeringModuleValidationSeverity",
    "EngineeringModuleValidationVerdict",
    "build_engineering_module_validation_contract",
    "EngineeringModuleReportContract",
    "EngineeringModuleReportPackage",
    "EngineeringModuleReportSection",
    "build_engineering_module_report_contract",
    "EngineeringModuleWorkflowContract",
    "EngineeringModuleWorkflowStepDefinition",
    "build_engineering_module_workflow_contract",
    "default_engineering_module_workflow_steps",
    "EngineeringModuleRuntimeAction",
    "EngineeringModuleRuntimeContract",
    "EngineeringModuleRuntimeRequest",
    "EngineeringModuleRuntimeRequestStatus",
    "EngineeringModuleRuntimeResult",
    "build_engineering_module_runtime_contract",
    "CANONICAL_STORAGE_FOLDERS",
    "EngineeringModuleStorageAction",
    "EngineeringModuleStorageContract",
    "EngineeringModuleStorageDomain",
    "EngineeringModuleStorageRequest",
    "EngineeringModuleStorageRequestStatus",
    "EngineeringModuleStorageResult",
    "build_engineering_module_storage_contract",
    "EngineeringModuleNotificationContract",
    "EngineeringModuleNotificationEvent",
    "EngineeringModuleNotificationLevel",
    "EngineeringModuleNotificationResult",
    "EngineeringModuleNotificationStatus",
    "EngineeringModuleNotificationTopic",
    "build_engineering_module_notification_contract",
    "EngineeringModuleIntegrationReadinessGate",
    "EngineeringModuleIntegrationReadinessResult",
    "EngineeringModuleIntegrationVerdict",
    "build_engineering_module_integration_readiness_gate",
]


def main() -> None:
    failures = []

    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.exists():
            failures.append(f"missing required file: {rel}")
            continue
        py_compile.compile(str(path), doraise=True)

    pkg = importlib.import_module("leaf_qt.module_interface")
    for name in REQUIRED_EXPORTS:
        if not hasattr(pkg, name):
            failures.append(f"missing module_interface package export: {name}")

    from leaf_qt.module_interface import (
        EngineeringModuleDependency,
        EngineeringModuleInterfaceStatus,
        EngineeringModuleReportSection,
        EngineeringModuleValidationMode,
        build_engineering_module_adapter_contract,
        build_engineering_module_dependency_graph,
        build_engineering_module_interface,
        build_engineering_module_integration_readiness_gate,
        build_engineering_module_notification_contract,
        build_engineering_module_registry,
        build_engineering_module_report_contract,
        build_engineering_module_runtime_contract,
        build_engineering_module_storage_contract,
        build_engineering_module_validation_contract,
        build_engineering_module_workflow_contract,
    )

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
                reason="Programme 28 completion gate verifies reusable module integration contracts.",
            ),
        ),
        metadata={"programme_completion": "28"},
    )

    workflow_platform = build_engineering_module_interface(
        module_id="workflow_platform_service",
        title="Workflow Platform Service",
        status=EngineeringModuleInterfaceStatus.READY,
        dependencies=(
            EngineeringModuleDependency(
                dependency_id="workflow_platform_provider",
                provides=("workflow.platform",),
                requires=(),
                optional=(),
                reason="Programme 26 provides workflow platform service.",
            ),
        ),
    )

    runtime_platform = build_engineering_module_interface(
        module_id="runtime_platform_service",
        title="Runtime Platform Service",
        status=EngineeringModuleInterfaceStatus.READY,
        dependencies=(
            EngineeringModuleDependency(
                dependency_id="runtime_platform_provider",
                provides=("runtime.platform",),
                requires=(),
                optional=(),
                reason="Runtime platform service provider for module interface gate.",
            ),
        ),
    )

    storage_platform = build_engineering_module_interface(
        module_id="storage_platform_service",
        title="Storage Platform Service",
        status=EngineeringModuleInterfaceStatus.READY,
        dependencies=(
            EngineeringModuleDependency(
                dependency_id="storage_platform_provider",
                provides=("storage.platform",),
                requires=(),
                optional=(),
                reason="Storage platform service provider for module interface gate.",
            ),
        ),
    )

    registry = build_engineering_module_registry(
        (workflow_platform, runtime_platform, storage_platform, interface)
    )
    dependency_graph = build_engineering_module_dependency_graph(registry)
    dependency_report = dependency_graph.report().as_dict()

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
        report_id="programme_28_completion_gate_module_report",
        title="Programme 28 Completion Gate Module Report",
        validation_result=validation_result,
        sections=(
            EngineeringModuleReportSection(
                section_id="summary",
                title="Summary",
                payload={"programme": "28", "ready": True},
            ),
        ),
    )

    workflow_contract = build_engineering_module_workflow_contract(interface=interface)
    runtime_contract = build_engineering_module_runtime_contract(
        interface=interface,
        runtime_reference="runtime:programme-28-completion",
    )
    storage_contract = build_engineering_module_storage_contract(interface=interface)
    notification_contract = build_engineering_module_notification_contract(interface=interface)

    readiness_gate = build_engineering_module_integration_readiness_gate(
        interface=interface,
        adapter_contract=adapter_contract,
        validation_result=validation_result,
        report_package=report_package,
        workflow_contract=workflow_contract,
        runtime_contract=runtime_contract,
        storage_contract=storage_contract,
        notification_contract=notification_contract,
        dependency_missing_requirements=dependency_graph.module_missing_requirements(
            interface.module_id
        ),
    )

    readiness_report = readiness_gate.report()
    readiness_result = readiness_report["result"]

    checks = {
        "interface_valid": not interface.validate(),
        "registry_valid": not registry.validate(),
        "dependency_graph_valid": not dependency_graph.validate(),
        "dependency_ready": dependency_graph.module_integration_ready(interface.module_id),
        "adapter_valid": not adapter_contract.validate_adapter(),
        "validation_passed": validation_result.passed(),
        "report_valid": not report_package.validate(),
        "workflow_valid": not workflow_contract.validate_contract(),
        "runtime_valid": not runtime_contract.validate_contract(),
        "storage_valid": not storage_contract.validate_contract(),
        "notification_valid": not notification_contract.validate_contract(),
        "integration_ready": readiness_result["ready"] is True,
        "non_mutating": (
            readiness_result["mutation_performed"] is False
            and readiness_result["solver_executed"] is False
            and readiness_result["runtime_mutation_performed"] is False
            and readiness_result["storage_mutation_performed"] is False
        ),
    }

    for check, passed in checks.items():
        if not passed:
            failures.append(f"Programme 28 completion check failed: {check}")

    final_report = {
        "schema": "LEAF_PROGRAMME_28_COMPLETION_GATE_PHASE_28L_V1",
        "programme": "28",
        "programme_name": "Modular Engineering Interface Platform",
        "phase": "28L",
        "required_files": REQUIRED_FILES,
        "required_exports": REQUIRED_EXPORTS,
        "checks": checks,
        "interface": interface.report(),
        "registry": registry.report(),
        "dependency_graph": dependency_report,
        "adapter": adapter_contract.report(),
        "validation": validation_result.as_dict(),
        "report_package": report_package.as_dict(),
        "workflow": workflow_contract.report(current_step_id="run_module_solver"),
        "runtime_contract_validation_failures": list(runtime_contract.validate_contract()),
        "storage_contract_validation_failures": list(storage_contract.validate_contract()),
        "notification_contract_validation_failures": list(notification_contract.validate_contract()),
        "integration_readiness": readiness_result,
        "status": {
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_28_COMPLETE_MODULAR_ENGINEERING_INTERFACE_PLATFORM_SIGNED_OFF"
                if not failures
                else "PROGRAMME_28_COMPLETION_GATE_FAILED"
            ),
            "next_programme": "29 Regen Demonstration Module Binding",
            "next_phase": "29A Regen Module Interface Binding",
        },
    }

    txt_path = REPORT_DIR / "programme_28_completion_gate_phase_28l.txt"
    json_path = REPORT_DIR / "programme_28_completion_gate_phase_28l.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 28 Completion Gate",
                "================================",
                f"passed={not failures}",
                "programme=28",
                "programme_name=Modular Engineering Interface Platform",
                f"required_files={len(REQUIRED_FILES)}",
                f"required_exports={len(REQUIRED_EXPORTS)}",
                f"module_id={interface.module_id}",
                f"registry_modules={registry.report()['module_count']}",
                f"dependency_missing={len(dependency_graph.module_missing_requirements(interface.module_id))}",
                f"readiness_verdict={readiness_result['verdict']}",
                f"integration_ready={readiness_result['ready']}",
                f"checks_passed={sum(1 for value in checks.values() if value)}",
                f"checks_total={len(checks)}",
                f"mutation_performed={readiness_result['mutation_performed']}",
                f"solver_executed={readiness_result['solver_executed']}",
                f"runtime_mutation_performed={readiness_result['runtime_mutation_performed']}",
                f"storage_mutation_performed={readiness_result['storage_mutation_performed']}",
                f"failures={len(failures)}",
                f"completion_notice={final_report['status']['completion_notice']}",
                f"next_programme={final_report['status']['next_programme']}",
                f"next_phase={final_report['status']['next_phase']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    json_path.write_text(json.dumps(final_report, indent=2), encoding="utf-8")

    if failures:
        print("FAIL_PHASE_28L_PROGRAMME_COMPLETION_GATE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_28L_PROGRAMME_COMPLETION_GATE")
    print("schema=LEAF_PROGRAMME_28_COMPLETION_GATE_PHASE_28L_V1")
    print("programme=28")
    print("programme_name=Modular Engineering Interface Platform")
    print(f"required_files={len(REQUIRED_FILES)}")
    print(f"required_exports={len(REQUIRED_EXPORTS)}")
    print(f"module_id={interface.module_id}")
    print(f"registry_modules={registry.report()['module_count']}")
    print(f"dependency_missing={len(dependency_graph.module_missing_requirements(interface.module_id))}")
    print(f"readiness_verdict={readiness_result['verdict']}")
    print(f"integration_ready={readiness_result['ready']}")
    print(f"checks_passed={sum(1 for value in checks.values() if value)}")
    print(f"checks_total={len(checks)}")
    print(f"mutation_performed={readiness_result['mutation_performed']}")
    print(f"solver_executed={readiness_result['solver_executed']}")
    print(f"runtime_mutation_performed={readiness_result['runtime_mutation_performed']}")
    print(f"storage_mutation_performed={readiness_result['storage_mutation_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_28_COMPLETE_MODULAR_ENGINEERING_INTERFACE_PLATFORM_SIGNED_OFF")
    print("next_programme=29 Regen Demonstration Module Binding")
    print("next_phase=29A Regen Module Interface Binding")


if __name__ == "__main__":
    main()
