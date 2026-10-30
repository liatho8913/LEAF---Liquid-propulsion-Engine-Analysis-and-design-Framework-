"""
LEAF Phase 16N.7
Apply Geometry Owner

Applies previously accepted staged geometry into a UI-level applied geometry payload.

Does NOT:
- regenerate solver
- run CEA
- permanently save design
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ApplyGeometryResult:
    applied: bool
    status: str
    applied_geometry: dict[str, Any] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)


class RegenApplyGeometryOwnerPhase16N7:
    def apply(self, results: dict[str, Any]) -> ApplyGeometryResult:
        if not isinstance(results, dict):
            return ApplyGeometryResult(
                applied=False,
                status="FAIL_APPLY_GEOMETRY_INVALID_RESULTS_PHASE_16N7",
                reasons=["Results payload is not a dictionary."],
            )

        accepted = bool(results.get("phase_16n6_recommendation_accepted"))

        staged = (
            results.get("phase_16n6_accepted_staged_geometry")
            or results.get("regen_geometry_commit_staged_geometry")
            or {}
        )

        reasons: list[str] = []

        if not accepted:
            reasons.append("Recommendation has not been accepted by the user.")

        if not isinstance(staged, dict) or not staged:
            reasons.append("No accepted staged geometry is available to apply.")

        if reasons:
            return ApplyGeometryResult(
                applied=False,
                status="FAIL_APPLY_GEOMETRY_BLOCKED_PHASE_16N7",
                reasons=reasons,
            )

        return ApplyGeometryResult(
            applied=True,
            status="PASS_APPLY_GEOMETRY_RECORDED_PHASE_16N7",
            applied_geometry=dict(staged),
            reasons=[],
        )


def attach_apply_geometry_result_phase_16n7(results: dict[str, Any]) -> dict[str, Any]:
    owner = RegenApplyGeometryOwnerPhase16N7()
    result = owner.apply(results)

    if not isinstance(results, dict):
        results = {}

    results["phase_16n7_apply_geometry_status"] = result.status
    results["phase_16n7_geometry_applied"] = result.applied
    results["phase_16n7_applied_geometry"] = dict(result.applied_geometry)
    results["phase_16n7_apply_geometry_reasons"] = list(result.reasons)

    # Compatibility payload for viewer and later solver-regeneration phase.
    if result.applied:
        results["regen_ui_applied_geometry"] = dict(result.applied_geometry)
        results["regen_current_geometry"] = dict(result.applied_geometry)

    # Safety locks.
    results["phase_16n7_solver_regenerated"] = False
    results["phase_16n7_cea_rerun"] = False

    return results
