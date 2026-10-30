"""
Programme 26E: Workflow Progress Tracker.

Reusable progress tracking for LEAF workflows.

Design rules:
- Reuse WorkflowModel and WorkflowDependencyGraph.
- Do not duplicate graph traversal logic.
- No Qt ownership.
- No solver execution.
- No storage writes.
- No runtime mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .graph import WorkflowDependencyGraph, build_workflow_dependency_graph
from .model import WorkflowModel, WorkflowStepStatus


@dataclass(frozen=True)
class WorkflowProgressSnapshot:
    schema: str
    workflow_id: str
    workflow_state: str
    total_steps: int
    complete_steps: int
    active_steps: int
    ready_steps: int
    blocked_steps: int
    failed_steps: int
    skipped_steps: int
    remaining_steps: int
    terminal_steps: int
    percent_complete: float
    percent_terminal: float
    current_ready_step: str | None
    ready_step_ids: Tuple[str, ...]
    blocked_step_ids: Tuple[str, ...]
    complete_step_ids: Tuple[str, ...]
    remaining_step_ids: Tuple[str, ...]
    execution_order: Tuple[str, ...]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "workflow_id": self.workflow_id,
            "workflow_state": self.workflow_state,
            "total_steps": self.total_steps,
            "complete_steps": self.complete_steps,
            "active_steps": self.active_steps,
            "ready_steps": self.ready_steps,
            "blocked_steps": self.blocked_steps,
            "failed_steps": self.failed_steps,
            "skipped_steps": self.skipped_steps,
            "remaining_steps": self.remaining_steps,
            "terminal_steps": self.terminal_steps,
            "percent_complete": self.percent_complete,
            "percent_terminal": self.percent_terminal,
            "current_ready_step": self.current_ready_step,
            "ready_step_ids": list(self.ready_step_ids),
            "blocked_step_ids": list(self.blocked_step_ids),
            "complete_step_ids": list(self.complete_step_ids),
            "remaining_step_ids": list(self.remaining_step_ids),
            "execution_order": list(self.execution_order),
        }


class WorkflowProgressTracker:
    """
    Shared progress tracker for workflow models.

    This class depends on the graph engine for readiness/blocker logic. It
    intentionally avoids reimplementing dependency traversal.
    """

    def __init__(self, workflow: WorkflowModel) -> None:
        self.workflow = workflow
        self.graph: WorkflowDependencyGraph = build_workflow_dependency_graph(workflow)

    def step_ids_by_status(self, status: WorkflowStepStatus) -> Tuple[str, ...]:
        return tuple(
            step.step_id
            for step in self.workflow.steps
            if step.status == status
        )

    def complete_step_ids(self) -> Tuple[str, ...]:
        return self.step_ids_by_status(WorkflowStepStatus.COMPLETE)

    def active_step_ids(self) -> Tuple[str, ...]:
        return self.step_ids_by_status(WorkflowStepStatus.ACTIVE)

    def failed_step_ids(self) -> Tuple[str, ...]:
        return self.step_ids_by_status(WorkflowStepStatus.FAILED)

    def skipped_step_ids(self) -> Tuple[str, ...]:
        return self.step_ids_by_status(WorkflowStepStatus.SKIPPED)

    def ready_step_ids(self) -> Tuple[str, ...]:
        return self.graph.ready_step_ids()

    def blocked_step_ids(self) -> Tuple[str, ...]:
        blocked: List[str] = []

        for step in self.workflow.steps:
            if step.status in {
                WorkflowStepStatus.COMPLETE,
                WorkflowStepStatus.FAILED,
                WorkflowStepStatus.SKIPPED,
            }:
                continue

            if self.graph.blockers_for(step.step_id):
                blocked.append(step.step_id)

        return tuple(blocked)

    def remaining_step_ids(self) -> Tuple[str, ...]:
        return tuple(
            step.step_id
            for step in self.workflow.steps
            if step.status not in {
                WorkflowStepStatus.COMPLETE,
                WorkflowStepStatus.FAILED,
                WorkflowStepStatus.SKIPPED,
            }
        )

    def current_ready_step(self) -> str | None:
        ready = self.ready_step_ids()
        if not ready:
            return None

        execution_order = self.graph.execution_order()
        for step_id in execution_order:
            if step_id in ready:
                return step_id

        return ready[0]

    def snapshot(self) -> WorkflowProgressSnapshot:
        total = len(self.workflow.steps)
        complete = len(self.complete_step_ids())
        active = len(self.active_step_ids())
        ready = len(self.ready_step_ids())
        blocked = len(self.blocked_step_ids())
        failed = len(self.failed_step_ids())
        skipped = len(self.skipped_step_ids())
        remaining = len(self.remaining_step_ids())
        terminal = complete + failed + skipped

        percent_complete = 0.0 if total == 0 else round((complete / total) * 100.0, 3)
        percent_terminal = 0.0 if total == 0 else round((terminal / total) * 100.0, 3)

        return WorkflowProgressSnapshot(
            schema="LEAF_WORKFLOW_PROGRESS_TRACKER_PHASE_26E_V1",
            workflow_id=self.workflow.workflow_id,
            workflow_state=self.workflow.state().value,
            total_steps=total,
            complete_steps=complete,
            active_steps=active,
            ready_steps=ready,
            blocked_steps=blocked,
            failed_steps=failed,
            skipped_steps=skipped,
            remaining_steps=remaining,
            terminal_steps=terminal,
            percent_complete=percent_complete,
            percent_terminal=percent_terminal,
            current_ready_step=self.current_ready_step(),
            ready_step_ids=self.ready_step_ids(),
            blocked_step_ids=self.blocked_step_ids(),
            complete_step_ids=self.complete_step_ids(),
            remaining_step_ids=self.remaining_step_ids(),
            execution_order=self.graph.execution_order(),
        )

    def report(self) -> Dict[str, Any]:
        snapshot = self.snapshot()
        graph_report = self.graph.report().as_dict()

        return {
            "schema": "LEAF_WORKFLOW_PROGRESS_REPORT_PHASE_26E_V1",
            "snapshot": snapshot.as_dict(),
            "graph": graph_report,
            "validation_failures": list(self.graph.validate()),
        }


def build_workflow_progress_tracker(workflow: WorkflowModel) -> WorkflowProgressTracker:
    return WorkflowProgressTracker(workflow)
