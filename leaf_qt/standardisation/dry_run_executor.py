"""
Programme 27H: Standardisation Dry-Run Executor.

Simulates standardisation repair execution without modifying the repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .repair_plan_owner import StandardisationRepairPlan, StandardisationRepairPlanItem
from .safety_gate import (
    StandardisationSafetyRequest,
    StandardisationSafetyVerdict,
    build_standardisation_safety_gate,
)


@dataclass(frozen=True)
class StandardisationDryRunAction:
    action_id: str
    plan_item_id: str
    action_type: str
    priority: str
    path: str
    would_modify: bool
    would_delete: bool
    would_archive: bool
    description: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "plan_item_id": self.plan_item_id,
            "action_type": self.action_type,
            "priority": self.priority,
            "path": self.path,
            "would_modify": self.would_modify,
            "would_delete": self.would_delete,
            "would_archive": self.would_archive,
            "description": self.description,
        }


@dataclass(frozen=True)
class StandardisationDryRunResult:
    schema: str
    plan_id: str
    safety_verdict: str
    allowed: bool
    dry_run_only: bool
    action_count: int
    actions: Tuple[StandardisationDryRunAction, ...]
    mutation_performed: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "plan_id": self.plan_id,
            "safety_verdict": self.safety_verdict,
            "allowed": self.allowed,
            "dry_run_only": self.dry_run_only,
            "action_count": self.action_count,
            "mutation_performed": self.mutation_performed,
            "actions": [action.as_dict() for action in self.actions[:250]],
            "actions_truncated": len(self.actions) > 250,
        }


class StandardisationDryRunExecutor:
    """
    Executes repair plans in simulation only.

    This class must never write, delete, archive, move, or patch repository
    files. It only produces structured "would-do" actions.
    """

    def __init__(self, repair_plan: StandardisationRepairPlan) -> None:
        self.repair_plan = repair_plan
        self.safety_gate = build_standardisation_safety_gate(repair_plan)

    def execute(
        self,
        request: StandardisationSafetyRequest,
        limit: int | None = None,
    ) -> StandardisationDryRunResult:
        safety = self.safety_gate.evaluate(request)

        if safety.verdict != StandardisationSafetyVerdict.SAFE_FOR_DRY_RUN_ONLY:
            return StandardisationDryRunResult(
                schema="LEAF_STANDARDISATION_DRY_RUN_EXECUTOR_PHASE_27H_V1",
                plan_id=self.repair_plan.plan_id,
                safety_verdict=safety.verdict.value,
                allowed=False,
                dry_run_only=True,
                action_count=0,
                actions=tuple(),
                mutation_performed=False,
            )

        items = self.repair_plan.planned_items
        if limit is not None:
            items = items[:limit]

        actions = tuple(
            self._build_action(index, item)
            for index, item in enumerate(items, start=1)
        )

        return StandardisationDryRunResult(
            schema="LEAF_STANDARDISATION_DRY_RUN_EXECUTOR_PHASE_27H_V1",
            plan_id=self.repair_plan.plan_id,
            safety_verdict=safety.verdict.value,
            allowed=True,
            dry_run_only=True,
            action_count=len(actions),
            actions=actions,
            mutation_performed=False,
        )

    def _build_action(
        self,
        index: int,
        item: StandardisationRepairPlanItem,
    ) -> StandardisationDryRunAction:
        return StandardisationDryRunAction(
            action_id=f"dry_run_action_{index:05d}",
            plan_item_id=item.plan_item_id,
            action_type=item.action_type.value,
            priority=item.priority.value,
            path=item.path,
            would_modify=False,
            would_delete=False,
            would_archive=False,
            description=(
                "Dry-run only. Would review this repair plan item and produce a "
                f"future manual patch proposal: {item.proposed_action}"
            ),
        )

    def report(
        self,
        request: StandardisationSafetyRequest,
        limit: int | None = None,
    ) -> Dict[str, Any]:
        result = self.execute(request=request, limit=limit)
        return {
            "schema": "LEAF_STANDARDISATION_DRY_RUN_EXECUTOR_REPORT_PHASE_27H_V1",
            "result": result.as_dict(),
            "safety": self.safety_gate.report(request),
            "policy": {
                "mutation_allowed": False,
                "deletion_allowed": False,
                "archive_allowed": False,
                "manual_patch_required_for_future_changes": True,
            },
        }


def build_standardisation_dry_run_executor(
    repair_plan: StandardisationRepairPlan,
) -> StandardisationDryRunExecutor:
    return StandardisationDryRunExecutor(repair_plan)
