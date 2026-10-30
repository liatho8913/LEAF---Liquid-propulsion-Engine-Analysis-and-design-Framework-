"""
Programme 26H Completion Gate.

Validates the reusable Workflow Runtime Bridge.
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
from leaf_qt.workflow.runtime_bridge import (
    WorkflowRuntimeBridgeAction,
    WorkflowRuntimeBridgeStatus,
    build_workflow_runtime_bridge,
)


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
        workflow_id="programme_26h_runtime_bridge_workflow",
        title="Programme 26H Runtime Bridge Workflow",
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

    ready_context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="run_solver",
        active_module="platform_test_module",
        runtime_reference="runtime:test-session",
    )

    blocked_context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="validate_outputs",
        active_module="platform_test_module",
        runtime_reference="runtime:test-session",
    )

    invalid_context = build_workflow_execution_context(
        workflow=workflow,
        current_step_id="run_solver",
        active_module="",
        runtime_reference="runtime:test-session",
    )

    ready_bridge = build_workflow_runtime_bridge(ready_context)
    blocked_bridge = build_workflow_runtime_bridge(blocked_context)
    invalid_bridge = build_workflow_runtime_bridge(invalid_context)

    execute_request = ready_bridge.build_request(
        WorkflowRuntimeBridgeAction.EXECUTE_STEP,
        payload={"gate": "26H"},
    )
    execute_report = ready_bridge.report(execute_request)

    blocked_request = blocked_bridge.build_request(WorkflowRuntimeBridgeAction.EXECUTE_STEP)
    blocked_report = blocked_bridge.report(blocked_request)

    event_request = ready_bridge.build_request(WorkflowRuntimeBridgeAction.EMIT_WORKFLOW_EVENT)
    event_report = ready_bridge.report(event_request)

    noop_request = ready_bridge.build_request(WorkflowRuntimeBridgeAction.NO_OP)
    noop_report = ready_bridge.report(noop_request)

    invalid_request = invalid_bridge.build_request(WorkflowRuntimeBridgeAction.EXECUTE_STEP)
    invalid_report = invalid_bridge.report(invalid_request)

    reports = {
        "execute": execute_report,
        "blocked": blocked_report,
        "event": event_report,
        "noop": noop_report,
        "invalid": invalid_report,
    }

    failures = []

    execute = reports["execute"]["result"]
    blocked = reports["blocked"]["result"]
    event = reports["event"]["result"]
    noop = reports["noop"]["result"]
    invalid = reports["invalid"]["result"]

    if execute["status"] != WorkflowRuntimeBridgeStatus.ACCEPTED.value:
        failures.append(f"execute status mismatch: actual={execute['status']}")

    if execute["accepted"] is not True:
        failures.append("ready EXECUTE_STEP request should be accepted")

    if execute["emitted_event"].get("mutation_performed") is not False:
        failures.append("runtime bridge must not mutate runtime directly")

    if execute["emitted_event"].get("event_type") != "workflow.runtime.execute_step_requested":
        failures.append(
            "execute emitted_event type mismatch: "
            f"actual={execute['emitted_event'].get('event_type')}"
        )

    if blocked["status"] != WorkflowRuntimeBridgeStatus.BLOCKED.value:
        failures.append(f"blocked status mismatch: actual={blocked['status']}")

    if blocked["accepted"] is not False:
        failures.append("blocked EXECUTE_STEP request should not be accepted")

    if event["status"] != WorkflowRuntimeBridgeStatus.ACCEPTED.value:
        failures.append(f"event status mismatch: actual={event['status']}")

    if event["accepted"] is not True:
        failures.append("EMIT_WORKFLOW_EVENT should be accepted")

    if noop["status"] != WorkflowRuntimeBridgeStatus.ACCEPTED.value:
        failures.append(f"noop status mismatch: actual={noop['status']}")

    if invalid["status"] != WorkflowRuntimeBridgeStatus.INVALID_CONTEXT.value:
        failures.append(f"invalid status mismatch: actual={invalid['status']}")

    if invalid["accepted"] is not False:
        failures.append("invalid context request should not be accepted")

    report = {
        "schema": "LEAF_WORKFLOW_RUNTIME_BRIDGE_COMPLETION_PHASE_26H_V1",
        "reports": reports,
        "gate": {
            "phase": "26H",
            "programme": "26",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_26H_WORKFLOW_RUNTIME_BRIDGE_COMPLETE"
                if not failures
                else "PROGRAMME_26H_WORKFLOW_RUNTIME_BRIDGE_FAILED"
            ),
            "next_phase": "26I Workflow Report Owner",
        },
    }

    txt_path = REPORT_DIR / "workflow_runtime_bridge_gate_phase_26h.txt"
    json_path = REPORT_DIR / "workflow_runtime_bridge_gate_phase_26h.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 26H Workflow Runtime Bridge Gate",
                "===============================================",
                f"passed={not failures}",
                f"workflow_id={workflow.workflow_id}",
                f"execute_status={execute['status']}",
                f"execute_accepted={execute['accepted']}",
                f"blocked_status={blocked['status']}",
                f"blocked_accepted={blocked['accepted']}",
                f"event_status={event['status']}",
                f"noop_status={noop['status']}",
                f"invalid_status={invalid['status']}",
                f"mutation_performed={execute['emitted_event'].get('mutation_performed')}",
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
        print("FAIL_PHASE_26H_WORKFLOW_RUNTIME_BRIDGE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_26H_WORKFLOW_RUNTIME_BRIDGE")
    print("schema=LEAF_WORKFLOW_RUNTIME_BRIDGE_PHASE_26H_V1")
    print(f"workflow_id={workflow.workflow_id}")
    print(f"execute_status={execute['status']}")
    print(f"execute_accepted={execute['accepted']}")
    print(f"blocked_status={blocked['status']}")
    print(f"blocked_accepted={blocked['accepted']}")
    print(f"event_status={event['status']}")
    print(f"noop_status={noop['status']}")
    print(f"invalid_status={invalid['status']}")
    print(f"mutation_performed={execute['emitted_event'].get('mutation_performed')}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_26H_WORKFLOW_RUNTIME_BRIDGE_COMPLETE")
    print("next_phase=26I Workflow Report Owner")


if __name__ == "__main__":
    main()
