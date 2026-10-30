"""
Programme 26J Completion Gate.

Signs off Programme 26: Engineering Workflow Orchestration Platform.
"""

from __future__ import annotations

import importlib
import json
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORT_DIR = ROOT / "LEAF_Reports" / "workflow_architecture"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

REQUIRED_FILES = [
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
]

REQUIRED_EXPORTS = [
    "WorkflowDependency",
    "WorkflowModel",
    "WorkflowState",
    "WorkflowStep",
    "WorkflowStepStatus",
    "build_workflow_model",
    "WorkflowStepDefinition",
    "WorkflowStepRegistry",
    "build_default_engineering_step_registry",
    "WorkflowDependencyGraph",
    "WorkflowGraphReport",
    "build_workflow_dependency_graph",
    "WorkflowExecutionContext",
    "WorkflowExecutionPermission",
    "WorkflowValidationMode",
    "build_workflow_execution_context",
    "WorkflowProgressSnapshot",
    "WorkflowProgressTracker",
    "build_workflow_progress_tracker",
    "WorkflowReadinessGate",
    "WorkflowReadinessResult",
    "WorkflowReadinessVerdict",
    "build_workflow_readiness_gate",
    "WorkflowRecommendation",
    "WorkflowRecommendationEngine",
    "WorkflowRecommendationKind",
    "build_workflow_recommendation_engine",
    "WorkflowRuntimeBridge",
    "WorkflowRuntimeBridgeAction",
    "WorkflowRuntimeBridgeRequest",
    "WorkflowRuntimeBridgeResult",
    "WorkflowRuntimeBridgeStatus",
    "build_workflow_runtime_bridge",
    "WorkflowReportOwner",
    "WorkflowReportPackage",
    "build_workflow_report_owner",
]


def main() -> None:
    failures = []

    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.exists():
            failures.append(f"missing required file: {rel}")
            continue
        py_compile.compile(str(path), doraise=True)

    workflow_pkg = importlib.import_module("leaf_qt.workflow")

    for name in REQUIRED_EXPORTS:
        if not hasattr(workflow_pkg, name):
            failures.append(f"missing workflow package export: {name}")

    from leaf_qt.workflow import (
        WorkflowRuntimeBridgeAction,
        WorkflowStepStatus,
        build_default_engineering_step_registry,
        build_workflow_execution_context,
        build_workflow_model,
        build_workflow_report_owner,
    )

    registry = build_default_engineering_step_registry()
    step_ids = [
        "define_inputs",
        "run_solver",
        "validate_outputs",
        "produce_report",
        "save_design",
    ]

    workflow = build_workflow_model(
        workflow_id="programme_26_completion_gate_workflow",
        title="Programme 26 Completion Gate Workflow",
        description="End-to-end workflow proving Programme 26 platform integration.",
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
        active_module="programme_26_completion_gate",
        runtime_reference="runtime:programme-26-gate",
        storage_reference="storage:programme-26-gate",
        metadata={"completion_gate": "26J"},
    )

    package = build_workflow_report_owner(context).build_report(
        include_runtime_bridge=True,
        bridge_action=WorkflowRuntimeBridgeAction.EXECUTE_STEP,
        bridge_payload={"completion_gate": "26J"},
        metadata={"programme_completion": "26"},
    )

    report_package = package.as_dict()
    summary = report_package["summary"]
    sections = report_package["sections"]

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
            failures.append(f"completion report missing section: {section}")

    if summary.get("readiness_verdict") != "READY":
        failures.append(f"expected readiness READY, actual={summary.get('readiness_verdict')}")

    if summary.get("recommendation_kind") != "PROCEED_CURRENT_STEP":
        failures.append(
            f"expected recommendation PROCEED_CURRENT_STEP, actual={summary.get('recommendation_kind')}"
        )

    if summary.get("runtime_bridge_status") != "ACCEPTED":
        failures.append(
            f"expected runtime bridge ACCEPTED, actual={summary.get('runtime_bridge_status')}"
        )

    if summary.get("mutation_performed") is not False:
        failures.append("runtime mutation must remain false at workflow bridge boundary")

    if sections["graph"]["execution_order"] != step_ids:
        failures.append("workflow graph execution order does not match default engineering process")

    if sections["progress"]["snapshot"]["percent_complete"] != 20.0:
        failures.append("workflow progress tracker did not report expected 20.0 percent completion")

    final_report = {
        "schema": "LEAF_PROGRAMME_26_COMPLETION_GATE_PHASE_26J_V1",
        "programme": "26",
        "programme_name": "Engineering Workflow Orchestration Platform",
        "phase": "26J",
        "required_files": REQUIRED_FILES,
        "required_exports": REQUIRED_EXPORTS,
        "workflow_report_package": report_package,
        "status": {
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_26_COMPLETE_ENGINEERING_WORKFLOW_ORCHESTRATION_PLATFORM_SIGNED_OFF"
                if not failures
                else "PROGRAMME_26_COMPLETION_GATE_FAILED"
            ),
            "next_programme": "27 Project-Wide Standardisation Platform",
            "next_phase": "27A Standardisation Inventory Model",
        },
    }

    txt_path = REPORT_DIR / "programme_26_completion_gate_phase_26j.txt"
    json_path = REPORT_DIR / "programme_26_completion_gate_phase_26j.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 26 Completion Gate",
                "================================",
                f"passed={not failures}",
                "programme=26",
                "programme_name=Engineering Workflow Orchestration Platform",
                f"required_files={len(REQUIRED_FILES)}",
                f"required_exports={len(REQUIRED_EXPORTS)}",
                f"workflow_id={workflow.workflow_id}",
                f"workflow_state={summary.get('workflow_state')}",
                f"current_step_id={summary.get('current_step_id')}",
                f"readiness_verdict={summary.get('readiness_verdict')}",
                f"recommendation_kind={summary.get('recommendation_kind')}",
                f"runtime_bridge_status={summary.get('runtime_bridge_status')}",
                f"mutation_performed={summary.get('mutation_performed')}",
                f"failures={len(failures)}",
                f"completion_notice={final_report['status']['completion_notice']}",
                f"next_programme={final_report['status']['next_programme']}",
                f"next_phase={final_report['status']['next_phase']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    json_path.write_text(json.dumps(final_report, indent=2), encoding="utf-8")

    if failures:
        print("FAIL_PHASE_26J_PROGRAMME_COMPLETION_GATE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_26J_PROGRAMME_COMPLETION_GATE")
    print("schema=LEAF_PROGRAMME_26_COMPLETION_GATE_PHASE_26J_V1")
    print("programme=26")
    print("programme_name=Engineering Workflow Orchestration Platform")
    print(f"required_files={len(REQUIRED_FILES)}")
    print(f"required_exports={len(REQUIRED_EXPORTS)}")
    print(f"workflow_id={workflow.workflow_id}")
    print(f"workflow_state={summary.get('workflow_state')}")
    print(f"current_step_id={summary.get('current_step_id')}")
    print(f"readiness_verdict={summary.get('readiness_verdict')}")
    print(f"recommendation_kind={summary.get('recommendation_kind')}")
    print(f"runtime_bridge_status={summary.get('runtime_bridge_status')}")
    print(f"mutation_performed={summary.get('mutation_performed')}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_26_COMPLETE_ENGINEERING_WORKFLOW_ORCHESTRATION_PLATFORM_SIGNED_OFF")
    print("next_programme=27 Project-Wide Standardisation Platform")
    print("next_phase=27A Standardisation Inventory Model")


if __name__ == "__main__":
    main()
