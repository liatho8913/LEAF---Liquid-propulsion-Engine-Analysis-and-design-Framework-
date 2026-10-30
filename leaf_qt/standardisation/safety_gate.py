"""
Programme 27G: Standardisation Safety Gate.

Safety gate for any future standardisation repair execution.

Design rules:
- No automatic repair authority.
- No mutation by default.
- Manual approval required.
- Dry-run required.
- Backup/checkpoint required before any future repair phase.
- Deletion/archive actions blocked unless explicitly approved in a later phase.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Tuple

from .repair_plan_owner import StandardisationRepairPlan


class StandardisationSafetyVerdict(str, Enum):
    SAFE_FOR_DRY_RUN_ONLY = "SAFE_FOR_DRY_RUN_ONLY"
    BLOCKED_NO_MANUAL_APPROVAL = "BLOCKED_NO_MANUAL_APPROVAL"
    BLOCKED_AUTOMATIC_REPAIR_ENABLED = "BLOCKED_AUTOMATIC_REPAIR_ENABLED"
    BLOCKED_MUTATION_REQUESTED = "BLOCKED_MUTATION_REQUESTED"
    BLOCKED_INVALID_PLAN = "BLOCKED_INVALID_PLAN"


@dataclass(frozen=True)
class StandardisationSafetyRequest:
    manual_approval: bool = False
    dry_run: bool = True
    mutation_requested: bool = False
    deletion_requested: bool = False
    archive_requested: bool = False
    checkpoint_reference: str | None = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "manual_approval": self.manual_approval,
            "dry_run": self.dry_run,
            "mutation_requested": self.mutation_requested,
            "deletion_requested": self.deletion_requested,
            "archive_requested": self.archive_requested,
            "checkpoint_reference": self.checkpoint_reference,
        }


@dataclass(frozen=True)
class StandardisationSafetyResult:
    schema: str
    verdict: StandardisationSafetyVerdict
    allowed: bool
    dry_run_only: bool
    reasons: Tuple[str, ...]
    request: StandardisationSafetyRequest
    mutation_performed: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "verdict": self.verdict.value,
            "allowed": self.allowed,
            "dry_run_only": self.dry_run_only,
            "reasons": list(self.reasons),
            "request": self.request.as_dict(),
            "mutation_performed": self.mutation_performed,
        }


class StandardisationSafetyGate:
    """
    Safety gate for future standardisation repair execution.

    Passing this gate does not allow mutation. It only allows future dry-run
    repair planning unless later phases add explicit, user-approved execution.
    """

    def __init__(self, repair_plan: StandardisationRepairPlan) -> None:
        self.repair_plan = repair_plan

    def evaluate(self, request: StandardisationSafetyRequest) -> StandardisationSafetyResult:
        reasons = []

        if self.repair_plan.automatic_repair_enabled:
            return self._blocked(
                StandardisationSafetyVerdict.BLOCKED_AUTOMATIC_REPAIR_ENABLED,
                request,
                ("Repair plan has automatic repair enabled, which is not allowed.",),
            )

        if self.repair_plan.mutation_performed:
            return self._blocked(
                StandardisationSafetyVerdict.BLOCKED_MUTATION_REQUESTED,
                request,
                ("Repair plan indicates mutation already occurred.",),
            )

        if self.repair_plan.source_total_findings > 0 and not self.repair_plan.planned_items:
            return self._blocked(
                StandardisationSafetyVerdict.BLOCKED_INVALID_PLAN,
                request,
                ("Repair plan has findings but no planned items.",),
            )

        if not request.manual_approval:
            reasons.append("Manual approval has not been provided.")

        if not request.dry_run:
            reasons.append("Dry-run mode is required at this stage.")

        if request.mutation_requested:
            reasons.append("Mutation was requested, but Programme 27G allows dry-run only.")

        if request.deletion_requested:
            reasons.append("Deletion was requested, but deletion is permanently blocked here.")

        if request.archive_requested:
            reasons.append("Archive was requested, but archive is blocked without later explicit approval.")

        if not request.checkpoint_reference:
            reasons.append("Checkpoint/reference is required before future repair execution.")

        if reasons:
            if not request.manual_approval:
                verdict = StandardisationSafetyVerdict.BLOCKED_NO_MANUAL_APPROVAL
            else:
                verdict = StandardisationSafetyVerdict.BLOCKED_MUTATION_REQUESTED
            return self._blocked(verdict, request, tuple(reasons))

        return StandardisationSafetyResult(
            schema="LEAF_STANDARDISATION_SAFETY_GATE_PHASE_27G_V1",
            verdict=StandardisationSafetyVerdict.SAFE_FOR_DRY_RUN_ONLY,
            allowed=True,
            dry_run_only=True,
            reasons=("Safety conditions satisfied for dry-run planning only.",),
            request=request,
            mutation_performed=False,
        )

    def _blocked(
        self,
        verdict: StandardisationSafetyVerdict,
        request: StandardisationSafetyRequest,
        reasons: Tuple[str, ...],
    ) -> StandardisationSafetyResult:
        return StandardisationSafetyResult(
            schema="LEAF_STANDARDISATION_SAFETY_GATE_PHASE_27G_V1",
            verdict=verdict,
            allowed=False,
            dry_run_only=True,
            reasons=reasons,
            request=request,
            mutation_performed=False,
        )

    def report(self, request: StandardisationSafetyRequest) -> Dict[str, Any]:
        result = self.evaluate(request)
        return {
            "schema": "LEAF_STANDARDISATION_SAFETY_GATE_REPORT_PHASE_27G_V1",
            "result": result.as_dict(),
            "repair_plan": self.repair_plan.as_dict(),
            "safety_policy": {
                "automatic_repair_allowed": False,
                "mutation_allowed": False,
                "deletion_allowed": False,
                "archive_allowed": False,
                "manual_approval_required": True,
                "dry_run_required": True,
                "checkpoint_required": True,
            },
        }


def build_standardisation_safety_gate(
    repair_plan: StandardisationRepairPlan,
) -> StandardisationSafetyGate:
    return StandardisationSafetyGate(repair_plan)
