from __future__ import annotations
from leaf_qt.status_presentation import status_severity
"""
LEAF Phase 16N.1
Regen Viewer Integration Report Owner

Owns formal UI/viewer payload integration reporting.

This does not:
- solve candidates
- mutate candidates
- accept/reject candidates
- commit geometry
- regenerate solver state

It only records whether viewer payloads exist and are suitable for display.
"""


from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from regen_viewer_payload_trace import RegenViewerPayloadTracer


@dataclass
class ViewerIntegrationCheck:
    viewer_name: str
    payload_name: str
    payload_present: bool
    payload_displayable: bool
    status: str
    notes: list[str] = field(default_factory=list)


class RegenViewerIntegrationReportOwner:
    def __init__(self) -> None:
        self.phase = "16N.1"
        self.checks: list[ViewerIntegrationCheck] = []

    def check_viewer_payload(
        self,
        viewer_name: str,
        payload_name: str,
        payload: Any,
    ) -> ViewerIntegrationCheck:
        tracer = RegenViewerPayloadTracer()
        trace = tracer.inspect_payload(payload_name, payload)

        displayable = False
        notes: list[str] = list(trace.notes)

        if trace.status in {"PRESENT_DICT", "PRESENT_LIST", "PRESENT_OBJECT"}:
            displayable = True

        if trace.status == "PRESENT_DICT" and trace.item_count == 0:
            displayable = False
            notes.append("Dictionary payload exists but is empty.")

        if trace.status == "PRESENT_LIST" and trace.item_count == 0:
            displayable = False
            notes.append("List payload exists but is empty.")

        if trace.status == "MISSING":
            status = "FAIL_PAYLOAD_MISSING"
        elif displayable:
            status = "PASS_PAYLOAD_DISPLAYABLE"
        else:
            status = "FAIL_PAYLOAD_NOT_DISPLAYABLE"

        check = ViewerIntegrationCheck(
            viewer_name=viewer_name,
            payload_name=payload_name,
            payload_present=trace.exists,
            payload_displayable=displayable,
            status=status,
            notes=notes,
        )

        self.checks.append(check)
        return check

    def overall_status(self) -> str:
        if not self.checks:
            return "FAIL_NO_VIEWER_CHECKS_RECORDED"

        failures = [
            check for check in self.checks
            if status_severity(check.status) != "PASS"
        ]

        if failures:
            return "FAIL_REGEN_VIEWER_INTEGRATION"

        return "PASS_REGEN_VIEWER_INTEGRATION_PHASE_16N1"

    def as_text_report(self) -> str:
        lines: list[str] = []
        lines.append("=" * 80)
        lines.append("LEAF PHASE 16N.1 — REGEN VIEWER INTEGRATION REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
        lines.append(f"Overall Status: {self.overall_status()}")
        lines.append("")

        for check in self.checks:
            lines.append(f"VIEWER: {check.viewer_name}")
            lines.append("-" * (8 + len(check.viewer_name)))
            lines.append(f"payload_name: {check.payload_name}")
            lines.append(f"payload_present: {check.payload_present}")
            lines.append(f"payload_displayable: {check.payload_displayable}")
            lines.append(f"status: {check.status}")
            lines.append("notes:")
            for note in check.notes:
                lines.append(f"  - {note}")
            lines.append("")

        return "\n".join(lines)

    def as_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "generated": datetime.now().isoformat(timespec="seconds"),
            "overall_status": self.overall_status(),
            "checks": [
                {
                    "viewer_name": c.viewer_name,
                    "payload_name": c.payload_name,
                    "payload_present": c.payload_present,
                    "payload_displayable": c.payload_displayable,
                    "status": c.status,
                    "notes": c.notes,
                }
                for c in self.checks
            ],
        }
