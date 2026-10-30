"""
Programme 27J Completion Gate.

Signs off Programme 27: Project-Wide Standardisation Platform.
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

REPORT_DIR = ROOT / "LEAF_Reports" / "standardisation_architecture"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

REQUIRED_FILES = [
    "leaf_qt/standardisation/__init__.py",
    "leaf_qt/standardisation/inventory_model.py",
    "leaf_qt/standardisation/rule_registry.py",
    "leaf_qt/standardisation/scanner.py",
    "leaf_qt/standardisation/finding_report_owner.py",
    "leaf_qt/standardisation/compliance_classifier.py",
    "leaf_qt/standardisation/repair_plan_owner.py",
    "leaf_qt/standardisation/safety_gate.py",
    "leaf_qt/standardisation/dry_run_executor.py",
    "leaf_qt/standardisation/report_router.py",
]

REQUIRED_EXPORTS = [
    "StandardisationArea",
    "StandardisationInventoryItem",
    "StandardisationInventoryModel",
    "build_standardisation_inventory_model",
    "StandardisationRule",
    "StandardisationRuleRegistry",
    "StandardisationRuleSeverity",
    "build_default_standardisation_rule_registry",
    "StandardisationFinding",
    "StandardisationFindingLevel",
    "StandardisationScanResult",
    "StandardisationScanner",
    "build_standardisation_scanner",
    "StandardisationFindingReportOwner",
    "StandardisationFindingReportPackage",
    "build_standardisation_finding_report_owner",
    "ClassifiedStandardisationFinding",
    "StandardisationComplianceCategory",
    "StandardisationComplianceClassificationReport",
    "StandardisationComplianceClassifier",
    "StandardisationRepairPriority",
    "build_standardisation_compliance_classifier",
    "StandardisationRepairActionType",
    "StandardisationRepairPlan",
    "StandardisationRepairPlanItem",
    "StandardisationRepairPlanOwner",
    "build_standardisation_repair_plan_owner",
    "StandardisationSafetyGate",
    "StandardisationSafetyRequest",
    "StandardisationSafetyResult",
    "StandardisationSafetyVerdict",
    "build_standardisation_safety_gate",
    "StandardisationDryRunAction",
    "StandardisationDryRunExecutor",
    "StandardisationDryRunResult",
    "build_standardisation_dry_run_executor",
    "StandardisationReportRouter",
    "StandardisationRoutedReport",
    "build_standardisation_report_router",
]


def main() -> None:
    failures = []

    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.exists():
            failures.append(f"missing required file: {rel}")
            continue
        py_compile.compile(str(path), doraise=True)

    standardisation_pkg = importlib.import_module("leaf_qt.standardisation")

    for name in REQUIRED_EXPORTS:
        if not hasattr(standardisation_pkg, name):
            failures.append(f"missing standardisation package export: {name}")

    from leaf_qt.standardisation import (
        StandardisationSafetyRequest,
        build_default_standardisation_rule_registry,
        build_standardisation_compliance_classifier,
        build_standardisation_dry_run_executor,
        build_standardisation_finding_report_owner,
        build_standardisation_inventory_model,
        build_standardisation_repair_plan_owner,
        build_standardisation_report_router,
        build_standardisation_safety_gate,
        build_standardisation_scanner,
    )

    inventory = build_standardisation_inventory_model()
    registry = build_default_standardisation_rule_registry()
    scanner = build_standardisation_scanner(ROOT, registry=registry)
    scan_result = scanner.scan()

    finding_owner = build_standardisation_finding_report_owner(scan_result)
    finding_report = finding_owner.build_report().as_dict()

    classification = build_standardisation_compliance_classifier(scan_result).classify()
    classification_report = classification.as_dict()

    repair_plan = build_standardisation_repair_plan_owner(classification).build_plan()
    repair_plan_report = repair_plan.as_dict()

    safety_request = StandardisationSafetyRequest(
        manual_approval=True,
        dry_run=True,
        mutation_requested=False,
        deletion_requested=False,
        archive_requested=False,
        checkpoint_reference="checkpoint:programme-27-completion-gate",
    )

    safety_report = build_standardisation_safety_gate(repair_plan).report(safety_request)

    dry_run_report = build_standardisation_dry_run_executor(repair_plan).report(
        safety_request,
        limit=50,
    )

    router = build_standardisation_report_router(ROOT)
    routed = router.route_report(
        report_id="programme_27_completion_gate_routed_summary",
        title="LEAF Programme 27 Routed Completion Summary",
        payload={
            "programme": "27",
            "programme_name": "Project-Wide Standardisation Platform",
            "inventory_items": inventory.report()["item_count"],
            "rules": registry.report()["rule_count"],
            "scanned_python_files": scan_result.scanned_python_files,
            "scan_findings": len(scan_result.findings),
            "repair_plan_items": len(repair_plan.planned_items),
            "dry_run_actions": dry_run_report["result"]["action_count"],
            "mutation_performed": False,
        },
    )

    inventory_report = inventory.report()
    registry_report = registry.report()
    routed_report = routed.as_dict()

    if inventory_report["item_count"] != 9:
        failures.append(f"expected inventory item_count=9, actual={inventory_report['item_count']}")

    if registry_report["rule_count"] != 9:
        failures.append(f"expected registry rule_count=9, actual={registry_report['rule_count']}")

    if scan_result.scanned_python_files <= 0:
        failures.append("standardisation scanner did not scan Python files")

    if finding_report["mutation_performed"] is not False:
        failures.append("finding report owner must not mutate repository")

    if classification_report["mutation_performed"] is not False:
        failures.append("compliance classifier must not mutate repository")

    if repair_plan_report["automatic_repair_enabled"] is not False:
        failures.append("repair plan must not enable automatic repair")

    if repair_plan_report["mutation_performed"] is not False:
        failures.append("repair plan owner must not mutate repository")

    if safety_report["result"]["verdict"] != "SAFE_FOR_DRY_RUN_ONLY":
        failures.append(f"safety gate verdict mismatch: {safety_report['result']['verdict']}")

    if safety_report["result"]["dry_run_only"] is not True:
        failures.append("safety gate must remain dry-run only")

    if dry_run_report["result"]["mutation_performed"] is not False:
        failures.append("dry-run executor must not mutate repository")

    if dry_run_report["policy"]["mutation_allowed"] is not False:
        failures.append("dry-run policy must not allow mutation")

    if routed_report["mutation_scope"] != "LEAF_Reports_only":
        failures.append(f"report router mutation_scope mismatch: {routed_report['mutation_scope']}")

    if routed_report["mutation_performed"] is not False:
        failures.append("report router must not report mutation")

    final_report = {
        "schema": "LEAF_PROGRAMME_27_COMPLETION_GATE_PHASE_27J_V1",
        "programme": "27",
        "programme_name": "Project-Wide Standardisation Platform",
        "phase": "27J",
        "required_files": REQUIRED_FILES,
        "required_exports": REQUIRED_EXPORTS,
        "inventory": inventory_report,
        "registry": registry_report,
        "scan_summary": scan_result.as_dict(),
        "finding_report_summary": finding_report["summary"],
        "classification_summary": {
            "total_findings": classification_report["total_findings"],
            "category_counts": classification_report["category_counts"],
            "priority_counts": classification_report["priority_counts"],
        },
        "repair_plan_summary": {
            "source_total_findings": repair_plan_report["source_total_findings"],
            "planned_item_count": repair_plan_report["planned_item_count"],
            "automatic_repair_enabled": repair_plan_report["automatic_repair_enabled"],
            "mutation_performed": repair_plan_report["mutation_performed"],
        },
        "safety": safety_report["result"],
        "dry_run": dry_run_report["result"],
        "routed_report": routed_report,
        "status": {
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_27_COMPLETE_PROJECT_WIDE_STANDARDISATION_PLATFORM_SIGNED_OFF"
                if not failures
                else "PROGRAMME_27_COMPLETION_GATE_FAILED"
            ),
            "next_programme": "28 Modular Engineering Interface Platform",
            "next_phase": "28A Engineering Module Interface Model",
        },
    }

    txt_path = REPORT_DIR / "programme_27_completion_gate_phase_27j.txt"
    json_path = REPORT_DIR / "programme_27_completion_gate_phase_27j.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 27 Completion Gate",
                "================================",
                f"passed={not failures}",
                "programme=27",
                "programme_name=Project-Wide Standardisation Platform",
                f"required_files={len(REQUIRED_FILES)}",
                f"required_exports={len(REQUIRED_EXPORTS)}",
                f"inventory_items={inventory_report['item_count']}",
                f"rules={registry_report['rule_count']}",
                f"scanned_python_files={scan_result.scanned_python_files}",
                f"scan_findings={len(scan_result.findings)}",
                f"repair_plan_items={len(repair_plan.planned_items)}",
                f"safety_verdict={safety_report['result']['verdict']}",
                f"dry_run_actions={dry_run_report['result']['action_count']}",
                f"automatic_repair_enabled={repair_plan_report['automatic_repair_enabled']}",
                f"mutation_performed={dry_run_report['result']['mutation_performed']}",
                f"routed_report={routed_report['json_path']}",
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
        print("FAIL_PHASE_27J_PROGRAMME_COMPLETION_GATE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_27J_PROGRAMME_COMPLETION_GATE")
    print("schema=LEAF_PROGRAMME_27_COMPLETION_GATE_PHASE_27J_V1")
    print("programme=27")
    print("programme_name=Project-Wide Standardisation Platform")
    print(f"required_files={len(REQUIRED_FILES)}")
    print(f"required_exports={len(REQUIRED_EXPORTS)}")
    print(f"inventory_items={inventory_report['item_count']}")
    print(f"rules={registry_report['rule_count']}")
    print(f"scanned_python_files={scan_result.scanned_python_files}")
    print(f"scan_findings={len(scan_result.findings)}")
    print(f"repair_plan_items={len(repair_plan.planned_items)}")
    print(f"safety_verdict={safety_report['result']['verdict']}")
    print(f"dry_run_actions={dry_run_report['result']['action_count']}")
    print(f"automatic_repair_enabled={repair_plan_report['automatic_repair_enabled']}")
    print(f"mutation_performed={dry_run_report['result']['mutation_performed']}")
    print(f"routed_report={routed_report['json_path']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_27_COMPLETE_PROJECT_WIDE_STANDARDISATION_PLATFORM_SIGNED_OFF")
    print("next_programme=28 Modular Engineering Interface Platform")
    print("next_phase=28A Engineering Module Interface Model")


if __name__ == "__main__":
    main()
