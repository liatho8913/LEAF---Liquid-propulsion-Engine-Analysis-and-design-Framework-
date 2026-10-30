"""
Programme 28F Completion Gate.

Validates the Engineering Module Report Contract.
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
from leaf_qt.module_interface.report_contract import (
    EngineeringModuleReportSection,
    build_engineering_module_report_contract,
)
from leaf_qt.module_interface.validation_contract import (
    EngineeringModuleValidationMode,
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
        "leaf_qt/module_interface/report_contract.py",
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
                reason="Regen report contract plugs into shared platform services.",
            ),
        ),
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
        metadata={"gate": "28F"},
    )

    report = report_contract.report(
        report_id="regen_demonstration_report_probe",
        title="Regen Demonstration Report Probe",
        validation_result=validation_result,
        sections=(
            EngineeringModuleReportSection(
                section_id="inputs",
                title="Inputs",
                payload={"available": True},
            ),
            EngineeringModuleReportSection(
                section_id="validation",
                title="Validation",
                payload={"verdict": validation_result.verdict().value},
            ),
        ),
        summary={"purpose": "28F gate"},
    )

    package = report["package"]
    failures = list(report["contract_validation_failures"])
    failures.extend(package["validation_failures"])

    if package["schema"] != "LEAF_ENGINEERING_MODULE_REPORT_CONTRACT_PHASE_28F_V1":
        failures.append(f"package schema mismatch: {package['schema']}")

    if package["summary"]["validation_verdict"] != "PASS":
        failures.append(f"validation verdict mismatch: {package['summary']['validation_verdict']}")

    if package["summary"]["validation_passed"] is not True:
        failures.append("validation_passed should be true")

    if package["summary"]["section_count"] != 2:
        failures.append(f"section_count mismatch: {package['summary']['section_count']}")

    if package["mutation_performed"] is not False:
        failures.append("report contract must not mutate")

    if package["solver_executed"] is not False:
        failures.append("report contract must not execute solver")

    if package["runtime_mutation_performed"] is not False:
        failures.append("report contract must not mutate runtime")

    if package["storage_mutation_performed"] is not False:
        failures.append("report contract must not mutate storage")

    duplicate_package = report_contract.build_report(
        report_id="duplicate_section_probe",
        title="Duplicate Section Probe",
        validation_result=validation_result,
        sections=(
            EngineeringModuleReportSection("duplicate", "Duplicate A", {}),
            EngineeringModuleReportSection("duplicate", "Duplicate B", {}),
        ),
    )

    if not any("duplicate section_id" in failure for failure in duplicate_package.validate()):
        failures.append("duplicate section validation did not trigger")

    final_report = {
        "schema": "LEAF_ENGINEERING_MODULE_REPORT_CONTRACT_COMPLETION_PHASE_28F_V1",
        "report_contract": report,
        "duplicate_section_validation_failures": list(duplicate_package.validate()),
        "gate": {
            "phase": "28F",
            "programme": "28",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_28F_ENGINEERING_MODULE_REPORT_CONTRACT_COMPLETE"
                if not failures
                else "PROGRAMME_28F_ENGINEERING_MODULE_REPORT_CONTRACT_FAILED"
            ),
            "next_phase": "28G Engineering Module Workflow Contract",
        },
    }

    txt_path = REPORT_DIR / "engineering_module_report_contract_gate_phase_28f.txt"
    json_path = REPORT_DIR / "engineering_module_report_contract_gate_phase_28f.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 28F Engineering Module Report Contract Gate",
                "=========================================================",
                f"passed={not failures}",
                f"module_id={package['module_id']}",
                f"report_id={package['report_id']}",
                f"report_owner={package['summary']['report_owner']}",
                f"validation_verdict={package['summary']['validation_verdict']}",
                f"validation_passed={package['summary']['validation_passed']}",
                f"section_count={package['summary']['section_count']}",
                f"mutation_performed={package['mutation_performed']}",
                f"solver_executed={package['solver_executed']}",
                f"runtime_mutation_performed={package['runtime_mutation_performed']}",
                f"storage_mutation_performed={package['storage_mutation_performed']}",
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
        print("FAIL_PHASE_28F_ENGINEERING_MODULE_REPORT_CONTRACT")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_28F_ENGINEERING_MODULE_REPORT_CONTRACT")
    print("schema=LEAF_ENGINEERING_MODULE_REPORT_CONTRACT_PHASE_28F_V1")
    print(f"module_id={package['module_id']}")
    print(f"report_id={package['report_id']}")
    print(f"report_owner={package['summary']['report_owner']}")
    print(f"validation_verdict={package['summary']['validation_verdict']}")
    print(f"validation_passed={package['summary']['validation_passed']}")
    print(f"section_count={package['summary']['section_count']}")
    print(f"mutation_performed={package['mutation_performed']}")
    print(f"solver_executed={package['solver_executed']}")
    print(f"runtime_mutation_performed={package['runtime_mutation_performed']}")
    print(f"storage_mutation_performed={package['storage_mutation_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_28F_ENGINEERING_MODULE_REPORT_CONTRACT_COMPLETE")
    print("next_phase=28G Engineering Module Workflow Contract")


if __name__ == "__main__":
    main()
