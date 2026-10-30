"""
Programme 26E Completion Gate.

Validates the reusable Workflow Progress Tracker.
"""

from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORT_DIR = ROOT / "LEAF_Reports" / "workflow_architecture"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

from leaf_qt.workflow.model import WorkflowStepStatus, build_workflow_model
from leaf_qt.workflow.progress_tracker import build_workflow_progress_tracker
from leaf_qt.workflow.registry import build_default_engineering_step_registry


def main() -> None:
    for rel in [
        "leaf_qt/workflow/__init__.py",
        "leaf_qt/workflow/model.py",
        "leaf_qt/workflow/registry.py",
        "leaf_qt/workflow/graph.py",
        "leaf_qt/workflow/execution_context.py",
        "leaf_qt/workflow/progress_tracker.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    registry = build_default_engineering_step_registry()

    workflow = build_workflow_model(
        workflow_id="programme_26e_progress_tracker_gate_workflow",
        title="Programme 26E Progress Tracker Gate Workflow",
        description="Workflow used to prove progress tracking behaviour.",
        steps=registry.build_steps(
            [
                "define_inputs",
                "run_solver",
                "validate_outputs",
                "produce_report",
                "save_design",
            ],
            statuses={
                "define_inputs": WorkflowStepStatus.COMPLETE,
                "run_solver": WorkflowStepStatus.ACTIVE,
                "validate_outputs": WorkflowStepStatus.NOT_STARTED,
                "produce_report": WorkflowStepStatus.NOT_STARTED,
                "save_design": WorkflowStepStatus.NOT_STARTED,
            },
        ),
    )

    tracker = build_workflow_progress_tracker(workflow)
    report = tracker.report()
    snapshot = report["snapshot"]

    failures = list(report["validation_failures"])

    checks = {
        "total_steps": 5,
        "complete_steps": 1,
        "active_steps": 1,
        "ready_steps": 1,
        "blocked_steps": 3,
        "failed_steps": 0,
        "skipped_steps": 0,
        "remaining_steps": 4,
        "terminal_steps": 1,
        "percent_complete": 20.0,
        "percent_terminal": 20.0,
        "current_ready_step": "run_solver",
    }

    for key, expected in checks.items():
        actual = snapshot[key]
        if actual != expected:
            failures.append(f"{key} mismatch: expected={expected!r}, actual={actual!r}")

    if snapshot["ready_step_ids"] != ["run_solver"]:
        failures.append(f"ready_step_ids mismatch: actual={snapshot['ready_step_ids']}")

    if snapshot["blocked_step_ids"] != [
        "validate_outputs",
        "produce_report",
        "save_design",
    ]:
        failures.append(f"blocked_step_ids mismatch: actual={snapshot['blocked_step_ids']}")

    if snapshot["complete_step_ids"] != ["define_inputs"]:
        failures.append(f"complete_step_ids mismatch: actual={snapshot['complete_step_ids']}")

    if snapshot["remaining_step_ids"] != [
        "run_solver",
        "validate_outputs",
        "produce_report",
        "save_design",
    ]:
        failures.append(f"remaining_step_ids mismatch: actual={snapshot['remaining_step_ids']}")

    if snapshot["execution_order"] != [
        "define_inputs",
        "run_solver",
        "validate_outputs",
        "produce_report",
        "save_design",
    ]:
        failures.append(f"execution_order mismatch: actual={snapshot['execution_order']}")

    complete_workflow = build_workflow_model(
        workflow_id="programme_26e_complete_progress_test",
        title="Programme 26E Complete Progress Test",
        steps=registry.build_steps(
            [
                "define_inputs",
                "run_solver",
                "validate_outputs",
                "produce_report",
                "save_design",
            ],
            statuses={
                "define_inputs": WorkflowStepStatus.COMPLETE,
                "run_solver": WorkflowStepStatus.COMPLETE,
                "validate_outputs": WorkflowStepStatus.COMPLETE,
                "produce_report": WorkflowStepStatus.COMPLETE,
                "save_design": WorkflowStepStatus.COMPLETE,
            },
        ),
    )

    complete_snapshot = build_workflow_progress_tracker(complete_workflow).snapshot().as_dict()

    if complete_snapshot["percent_complete"] != 100.0:
        failures.append(
            f"complete workflow percent_complete mismatch: actual={complete_snapshot['percent_complete']}"
        )

    if complete_snapshot["remaining_steps"] != 0:
        failures.append(
            f"complete workflow remaining_steps mismatch: actual={complete_snapshot['remaining_steps']}"
        )

    if complete_snapshot["current_ready_step"] is not None:
        failures.append(
            f"complete workflow current_ready_step should be None, actual={complete_snapshot['current_ready_step']}"
        )

    report["complete_workflow_snapshot"] = complete_snapshot
    report["gate"] = {
        "phase": "26E",
        "programme": "26",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_26E_WORKFLOW_PROGRESS_TRACKER_COMPLETE"
            if not failures
            else "PROGRAMME_26E_WORKFLOW_PROGRESS_TRACKER_FAILED"
        ),
        "next_phase": "26F Workflow Blocker / Readiness Gate",
    }

    txt_path = REPORT_DIR / "workflow_progress_tracker_gate_phase_26e.txt"
    json_path = REPORT_DIR / "workflow_progress_tracker_gate_phase_26e.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 26E Workflow Progress Tracker Gate",
                "================================================",
                f"passed={not failures}",
                f"workflow_id={snapshot['workflow_id']}",
                f"workflow_state={snapshot['workflow_state']}",
                f"total_steps={snapshot['total_steps']}",
                f"complete_steps={snapshot['complete_steps']}",
                f"active_steps={snapshot['active_steps']}",
                f"ready_steps={snapshot['ready_steps']}",
                f"blocked_steps={snapshot['blocked_steps']}",
                f"remaining_steps={snapshot['remaining_steps']}",
                f"percent_complete={snapshot['percent_complete']}",
                f"current_ready_step={snapshot['current_ready_step']}",
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
        print("FAIL_PHASE_26E_WORKFLOW_PROGRESS_TRACKER")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_26E_WORKFLOW_PROGRESS_TRACKER")
    print("schema=LEAF_WORKFLOW_PROGRESS_TRACKER_PHASE_26E_V1")
    print(f"workflow_id={snapshot['workflow_id']}")
    print(f"workflow_state={snapshot['workflow_state']}")
    print(f"total_steps={snapshot['total_steps']}")
    print(f"complete_steps={snapshot['complete_steps']}")
    print(f"active_steps={snapshot['active_steps']}")
    print(f"ready_steps={snapshot['ready_steps']}")
    print(f"blocked_steps={snapshot['blocked_steps']}")
    print(f"remaining_steps={snapshot['remaining_steps']}")
    print(f"percent_complete={snapshot['percent_complete']}")
    print(f"current_ready_step={snapshot['current_ready_step']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_26E_WORKFLOW_PROGRESS_TRACKER_COMPLETE")
    print("next_phase=26F Workflow Blocker / Readiness Gate")


if __name__ == "__main__":
    main()
