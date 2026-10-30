"""
Programme 26C: Workflow Dependency Graph.

Reusable workflow graph engine.

Design rules:
- Pure platform infrastructure.
- No Qt ownership.
- No engineering-domain hardcoding.
- No storage/runtime/report side effects.
- Centralises dependency traversal so later workflow systems do not duplicate it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Set, Tuple

from .model import WorkflowModel, WorkflowStepStatus


@dataclass(frozen=True)
class WorkflowGraphReport:
    schema: str
    workflow_id: str
    node_count: int
    edge_count: int
    root_nodes: Tuple[str, ...]
    leaf_nodes: Tuple[str, ...]
    execution_order: Tuple[str, ...]
    cycles: Tuple[str, ...]
    validation_failures: Tuple[str, ...]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "workflow_id": self.workflow_id,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "root_nodes": list(self.root_nodes),
            "leaf_nodes": list(self.leaf_nodes),
            "execution_order": list(self.execution_order),
            "cycles": list(self.cycles),
            "validation_failures": list(self.validation_failures),
        }


class WorkflowDependencyGraph:
    """
    Shared dependency graph for workflow models.

    Edge direction:
        dependency -> dependent

    Example:
        define_inputs -> run_solver -> validate_outputs
    """

    def __init__(self, workflow: WorkflowModel) -> None:
        self.workflow = workflow
        self.workflow_id = workflow.workflow_id
        self._steps = workflow.step_map()
        self._children: Dict[str, Set[str]] = {step_id: set() for step_id in self._steps}
        self._parents: Dict[str, Set[str]] = {step_id: set() for step_id in self._steps}
        self._build()

    def _build(self) -> None:
        for step in self.workflow.steps:
            for dependency in step.dependencies:
                parent = dependency.required_step_id
                child = step.step_id

                if parent not in self._steps:
                    continue

                self._children[parent].add(child)
                self._parents[child].add(parent)

    @property
    def nodes(self) -> Tuple[str, ...]:
        return tuple(self._steps.keys())

    @property
    def edges(self) -> Tuple[Tuple[str, str], ...]:
        result: List[Tuple[str, str]] = []
        for parent in self.nodes:
            for child in sorted(self._children[parent]):
                result.append((parent, child))
        return tuple(result)

    def parents(self, step_id: str) -> Tuple[str, ...]:
        self._require_step(step_id)
        return tuple(sorted(self._parents[step_id]))

    def children(self, step_id: str) -> Tuple[str, ...]:
        self._require_step(step_id)
        return tuple(sorted(self._children[step_id]))

    def ancestors(self, step_id: str) -> Tuple[str, ...]:
        self._require_step(step_id)
        found: Set[str] = set()

        def walk(current: str) -> None:
            for parent in self._parents[current]:
                if parent not in found:
                    found.add(parent)
                    walk(parent)

        walk(step_id)
        return tuple(sorted(found))

    def descendants(self, step_id: str) -> Tuple[str, ...]:
        self._require_step(step_id)
        found: Set[str] = set()

        def walk(current: str) -> None:
            for child in self._children[current]:
                if child not in found:
                    found.add(child)
                    walk(child)

        walk(step_id)
        return tuple(sorted(found))

    def root_nodes(self) -> Tuple[str, ...]:
        return tuple(step_id for step_id in self.nodes if not self._parents[step_id])

    def leaf_nodes(self) -> Tuple[str, ...]:
        return tuple(step_id for step_id in self.nodes if not self._children[step_id])

    def cycles(self) -> Tuple[str, ...]:
        cycles: List[str] = []
        visiting: Set[str] = set()
        visited: Set[str] = set()

        def visit(step_id: str, trail: Tuple[str, ...]) -> None:
            if step_id in visited:
                return

            if step_id in visiting:
                if step_id in trail:
                    start = trail.index(step_id)
                    cycle_path = (*trail[start:], step_id)
                else:
                    cycle_path = (*trail, step_id)
                cycles.append(" -> ".join(cycle_path))
                return

            visiting.add(step_id)
            for child in self._children.get(step_id, set()):
                visit(child, (*trail, step_id))
            visiting.remove(step_id)
            visited.add(step_id)

        for step_id in self.nodes:
            visit(step_id, tuple())

        return tuple(sorted(set(cycles)))

    def execution_order(self) -> Tuple[str, ...]:
        """
        Return topological execution order.

        If cycles exist, returns the acyclic partial order available before the
        cycle prevents completion.
        """

        in_degree = {step_id: len(self._parents[step_id]) for step_id in self.nodes}
        ready = [step_id for step_id in self.nodes if in_degree[step_id] == 0]
        order: List[str] = []

        while ready:
            step_id = ready.pop(0)
            order.append(step_id)

            for child in sorted(self._children[step_id]):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    ready.append(child)

        return tuple(order)

    def missing_dependencies(self) -> Tuple[str, ...]:
        failures: List[str] = []
        step_ids = set(self._steps)

        for step in self.workflow.steps:
            for dependency in step.dependencies:
                if dependency.required_step_id not in step_ids:
                    failures.append(
                        f"{step.step_id} depends on missing step {dependency.required_step_id}"
                    )

        return tuple(failures)

    def blockers_for(self, step_id: str) -> Tuple[str, ...]:
        self._require_step(step_id)
        blockers: List[str] = []

        step = self._steps[step_id]

        for dependency in step.dependencies:
            required = self._steps.get(dependency.required_step_id)

            if required is None:
                blockers.append(
                    f"Missing dependency {dependency.required_step_id}: {dependency.reason}"
                )
                continue

            if required.status != WorkflowStepStatus.COMPLETE:
                blockers.append(
                    f"{dependency.required_step_id} is {required.status.value}: "
                    f"{dependency.reason}"
                )

        return tuple(blockers)

    def ready_step_ids(self) -> Tuple[str, ...]:
        ready: List[str] = []

        for step_id in self.nodes:
            step = self._steps[step_id]

            if step.status in {
                WorkflowStepStatus.COMPLETE,
                WorkflowStepStatus.FAILED,
                WorkflowStepStatus.SKIPPED,
            }:
                continue

            if not self.blockers_for(step_id):
                ready.append(step_id)

        return tuple(ready)

    def unblocks(self, step_id: str) -> Tuple[str, ...]:
        """
        Return incomplete downstream steps that directly depend on this step.
        """

        self._require_step(step_id)
        result: List[str] = []

        for child_id in self.children(step_id):
            child = self._steps[child_id]
            if child.status not in {
                WorkflowStepStatus.COMPLETE,
                WorkflowStepStatus.FAILED,
                WorkflowStepStatus.SKIPPED,
            }:
                result.append(child_id)

        return tuple(result)

    def validate(self) -> Tuple[str, ...]:
        failures: List[str] = []
        failures.extend(self.missing_dependencies())

        for cycle in self.cycles():
            failures.append(f"workflow dependency cycle detected: {cycle}")

        order = self.execution_order()
        if len(order) != len(self.nodes) and not self.cycles():
            failures.append("workflow execution order incomplete for unknown reason")

        return tuple(failures)

    def report(self) -> WorkflowGraphReport:
        return WorkflowGraphReport(
            schema="LEAF_WORKFLOW_DEPENDENCY_GRAPH_PHASE_26C_V1",
            workflow_id=self.workflow_id,
            node_count=len(self.nodes),
            edge_count=len(self.edges),
            root_nodes=self.root_nodes(),
            leaf_nodes=self.leaf_nodes(),
            execution_order=self.execution_order(),
            cycles=self.cycles(),
            validation_failures=self.validate(),
        )

    def _require_step(self, step_id: str) -> None:
        if step_id not in self._steps:
            raise KeyError(f"unknown workflow step: {step_id}")


def build_workflow_dependency_graph(workflow: WorkflowModel) -> WorkflowDependencyGraph:
    return WorkflowDependencyGraph(workflow)
