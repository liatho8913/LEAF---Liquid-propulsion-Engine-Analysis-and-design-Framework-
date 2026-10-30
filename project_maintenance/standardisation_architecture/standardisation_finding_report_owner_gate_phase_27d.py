"""
Programme 27D Completion Gate.

Validates the Standardisation Finding Report Owner.
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

from leaf_qt.standardisation.finding_report_owner import (
    build_standardisation_finding_report_owner,
)
from leaf_qt.standardisation.scanner import build_standardisation_scanner


def main() -> None:
    for rel in [
        "leaf_qt/standardisation/__init__.py",
        "leaf_qt/standardisation/inventory_model.py",
        "leaf_qt/standardisation/rule_registry.py",
        "leaf_qt/standardisation/scanner.py",
        "leaf_qt/standardisation/finding_report_owner.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    scan_result = build_standardisation_scanner(ROOT).scan()
    owner = build_standardisation_finding_report_owner(scan_result)
    package = owner.build_report()
    report = package.as_dict()

    summary = report["summary"]
    sections = report["sections"]
    failures = []

    required_sections = [
        "finding_counts",
        "top_rules",
        "top_paths",
        "errors",
        "warnings",
        "infos",
        "actionable_priority",
    ]

    for section in required_sections:
        if section not in sections:
            failures.append(f"missing report section: {section}")

    if report["schema"] != "LEAF_STANDARDISATION_FINDING_REPORT_OWNER_PHASE_27D_V1":
        failures.append(f"schema mismatch: actual={report['schema']}")

    if report["mutation_performed"] is not False:
        failures.append("finding report owner must not mutate repository")

    if summary["mutation_performed"] is not False:
        failures.append("summary mutation flag must remain false")

    if summary["scanned_python_files"] <= 0:
        failures.append("report owner received no scanned Python files")

    if summary["total_findings"] != (
        summary["info_findings"] + summary["warning_findings"] + summary["error_findings"]
    ):
        failures.append("finding count totals do not reconcile")

    if not sections["top_rules"] and summary["total_findings"] > 0:
        failures.append("top_rules should not be empty when findings exist")

    if not sections["actionable_priority"] and summary["total_findings"] > 0:
        failures.append("actionable_priority should not be empty when findings exist")

    report["gate"] = {
        "phase": "27D",
        "programme": "27",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_27D_STANDARDISATION_FINDING_REPORT_OWNER_COMPLETE"
            if not failures
            else "PROGRAMME_27D_STANDARDISATION_FINDING_REPORT_OWNER_FAILED"
        ),
        "next_phase": "27E Standardisation Compliance Classifier",
    }

    txt_path = REPORT_DIR / "standardisation_finding_report_owner_gate_phase_27d.txt"
    json_path = REPORT_DIR / "standardisation_finding_report_owner_gate_phase_27d.json"

    top_rule = sections["top_rules"][0]["rule_id"] if sections["top_rules"] else "NONE"
    top_rule_count = sections["top_rules"][0]["count"] if sections["top_rules"] else 0

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 27D Standardisation Finding Report Owner Gate",
                "===========================================================",
                f"passed={not failures}",
                f"report_id={report['report_id']}",
                f"scanned_python_files={summary['scanned_python_files']}",
                f"scanned_report_files={summary['scanned_report_files']}",
                f"total_findings={summary['total_findings']}",
                f"info_findings={summary['info_findings']}",
                f"warning_findings={summary['warning_findings']}",
                f"error_findings={summary['error_findings']}",
                f"top_rule={top_rule}",
                f"top_rule_count={top_rule_count}",
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
        print("FAIL_PHASE_27D_STANDARDISATION_FINDING_REPORT_OWNER")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_27D_STANDARDISATION_FINDING_REPORT_OWNER")
    print("schema=LEAF_STANDARDISATION_FINDING_REPORT_OWNER_PHASE_27D_V1")
    print(f"report_id={report['report_id']}")
    print(f"scanned_python_files={summary['scanned_python_files']}")
    print(f"scanned_report_files={summary['scanned_report_files']}")
    print(f"total_findings={summary['total_findings']}")
    print(f"info_findings={summary['info_findings']}")
    print(f"warning_findings={summary['warning_findings']}")
    print(f"error_findings={summary['error_findings']}")
    print(f"top_rule={top_rule}")
    print(f"top_rule_count={top_rule_count}")
    print(f"mutation_performed={report['mutation_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_27D_STANDARDISATION_FINDING_REPORT_OWNER_COMPLETE")
    print("next_phase=27E Standardisation Compliance Classifier")


if __name__ == "__main__":
    main()
