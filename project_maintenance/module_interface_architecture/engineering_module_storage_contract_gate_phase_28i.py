"""
Programme 28I Completion Gate.

Validates the Engineering Module Storage Contract.
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
from leaf_qt.module_interface.storage_contract import (
    CANONICAL_STORAGE_FOLDERS,
    EngineeringModuleStorageAction,
    EngineeringModuleStorageDomain,
    EngineeringModuleStorageRequest,
    EngineeringModuleStorageRequestStatus,
    build_engineering_module_storage_contract,
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
                reason="Regen storage contract targets canonical storage through safe events.",
            ),
        ),
    )

    contract = build_engineering_module_storage_contract(
        interface=interface,
        metadata={"gate": "28I"},
    )

    design_report = contract.report(
        action=EngineeringModuleStorageAction.PREPARE_SAVE_DESIGN,
        domain=EngineeringModuleStorageDomain.DESIGN,
        storage_key="regen_demo_design",
        payload={"dry_run": True},
    )

    report_attach = contract.report(
        action=EngineeringModuleStorageAction.ATTACH_REPORT,
        domain=EngineeringModuleStorageDomain.REPORT,
        storage_key="regen_demo_report",
        payload={"report_id": "probe"},
    )

    snapshot_report = contract.report(
        action=EngineeringModuleStorageAction.REQUEST_STORAGE_SNAPSHOT,
        domain=EngineeringModuleStorageDomain.PROJECT,
        storage_key="project_snapshot",
    )

    invalid_key_request = contract.build_request(
        action=EngineeringModuleStorageAction.PREPARE_SAVE_DESIGN,
        domain=EngineeringModuleStorageDomain.DESIGN,
        storage_key="../unsafe_path",
    )
    invalid_key_result = contract.submit(invalid_key_request).as_dict()

    wrong_module_request = EngineeringModuleStorageRequest(
        module_id="wrong_module",
        action=EngineeringModuleStorageAction.PREPARE_SAVE_DESIGN,
        domain=EngineeringModuleStorageDomain.DESIGN,
        storage_key="safe_key",
    )
    wrong_module_result = contract.submit(wrong_module_request).as_dict()

    failures = []

    design = design_report["result"]
    attach = report_attach["result"]
    snapshot = snapshot_report["result"]

    if design["status"] != EngineeringModuleStorageRequestStatus.ACCEPTED.value:
        failures.append(f"design status mismatch: {design['status']}")

    if design["canonical_folder"] != "LEAF_Designs":
        failures.append(f"design canonical folder mismatch: {design['canonical_folder']}")

    if attach["canonical_folder"] != "LEAF_Reports":
        failures.append(f"report canonical folder mismatch: {attach['canonical_folder']}")

    if snapshot["canonical_folder"] != "LEAF_Projects":
        failures.append(f"project canonical folder mismatch: {snapshot['canonical_folder']}")

    if invalid_key_result["status"] != EngineeringModuleStorageRequestStatus.INVALID.value:
        failures.append("unsafe storage key should be invalid")

    if wrong_module_result["status"] != EngineeringModuleStorageRequestStatus.INVALID.value:
        failures.append("wrong module storage request should be invalid")

    expected_folders = {
        "PROJECT": "LEAF_Projects",
        "DESIGN": "LEAF_Designs",
        "REPORT": "LEAF_Reports",
        "EXPORT": "LEAF_Exports",
    }

    actual_folders = {domain.value: folder for domain, folder in CANONICAL_STORAGE_FOLDERS.items()}
    if actual_folders != expected_folders:
        failures.append(f"canonical folder map mismatch: {actual_folders}")

    for label, report in [
        ("design", design_report),
        ("attach", report_attach),
        ("snapshot", snapshot_report),
    ]:
        for flag in ["mutation_performed", "file_written", "file_deleted", "archive_performed"]:
            if report[flag] is not False:
                failures.append(f"{label} report {flag} must remain False")
            if report["result"][flag] is not False:
                failures.append(f"{label} result {flag} must remain False")
            if report["result"]["storage_event"].get(flag) is not False:
                failures.append(f"{label} storage_event {flag} must remain False")

    final_report = {
        "schema": "LEAF_ENGINEERING_MODULE_STORAGE_CONTRACT_COMPLETION_PHASE_28I_V1",
        "design_report": design_report,
        "report_attach": report_attach,
        "snapshot_report": snapshot_report,
        "invalid_key_result": invalid_key_result,
        "wrong_module_result": wrong_module_result,
        "gate": {
            "phase": "28I",
            "programme": "28",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_28I_ENGINEERING_MODULE_STORAGE_CONTRACT_COMPLETE"
                if not failures
                else "PROGRAMME_28I_ENGINEERING_MODULE_STORAGE_CONTRACT_FAILED"
            ),
            "next_phase": "28J Engineering Module Notification Contract",
        },
    }

    txt_path = REPORT_DIR / "engineering_module_storage_contract_gate_phase_28i.txt"
    json_path = REPORT_DIR / "engineering_module_storage_contract_gate_phase_28i.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 28I Engineering Module Storage Contract Gate",
                "==========================================================",
                f"passed={not failures}",
                f"module_id={interface.module_id}",
                f"design_status={design['status']}",
                f"design_canonical_folder={design['canonical_folder']}",
                f"report_canonical_folder={attach['canonical_folder']}",
                f"project_canonical_folder={snapshot['canonical_folder']}",
                f"invalid_key_status={invalid_key_result['status']}",
                f"wrong_module_status={wrong_module_result['status']}",
                f"mutation_performed={design['mutation_performed']}",
                f"file_written={design['file_written']}",
                f"file_deleted={design['file_deleted']}",
                f"archive_performed={design['archive_performed']}",
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
        print("FAIL_PHASE_28I_ENGINEERING_MODULE_STORAGE_CONTRACT")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_28I_ENGINEERING_MODULE_STORAGE_CONTRACT")
    print("schema=LEAF_ENGINEERING_MODULE_STORAGE_CONTRACT_PHASE_28I_V1")
    print(f"module_id={interface.module_id}")
    print(f"design_status={design['status']}")
    print(f"design_canonical_folder={design['canonical_folder']}")
    print(f"report_canonical_folder={attach['canonical_folder']}")
    print(f"project_canonical_folder={snapshot['canonical_folder']}")
    print(f"invalid_key_status={invalid_key_result['status']}")
    print(f"wrong_module_status={wrong_module_result['status']}")
    print(f"mutation_performed={design['mutation_performed']}")
    print(f"file_written={design['file_written']}")
    print(f"file_deleted={design['file_deleted']}")
    print(f"archive_performed={design['archive_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_28I_ENGINEERING_MODULE_STORAGE_CONTRACT_COMPLETE")
    print("next_phase=28J Engineering Module Notification Contract")


if __name__ == "__main__":
    main()
