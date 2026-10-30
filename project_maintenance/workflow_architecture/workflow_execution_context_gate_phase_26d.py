"""
Programme 26D Completion Gate.

Validates the reusable Workflow Execution Context.
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

from leaf_qt.workflow.execution_context import (
    WorkflowExecutionPermission,
    WorkflowValidationMode,
    build_workflow_execution_context,
)
from leaf_qt.workflow.model import WorkflowStepStatus, build_workflow_model
from leaf_qt.workflow.registry import build_default_engineering_step_registry


def main() -> None:
    for rel in [
        "leaf_qt/workflow/__init__.py",
        "leaf_qt/workflow/model.py",
        "leaf_qt/workflow/registry.py",
        "leaf_qt/workflow/graph.py",
        "leaf_qt/workflow/execution_context.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    registry = build_default_engineering_step_registry()

    workflow = build_workflow_model(
        workflow_id="programme_26d_execution_context_gate_workflow",
        title="Programme 26D Execution Context Gate Workflow",
        description="Workflow used to prove execution permission and blocker behaviour.",
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

    allowed_context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="run_solver",
        active_module="platform_test_module",
        validation_mode=WorkflowValidationMode.SOURCED_VALIDATION_MODE,
        runtime_reference="runtime:test-session",
        storage_reference="storage:test-design",
        metadata={"gate": "26D"},
    )

    blocked_context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="validate_outputs",
        active_module="platform_test_module",
    )

    unknown_context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="missing_step",
        active_module="platform_test_module",
    )

    complete_context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="define_inputs",
        active_module="platform_test_module",
    )

    failures = []

    for context in [
        allowed_context,
        blocked_context,
        unknown_context,
        complete_context,
    ]:
        failures.extend(context.validate())

    allowed_report = allowed_context.report()
    blocked_report = blocked_context.report()
    unknown_report = unknown_context.report()
    complete_report = complete_context.report()

    if allowed_context.permission() != WorkflowExecutionPermission.ALLOWED:
        failures.append(
            f"run_solver should be ALLOWED, actual={allowed_context.permission().value}"
        )

    if not allowed_context.can_execute():
        failures.append("run_solver context should be executable")

    if blocked_context.permission() != WorkflowExecutionPermission.BLOCKED:
        failures.append(
            f"validate_outputs should be BLOCKED, actual={blocked_context.permission().value}"
        )

    if blocked_context.can_execute():
        failures.append("blocked context should not be executable")

    if not blocked_context.blockers():
        failures.append("blocked context should include blocker reasons")

    if unknown_context.permission() != WorkflowExecutionPermission.UNKNOWN_STEP:
        failures.append(
            f"missing_step should be UNKNOWN_STEP, actual={unknown_context.permission().value}"
        )

    if complete_context.permission() != WorkflowExecutionPermission.COMPLETE:
        failures.append(
            f"define_inputs should be COMPLETE, actual={complete_context.permission().value}"
        )

    if allowed_report["validation_mode"] != "SOURCED_VALIDATION_MODE":
        failures.append("allowed context did not preserve validation mode")

    if allowed_report["runtime_reference"] != "runtime:test-session":
        failures.append("allowed context did not preserve runtime reference")

    if allowed_report["storage_reference"] != "storage:test-design":
        failures.append("allowed context did not preserve storage reference")

    if "run_solver" not in allowed_report["next_ready_steps"]:
        failures.append("run_solver should appear in next_ready_steps")

    report = {
        "schema": "LEAF_WORKFLOW_EXECUTION_CONTEXT_GATE_PHASE_26D_V1",
        "allowed_context": allowed_report,
        "blocked_context": blocked_report,
        "unknown_context": unknown_report,
        "complete_context": complete_report,
        "gate": {
            "phase": "26D",
            "programme": "26",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_26D_WORKFLOW_EXECUTION_CONTEXT_COMPLETE"
                if not failures
                else "PROGRAMME_26D_WORKFLOW_EXECUTION_CONTEXT_FAILED"
            ),
            "next_phase": "26E Workflow Progress Tracker",
        },
    }

    txt_path = REPORT_DIR / "workflow_execution_context_gate_phase_26d.txt"
    json_path = REPORT_DIR / "workflow_execution_context_gate_phase_26d.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 26D Workflow Execution Context Gate",
                "=================================================",
                f"passed={not failures}",
                f"workflow_id={workflow.workflow_id}",
                f"allowed_step={allowed_report['current_step_id']}",
                f"allowed_permission={allowed_report['permission']}",
                f"blocked_step={blocked_report['current_step_id']}",
                f"blocked_permission={blocked_report['permission']}",
                f"unknown_permission={unknown_report['permission']}",
                f"complete_permission={complete_report['permission']}",
                f"can_execute={allowed_report['can_execute']}",
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
        print("FAIL_PHASE_26D_WORKFLOW_EXECUTION_CONTEXT")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_26D_WORKFLOW_EXECUTION_CONTEXT")
    print("schema=LEAF_WORKFLOW_EXECUTION_CONTEXT_PHASE_26D_V1")
    print(f"workflow_id={workflow.workflow_id}")
    print(f"allowed_step={allowed_report['current_step_id']}")
    print(f"allowed_permission={allowed_report['permission']}")
    print(f"blocked_step={blocked_report['current_step_id']}")
    print(f"blocked_permission={blocked_report['permission']}")
    print(f"unknown_permission={unknown_report['permission']}")
    print(f"complete_permission={complete_report['permission']}")
    print(f"can_execute={allowed_report['can_execute']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_26D_WORKFLOW_EXECUTION_CONTEXT_COMPLETE")
    print("next_phase=26E Workflow Progress Tracker")


if __name__ == "__main__":
    main()
