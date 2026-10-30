"""
Programme 28J Completion Gate.

Validates the Engineering Module Notification Contract.
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
from leaf_qt.module_interface.notification_contract import (
    EngineeringModuleNotificationEvent,
    EngineeringModuleNotificationLevel,
    EngineeringModuleNotificationStatus,
    EngineeringModuleNotificationTopic,
    build_engineering_module_notification_contract,
)


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
                reason="Regen notification contract emits safe module events.",
            ),
        ),
    )

    contract = build_engineering_module_notification_contract(
        interface=interface,
        metadata={"gate": "28J"},
    )

    success_report = contract.report(
        topic=EngineeringModuleNotificationTopic.MODULE_STATUS,
        level=EngineeringModuleNotificationLevel.SUCCESS,
        title="Module interface ready",
        message="The regen demonstration module notification contract is ready.",
        payload={"gate": "28J"},
    )

    warning_report = contract.report(
        topic=EngineeringModuleNotificationTopic.VALIDATION,
        level=EngineeringModuleNotificationLevel.WARNING,
        title="Validation warning probe",
        message="This is a non-delivered validation warning event probe.",
    )

    invalid_event = EngineeringModuleNotificationEvent(
        module_id="wrong_module",
        topic=EngineeringModuleNotificationTopic.MODULE_STATUS,
        level=EngineeringModuleNotificationLevel.INFO,
        title="Wrong module probe",
        message="This should be rejected.",
    )
    invalid_result = contract.emit(invalid_event).as_dict()

    empty_event = EngineeringModuleNotificationEvent(
        module_id=interface.module_id,
        topic=EngineeringModuleNotificationTopic.MODULE_STATUS,
        level=EngineeringModuleNotificationLevel.INFO,
        title="",
        message="This should be rejected.",
    )
    empty_result = contract.emit(empty_event).as_dict()

    success = success_report["result"]
    warning = warning_report["result"]

    failures = []

    if success["status"] != EngineeringModuleNotificationStatus.ACCEPTED.value:
        failures.append(f"success status mismatch: {success['status']}")

    if success["accepted"] is not True:
        failures.append("success notification should be accepted as event")

    if success["notification_delivered"] is not False:
        failures.append("module notification contract must not deliver notifications")

    if success["event"].get("delivery_owned_by_module") is not False:
        failures.append("module must not own notification delivery")

    if warning["status"] != EngineeringModuleNotificationStatus.ACCEPTED.value:
        failures.append(f"warning status mismatch: {warning['status']}")

    if invalid_result["status"] != EngineeringModuleNotificationStatus.INVALID.value:
        failures.append(f"invalid module event status mismatch: {invalid_result['status']}")

    if empty_result["status"] != EngineeringModuleNotificationStatus.INVALID.value:
        failures.append(f"empty title event status mismatch: {empty_result['status']}")

    for label, report in [
        ("success", success_report),
        ("warning", warning_report),
    ]:
        for flag in [
            "mutation_performed",
            "solver_executed",
            "runtime_mutation_performed",
            "storage_mutation_performed",
            "file_written",
            "file_deleted",
            "archive_performed",
        ]:
            if report[flag] is not False:
                failures.append(f"{label} report {flag} must remain False")
            if report["result"][flag] is not False:
                failures.append(f"{label} result {flag} must remain False")
            if report["result"]["event"].get(flag) is not False:
                failures.append(f"{label} event {flag} must remain False")

    if success_report["delivery_policy"]["module_owns_delivery"] is not False:
        failures.append("delivery policy must not allow module-owned delivery")

    final_report = {
        "schema": "LEAF_ENGINEERING_MODULE_NOTIFICATION_CONTRACT_COMPLETION_PHASE_28J_V1",
        "success_report": success_report,
        "warning_report": warning_report,
        "invalid_result": invalid_result,
        "empty_result": empty_result,
        "gate": {
            "phase": "28J",
            "programme": "28",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_28J_ENGINEERING_MODULE_NOTIFICATION_CONTRACT_COMPLETE"
                if not failures
                else "PROGRAMME_28J_ENGINEERING_MODULE_NOTIFICATION_CONTRACT_FAILED"
            ),
            "next_phase": "28K Engineering Module Integration Readiness Gate",
        },
    }

    txt_path = REPORT_DIR / "engineering_module_notification_contract_gate_phase_28j.txt"
    json_path = REPORT_DIR / "engineering_module_notification_contract_gate_phase_28j.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 28J Engineering Module Notification Contract Gate",
                "===============================================================",
                f"passed={not failures}",
                f"module_id={interface.module_id}",
                f"success_status={success['status']}",
                f"success_accepted={success['accepted']}",
                f"warning_status={warning['status']}",
                f"invalid_status={invalid_result['status']}",
                f"empty_status={empty_result['status']}",
                f"notification_delivered={success['notification_delivered']}",
                f"module_owns_delivery={success_report['delivery_policy']['module_owns_delivery']}",
                f"mutation_performed={success['mutation_performed']}",
                f"solver_executed={success['solver_executed']}",
                f"runtime_mutation_performed={success['runtime_mutation_performed']}",
                f"storage_mutation_performed={success['storage_mutation_performed']}",
                f"file_written={success['file_written']}",
                f"file_deleted={success['file_deleted']}",
                f"archive_performed={success['archive_performed']}",
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
        print("FAIL_PHASE_28J_ENGINEERING_MODULE_NOTIFICATION_CONTRACT")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_28J_ENGINEERING_MODULE_NOTIFICATION_CONTRACT")
    print("schema=LEAF_ENGINEERING_MODULE_NOTIFICATION_CONTRACT_PHASE_28J_V1")
    print(f"module_id={interface.module_id}")
    print(f"success_status={success['status']}")
    print(f"success_accepted={success['accepted']}")
    print(f"warning_status={warning['status']}")
    print(f"invalid_status={invalid_result['status']}")
    print(f"empty_status={empty_result['status']}")
    print(f"notification_delivered={success['notification_delivered']}")
    print(f"module_owns_delivery={success_report['delivery_policy']['module_owns_delivery']}")
    print(f"mutation_performed={success['mutation_performed']}")
    print(f"solver_executed={success['solver_executed']}")
    print(f"runtime_mutation_performed={success['runtime_mutation_performed']}")
    print(f"storage_mutation_performed={success['storage_mutation_performed']}")
    print(f"file_written={success['file_written']}")
    print(f"file_deleted={success['file_deleted']}")
    print(f"archive_performed={success['archive_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_28J_ENGINEERING_MODULE_NOTIFICATION_CONTRACT_COMPLETE")
    print("next_phase=28K Engineering Module Integration Readiness Gate")


if __name__ == "__main__":
    main()
