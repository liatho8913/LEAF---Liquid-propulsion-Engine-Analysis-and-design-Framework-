"""
Programme 26G: Workflow Recommendation Engine.

Reusable recommendation layer for LEAF workflows.

Design rules:
- Reuse readiness gate and progress tracker.
- Do not execute solvers.
- Do not mutate runtime or storage.
- Do not duplicate dependency traversal.
- Provide explainable recommendations for future Qt/report/runtime layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Tuple

from .execution_context import WorkflowExecutionContext
from .progress_tracker import build_workflow_progress_tracker
from .readiness_gate import WorkflowReadinessVerdict, build_workflow_readiness_gate


class WorkflowRecommendationKind(str, Enum):
    PROCEED_CURRENT_STEP = "PROCEED_CURRENT_STEP"
    COMPLETE_DEPENDENCIES = "COMPLETE_DEPENDENCIES"
    MOVE_TO_NEXT_READY_STEP = "MOVE_TO_NEXT_READY_STEP"
    WORKFLOW_COMPLETE = "WORKFLOW_COMPLETE"
    FIX_CONTEXT = "FIX_CONTEXT"
    FIX_FAILED_STEP = "FIX_FAILED_STEP"
    UNKNOWN_STEP = "UNKNOWN_STEP"
    NO_ACTION_AVAILABLE = "NO_ACTION_AVAILABLE"


@dataclass(frozen=True)
class WorkflowRecommendation:
    schema: str
    workflow_id: str
    current_step_id: str
    kind: WorkflowRecommendationKind
    recommended_step_id: str | None
    title: str
    reason: str
    action: str
    can_proceed: bool
    blockers: Tuple[str, ...]
    incomplete_dependencies: Tuple[str, ...]
    progress_percent: float
    next_ready_steps: Tuple[str, ...]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "workflow_id": self.workflow_id,
            "current_step_id": self.current_step_id,
            "kind": self.kind.value,
            "recommended_step_id": self.recommended_step_id,
            "title": self.title,
            "reason": self.reason,
            "action": self.action,
            "can_proceed": self.can_proceed,
            "blockers": list(self.blockers),
            "incomplete_dependencies": list(self.incomplete_dependencies),
            "progress_percent": self.progress_percent,
            "next_ready_steps": list(self.next_ready_steps),
        }


class WorkflowRecommendationEngine:
    """
    Explainable workflow recommendation engine.

    This engine interprets existing workflow state. It does not own workflow
    truth. Truth remains in model, graph, progress tracker, and readiness gate.
    """

    def __init__(self, context: WorkflowExecutionContext) -> None:
        self.context = context
        self.readiness_gate = build_workflow_readiness_gate(context)
        self.progress_tracker = build_workflow_progress_tracker(context.workflow)

    def recommend(self) -> WorkflowRecommendation:
        readiness = self.readiness_gate.evaluate()
        snapshot = self.progress_tracker.snapshot()

        if readiness.verdict == WorkflowReadinessVerdict.READY:
            return WorkflowRecommendation(
                schema="LEAF_WORKFLOW_RECOMMENDATION_PHASE_26G_V1",
                workflow_id=readiness.workflow_id,
                current_step_id=readiness.step_id,
                kind=WorkflowRecommendationKind.PROCEED_CURRENT_STEP,
                recommended_step_id=readiness.step_id,
                title="Proceed with current workflow step",
                reason="The current step has no blockers and the readiness gate allows execution.",
                action=f"Execute or continue workflow step: {readiness.step_id}",
                can_proceed=True,
                blockers=readiness.blockers,
                incomplete_dependencies=readiness.incomplete_dependencies,
                progress_percent=readiness.progress_percent,
                next_ready_steps=readiness.next_ready_steps,
            )

        if readiness.verdict == WorkflowReadinessVerdict.BLOCKED:
            recommended = readiness.recommended_next_step
            if recommended:
                kind = WorkflowRecommendationKind.COMPLETE_DEPENDENCIES
                title = "Complete blocking dependency first"
                action = f"Complete ready prerequisite step: {recommended}"
                reason = (
                    "The selected step is blocked. LEAF recommends completing the "
                    "next ready dependency path before returning to the blocked step."
                )
            else:
                kind = WorkflowRecommendationKind.NO_ACTION_AVAILABLE
                title = "No executable workflow step available"
                action = "Review blockers and dependency graph."
                reason = "The selected step is blocked and no ready step is currently available."

            return WorkflowRecommendation(
                schema="LEAF_WORKFLOW_RECOMMENDATION_PHASE_26G_V1",
                workflow_id=readiness.workflow_id,
                current_step_id=readiness.step_id,
                kind=kind,
                recommended_step_id=recommended,
                title=title,
                reason=reason,
                action=action,
                can_proceed=False,
                blockers=readiness.blockers,
                incomplete_dependencies=readiness.incomplete_dependencies,
                progress_percent=readiness.progress_percent,
                next_ready_steps=readiness.next_ready_steps,
            )

        if readiness.verdict == WorkflowReadinessVerdict.COMPLETE:
            next_ready = readiness.recommended_next_step
            if next_ready:
                return WorkflowRecommendation(
                    schema="LEAF_WORKFLOW_RECOMMENDATION_PHASE_26G_V1",
                    workflow_id=readiness.workflow_id,
                    current_step_id=readiness.step_id,
                    kind=WorkflowRecommendationKind.MOVE_TO_NEXT_READY_STEP,
                    recommended_step_id=next_ready,
                    title="Move to next ready workflow step",
                    reason="The current step is already complete and another step is ready.",
                    action=f"Move workflow focus to: {next_ready}",
                    can_proceed=False,
                    blockers=readiness.blockers,
                    incomplete_dependencies=readiness.incomplete_dependencies,
                    progress_percent=readiness.progress_percent,
                    next_ready_steps=readiness.next_ready_steps,
                )

            return WorkflowRecommendation(
                schema="LEAF_WORKFLOW_RECOMMENDATION_PHASE_26G_V1",
                workflow_id=readiness.workflow_id,
                current_step_id=readiness.step_id,
                kind=WorkflowRecommendationKind.WORKFLOW_COMPLETE,
                recommended_step_id=None,
                title="Workflow complete",
                reason="The current step is complete and no further ready steps remain.",
                action="Review final reports or save/export the completed workflow.",
                can_proceed=False,
                blockers=readiness.blockers,
                incomplete_dependencies=readiness.incomplete_dependencies,
                progress_percent=snapshot.percent_complete,
                next_ready_steps=readiness.next_ready_steps,
            )

        if readiness.verdict == WorkflowReadinessVerdict.FAILED:
            return WorkflowRecommendation(
                schema="LEAF_WORKFLOW_RECOMMENDATION_PHASE_26G_V1",
                workflow_id=readiness.workflow_id,
                current_step_id=readiness.step_id,
                kind=WorkflowRecommendationKind.FIX_FAILED_STEP,
                recommended_step_id=readiness.step_id,
                title="Resolve failed workflow step",
                reason="The selected workflow step is marked as failed.",
                action=f"Inspect failure reports for step: {readiness.step_id}",
                can_proceed=False,
                blockers=readiness.blockers,
                incomplete_dependencies=readiness.incomplete_dependencies,
                progress_percent=readiness.progress_percent,
                next_ready_steps=readiness.next_ready_steps,
            )

        if readiness.verdict == WorkflowReadinessVerdict.UNKNOWN_STEP:
            return WorkflowRecommendation(
                schema="LEAF_WORKFLOW_RECOMMENDATION_PHASE_26G_V1",
                workflow_id=readiness.workflow_id,
                current_step_id=readiness.step_id,
                kind=WorkflowRecommendationKind.UNKNOWN_STEP,
                recommended_step_id=readiness.recommended_next_step,
                title="Select a known workflow step",
                reason="The requested current step does not exist in the workflow model.",
                action="Select one of the registered workflow steps before proceeding.",
                can_proceed=False,
                blockers=readiness.blockers,
                incomplete_dependencies=readiness.incomplete_dependencies,
                progress_percent=readiness.progress_percent,
                next_ready_steps=readiness.next_ready_steps,
            )

        return WorkflowRecommendation(
            schema="LEAF_WORKFLOW_RECOMMENDATION_PHASE_26G_V1",
            workflow_id=readiness.workflow_id,
            current_step_id=readiness.step_id,
            kind=WorkflowRecommendationKind.FIX_CONTEXT,
            recommended_step_id=readiness.recommended_next_step,
            title="Fix workflow execution context",
            reason="The workflow execution context failed validation.",
            action="Repair the active module, current step, workflow model, or validation mode.",
            can_proceed=False,
            blockers=readiness.blockers,
            incomplete_dependencies=readiness.incomplete_dependencies,
            progress_percent=readiness.progress_percent,
            next_ready_steps=readiness.next_ready_steps,
        )

    def report(self) -> Dict[str, Any]:
        recommendation = self.recommend()
        return {
            "schema": "LEAF_WORKFLOW_RECOMMENDATION_REPORT_PHASE_26G_V1",
            "recommendation": recommendation.as_dict(),
            "readiness": self.readiness_gate.evaluate().as_dict(),
            "progress": self.progress_tracker.snapshot().as_dict(),
        }


def build_workflow_recommendation_engine(
    context: WorkflowExecutionContext,
) -> WorkflowRecommendationEngine:
    return WorkflowRecommendationEngine(context)
