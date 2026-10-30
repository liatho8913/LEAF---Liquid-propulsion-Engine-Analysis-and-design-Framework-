"""
Programme 28H Completion Gate.

Validates the Engineering Module Runtime Contract.
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
from leaf_qt.module_interface.runtime_contract import (
    EngineeringModuleRuntimeAction,
    EngineeringModuleRuntimeRequest,
    EngineeringModuleRuntimeRequestStatus,
    build_engineering_module_runtime_contract,
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
                reason="Regen runtime contract requests runtime actions through safe events.",
            ),
        ),
    )

    contract = build_engineering_module_runtime_contract(
        interface=interface,
        runtime_reference="runtime:module-interface-28h",
        metadata={"gate": "28H"},
    )

    execute_report = contract.report(
        action=EngineeringModuleRuntimeAction.REQUEST_SOLVER_EXECUTION,
        payload={"dry_run": True, "source": "28H gate"},
    )

    snapshot_report = contract.report(
        action=EngineeringModuleRuntimeAction.REQUEST_STATE_SNAPSHOT,
        payload={"scope": "module"},
    )

    noop_report = contract.report(
        action=EngineeringModuleRuntimeAction.NO_OP,
    )

    invalid_request = EngineeringModuleRuntimeRequest(
        module_id="wrong_module",
        action=EngineeringModuleRuntimeAction.REQUEST_SOLVER_EXECUTION,
        payload={},
        runtime_reference="runtime:module-interface-28h",
    )
    invalid_result = contract.submit(invalid_request).as_dict()

    reports = {
        "execute": execute_report,
        "snapshot": snapshot_report,
        "noop": noop_report,
        "invalid": invalid_result,
    }

    failures = []

    execute = execute_report["result"]
    snapshot = snapshot_report["result"]
    noop = noop_report["result"]

    if execute["status"] != EngineeringModuleRuntimeRequestStatus.ACCEPTED.value:
        failures.append(f"execute status mismatch: {execute['status']}")

    if execute["accepted"] is not True:
        failures.append("runtime execute request should be accepted as event")

    if execute["solver_executed"] is not False:
        failures.append("runtime contract must not execute solver")

    if execute["runtime_mutation_performed"] is not False:
        failures.append("runtime contract must not mutate runtime")

    if execute["storage_mutation_performed"] is not False:
        failures.append("runtime contract must not mutate storage")

    if execute["emitted_event"].get("mutation_performed") is not False:
        failures.append("emitted event must not indicate mutation")

    if snapshot["status"] != EngineeringModuleRuntimeRequestStatus.ACCEPTED.value:
        failures.append(f"snapshot status mismatch: {snapshot['status']}")

    if noop["status"] != EngineeringModuleRuntimeRequestStatus.ACCEPTED.value:
        failures.append(f"noop status mismatch: {noop['status']}")

    if invalid_result["status"] != EngineeringModuleRuntimeRequestStatus.INVALID.value:
        failures.append(f"invalid request status mismatch: {invalid_result['status']}")

    if invalid_result["accepted"] is not False:
        failures.append("invalid module request should not be accepted")

    for label, report in [
        ("execute", execute_report),
        ("snapshot", snapshot_report),
        ("noop", noop_report),
    ]:
        for flag in [
            "mutation_performed",
            "solver_executed",
            "runtime_mutation_performed",
            "storage_mutation_performed",
        ]:
            if report[flag] is not False:
                failures.append(f"{label} report {flag} must remain False")

    final_report = {
        "schema": "LEAF_ENGINEERING_MODULE_RUNTIME_CONTRACT_COMPLETION_PHASE_28H_V1",
        "reports": reports,
        "gate": {
            "phase": "28H",
            "programme": "28",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_28H_ENGINEERING_MODULE_RUNTIME_CONTRACT_COMPLETE"
                if not failures
                else "PROGRAMME_28H_ENGINEERING_MODULE_RUNTIME_CONTRACT_FAILED"
            ),
            "next_phase": "28I Engineering Module Storage Contract",
        },
    }

    txt_path = REPORT_DIR / "engineering_module_runtime_contract_gate_phase_28h.txt"
    json_path = REPORT_DIR / "engineering_module_runtime_contract_gate_phase_28h.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 28H Engineering Module Runtime Contract Gate",
                "==========================================================",
                f"passed={not failures}",
                f"module_id={interface.module_id}",
                f"execute_status={execute['status']}",
                f"execute_accepted={execute['accepted']}",
                f"snapshot_status={snapshot['status']}",
                f"noop_status={noop['status']}",
                f"invalid_status={invalid_result['status']}",
                f"solver_executed={execute['solver_executed']}",
                f"mutation_performed={execute['mutation_performed']}",
                f"runtime_mutation_performed={execute['runtime_mutation_performed']}",
                f"storage_mutation_performed={execute['storage_mutation_performed']}",
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
        print("FAIL_PHASE_28H_ENGINEERING_MODULE_RUNTIME_CONTRACT")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_28H_ENGINEERING_MODULE_RUNTIME_CONTRACT")
    print("schema=LEAF_ENGINEERING_MODULE_RUNTIME_CONTRACT_PHASE_28H_V1")
    print(f"module_id={interface.module_id}")
    print(f"execute_status={execute['status']}")
    print(f"execute_accepted={execute['accepted']}")
    print(f"snapshot_status={snapshot['status']}")
    print(f"noop_status={noop['status']}")
    print(f"invalid_status={invalid_result['status']}")
    print(f"solver_executed={execute['solver_executed']}")
    print(f"mutation_performed={execute['mutation_performed']}")
    print(f"runtime_mutation_performed={execute['runtime_mutation_performed']}")
    print(f"storage_mutation_performed={execute['storage_mutation_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_28H_ENGINEERING_MODULE_RUNTIME_CONTRACT_COMPLETE")
    print("next_phase=28I Engineering Module Storage Contract")


if __name__ == "__main__":
    main()
