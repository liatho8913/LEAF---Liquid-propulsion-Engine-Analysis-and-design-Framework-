"""
Programme 26G Completion Gate.

Validates the reusable Workflow Recommendation Engine.
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
from leaf_qt.workflow.recommendation_engine import (
    WorkflowRecommendationKind,
    build_workflow_recommendation_engine,
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
        "leaf_qt/workflow/recommendation_engine.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    registry = build_default_engineering_step_registry()
    step_ids = [
        "define_inputs",
        "run_solver",
        "validate_outputs",
        "produce_report",
        "save_design",
    ]

    workflow = build_workflow_model(
        workflow_id="programme_26g_recommendation_engine_workflow",
        title="Programme 26G Recommendation Engine Workflow",
        steps=registry.build_steps(
            step_ids,
            statuses={
                "define_inputs": WorkflowStepStatus.COMPLETE,
                "run_solver": WorkflowStepStatus.READY,
                "validate_outputs": WorkflowStepStatus.NOT_STARTED,
                "produce_report": WorkflowStepStatus.NOT_STARTED,
                "save_design": WorkflowStepStatus.NOT_STARTED,
            },
        ),
    )

    ready_report = build_workflow_recommendation_engine(
        build_workflow_execution_context(workflow, "run_solver", "platform_test_module")
    ).report()

    blocked_report = build_workflow_recommendation_engine(
        build_workflow_execution_context(workflow, "validate_outputs", "platform_test_module")
    ).report()

    complete_report = build_workflow_recommendation_engine(
        build_workflow_execution_context(workflow, "define_inputs", "platform_test_module")
    ).report()

    unknown_report = build_workflow_recommendation_engine(
        build_workflow_execution_context(workflow, "missing_step", "platform_test_module")
    ).report()

    invalid_report = build_workflow_recommendation_engine(
        build_workflow_execution_context(workflow, "run_solver", "")
    ).report()

    complete_workflow = build_workflow_model(
        workflow_id="programme_26g_complete_workflow",
        title="Programme 26G Complete Workflow",
        steps=registry.build_steps(
            step_ids,
            statuses={step_id: WorkflowStepStatus.COMPLETE for step_id in step_ids},
        ),
    )

    workflow_complete_report = build_workflow_recommendation_engine(
        build_workflow_execution_context(
            complete_workflow,
            "save_design",
            "platform_test_module",
        )
    ).report()

    failed_workflow = build_workflow_model(
        workflow_id="programme_26g_failed_workflow",
        title="Programme 26G Failed Workflow",
        steps=registry.build_steps(
            step_ids,
            statuses={
                "define_inputs": WorkflowStepStatus.COMPLETE,
                "run_solver": WorkflowStepStatus.FAILED,
                "validate_outputs": WorkflowStepStatus.NOT_STARTED,
                "produce_report": WorkflowStepStatus.NOT_STARTED,
                "save_design": WorkflowStepStatus.NOT_STARTED,
            },
        ),
    )

    failed_report = build_workflow_recommendation_engine(
        build_workflow_execution_context(failed_workflow, "run_solver", "platform_test_module")
    ).report()

    reports = {
        "ready": ready_report,
        "blocked": blocked_report,
        "complete": complete_report,
        "unknown": unknown_report,
        "invalid": invalid_report,
        "workflow_complete": workflow_complete_report,
        "failed": failed_report,
    }

    failures = []

    expected_kinds = {
        "ready": WorkflowRecommendationKind.PROCEED_CURRENT_STEP.value,
        "blocked": WorkflowRecommendationKind.COMPLETE_DEPENDENCIES.value,
        "complete": WorkflowRecommendationKind.MOVE_TO_NEXT_READY_STEP.value,
        "unknown": WorkflowRecommendationKind.UNKNOWN_STEP.value,
        "invalid": WorkflowRecommendationKind.FIX_CONTEXT.value,
        "workflow_complete": WorkflowRecommendationKind.WORKFLOW_COMPLETE.value,
        "failed": WorkflowRecommendationKind.FIX_FAILED_STEP.value,
    }

    for label, expected in expected_kinds.items():
        actual = reports[label]["recommendation"]["kind"]
        if actual != expected:
            failures.append(f"{label} kind mismatch: expected={expected}, actual={actual}")

    if reports["ready"]["recommendation"]["recommended_step_id"] != "run_solver":
        failures.append("ready recommendation should recommend run_solver")

    if reports["ready"]["recommendation"]["can_proceed"] is not True:
        failures.append("ready recommendation should allow proceed")

    if reports["blocked"]["recommendation"]["recommended_step_id"] != "run_solver":
        failures.append("blocked recommendation should redirect to run_solver")

    if reports["blocked"]["recommendation"]["can_proceed"] is not False:
        failures.append("blocked recommendation should not allow proceed")

    if "run_solver" not in reports["blocked"]["recommendation"]["incomplete_dependencies"]:
        failures.append("blocked recommendation should explain run_solver dependency")

    if reports["workflow_complete"]["recommendation"]["recommended_step_id"] is not None:
        failures.append("complete workflow should not recommend another step")

    if reports["invalid"]["recommendation"]["can_proceed"] is not False:
        failures.append("invalid recommendation should not allow proceed")

    report = {
        "schema": "LEAF_WORKFLOW_RECOMMENDATION_ENGINE_COMPLETION_PHASE_26G_V1",
        "reports": reports,
        "gate": {
            "phase": "26G",
            "programme": "26",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_26G_WORKFLOW_RECOMMENDATION_ENGINE_COMPLETE"
                if not failures
                else "PROGRAMME_26G_WORKFLOW_RECOMMENDATION_ENGINE_FAILED"
            ),
            "next_phase": "26H Workflow Runtime Bridge",
        },
    }

    txt_path = REPORT_DIR / "workflow_recommendation_engine_gate_phase_26g.txt"
    json_path = REPORT_DIR / "workflow_recommendation_engine_gate_phase_26g.json"

    ready = reports["ready"]["recommendation"]
    blocked = reports["blocked"]["recommendation"]

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 26G Workflow Recommendation Engine Gate",
                "=====================================================",
                f"passed={not failures}",
                f"workflow_id={workflow.workflow_id}",
                f"ready_kind={ready['kind']}",
                f"ready_recommended_step={ready['recommended_step_id']}",
                f"blocked_kind={blocked['kind']}",
                f"blocked_recommended_step={blocked['recommended_step_id']}",
                f"workflow_complete_kind={reports['workflow_complete']['recommendation']['kind']}",
                f"failed_kind={reports['failed']['recommendation']['kind']}",
                f"unknown_kind={reports['unknown']['recommendation']['kind']}",
                f"invalid_kind={reports['invalid']['recommendation']['kind']}",
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
        print("FAIL_PHASE_26G_WORKFLOW_RECOMMENDATION_ENGINE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_26G_WORKFLOW_RECOMMENDATION_ENGINE")
    print("schema=LEAF_WORKFLOW_RECOMMENDATION_ENGINE_PHASE_26G_V1")
    print(f"workflow_id={workflow.workflow_id}")
    print(f"ready_kind={ready['kind']}")
    print(f"ready_recommended_step={ready['recommended_step_id']}")
    print(f"blocked_kind={blocked['kind']}")
    print(f"blocked_recommended_step={blocked['recommended_step_id']}")
    print(f"workflow_complete_kind={reports['workflow_complete']['recommendation']['kind']}")
    print(f"failed_kind={reports['failed']['recommendation']['kind']}")
    print(f"unknown_kind={reports['unknown']['recommendation']['kind']}")
    print(f"invalid_kind={reports['invalid']['recommendation']['kind']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_26G_WORKFLOW_RECOMMENDATION_ENGINE_COMPLETE")
    print("next_phase=26H Workflow Runtime Bridge")


if __name__ == "__main__":
    main()
