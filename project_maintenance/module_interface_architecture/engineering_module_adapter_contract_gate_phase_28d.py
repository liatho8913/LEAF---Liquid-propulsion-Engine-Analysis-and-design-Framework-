"""
Programme 28D Completion Gate.

Validates the Engineering Module Adapter Contract.
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

from leaf_qt.module_interface.adapter_contract import (
    EngineeringModuleAdapterCapability,
    EngineeringModuleAdapterStatus,
    build_engineering_module_adapter_contract,
    default_adapter_capability_map,
)
from leaf_qt.module_interface.interface_model import (
    EngineeringModuleDependency,
    EngineeringModuleInterfaceStatus,
    build_engineering_module_interface,
)


def main() -> None:
    for rel in [
        "leaf_qt/module_interface/__init__.py",
        "leaf_qt/module_interface/interface_model.py",
        "leaf_qt/module_interface/module_registry.py",
        "leaf_qt/module_interface/dependency_graph.py",
        "leaf_qt/module_interface/adapter_contract.py",
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
                reason="Regen demonstration module plugs into shared platform services.",
            ),
        ),
    )

    contract = build_engineering_module_adapter_contract(
        adapter_id="regen_demonstration_adapter",
        interface=interface,
        metadata={"gate": "28D"},
    )

    report = contract.report()
    failures = list(report["validation_failures"])

    expected_count = len(EngineeringModuleAdapterCapability)
    capability_report = report["capabilities"]

    if capability_report["capability_count"] != expected_count:
        failures.append(
            f"expected capability_count={expected_count}, actual={capability_report['capability_count']}"
        )

    dry_run_solver = contract.dry_run(
        EngineeringModuleAdapterCapability.SOLVER,
        payload={"input": "probe"},
    ).as_dict()

    if dry_run_solver["status"] != EngineeringModuleAdapterStatus.READY.value:
        failures.append(f"solver dry-run status mismatch: actual={dry_run_solver['status']}")

    if dry_run_solver["solver_executed"] is not False:
        failures.append("adapter dry-run must not execute solver")

    if dry_run_solver["mutation_performed"] is not False:
        failures.append("adapter dry-run must not mutate")

    if dry_run_solver["runtime_mutation_performed"] is not False:
        failures.append("adapter dry-run must not mutate runtime")

    if dry_run_solver["storage_mutation_performed"] is not False:
        failures.append("adapter dry-run must not mutate storage")

    partial_map = default_adapter_capability_map("partial_adapter")
    partial_map.pop(EngineeringModuleAdapterCapability.STORAGE)

    partial_contract = build_engineering_module_adapter_contract(
        adapter_id="partial_adapter",
        interface=interface,
        capability_map=partial_map,
    )

    partial_failures = partial_contract.validate_adapter()
    if not any("missing" in failure for failure in partial_failures):
        failures.append("partial adapter did not report missing capability map entry")

    blocked_result = partial_contract.dry_run(EngineeringModuleAdapterCapability.STORAGE).as_dict()
    if blocked_result["status"] != EngineeringModuleAdapterStatus.BLOCKED.value:
        failures.append("partial adapter storage dry-run should be blocked")

    report["dry_run_solver"] = dry_run_solver
    report["partial_adapter_failures"] = list(partial_failures)
    report["blocked_result"] = blocked_result
    report["gate"] = {
        "phase": "28D",
        "programme": "28",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_28D_ENGINEERING_MODULE_ADAPTER_CONTRACT_COMPLETE"
            if not failures
            else "PROGRAMME_28D_ENGINEERING_MODULE_ADAPTER_CONTRACT_FAILED"
        ),
        "next_phase": "28E Engineering Module Validation Contract",
    }

    txt_path = REPORT_DIR / "engineering_module_adapter_contract_gate_phase_28d.txt"
    json_path = REPORT_DIR / "engineering_module_adapter_contract_gate_phase_28d.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 28D Engineering Module Adapter Contract Gate",
                "==========================================================",
                f"passed={not failures}",
                f"adapter_id={report['adapter_id']}",
                f"module_id={report['module_id']}",
                f"capability_count={capability_report['capability_count']}",
                f"dry_run_solver_status={dry_run_solver['status']}",
                f"solver_executed={dry_run_solver['solver_executed']}",
                f"mutation_performed={dry_run_solver['mutation_performed']}",
                f"runtime_mutation_performed={dry_run_solver['runtime_mutation_performed']}",
                f"storage_mutation_performed={dry_run_solver['storage_mutation_performed']}",
                f"partial_adapter_failures={len(partial_failures)}",
                f"blocked_result_status={blocked_result['status']}",
                f"failures={len(failures)}",
                f"completion_notice={report['gate']['completion_notice']}",
                f"next_phase={report['gate']['next_phase']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if failures:
        print("FAIL_PHASE_28D_ENGINEERING_MODULE_ADAPTER_CONTRACT")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_28D_ENGINEERING_MODULE_ADAPTER_CONTRACT")
    print("schema=LEAF_ENGINEERING_MODULE_ADAPTER_CONTRACT_PHASE_28D_V1")
    print(f"adapter_id={report['adapter_id']}")
    print(f"module_id={report['module_id']}")
    print(f"capability_count={capability_report['capability_count']}")
    print(f"dry_run_solver_status={dry_run_solver['status']}")
    print(f"solver_executed={dry_run_solver['solver_executed']}")
    print(f"mutation_performed={dry_run_solver['mutation_performed']}")
    print(f"runtime_mutation_performed={dry_run_solver['runtime_mutation_performed']}")
    print(f"storage_mutation_performed={dry_run_solver['storage_mutation_performed']}")
    print(f"partial_adapter_failures={len(partial_failures)}")
    print(f"blocked_result_status={blocked_result['status']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_28D_ENGINEERING_MODULE_ADAPTER_CONTRACT_COMPLETE")
    print("next_phase=28E Engineering Module Validation Contract")


if __name__ == "__main__":
    main()
