"""
LEAF Phase 16N.5
Station Viewer Live Feed Validator

Checks whether station/table viewer payloads are available for display.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StationLiveFeedValidationResult:
    status: str
    station_payload_present: bool
    station_count: int
    automatic_geometry_present: bool
    recommendation_present: bool
    notes: list[str] = field(default_factory=list)


class RegenStationLiveFeedValidatorPhase16N5:
    def validate(self, results: dict[str, Any]) -> StationLiveFeedValidationResult:
        if not isinstance(results, dict):
            return StationLiveFeedValidationResult(
                status="FAIL_STATION_LIVE_FEED_INVALID_RESULTS_PHASE_16N5",
                station_payload_present=False,
                station_count=0,
                automatic_geometry_present=False,
                recommendation_present=False,
                notes=["Results payload is not a dictionary."],
            )

        station_payload = (
            results.get("station_rows")
            or results.get("stations")
            or results.get("regen_station_rows")
            or results.get("regen_station_payload")
            or results.get("regen_axial_station_rows")
            or []
        )

        station_present = isinstance(station_payload, list) and len(station_payload) > 0
        station_count = len(station_payload) if isinstance(station_payload, list) else 0

        automatic_geometry = results.get("regen_geometry_commit_staged_geometry") or {}
        automatic_present = isinstance(automatic_geometry, dict) and bool(automatic_geometry)

        recommendation_present = bool(
            results.get("regen_geometry_commit_decision")
            or results.get("regen_autonomous_geometry_commit_report")
        )

        notes: list[str] = []

        if not station_present:
            notes.append("Station payload is missing or empty.")

        if not automatic_present:
            notes.append("Automatic/staged geometry payload is missing.")

        if not recommendation_present:
            notes.append("Recommendation/decision payload is missing.")

        if station_present and automatic_present and recommendation_present:
            status = "PASS_STATION_LIVE_FEED_VALIDATION_PHASE_16N5"
        else:
            status = "FAIL_STATION_LIVE_FEED_VALIDATION_PHASE_16N5"

        return StationLiveFeedValidationResult(
            status=status,
            station_payload_present=station_present,
            station_count=station_count,
            automatic_geometry_present=automatic_present,
            recommendation_present=recommendation_present,
            notes=notes,
        )
