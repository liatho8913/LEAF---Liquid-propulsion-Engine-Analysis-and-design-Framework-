"""
Programme 26A: Engineering Workflow Model.

This module defines the reusable platform-level workflow model for LEAF.

Design rules:
- No Qt ownership.
- No engineering-domain hardcoding.
- No runtime/storage/report side effects.
- Reusable by regen, nozzle, chamber, turbomachinery, CFD, and future modules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


class WorkflowStepStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    READY = "READY"
    BLOCKED = "BLOCKED"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class WorkflowState(str, Enum):
    EMPTY = "EMPTY"
    READY = "READY"
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


@dataclass(frozen=True)
class WorkflowDependency:
    """
    A dependency from one workflow step to another.

    required_step_id:
        The step that must be complete before the dependent step is ready.
    reason:
        Human-readable explanation for reports and blockers.
    """

    required_step_id: str
    reason: str = "Required previous workflow step is incomplete."

    def validate(self) -> List[str]:
        failures: List[str] = []
        if not self.required_step_id or not self.required_step_id.strip():
            failures.append("dependency.required_step_id is empty")
        if not self.reason or not self.reason.strip():
            failures.append(f"dependency.reason is empty for {self.required_step_id!r}")
        return failures


@dataclass
class WorkflowStep:
    """
    A reusable workflow step.

    This is intentionally generic. Engineering modules attach meaning through
    metadata and later registries, not through hardcoded platform behaviour.
    """

    step_id: str
    title: str
    description: str = ""
    owner: str = "platform"
    status: WorkflowStepStatus = WorkflowStepStatus.NOT_STARTED
    dependencies: Tuple[WorkflowDependency, ...] = field(default_factory=tuple)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.step_id or not self.step_id.strip():
            failures.append("step.step_id is empty")

        if not self.title or not self.title.strip():
            failures.append(f"step.title is empty for {self.step_id!r}")

        if not self.owner or not self.owner.strip():
            failures.append(f"step.owner is empty for {self.step_id!r}")

        if not isinstance(self.status, WorkflowStepStatus):
            failures.append(f"step.status is invalid for {self.step_id!r}: {self.status!r}")

        for dependency in self.dependencies:
            failures.extend(dependency.validate())

        return failures

    def dependency_ids(self) -> Tuple[str, ...]:
        return tuple(dependency.required_step_id for dependency in self.dependencies)

    def is_terminal(self) -> bool:
        return self.status in {
            WorkflowStepStatus.COMPLETE,
            WorkflowStepStatus.FAILED,
            WorkflowStepStatus.SKIPPED,
        }


@dataclass
class WorkflowModel:
    """
    Reusable engineering workflow model.

    This model describes the workflow only. It does not execute actions.
    Execution belongs to later Programme 26 phases.
    """

    workflow_id: str
    title: str
    description: str = ""
    version: str = "1.0.0"
    steps: Tuple[WorkflowStep, ...] = field(default_factory=tuple)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.workflow_id or not self.workflow_id.strip():
            failures.append("workflow.workflow_id is empty")

        if not self.title or not self.title.strip():
            failures.append(f"workflow.title is empty for {self.workflow_id!r}")

        if not self.version or not self.version.strip():
            failures.append(f"workflow.version is empty for {self.workflow_id!r}")

        seen: set[str] = set()
        step_ids = {step.step_id for step in self.steps}

        for step in self.steps:
            failures.extend(step.validate())

            if step.step_id in seen:
                failures.append(f"duplicate step_id: {step.step_id!r}")
            seen.add(step.step_id)

            for dependency_id in step.dependency_ids():
                if dependency_id not in step_ids:
                    failures.append(
                        f"step {step.step_id!r} depends on missing step {dependency_id!r}"
                    )

                if dependency_id == step.step_id:
                    failures.append(f"step {step.step_id!r} depends on itself")

        failures.extend(self._detect_cycles())

        return failures

    def _detect_cycles(self) -> List[str]:
        failures: List[str] = []
        graph = {step.step_id: step.dependency_ids() for step in self.steps}
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(step_id: str, trail: Tuple[str, ...]) -> None:
            if step_id in visited:
                return
            if step_id in visiting:
                cycle = " -> ".join((*trail, step_id))
                failures.append(f"workflow dependency cycle detected: {cycle}")
                return

            visiting.add(step_id)
            for dependency_id in graph.get(step_id, ()):
                visit(dependency_id, (*trail, step_id))
            visiting.remove(step_id)
            visited.add(step_id)

        for step_id in graph:
            visit(step_id, tuple())

        return failures

    def step_map(self) -> Dict[str, WorkflowStep]:
        return {step.step_id: step for step in self.steps}

    def blockers_for(self, step_id: str) -> List[str]:
        steps = self.step_map()
        step = steps.get(step_id)

        if step is None:
            return [f"Unknown workflow step: {step_id}"]

        blockers: List[str] = []

        for dependency in step.dependencies:
            required = steps.get(dependency.required_step_id)
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

        return blockers

    def ready_step_ids(self) -> Tuple[str, ...]:
        ready: List[str] = []

        for step in self.steps:
            if step.status in {
                WorkflowStepStatus.COMPLETE,
                WorkflowStepStatus.FAILED,
                WorkflowStepStatus.SKIPPED,
            }:
                continue

            if not self.blockers_for(step.step_id):
                ready.append(step.step_id)

        return tuple(ready)

    def state(self) -> WorkflowState:
        if not self.steps:
            return WorkflowState.EMPTY

        statuses = {step.status for step in self.steps}

        if WorkflowStepStatus.FAILED in statuses:
            return WorkflowState.FAILED

        if all(step.status == WorkflowStepStatus.COMPLETE for step in self.steps):
            return WorkflowState.COMPLETE

        if WorkflowStepStatus.ACTIVE in statuses:
            return WorkflowState.ACTIVE

        if self.ready_step_ids():
            return WorkflowState.READY

        return WorkflowState.BLOCKED

    def progress(self) -> Dict[str, Any]:
        total = len(self.steps)
        complete = sum(1 for step in self.steps if step.status == WorkflowStepStatus.COMPLETE)
        failed = sum(1 for step in self.steps if step.status == WorkflowStepStatus.FAILED)
        skipped = sum(1 for step in self.steps if step.status == WorkflowStepStatus.SKIPPED)
        ready = len(self.ready_step_ids())

        percent_complete = 0.0 if total == 0 else round((complete / total) * 100.0, 3)

        return {
            "workflow_id": self.workflow_id,
            "state": self.state().value,
            "total_steps": total,
            "complete_steps": complete,
            "failed_steps": failed,
            "skipped_steps": skipped,
            "ready_steps": ready,
            "percent_complete": percent_complete,
        }

    def report(self) -> Dict[str, Any]:
        return {
            "schema": "LEAF_WORKFLOW_MODEL_PHASE_26A_V1",
            "workflow_id": self.workflow_id,
            "title": self.title,
            "version": self.version,
            "state": self.state().value,
            "progress": self.progress(),
            "ready_step_ids": list(self.ready_step_ids()),
            "validation_failures": self.validate(),
            "steps": [
                {
                    "step_id": step.step_id,
                    "title": step.title,
                    "owner": step.owner,
                    "status": step.status.value,
                    "dependencies": list(step.dependency_ids()),
                    "blockers": self.blockers_for(step.step_id),
                }
                for step in self.steps
            ],
        }


def build_workflow_model(
    workflow_id: str,
    title: str,
    steps: Iterable[WorkflowStep],
    description: str = "",
    version: str = "1.0.0",
    metadata: Optional[Mapping[str, Any]] = None,
) -> WorkflowModel:
    """
    Factory used by future registries and module adapters.

    Keeping construction here prevents each engineering module from inventing
    its own workflow model shape.
    """

    return WorkflowModel(
        workflow_id=workflow_id,
        title=title,
        description=description,
        version=version,
        steps=tuple(steps),
        metadata=dict(metadata or {}),
    )
