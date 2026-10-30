"""
Programme 26B Completion Gate.

Validates the reusable Workflow Step Registry.
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
from leaf_qt.workflow.registry import (
    WorkflowDependency,
    WorkflowStepDefinition,
    WorkflowStepRegistry,
    build_default_engineering_step_registry,
)


def main() -> None:
    py_compile.compile(str(ROOT / "leaf_qt" / "workflow" / "__init__.py"), doraise=True)
    py_compile.compile(str(ROOT / "leaf_qt" / "workflow" / "model.py"), doraise=True)
    py_compile.compile(str(ROOT / "leaf_qt" / "workflow" / "registry.py"), doraise=True)

    registry = build_default_engineering_step_registry()
    failures = registry.validate()

    expected_ids = (
        "define_inputs",
        "run_solver",
        "validate_outputs",
        "produce_report",
        "save_design",
    )

    actual_ids = tuple(definition.step_id for definition in registry.all_definitions())
    if actual_ids != expected_ids:
        failures.append(f"default registry ids mismatch: expected={expected_ids}, actual={actual_ids}")

    statuses = {
        "define_inputs": WorkflowStepStatus.COMPLETE,
        "run_solver": WorkflowStepStatus.READY,
    }

    workflow = build_workflow_model(
        workflow_id="programme_26b_registry_gate_workflow",
        title="Programme 26B Registry Gate Workflow",
        description="Workflow built entirely from registered reusable step definitions.",
        steps=registry.build_steps(expected_ids, statuses=statuses),
    )

    workflow_failures = workflow.validate()
    failures.extend(workflow_failures)

    if workflow.ready_step_ids() != ("run_solver",):
        failures.append(
            f"ready step mismatch: expected=('run_solver',), actual={workflow.ready_step_ids()}"
        )

    validate_blockers = workflow.blockers_for("validate_outputs")
    if not validate_blockers:
        failures.append("validate_outputs should be blocked until run_solver is complete")

    duplicate_error_detected = False
    try:
        registry.register(
            WorkflowStepDefinition(
                step_id="define_inputs",
                title="Duplicate Define Inputs",
            )
        )
    except ValueError:
        duplicate_error_detected = True

    if not duplicate_error_detected:
        failures.append("duplicate registry insertion was not rejected")

    missing_dependency_registry = WorkflowStepRegistry("missing_dependency_test")
    missing_dependency_registry.register(
        WorkflowStepDefinition(
            step_id="orphan",
            title="Orphan",
            dependencies=(
                WorkflowDependency(
                    required_step_id="missing",
                    reason="Missing dependency must be reported.",
                ),
            ),
        )
    )

    missing_dependency_failures = missing_dependency_registry.validate()
    if not any("unregistered" in failure for failure in missing_dependency_failures):
        failures.append("registry did not report unregistered dependency")

    cycle_registry = WorkflowStepRegistry("cycle_test")
    cycle_registry.register_many(
        [
            WorkflowStepDefinition(
                step_id="a",
                title="A",
                dependencies=(WorkflowDependency("b", "cycle test"),),
            ),
            WorkflowStepDefinition(
                step_id="b",
                title="B",
                dependencies=(WorkflowDependency("a", "cycle test"),),
            ),
        ]
    )

    cycle_failures = cycle_registry.validate()
    if not any("cycle" in failure.lower() for failure in cycle_failures):
        failures.append("registry did not detect dependency cycle")

    report = registry.report()
    report["workflow_report"] = workflow.report()
    report["gate"] = {
        "phase": "26B",
        "programme": "26",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_26B_WORKFLOW_STEP_REGISTRY_COMPLETE"
            if not failures
            else "PROGRAMME_26B_WORKFLOW_STEP_REGISTRY_FAILED"
        ),
        "next_phase": "26C Workflow Dependency Graph",
    }

    txt_path = REPORT_DIR / "workflow_step_registry_gate_phase_26b.txt"
    json_path = REPORT_DIR / "workflow_step_registry_gate_phase_26b.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 26B Workflow Step Registry Gate",
                "===============================================",
                f"passed={not failures}",
                f"registry_id={registry.registry_id}",
                f"definition_count={report['definition_count']}",
                f"default_step_ids={','.join(actual_ids)}",
                f"workflow_state={report['workflow_report']['state']}",
                f"ready_step_ids={','.join(report['workflow_report']['ready_step_ids'])}",
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
        print("FAIL_PHASE_26B_WORKFLOW_STEP_REGISTRY")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_26B_WORKFLOW_STEP_REGISTRY")
    print("schema=LEAF_WORKFLOW_STEP_REGISTRY_PHASE_26B_V1")
    print(f"registry_id={registry.registry_id}")
    print(f"definition_count={report['definition_count']}")
    print(f"default_step_ids={','.join(actual_ids)}")
    print(f"workflow_state={report['workflow_report']['state']}")
    print(f"ready_step_ids={','.join(report['workflow_report']['ready_step_ids'])}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_26B_WORKFLOW_STEP_REGISTRY_COMPLETE")
    print("next_phase=26C Workflow Dependency Graph")


if __name__ == "__main__":
    main()
