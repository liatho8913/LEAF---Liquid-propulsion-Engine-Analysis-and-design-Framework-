"""
Programme 26F Completion Gate.

Validates the reusable Workflow Blocker / Readiness Gate.
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

from leaf_qt.workflow.execution_context import build_workflow_execution_context
from leaf_qt.workflow.model import WorkflowStepStatus, build_workflow_model
from leaf_qt.workflow.readiness_gate import (
    WorkflowReadinessVerdict,
    build_workflow_readiness_gate,
)
from leaf_qt.workflow.registry import build_default_engineering_step_registry


def main() -> None:
    for rel in [
        "leaf_qt/workflow/__init__.py",
        "leaf_qt/workflow/model.py",
        "leaf_qt/workflow/registry.py",
        "leaf_qt/workflow/graph.py",
        "leaf_qt/workflow/execution_context.py",
        "leaf_qt/workflow/progress_tracker.py",
        "leaf_qt/workflow/readiness_gate.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    registry = build_default_engineering_step_registry()

    workflow = build_workflow_model(
        workflow_id="programme_26f_readiness_gate_workflow",
        title="Programme 26F Readiness Gate Workflow",
        description="Workflow used to prove readiness and blocker gate behaviour.",
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
                "run_solver": WorkflowStepStatus.READY,
                "validate_outputs": WorkflowStepStatus.NOT_STARTED,
                "produce_report": WorkflowStepStatus.NOT_STARTED,
                "save_design": WorkflowStepStatus.NOT_STARTED,
            },
        ),
    )

    ready_context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="run_solver",
        active_module="platform_test_module",
    )

    blocked_context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="validate_outputs",
        active_module="platform_test_module",
    )

    complete_context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="define_inputs",
        active_module="platform_test_module",
    )

    unknown_context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="missing_step",
        active_module="platform_test_module",
    )

    invalid_context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="run_solver",
        active_module="",
    )

    ready_report = build_workflow_readiness_gate(ready_context).report()
    blocked_report = build_workflow_readiness_gate(blocked_context).report()
    complete_report = build_workflow_readiness_gate(complete_context).report()
    unknown_report = build_workflow_readiness_gate(unknown_context).report()
    invalid_report = build_workflow_readiness_gate(invalid_context).report()

    ready = ready_report["result"]
    blocked = blocked_report["result"]
    complete = complete_report["result"]
    unknown = unknown_report["result"]
    invalid = invalid_report["result"]

    failures = []

    if ready["verdict"] != WorkflowReadinessVerdict.READY.value:
        failures.append(f"ready verdict mismatch: actual={ready['verdict']}")

    if ready["can_proceed"] is not True:
        failures.append("ready context should allow proceed")

    if ready["recommended_next_step"] != "run_solver":
        failures.append(
            f"ready recommended_next_step mismatch: actual={ready['recommended_next_step']}"
        )

    if blocked["verdict"] != WorkflowReadinessVerdict.BLOCKED.value:
        failures.append(f"blocked verdict mismatch: actual={blocked['verdict']}")

    if blocked["can_proceed"] is not False:
        failures.append("blocked context should not allow proceed")

    if blocked["incomplete_dependencies"] != ["run_solver"]:
        failures.append(
            "blocked incomplete_dependencies mismatch: "
            f"actual={blocked['incomplete_dependencies']}"
        )

    if not blocked["blockers"]:
        failures.append("blocked context should include blocker messages")

    if complete["verdict"] != WorkflowReadinessVerdict.COMPLETE.value:
        failures.append(f"complete verdict mismatch: actual={complete['verdict']}")

    if unknown["verdict"] != WorkflowReadinessVerdict.UNKNOWN_STEP.value:
        failures.append(f"unknown verdict mismatch: actual={unknown['verdict']}")

    if invalid["verdict"] != WorkflowReadinessVerdict.INVALID_CONTEXT.value:
        failures.append(f"invalid verdict mismatch: actual={invalid['verdict']}")

    if not invalid["validation_failures"]:
        failures.append("invalid context should include validation failures")

    report = {
        "schema": "LEAF_WORKFLOW_READINESS_GATE_COMPLETION_PHASE_26F_V1",
        "ready_report": ready_report,
        "blocked_report": blocked_report,
        "complete_report": complete_report,
        "unknown_report": unknown_report,
        "invalid_report": invalid_report,
        "gate": {
            "phase": "26F",
            "programme": "26",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_26F_WORKFLOW_BLOCKER_READINESS_GATE_COMPLETE"
                if not failures
                else "PROGRAMME_26F_WORKFLOW_BLOCKER_READINESS_GATE_FAILED"
            ),
            "next_phase": "26G Workflow Recommendation Engine",
        },
    }

    txt_path = REPORT_DIR / "workflow_readiness_gate_phase_26f.txt"
    json_path = REPORT_DIR / "workflow_readiness_gate_phase_26f.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 26F Workflow Blocker / Readiness Gate",
                "====================================================",
                f"passed={not failures}",
                f"workflow_id={workflow.workflow_id}",
                f"ready_verdict={ready['verdict']}",
                f"ready_can_proceed={ready['can_proceed']}",
                f"blocked_verdict={blocked['verdict']}",
                f"blocked_dependencies={','.join(blocked['incomplete_dependencies'])}",
                f"complete_verdict={complete['verdict']}",
                f"unknown_verdict={unknown['verdict']}",
                f"invalid_verdict={invalid['verdict']}",
                f"recommended_next_step={ready['recommended_next_step']}",
                f"progress_percent={ready['progress_percent']}",
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
        print("FAIL_PHASE_26F_WORKFLOW_BLOCKER_READINESS_GATE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_26F_WORKFLOW_BLOCKER_READINESS_GATE")
    print("schema=LEAF_WORKFLOW_READINESS_GATE_PHASE_26F_V1")
    print(f"workflow_id={workflow.workflow_id}")
    print(f"ready_verdict={ready['verdict']}")
    print(f"ready_can_proceed={ready['can_proceed']}")
    print(f"blocked_verdict={blocked['verdict']}")
    print(f"blocked_dependencies={','.join(blocked['incomplete_dependencies'])}")
    print(f"complete_verdict={complete['verdict']}")
    print(f"unknown_verdict={unknown['verdict']}")
    print(f"invalid_verdict={invalid['verdict']}")
    print(f"recommended_next_step={ready['recommended_next_step']}")
    print(f"progress_percent={ready['progress_percent']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_26F_WORKFLOW_BLOCKER_READINESS_GATE_COMPLETE")
    print("next_phase=26G Workflow Recommendation Engine")


if __name__ == "__main__":
    main()
