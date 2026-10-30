"""
Programme 27F Completion Gate.

Validates the non-mutating Standardisation Repair Plan Owner.
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
    build_standardisation_compliance_classifier,
)
from leaf_qt.standardisation.repair_plan_owner import (
    StandardisationRepairActionType,
    build_standardisation_repair_plan_owner,
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
        "leaf_qt/standardisation/repair_plan_owner.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    scan_result = build_standardisation_scanner(ROOT).scan()
    classification_report = build_standardisation_compliance_classifier(scan_result).classify()
    owner = build_standardisation_repair_plan_owner(classification_report)
    report = owner.report()

    failures = []

    if report["schema"] != "LEAF_STANDARDISATION_REPAIR_PLAN_OWNER_PHASE_27F_V1":
        failures.append(f"schema mismatch: actual={report['schema']}")

    if report["mutation_performed"] is not False:
        failures.append("repair plan owner must not mutate repository")

    if report["automatic_repair_enabled"] is not False:
        failures.append("automatic repair must remain disabled")

    if report["manual_approval_required"] is not True:
        failures.append("manual approval must be required for repair plan")

    if report["source_total_findings"] != classification_report.total_findings:
        failures.append("source finding count mismatch")

    if classification_report.total_findings > 0 and report["planned_item_count"] <= 0:
        failures.append("repair plan should include planned items when findings exist")

    if any(item.get("mutation_allowed") for item in report["planned_items"]):
        failures.append("repair plan items must not allow mutation")

    if any(not item.get("manual_approval_required") for item in report["planned_items"]):
        failures.append("all repair plan items must require manual approval")

    if classification_report.total_findings > 0:
        action_counts = report["action_counts"]
        if action_counts[StandardisationRepairActionType.STANDARDISE_GATE_REPORTING.value] <= 0:
            failures.append("expected at least one gate reporting repair plan item")

    report["gate"] = {
        "phase": "27F",
        "programme": "27",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_27F_STANDARDISATION_REPAIR_PLAN_OWNER_COMPLETE"
            if not failures
            else "PROGRAMME_27F_STANDARDISATION_REPAIR_PLAN_OWNER_FAILED"
        ),
        "next_phase": "27G Standardisation Safety Gate",
    }

    txt_path = REPORT_DIR / "standardisation_repair_plan_owner_gate_phase_27f.txt"
    json_path = REPORT_DIR / "standardisation_repair_plan_owner_gate_phase_27f.json"

    top_action = report["top_actions"][0]["action_type"] if report["top_actions"] else "NONE"
    top_action_count = report["top_actions"][0]["count"] if report["top_actions"] else 0
    top_priority = report["top_priorities"][0]["priority"] if report["top_priorities"] else "NONE"
    top_priority_count = report["top_priorities"][0]["count"] if report["top_priorities"] else 0

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 27F Standardisation Repair Plan Owner Gate",
                "=======================================================",
                f"passed={not failures}",
                f"plan_id={report['plan_id']}",
                f"source_total_findings={report['source_total_findings']}",
                f"planned_item_count={report['planned_item_count']}",
                f"top_action={top_action}",
                f"top_action_count={top_action_count}",
                f"top_priority={top_priority}",
                f"top_priority_count={top_priority_count}",
                f"automatic_repair_enabled={report['automatic_repair_enabled']}",
                f"manual_approval_required={report['manual_approval_required']}",
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
        print("FAIL_PHASE_27F_STANDARDISATION_REPAIR_PLAN_OWNER")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_27F_STANDARDISATION_REPAIR_PLAN_OWNER")
    print("schema=LEAF_STANDARDISATION_REPAIR_PLAN_OWNER_PHASE_27F_V1")
    print(f"plan_id={report['plan_id']}")
    print(f"source_total_findings={report['source_total_findings']}")
    print(f"planned_item_count={report['planned_item_count']}")
    print(f"top_action={top_action}")
    print(f"top_action_count={top_action_count}")
    print(f"top_priority={top_priority}")
    print(f"top_priority_count={top_priority_count}")
    print(f"automatic_repair_enabled={report['automatic_repair_enabled']}")
    print(f"manual_approval_required={report['manual_approval_required']}")
    print(f"mutation_performed={report['mutation_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_27F_STANDARDISATION_REPAIR_PLAN_OWNER_COMPLETE")
    print("next_phase=27G Standardisation Safety Gate")


if __name__ == "__main__":
    main()
