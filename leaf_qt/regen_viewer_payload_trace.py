"""
LEAF Phase 16N.1
Runtime Regen Viewer Payload Trace

Non-invasive diagnostic utility.

This module does not solve, mutate, accept, reject, or commit geometry.
It only records whether viewer payloads exist and whether they contain usable data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import json
from pathlib import Path

from core.architecture.io import write_json_artifact, write_text_artifact
from datetime import datetime


@dataclass
class ViewerPayloadTraceResult:
    name: str
    exists: bool
    payload_type: str
    keys: list[str] = field(default_factory=list)
    item_count: int | None = None
    status: str = "UNKNOWN"
    notes: list[str] = field(default_factory=list)


class RegenViewerPayloadTracer:
    def __init__(self) -> None:
        self.results: list[ViewerPayloadTraceResult] = []

    def inspect_payload(self, name: str, payload: Any) -> ViewerPayloadTraceResult:
        result = ViewerPayloadTraceResult(
            name=name,
            exists=payload is not None,
            payload_type=type(payload).__name__,
        )

        if payload is None:
            result.status = "MISSING"
            result.notes.append("Payload is None.")
            self.results.append(result)
            return result

        if isinstance(payload, dict):
            result.keys = sorted(str(k) for k in payload.keys())
            result.item_count = len(payload)
            result.status = "PRESENT_DICT"
            if not payload:
                result.notes.append("Payload dictionary is empty.")
            else:
                result.notes.append("Payload dictionary contains data.")

        elif isinstance(payload, list):
            result.item_count = len(payload)
            result.status = "PRESENT_LIST"
            if not payload:
                result.notes.append("Payload list is empty.")
            else:
                result.notes.append("Payload list contains data.")

        else:
            result.status = "PRESENT_OBJECT"
            result.notes.append("Payload exists as object instance.")
            public_attrs = [
                attr for attr in dir(payload)
                if not attr.startswith("_")
            ]
            result.keys = public_attrs[:50]

        self.results.append(result)
        return result

    def as_text_report(self) -> str:
        lines: list[str] = []
        lines.append("=" * 80)
        lines.append("LEAF PHASE 16N.1 — REGEN VIEWER PAYLOAD TRACE REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
        lines.append("")

        for result in self.results:
            lines.append(f"PAYLOAD: {result.name}")
            lines.append("-" * (9 + len(result.name)))
            lines.append(f"exists: {result.exists}")
            lines.append(f"type: {result.payload_type}")
            lines.append(f"status: {result.status}")
            lines.append(f"item_count: {result.item_count}")
            lines.append(f"keys: {result.keys}")
            lines.append("notes:")
            for note in result.notes:
                lines.append(f"  - {note}")
            lines.append("")

        if not self.results:
            lines.append("No payloads were inspected.")

        return "\n".join(lines)

    def write_report(self, path: str | Path) -> Path:
        output_path = Path(path)
        write_text_artifact(self.as_text_report(), output_path)
        return output_path

    def as_json_dict(self) -> dict[str, Any]:
        return {
            "phase": "16N.1",
            "purpose": "regen_viewer_payload_trace",
            "generated": datetime.now().isoformat(timespec="seconds"),
            "results": [
                {
                    "name": r.name,
                    "exists": r.exists,
                    "payload_type": r.payload_type,
                    "keys": r.keys,
                    "item_count": r.item_count,
                    "status": r.status,
                    "notes": r.notes,
                }
                for r in self.results
            ],
        }

    def write_json(self, path: str | Path) -> Path:
        output_path = Path(path)
        write_json_artifact(self.as_json_dict(), output_path)
        return output_path
