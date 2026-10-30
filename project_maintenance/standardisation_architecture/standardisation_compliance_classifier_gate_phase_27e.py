"""
Programme 27E Completion Gate.

Validates the Standardisation Compliance Classifier.
"""

from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORT_DIR = ROOT / "LEAF_Reports" / "standardisation_architecture"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

from leaf_qt.standardisation.compliance_classifier import (
    StandardisationComplianceCategory,
    StandardisationRepairPriority,
    build_standardisation_compliance_classifier,
)
from leaf_qt.standardisation.scanner import build_standardisation_scanner


def main() -> None:
    for rel in [
        "leaf_qt/standardisation/__init__.py",
        "leaf_qt/standardisation/inventory_model.py",
        "leaf_qt/standardisation/rule_registry.py",
        "leaf_qt/standardisation/scanner.py",
        "leaf_qt/standardisation/finding_report_owner.py",
        "leaf_qt/standardisation/compliance_classifier.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    scan_result = build_standardisation_scanner(ROOT).scan()
    classifier = build_standardisation_compliance_classifier(scan_result)
    report = classifier.report()

    failures = []

    if report["schema"] != "LEAF_STANDARDISATION_COMPLIANCE_CLASSIFIER_PHASE_27E_V1":
        failures.append(f"schema mismatch: actual={report['schema']}")

    if report["mutation_performed"] is not False:
        failures.append("compliance classifier must not mutate repository")

    if report["total_findings"] != len(scan_result.findings):
        failures.append("classified finding count does not match scan finding count")

    category_total = sum(report["category_counts"].values())
    if category_total != report["total_findings"]:
        failures.append(
            f"category count total mismatch: expected={report['total_findings']}, actual={category_total}"
        )

    priority_total = sum(report["priority_counts"].values())
    if priority_total != report["total_findings"]:
        failures.append(
            f"priority count total mismatch: expected={report['total_findings']}, actual={priority_total}"
        )

    if report["category_counts"][StandardisationComplianceCategory.GATE_STANDARDISATION_ISSUE.value] <= 0:
        failures.append("expected at least one gate standardisation issue")

    if report["priority_counts"][StandardisationRepairPriority.MEDIUM.value] <= 0:
        failures.append("expected at least one medium-priority classified finding")

    if any(item.get("mutation_allowed") for item in report["classified_findings"]):
        failures.append("classifier must not mark mutation_allowed true")

    report["gate"] = {
        "phase": "27E",
        "programme": "27",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_27E_STANDARDISATION_COMPLIANCE_CLASSIFIER_COMPLETE"
            if not failures
            else "PROGRAMME_27E_STANDARDISATION_COMPLIANCE_CLASSIFIER_FAILED"
        ),
        "next_phase": "27F Standardisation Repair Plan Owner",
    }

    txt_path = REPORT_DIR / "standardisation_compliance_classifier_gate_phase_27e.txt"
    json_path = REPORT_DIR / "standardisation_compliance_classifier_gate_phase_27e.json"

    top_category = report["top_categories"][0]["category"] if report["top_categories"] else "NONE"
    top_category_count = report["top_categories"][0]["count"] if report["top_categories"] else 0
    top_priority = report["top_priorities"][0]["priority"] if report["top_priorities"] else "NONE"
    top_priority_count = report["top_priorities"][0]["count"] if report["top_priorities"] else 0

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 27E Standardisation Compliance Classifier Gate",
                "============================================================",
                f"passed={not failures}",
                f"total_findings={report['total_findings']}",
                f"top_category={top_category}",
                f"top_category_count={top_category_count}",
                f"top_priority={top_priority}",
                f"top_priority_count={top_priority_count}",
                f"gate_issues={report['category_counts'][StandardisationComplianceCategory.GATE_STANDARDISATION_ISSUE.value]}",
                f"platform_structural_issues={report['category_counts'][StandardisationComplianceCategory.PLATFORM_STRUCTURAL_ISSUE.value]}",
                f"legacy_noise={report['category_counts'][StandardisationComplianceCategory.LEGACY_EXPECTED_NOISE.value]}",
                f"mutation_performed={report['mutation_performed']}",
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
        print("FAIL_PHASE_27E_STANDARDISATION_COMPLIANCE_CLASSIFIER")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_27E_STANDARDISATION_COMPLIANCE_CLASSIFIER")
    print("schema=LEAF_STANDARDISATION_COMPLIANCE_CLASSIFIER_PHASE_27E_V1")
    print(f"total_findings={report['total_findings']}")
    print(f"top_category={top_category}")
    print(f"top_category_count={top_category_count}")
    print(f"top_priority={top_priority}")
    print(f"top_priority_count={top_priority_count}")
    print(f"gate_issues={report['category_counts'][StandardisationComplianceCategory.GATE_STANDARDISATION_ISSUE.value]}")
    print(f"platform_structural_issues={report['category_counts'][StandardisationComplianceCategory.PLATFORM_STRUCTURAL_ISSUE.value]}")
    print(f"legacy_noise={report['category_counts'][StandardisationComplianceCategory.LEGACY_EXPECTED_NOISE.value]}")
    print(f"mutation_performed={report['mutation_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_27E_STANDARDISATION_COMPLIANCE_CLASSIFIER_COMPLETE")
    print("next_phase=27F Standardisation Repair Plan Owner")


if __name__ == "__main__":
    main()
