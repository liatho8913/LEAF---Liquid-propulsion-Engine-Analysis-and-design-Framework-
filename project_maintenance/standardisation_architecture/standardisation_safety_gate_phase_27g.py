"""
Programme 27G Completion Gate.

Validates the Standardisation Safety Gate.
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

from leaf_qt.standardisation.compliance_classifier import build_standardisation_compliance_classifier
from leaf_qt.standardisation.repair_plan_owner import build_standardisation_repair_plan_owner
from leaf_qt.standardisation.safety_gate import (
    StandardisationSafetyRequest,
    StandardisationSafetyVerdict,
    build_standardisation_safety_gate,
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
        "leaf_qt/standardisation/safety_gate.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    scan_result = build_standardisation_scanner(ROOT).scan()
    classification = build_standardisation_compliance_classifier(scan_result).classify()
    repair_plan = build_standardisation_repair_plan_owner(classification).build_plan()
    gate = build_standardisation_safety_gate(repair_plan)

    blocked_no_approval = gate.report(
        StandardisationSafetyRequest(
            manual_approval=False,
            dry_run=True,
            mutation_requested=False,
            checkpoint_reference="checkpoint:27g-test",
        )
    )

    blocked_mutation = gate.report(
        StandardisationSafetyRequest(
            manual_approval=True,
            dry_run=True,
            mutation_requested=True,
            checkpoint_reference="checkpoint:27g-test",
        )
    )

    blocked_no_checkpoint = gate.report(
        StandardisationSafetyRequest(
            manual_approval=True,
            dry_run=True,
            mutation_requested=False,
            checkpoint_reference=None,
        )
    )

    safe_dry_run = gate.report(
        StandardisationSafetyRequest(
            manual_approval=True,
            dry_run=True,
            mutation_requested=False,
            deletion_requested=False,
            archive_requested=False,
            checkpoint_reference="checkpoint:27g-test",
        )
    )

    reports = {
        "blocked_no_approval": blocked_no_approval,
        "blocked_mutation": blocked_mutation,
        "blocked_no_checkpoint": blocked_no_checkpoint,
        "safe_dry_run": safe_dry_run,
    }

    failures = []

    if blocked_no_approval["result"]["verdict"] != StandardisationSafetyVerdict.BLOCKED_NO_MANUAL_APPROVAL.value:
        failures.append("missing manual approval should be blocked")

    if blocked_mutation["result"]["allowed"] is not False:
        failures.append("mutation request should be blocked")

    if blocked_no_checkpoint["result"]["allowed"] is not False:
        failures.append("missing checkpoint should be blocked")

    if safe_dry_run["result"]["verdict"] != StandardisationSafetyVerdict.SAFE_FOR_DRY_RUN_ONLY.value:
        failures.append(f"safe dry-run verdict mismatch: {safe_dry_run['result']['verdict']}")

    if safe_dry_run["result"]["allowed"] is not True:
        failures.append("safe dry-run request should be allowed")

    if safe_dry_run["result"]["dry_run_only"] is not True:
        failures.append("safe request must remain dry-run only")

    for label, report in reports.items():
        if report["result"]["mutation_performed"] is not False:
            failures.append(f"{label} result indicates mutation occurred")
        if report["safety_policy"]["mutation_allowed"] is not False:
            failures.append(f"{label} policy allowed mutation")

    final_report = {
        "schema": "LEAF_STANDARDISATION_SAFETY_GATE_COMPLETION_PHASE_27G_V1",
        "reports": reports,
        "gate": {
            "phase": "27G",
            "programme": "27",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_27G_STANDARDISATION_SAFETY_GATE_COMPLETE"
                if not failures
                else "PROGRAMME_27G_STANDARDISATION_SAFETY_GATE_FAILED"
            ),
            "next_phase": "27H Standardisation Dry-Run Executor",
        },
    }

    txt_path = REPORT_DIR / "standardisation_safety_gate_phase_27g.txt"
    json_path = REPORT_DIR / "standardisation_safety_gate_phase_27g.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 27G Standardisation Safety Gate",
                "=============================================",
                f"passed={not failures}",
                f"blocked_no_approval={blocked_no_approval['result']['verdict']}",
                f"blocked_mutation_allowed={blocked_mutation['result']['allowed']}",
                f"blocked_no_checkpoint_allowed={blocked_no_checkpoint['result']['allowed']}",
                f"safe_dry_run_verdict={safe_dry_run['result']['verdict']}",
                f"safe_dry_run_allowed={safe_dry_run['result']['allowed']}",
                f"dry_run_only={safe_dry_run['result']['dry_run_only']}",
                f"mutation_performed={safe_dry_run['result']['mutation_performed']}",
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
        print("FAIL_PHASE_27G_STANDARDISATION_SAFETY_GATE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_27G_STANDARDISATION_SAFETY_GATE")
    print("schema=LEAF_STANDARDISATION_SAFETY_GATE_PHASE_27G_V1")
    print(f"blocked_no_approval={blocked_no_approval['result']['verdict']}")
    print(f"blocked_mutation_allowed={blocked_mutation['result']['allowed']}")
    print(f"blocked_no_checkpoint_allowed={blocked_no_checkpoint['result']['allowed']}")
    print(f"safe_dry_run_verdict={safe_dry_run['result']['verdict']}")
    print(f"safe_dry_run_allowed={safe_dry_run['result']['allowed']}")
    print(f"dry_run_only={safe_dry_run['result']['dry_run_only']}")
    print(f"mutation_performed={safe_dry_run['result']['mutation_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_27G_STANDARDISATION_SAFETY_GATE_COMPLETE")
    print("next_phase=27H Standardisation Dry-Run Executor")


if __name__ == "__main__":
    main()
