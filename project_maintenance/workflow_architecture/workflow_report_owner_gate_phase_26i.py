"""
Programme 26I Completion Gate.

Validates the reusable Workflow Report Owner.
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
from leaf_qt.workflow.registry import build_default_engineering_step_registry
from leaf_qt.workflow.report_owner import build_workflow_report_owner
from leaf_qt.workflow.runtime_bridge import WorkflowRuntimeBridgeAction


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
        "leaf_qt/workflow/runtime_bridge.py",
        "leaf_qt/workflow/report_owner.py",
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
        workflow_id="programme_26i_workflow_report_owner_workflow",
        title="Programme 26I Workflow Report Owner Workflow",
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

    context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="run_solver",
        active_module="platform_test_module",
        runtime_reference="runtime:test-session",
        storage_reference="storage:test-design",
    )

    owner = build_workflow_report_owner(context)
    package = owner.build_report(
        include_runtime_bridge=True,
        bridge_action=WorkflowRuntimeBridgeAction.EXECUTE_STEP,
        bridge_payload={"gate": "26I"},
        metadata={"gate": "workflow_report_owner_gate_phase_26i"},
    )

    report = package.as_dict()
    summary = report["summary"]
    sections = report["sections"]
    metadata = report["metadata"]

    failures = []

    required_sections = [
        "model",
        "graph",
        "progress",
        "readiness",
        "recommendation",
        "context",
        "runtime_bridge",
    ]

    for section in required_sections:
        if section not in sections:
            failures.append(f"missing report section: {section}")

    if report["schema"] != "LEAF_WORKFLOW_REPORT_OWNER_PHASE_26I_V1":
        failures.append(f"schema mismatch: actual={report['schema']}")

    if report["workflow_id"] != workflow.workflow_id:
        failures.append("workflow_id mismatch")

    if metadata.get("qt_owned") is not False:
        failures.append("report owner must not be Qt-owned")

    if metadata.get("runtime_mutation_performed") is not False:
        failures.append("report owner must not mutate runtime")

    expected_summary = {
        "workflow_state": "READY",
        "current_step_id": "run_solver",
        "active_module": "platform_test_module",
        "percent_complete": 20.0,
        "ready_steps": 1,
        "blocked_steps": 3,
        "remaining_steps": 4,
        "readiness_verdict": "READY",
        "can_proceed": True,
        "recommendation_kind": "PROCEED_CURRENT_STEP",
        "recommended_step_id": "run_solver",
        "runtime_bridge_status": "ACCEPTED",
        "runtime_bridge_accepted": True,
        "mutation_performed": False,
    }

    for key, expected in expected_summary.items():
        actual = summary.get(key)
        if actual != expected:
            failures.append(f"summary {key} mismatch: expected={expected!r}, actual={actual!r}")

    if sections["runtime_bridge"]["result"]["emitted_event"].get("mutation_performed") is not False:
        failures.append("runtime bridge section indicates mutation occurred")

    if sections["progress"]["snapshot"]["execution_order"] != step_ids:
        failures.append("progress execution order mismatch")

    if sections["graph"]["execution_order"] != step_ids:
        failures.append("graph execution order mismatch")

    report["gate"] = {
        "phase": "26I",
        "programme": "26",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_26I_WORKFLOW_REPORT_OWNER_COMPLETE"
            if not failures
            else "PROGRAMME_26I_WORKFLOW_REPORT_OWNER_FAILED"
        ),
        "next_phase": "26J Programme Completion Gate",
    }

    txt_path = REPORT_DIR / "workflow_report_owner_gate_phase_26i.txt"
    json_path = REPORT_DIR / "workflow_report_owner_gate_phase_26i.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 26I Workflow Report Owner Gate",
                "============================================",
                f"passed={not failures}",
                f"workflow_id={report['workflow_id']}",
                f"report_type={report['report_type']}",
                f"sections={','.join(required_sections)}",
                f"workflow_state={summary['workflow_state']}",
                f"current_step_id={summary['current_step_id']}",
                f"readiness_verdict={summary['readiness_verdict']}",
                f"recommendation_kind={summary['recommendation_kind']}",
                f"runtime_bridge_status={summary['runtime_bridge_status']}",
                f"mutation_performed={summary['mutation_performed']}",
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
        print("FAIL_PHASE_26I_WORKFLOW_REPORT_OWNER")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_26I_WORKFLOW_REPORT_OWNER")
    print("schema=LEAF_WORKFLOW_REPORT_OWNER_PHASE_26I_V1")
    print(f"workflow_id={report['workflow_id']}")
    print(f"report_type={report['report_type']}")
    print(f"sections={','.join(required_sections)}")
    print(f"workflow_state={summary['workflow_state']}")
    print(f"current_step_id={summary['current_step_id']}")
    print(f"readiness_verdict={summary['readiness_verdict']}")
    print(f"recommendation_kind={summary['recommendation_kind']}")
    print(f"runtime_bridge_status={summary['runtime_bridge_status']}")
    print(f"mutation_performed={summary['mutation_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_26I_WORKFLOW_REPORT_OWNER_COMPLETE")
    print("next_phase=26J Programme Completion Gate")


if __name__ == "__main__":
    main()
