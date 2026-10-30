"""
Programme 26F: Workflow Blocker / Readiness Gate.

Formal readiness gate for LEAF workflow steps.

Design rules:
- Reuse WorkflowExecutionContext, WorkflowDependencyGraph, and WorkflowProgressTracker.
- Do not execute solvers.
- Do not mutate runtime or storage.
- Do not duplicate graph traversal.
- Provide a single authoritative readiness verdict for later runtime bridge phases.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple

from .execution_context import WorkflowExecutionContext, WorkflowExecutionPermission
from .model import WorkflowStepStatus
from .progress_tracker import build_workflow_progress_tracker


class WorkflowReadinessVerdict(str, Enum):
    READY = "READY"
    BLOCKED = "BLOCKED"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    UNKNOWN_STEP = "UNKNOWN_STEP"
    INVALID_CONTEXT = "INVALID_CONTEXT"


@dataclass(frozen=True)
class WorkflowReadinessResult:
    schema: str
    workflow_id: str
    step_id: str
    verdict: WorkflowReadinessVerdict
    can_proceed: bool
    permission: str
    blockers: Tuple[str, ...]
    incomplete_dependencies: Tuple[str, ...]
    next_ready_steps: Tuple[str, ...]
    recommended_next_step: str | None
    progress_percent: float
    validation_failures: Tuple[str, ...]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "workflow_id": self.workflow_id,
            "step_id": self.step_id,
            "verdict": self.verdict.value,
            "can_proceed": self.can_proceed,
            "permission": self.permission,
            "blockers": list(self.blockers),
            "incomplete_dependencies": list(self.incomplete_dependencies),
            "next_ready_steps": list(self.next_ready_steps),
            "recommended_next_step": self.recommended_next_step,
            "progress_percent": self.progress_percent,
            "validation_failures": list(self.validation_failures),
        }


class WorkflowReadinessGate:
    """
    Single readiness gate for workflow execution decisions.

    Later runtime bridge code should call this gate before executing workflow
    actions. This prevents each module from inventing bespoke readiness checks.
    """

    def __init__(self, context: WorkflowExecutionContext) -> None:
        self.context = context
        self.graph = context.graph()
        self.tracker = build_workflow_progress_tracker(context.workflow)

    def evaluate(self) -> WorkflowReadinessResult:
        validation_failures = tuple(self.context.validate())
        permission = self.context.permission()
        blockers = tuple(self.context.blockers())
        incomplete_dependencies = self._incomplete_dependencies()
        snapshot = self.tracker.snapshot()

        if validation_failures:
            verdict = WorkflowReadinessVerdict.INVALID_CONTEXT
            can_proceed = False
        elif permission == WorkflowExecutionPermission.ALLOWED:
            verdict = WorkflowReadinessVerdict.READY
            can_proceed = True
        elif permission == WorkflowExecutionPermission.COMPLETE:
            verdict = WorkflowReadinessVerdict.COMPLETE
            can_proceed = False
        elif permission == WorkflowExecutionPermission.FAILED:
            verdict = WorkflowReadinessVerdict.FAILED
            can_proceed = False
        elif permission == WorkflowExecutionPermission.UNKNOWN_STEP:
            verdict = WorkflowReadinessVerdict.UNKNOWN_STEP
            can_proceed = False
        else:
            verdict = WorkflowReadinessVerdict.BLOCKED
            can_proceed = False

        return WorkflowReadinessResult(
            schema="LEAF_WORKFLOW_READINESS_GATE_PHASE_26F_V1",
            workflow_id=self.context.workflow.workflow_id,
            step_id=self.context.current_step_id,
            verdict=verdict,
            can_proceed=can_proceed,
            permission=permission.value,
            blockers=blockers,
            incomplete_dependencies=incomplete_dependencies,
            next_ready_steps=tuple(snapshot.ready_step_ids),
            recommended_next_step=snapshot.current_ready_step,
            progress_percent=snapshot.percent_complete,
            validation_failures=validation_failures,
        )

    def _incomplete_dependencies(self) -> Tuple[str, ...]:
        step = self.context.current_step()
        if step is None:
            return tuple()

        incomplete: List[str] = []
        step_map = self.context.workflow.step_map()

        for dependency in step.dependencies:
            required = step_map.get(dependency.required_step_id)
            if required is None:
                incomplete.append(dependency.required_step_id)
                continue

            if required.status != WorkflowStepStatus.COMPLETE:
                incomplete.append(dependency.required_step_id)

        return tuple(incomplete)

    def report(self) -> Dict[str, Any]:
        result = self.evaluate()

        return {
            "schema": "LEAF_WORKFLOW_READINESS_REPORT_PHASE_26F_V1",
            "result": result.as_dict(),
            "context": self.context.report(),
            "progress": self.tracker.snapshot().as_dict(),
            "graph": self.graph.report().as_dict(),
        }


def build_workflow_readiness_gate(context: WorkflowExecutionContext) -> WorkflowReadinessGate:
    return WorkflowReadinessGate(context)
