"""
Programme 27H Completion Gate.

Validates the non-mutating Standardisation Dry-Run Executor.
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
from leaf_qt.standardisation.dry_run_executor import build_standardisation_dry_run_executor
from leaf_qt.standardisation.repair_plan_owner import build_standardisation_repair_plan_owner
from leaf_qt.standardisation.safety_gate import StandardisationSafetyRequest
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
        "leaf_qt/standardisation/dry_run_executor.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    scan_result = build_standardisation_scanner(ROOT).scan()
    classification = build_standardisation_compliance_classifier(scan_result).classify()
    repair_plan = build_standardisation_repair_plan_owner(classification).build_plan()
    executor = build_standardisation_dry_run_executor(repair_plan)

    safe_request = StandardisationSafetyRequest(
        manual_approval=True,
        dry_run=True,
        mutation_requested=False,
        deletion_requested=False,
        archive_requested=False,
        checkpoint_reference="checkpoint:27h-dry-run",
    )

    blocked_request = StandardisationSafetyRequest(
        manual_approval=False,
        dry_run=True,
        mutation_requested=False,
        checkpoint_reference="checkpoint:27h-dry-run",
    )

    safe_report = executor.report(safe_request, limit=50)
    blocked_report = executor.report(blocked_request, limit=50)

    safe = safe_report["result"]
    blocked = blocked_report["result"]

    failures = []

    if safe["schema"] != "LEAF_STANDARDISATION_DRY_RUN_EXECUTOR_PHASE_27H_V1":
        failures.append(f"schema mismatch: actual={safe['schema']}")

    if safe["allowed"] is not True:
        failures.append("safe dry-run should be allowed")

    if safe["dry_run_only"] is not True:
        failures.append("dry-run result must remain dry_run_only")

    if safe["mutation_performed"] is not False:
        failures.append("dry-run executor must not mutate repository")

    if safe["action_count"] <= 0 and repair_plan.planned_items:
        failures.append("safe dry-run should produce actions when plan items exist")

    for action in safe["actions"]:
        if action["would_modify"] or action["would_delete"] or action["would_archive"]:
            failures.append("dry-run action attempted modification/deletion/archive")

    if blocked["allowed"] is not False:
        failures.append("blocked request should not be allowed")

    if blocked["action_count"] != 0:
        failures.append("blocked request should produce zero actions")

    if safe_report["policy"]["mutation_allowed"] is not False:
        failures.append("dry-run report policy must not allow mutation")

    final_report = {
        "schema": "LEAF_STANDARDISATION_DRY_RUN_EXECUTOR_COMPLETION_PHASE_27H_V1",
        "safe_report": safe_report,
        "blocked_report": blocked_report,
        "gate": {
            "phase": "27H",
            "programme": "27",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_27H_STANDARDISATION_DRY_RUN_EXECUTOR_COMPLETE"
                if not failures
                else "PROGRAMME_27H_STANDARDISATION_DRY_RUN_EXECUTOR_FAILED"
            ),
            "next_phase": "27I Standardisation Report Router",
        },
    }

    txt_path = REPORT_DIR / "standardisation_dry_run_executor_gate_phase_27h.txt"
    json_path = REPORT_DIR / "standardisation_dry_run_executor_gate_phase_27h.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 27H Standardisation Dry-Run Executor Gate",
                "=======================================================",
                f"passed={not failures}",
                f"plan_id={safe['plan_id']}",
                f"safety_verdict={safe['safety_verdict']}",
                f"allowed={safe['allowed']}",
                f"dry_run_only={safe['dry_run_only']}",
                f"action_count={safe['action_count']}",
                f"blocked_allowed={blocked['allowed']}",
                f"blocked_action_count={blocked['action_count']}",
                f"mutation_performed={safe['mutation_performed']}",
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
        print("FAIL_PHASE_27H_STANDARDISATION_DRY_RUN_EXECUTOR")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_27H_STANDARDISATION_DRY_RUN_EXECUTOR")
    print("schema=LEAF_STANDARDISATION_DRY_RUN_EXECUTOR_PHASE_27H_V1")
    print(f"plan_id={safe['plan_id']}")
    print(f"safety_verdict={safe['safety_verdict']}")
    print(f"allowed={safe['allowed']}")
    print(f"dry_run_only={safe['dry_run_only']}")
    print(f"action_count={safe['action_count']}")
    print(f"blocked_allowed={blocked['allowed']}")
    print(f"blocked_action_count={blocked['action_count']}")
    print(f"mutation_performed={safe['mutation_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_27H_STANDARDISATION_DRY_RUN_EXECUTOR_COMPLETE")
    print("next_phase=27I Standardisation Report Router")


if __name__ == "__main__":
    main()
