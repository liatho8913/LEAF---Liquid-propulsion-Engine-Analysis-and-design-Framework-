"""
Programme 26A Completion Gate.

Validates the reusable Engineering Workflow Model.
"""

from __future__ import annotations

import json
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORT_DIR = ROOT / "LEAF_Reports" / "workflow_architecture"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

from leaf_qt.workflow.model import (
    WorkflowDependency,
    WorkflowStep,
    WorkflowStepStatus,
    build_workflow_model,
)


def build_gate_workflow():
    return build_workflow_model(
        workflow_id="programme_26a_gate_workflow",
        title="Programme 26A Gate Workflow",
        description="Validation workflow proving reusable workflow model behaviour.",
        steps=[
            WorkflowStep(
                step_id="inputs",
                title="Inputs Defined",
                description="Engineering inputs exist.",
                owner="workflow_platform",
                status=WorkflowStepStatus.COMPLETE,
            ),
            WorkflowStep(
                step_id="solve",
                title="Solver Executed",
                description="Solver can execute after inputs are defined.",
                owner="workflow_platform",
                status=WorkflowStepStatus.READY,
                dependencies=(
                    WorkflowDependency(
                        required_step_id="inputs",
                        reason="Solver execution requires complete inputs.",
                    ),
                ),
            ),
            WorkflowStep(
                step_id="validate",
                title="Validation Complete",
                description="Validation waits for solver completion.",
                owner="workflow_platform",
                status=WorkflowStepStatus.NOT_STARTED,
                dependencies=(
                    WorkflowDependency(
                        required_step_id="solve",
                        reason="Validation requires completed solver outputs.",
                    ),
                ),
            ),
        ],
    )


def main() -> None:
    py_compile.compile(str(ROOT / "leaf_qt" / "workflow" / "__init__.py"), doraise=True)
    py_compile.compile(str(ROOT / "leaf_qt" / "workflow" / "model.py"), doraise=True)

    workflow = build_gate_workflow()
    validation_failures = workflow.validate()
    progress = workflow.progress()
    report = workflow.report()

    expected_ready = ("solve",)
    failures = list(validation_failures)

    if workflow.ready_step_ids() != expected_ready:
        failures.append(
            f"ready_step_ids mismatch: expected={expected_ready}, actual={workflow.ready_step_ids()}"
        )

    validate_blockers = workflow.blockers_for("validate")
    if not validate_blockers:
        failures.append("validate step should be blocked until solve is complete")

    if progress["total_steps"] != 3:
        failures.append(f"expected total_steps=3, actual={progress['total_steps']}")

    if progress["complete_steps"] != 1:
        failures.append(f"expected complete_steps=1, actual={progress['complete_steps']}")

    if progress["percent_complete"] != 33.333:
        failures.append(f"expected percent_complete=33.333, actual={progress['percent_complete']}")

    bad_workflow = build_workflow_model(
        workflow_id="bad_cycle_workflow",
        title="Bad Cycle Workflow",
        steps=[
            WorkflowStep(
                step_id="a",
                title="A",
                dependencies=(WorkflowDependency("b", "cycle test"),),
            ),
            WorkflowStep(
                step_id="b",
                title="B",
                dependencies=(WorkflowDependency("a", "cycle test"),),
            ),
        ],
    )

    cycle_failures = bad_workflow.validate()
    if not any("cycle" in failure.lower() for failure in cycle_failures):
        failures.append("cycle detection did not detect cyclic workflow dependencies")

    report["gate"] = {
        "phase": "26A",
        "programme": "26",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_26A_ENGINEERING_WORKFLOW_MODEL_COMPLETE"
            if not failures
            else "PROGRAMME_26A_ENGINEERING_WORKFLOW_MODEL_FAILED"
        ),
        "next_phase": "26B Workflow Step Registry",
    }

    txt_path = REPORT_DIR / "workflow_model_gate_phase_26a.txt"
    json_path = REPORT_DIR / "workflow_model_gate_phase_26a.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 26A Workflow Model Gate",
                "======================================",
                f"passed={not failures}",
                f"workflow_state={report['state']}",
                f"ready_step_ids={report['ready_step_ids']}",
                f"total_steps={progress['total_steps']}",
                f"complete_steps={progress['complete_steps']}",
                f"percent_complete={progress['percent_complete']}",
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
        print("FAIL_PHASE_26A_ENGINEERING_WORKFLOW_MODEL")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_26A_ENGINEERING_WORKFLOW_MODEL")
    print("schema=LEAF_WORKFLOW_MODEL_PHASE_26A_V1")
    print(f"workflow_state={report['state']}")
    print(f"ready_step_ids={','.join(report['ready_step_ids'])}")
    print(f"total_steps={progress['total_steps']}")
    print(f"complete_steps={progress['complete_steps']}")
    print(f"percent_complete={progress['percent_complete']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_26A_ENGINEERING_WORKFLOW_MODEL_COMPLETE")
    print("next_phase=26B Workflow Step Registry")


if __name__ == "__main__":
    main()
