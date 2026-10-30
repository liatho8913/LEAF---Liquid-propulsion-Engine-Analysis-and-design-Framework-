"""
LEAF Phase 16N.3
Recommendation Payload UI Owner

Builds a clean UI-facing recommendation payload from candidate ranking,
automatic geometry decision, and staged geometry commit results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RegenRecommendationUIPayload:
    available: bool
    status: str
    candidate_id: str | None = None
    rank: int | None = None
    score: float | None = None
    decision: str | None = None
    reason: str | None = None
    blockers: list[str] = field(default_factory=list)
    staged_geometry: dict[str, Any] = field(default_factory=dict)
    ready_for_user_acceptance: bool = False


class RegenRecommendationPayloadUIOwnerPhase16N3:
    def build(self, results: dict[str, Any]) -> RegenRecommendationUIPayload:
        if not isinstance(results, dict):
            return RegenRecommendationUIPayload(
                available=False,
                status="FAIL_RECOMMENDATION_UI_PAYLOAD_INVALID_RESULTS_PHASE_16N3",
                blockers=["Results payload is not a dictionary."],
            )

        candidate = self._extract_candidate(results)
        staged_geometry = results.get("regen_geometry_commit_staged_geometry") or {}
        if not isinstance(staged_geometry, dict):
            staged_geometry = {}

        decision = results.get(
            "regen_geometry_commit_decision"
        )

        reason = (
            results.get("regen_autonomous_geometry_commit_reason")
            or results.get("regen_geometry_commit_reason")
        )

        blockers = []
        for key in [
            "regen_autonomous_geometry_commit_blockers",
        ]:
            value = results.get(key)
            if isinstance(value, list):
                blockers.extend(str(v) for v in value)

        ready = bool(
            results.get("regen_geometry_commit_candidate_ready")
            or results.get("regen_geometry_commit_requires_user_acceptance")
        )

        available = bool(candidate or staged_geometry or decision or reason)

        if not available:
            return RegenRecommendationUIPayload(
                available=False,
                status="FAIL_RECOMMENDATION_UI_PAYLOAD_MISSING_PHASE_16N3",
                blockers=["No recommendation, candidate, decision, or staged geometry payload found."],
            )

        if not staged_geometry:
            blockers.append("No staged geometry is available for UI acceptance.")

        if not ready:
            blockers.append("Recommendation is not marked ready for user acceptance.")

        status = (
            "PASS_RECOMMENDATION_UI_PAYLOAD_READY_PHASE_16N3"
            if staged_geometry and ready
            else "WARN_RECOMMENDATION_UI_PAYLOAD_DISPLAY_ONLY_PHASE_16N3"
        )

        return RegenRecommendationUIPayload(
            available=True,
            status=status,
            candidate_id=self._candidate_id(candidate),
            rank=self._candidate_rank(candidate),
            score=self._candidate_score(candidate),
            decision=str(decision) if decision is not None else None,
            reason=str(reason) if reason is not None else None,
            blockers=blockers,
            staged_geometry=dict(staged_geometry),
            ready_for_user_acceptance=ready,
        )

    def as_text(self, payload: RegenRecommendationUIPayload) -> str:
        lines = [
            "REGEN RECOMMENDATION UI PAYLOAD",
            "===============================",
            "",
            f"Status: {payload.status}",
            f"Available: {payload.available}",
            f"Ready For User Acceptance: {payload.ready_for_user_acceptance}",
            "",
            f"Candidate ID: {payload.candidate_id}",
            f"Rank: {payload.rank}",
            f"Score: {payload.score}",
            f"Decision: {payload.decision}",
            "",
            "Reason:",
            f"- {payload.reason or 'No reason supplied.'}",
            "",
            "Blockers:",
        ]

        if payload.blockers:
            for blocker in payload.blockers:
                lines.append(f"- {blocker}")
        else:
            lines.append("- None.")

        lines.extend(["", "Staged Geometry:"])

        if payload.staged_geometry:
            for key, value in sorted(payload.staged_geometry.items()):
                lines.append(f"- {key}: {value}")
        else:
            lines.append("- None.")

        return "\n".join(lines)

    def _extract_candidate(self, results: dict[str, Any]) -> dict[str, Any]:
        for key in [
            "regen_candidate_ranking_winner",
            "regen_candidate_ranking_best_candidate",
            "regen_best_ranked_candidate",
            "regen_selected_ranked_candidate",
            "regen_selected_candidate",
        ]:
            value = results.get(key)
            if isinstance(value, dict) and value:
                return value
        return {}

    def _candidate_id(self, candidate: dict[str, Any]) -> str | None:
        value = candidate.get("candidate_id") or candidate.get("id")
        return str(value) if value is not None else None

    def _candidate_rank(self, candidate: dict[str, Any]) -> int | None:
        value = candidate.get("rank")
        try:
            return int(value)
        except Exception:
            return None

    def _candidate_score(self, candidate: dict[str, Any]) -> float | None:
        value = candidate.get("score")
        try:
            return float(value)
        except Exception:
            return None
