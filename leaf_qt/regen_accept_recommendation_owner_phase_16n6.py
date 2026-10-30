"""
LEAF Phase 16N.6
Accept Recommendation Owner

Records user acceptance of staged automatic geometry.

Does NOT:
- apply geometry
- mutate live inputs
- regenerate solver
- commit permanently
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AcceptRecommendationResult:
    accepted: bool
    status: str
    staged_geometry: dict[str, Any] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)


class RegenAcceptRecommendationOwnerPhase16N6:
    def accept(self, results: dict[str, Any]) -> AcceptRecommendationResult:
        if not isinstance(results, dict):
            return AcceptRecommendationResult(
                accepted=False,
                status="FAIL_ACCEPT_RECOMMENDATION_INVALID_RESULTS_PHASE_16N6",
                reasons=["Results payload is not a dictionary."],
            )

        staged = results.get("regen_geometry_commit_staged_geometry") or {}
        ready = bool(
            results.get("regen_geometry_commit_candidate_ready")
            or results.get("regen_geometry_commit_requires_user_acceptance")
        )

        reasons: list[str] = []

        if not isinstance(staged, dict) or not staged:
            reasons.append("No staged geometry is available to accept.")

        if not ready:
            reasons.append("Recommendation is not marked ready for user acceptance.")

        if reasons:
            return AcceptRecommendationResult(
                accepted=False,
                status="FAIL_ACCEPT_RECOMMENDATION_BLOCKED_PHASE_16N6",
                reasons=reasons,
            )

        return AcceptRecommendationResult(
            accepted=True,
            status="PASS_ACCEPT_RECOMMENDATION_RECORDED_PHASE_16N6",
            staged_geometry=dict(staged),
            reasons=[],
        )


def attach_accept_recommendation_result_phase_16n6(results: dict[str, Any]) -> dict[str, Any]:
    owner = RegenAcceptRecommendationOwnerPhase16N6()
    result = owner.accept(results)

    if not isinstance(results, dict):
        results = {}

    results["phase_16n6_accept_recommendation_status"] = result.status
    results["phase_16n6_recommendation_accepted"] = result.accepted
    results["phase_16n6_accepted_staged_geometry"] = dict(result.staged_geometry)
    results["phase_16n6_accept_recommendation_reasons"] = list(result.reasons)

    # Safety locks.
    results["phase_16n6_geometry_applied"] = False
    results["phase_16n6_solver_regenerated"] = False
    results["phase_16n6_live_geometry_modified"] = False

    return results
