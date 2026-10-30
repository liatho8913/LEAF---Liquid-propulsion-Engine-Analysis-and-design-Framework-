"""
LEAF Phase 16N.8
Solver Regeneration Request Owner

Records that the UI has requested solver regeneration after accepted geometry
has been applied.

Does NOT directly run CEA or the full engine solver.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SolverRegenerationRequestResult:
    requested: bool
    status: str
    regeneration_geometry: dict[str, Any] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)


class RegenSolverRegenerationRequestOwnerPhase16N8:
    def request(self, results: dict[str, Any]) -> SolverRegenerationRequestResult:
        if not isinstance(results, dict):
            return SolverRegenerationRequestResult(
                requested=False,
                status="FAIL_SOLVER_REGENERATION_REQUEST_INVALID_RESULTS_PHASE_16N8",
                reasons=["Results payload is not a dictionary."],
            )

        geometry_applied = bool(results.get("phase_16n7_geometry_applied"))

        geometry = (
            results.get("regen_ui_applied_geometry")
            or results.get("phase_16n7_applied_geometry")
            or results.get("regen_current_geometry")
            or {}
        )

        reasons: list[str] = []

        if not geometry_applied:
            reasons.append("Accepted geometry has not been applied.")

        if not isinstance(geometry, dict) or not geometry:
            reasons.append("No applied geometry payload is available for regeneration.")

        if reasons:
            return SolverRegenerationRequestResult(
                requested=False,
                status="FAIL_SOLVER_REGENERATION_REQUEST_BLOCKED_PHASE_16N8",
                reasons=reasons,
            )

        return SolverRegenerationRequestResult(
            requested=True,
            status="PASS_SOLVER_REGENERATION_REQUEST_RECORDED_PHASE_16N8",
            regeneration_geometry=dict(geometry),
            reasons=[],
        )


def attach_solver_regeneration_request_phase_16n8(results: dict[str, Any]) -> dict[str, Any]:
    owner = RegenSolverRegenerationRequestOwnerPhase16N8()
    result = owner.request(results)

    if not isinstance(results, dict):
        results = {}

    results["phase_16n8_solver_regeneration_request_status"] = result.status
    results["phase_16n8_solver_regeneration_requested"] = result.requested
    results["phase_16n8_solver_regeneration_geometry"] = dict(result.regeneration_geometry)
    results["phase_16n8_solver_regeneration_reasons"] = list(result.reasons)

    # Safety distinction:
    # request recorded != solver has actually rerun.
    results["phase_16n8_solver_regenerated"] = False
    results["phase_16n8_cea_rerun"] = False

    return results
