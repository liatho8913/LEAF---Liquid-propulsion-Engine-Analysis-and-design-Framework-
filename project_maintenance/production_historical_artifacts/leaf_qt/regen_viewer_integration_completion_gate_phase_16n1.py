"""
LEAF Phase 16N.1
Regen Viewer Integration Completion Gate
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from regen_viewer_integration_report_owner import RegenViewerIntegrationReportOwner


REQUIRED_VIEWERS = [
    "Candidate Ranking Window",
    "Cross Section Viewer",
    "Station Viewer",
    "Recommendation Viewer",
]


@dataclass
class RegenViewerIntegrationCompletionResult:
    phase: str
    status: str
    required_viewers: list[str]
    checked_viewers: list[str]
    missing_viewers: list[str]
    notes: list[str]


class RegenViewerIntegrationCompletionGatePhase16N1:
    def __init__(self) -> None:
        self.phase = "16N.1"

    def evaluate(
        self,
        payloads_by_viewer: dict[str, Any],
    ) -> RegenViewerIntegrationCompletionResult:
        owner = RegenViewerIntegrationReportOwner()

        for viewer_name, payload in payloads_by_viewer.items():
            owner.check_viewer_payload(
                viewer_name=viewer_name,
                payload_name=f"{viewer_name.lower().replace(' ', '_')}_payload",
                payload=payload,
            )

        checked = sorted(payloads_by_viewer.keys())
        missing = [
            viewer for viewer in REQUIRED_VIEWERS
            if viewer not in payloads_by_viewer
        ]

        notes: list[str] = []

        if missing:
            notes.append("One or more required regen viewer payload paths were not checked.")

        owner_status = owner.overall_status()

        if missing:
            status = "FAIL_REGEN_VIEWER_INTEGRATION_MISSING_VIEWERS_PHASE_16N1"
        elif owner_status != "PASS_REGEN_VIEWER_INTEGRATION_PHASE_16N1":
            status = "FAIL_REGEN_VIEWER_INTEGRATION_PAYLOADS_PHASE_16N1"
        else:
            status = "PASS_REGEN_VIEWER_INTEGRATION_COMPLETION_GATE_PHASE_16N1"

        return RegenViewerIntegrationCompletionResult(
            phase=self.phase,
            status=status,
            required_viewers=list(REQUIRED_VIEWERS),
            checked_viewers=checked,
            missing_viewers=missing,
            notes=notes,
        )
