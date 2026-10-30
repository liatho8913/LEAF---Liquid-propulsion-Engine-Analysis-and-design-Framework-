"""
LEAF Phase 16N.4
Cross Section Viewer Live Feed Validator

Checks whether the cross-section viewer can receive and expose
manual/current geometry and automatic/staged geometry payloads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CrossSectionLiveFeedValidationResult:
    status: str
    manual_geometry_present: bool
    automatic_geometry_present: bool
    recommendation_present: bool
    button_state_present: bool
    notes: list[str] = field(default_factory=list)


class RegenCrossSectionLiveFeedValidatorPhase16N4:
    def validate(self, results: dict[str, Any]) -> CrossSectionLiveFeedValidationResult:
        if not isinstance(results, dict):
            return CrossSectionLiveFeedValidationResult(
                status="FAIL_CROSS_SECTION_LIVE_FEED_INVALID_RESULTS_PHASE_16N4",
                manual_geometry_present=False,
                automatic_geometry_present=False,
                recommendation_present=False,
                button_state_present=False,
                notes=["Results payload is not a dictionary."],
            )

        manual_geometry = (
            results.get("regen_manual_geometry")
            or results.get("regen_current_geometry")
            or results.get("regen_geometry_current")
            or results.get("regen_geometry_baseline")
            or {}
        )

        automatic_geometry = (
            results.get("regen_geometry_commit_staged_geometry")
            or results.get("regen_autonomous_geometry_staged_candidate", {}).get("staged_geometry", {})
            if isinstance(results.get("regen_autonomous_geometry_staged_candidate", {}), dict)
            else {}
        )

        recommendation_present = bool(
            results.get("regen_autonomous_geometry_commit_report")
            or results.get("regen_geometry_commit_decision")
        )

        button_state_present = bool(
            results.get("phase_16n2_automatic_geometry_button_state")
        )

        manual_present = isinstance(manual_geometry, dict) and bool(manual_geometry)
        auto_present = isinstance(automatic_geometry, dict) and bool(automatic_geometry)

        notes: list[str] = []

        if not manual_present:
            notes.append("Manual/current geometry payload is missing.")

        if not auto_present:
            notes.append("Automatic/staged geometry payload is missing.")

        if not recommendation_present:
            notes.append("Recommendation/decision payload is missing.")

        if not button_state_present:
            notes.append("Automatic geometry button state has not been recorded.")

        if manual_present and auto_present and recommendation_present:
            status = "PASS_CROSS_SECTION_LIVE_FEED_VALIDATION_PHASE_16N4"
        else:
            status = "FAIL_CROSS_SECTION_LIVE_FEED_VALIDATION_PHASE_16N4"

        return CrossSectionLiveFeedValidationResult(
            status=status,
            manual_geometry_present=manual_present,
            automatic_geometry_present=auto_present,
            recommendation_present=recommendation_present,
            button_state_present=button_state_present,
            notes=notes,
        )
