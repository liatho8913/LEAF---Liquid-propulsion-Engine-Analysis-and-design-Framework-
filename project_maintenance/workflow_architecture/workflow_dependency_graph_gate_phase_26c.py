"""
Programme 26C Completion Gate.

Validates the reusable Workflow Dependency Graph.
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

from leaf_qt.workflow.graph import build_workflow_dependency_graph
from leaf_qt.workflow.model import WorkflowDependency, WorkflowStep, WorkflowStepStatus, build_workflow_model
from leaf_qt.workflow.registry import build_default_engineering_step_registry


def main() -> None:
    py_compile.compile(str(ROOT / "leaf_qt" / "workflow" / "__init__.py"), doraise=True)
    py_compile.compile(str(ROOT / "leaf_qt" / "workflow" / "model.py"), doraise=True)
    py_compile.compile(str(ROOT / "leaf_qt" / "workflow" / "registry.py"), doraise=True)
    py_compile.compile(str(ROOT / "leaf_qt" / "workflow" / "graph.py"), doraise=True)

    registry = build_default_engineering_step_registry()

    workflow = build_workflow_model(
        workflow_id="programme_26c_dependency_graph_gate_workflow",
        title="Programme 26C Dependency Graph Gate Workflow",
        description="Workflow built from registry definitions and analysed through graph infrastructure.",
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
            },
        ),
    )

    graph = build_workflow_dependency_graph(workflow)
    graph_report = graph.report()
    failures = list(graph.validate())

    expected_order = (
        "define_inputs",
        "run_solver",
        "validate_outputs",
        "produce_report",
        "save_design",
    )

    if graph.execution_order() != expected_order:
        failures.append(
            f"execution_order mismatch: expected={expected_order}, actual={graph.execution_order()}"
        )

    if graph.root_nodes() != ("define_inputs",):
        failures.append(f"root_nodes mismatch: actual={graph.root_nodes()}")

    if graph.leaf_nodes() != ("save_design",):
        failures.append(f"leaf_nodes mismatch: actual={graph.leaf_nodes()}")

    if graph.parents("run_solver") != ("define_inputs",):
        failures.append(f"parents(run_solver) mismatch: actual={graph.parents('run_solver')}")

    if graph.children("run_solver") != ("validate_outputs",):
        failures.append(f"children(run_solver) mismatch: actual={graph.children('run_solver')}")

    if graph.ancestors("save_design") != (
        "define_inputs",
        "produce_report",
        "run_solver",
        "validate_outputs",
    ):
        failures.append(f"ancestors(save_design) mismatch: actual={graph.ancestors('save_design')}")

    if graph.descendants("define_inputs") != (
        "produce_report",
        "run_solver",
        "save_design",
        "validate_outputs",
    ):
        failures.append(f"descendants(define_inputs) mismatch: actual={graph.descendants('define_inputs')}")

    if graph.ready_step_ids() != ("run_solver",):
        failures.append(f"ready_step_ids mismatch: actual={graph.ready_step_ids()}")

    blockers = graph.blockers_for("validate_outputs")
    if not blockers:
        failures.append("validate_outputs should be blocked until run_solver is complete")

    if graph.unblocks("run_solver") != ("validate_outputs",):
        failures.append(f"unblocks(run_solver) mismatch: actual={graph.unblocks('run_solver')}")

    cycle_workflow = build_workflow_model(
        workflow_id="programme_26c_cycle_test",
        title="Programme 26C Cycle Test",
        steps=[
            WorkflowStep(
                step_id="a",
                title="A",
                dependencies=(WorkflowDependency("c", "cycle test"),),
            ),
            WorkflowStep(
                step_id="b",
                title="B",
                dependencies=(WorkflowDependency("a", "cycle test"),),
            ),
            WorkflowStep(
                step_id="c",
                title="C",
                dependencies=(WorkflowDependency("b", "cycle test"),),
            ),
        ],
    )

    cycle_graph = build_workflow_dependency_graph(cycle_workflow)
    if not cycle_graph.cycles():
        failures.append("cycle graph did not report dependency cycle")

    missing_workflow = build_workflow_model(
        workflow_id="programme_26c_missing_dependency_test",
        title="Programme 26C Missing Dependency Test",
        steps=[
            WorkflowStep(
                step_id="orphan",
                title="Orphan",
                dependencies=(WorkflowDependency("missing", "missing dependency test"),),
            ),
        ],
    )

    missing_graph = build_workflow_dependency_graph(missing_workflow)
    if not missing_graph.missing_dependencies():
        failures.append("missing dependency graph did not report missing dependency")

    report = graph_report.as_dict()
    report["gate"] = {
        "phase": "26C",
        "programme": "26",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_26C_WORKFLOW_DEPENDENCY_GRAPH_COMPLETE"
            if not failures
            else "PROGRAMME_26C_WORKFLOW_DEPENDENCY_GRAPH_FAILED"
        ),
        "next_phase": "26D Workflow Execution Context",
    }

    txt_path = REPORT_DIR / "workflow_dependency_graph_gate_phase_26c.txt"
    json_path = REPORT_DIR / "workflow_dependency_graph_gate_phase_26c.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 26C Workflow Dependency Graph Gate",
                "================================================",
                f"passed={not failures}",
                f"workflow_id={workflow.workflow_id}",
                f"node_count={report['node_count']}",
                f"edge_count={report['edge_count']}",
                f"root_nodes={','.join(report['root_nodes'])}",
                f"leaf_nodes={','.join(report['leaf_nodes'])}",
                f"execution_order={','.join(report['execution_order'])}",
                f"ready_step_ids={','.join(graph.ready_step_ids())}",
                f"cycles={len(report['cycles'])}",
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
        print("FAIL_PHASE_26C_WORKFLOW_DEPENDENCY_GRAPH")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_26C_WORKFLOW_DEPENDENCY_GRAPH")
    print("schema=LEAF_WORKFLOW_DEPENDENCY_GRAPH_PHASE_26C_V1")
    print(f"workflow_id={workflow.workflow_id}")
    print(f"node_count={report['node_count']}")
    print(f"edge_count={report['edge_count']}")
    print(f"root_nodes={','.join(report['root_nodes'])}")
    print(f"leaf_nodes={','.join(report['leaf_nodes'])}")
    print(f"execution_order={','.join(report['execution_order'])}")
    print(f"ready_step_ids={','.join(graph.ready_step_ids())}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_26C_WORKFLOW_DEPENDENCY_GRAPH_COMPLETE")
    print("next_phase=26D Workflow Execution Context")


if __name__ == "__main__":
    main()
