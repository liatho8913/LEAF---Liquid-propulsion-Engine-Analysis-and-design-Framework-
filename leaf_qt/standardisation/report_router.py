"""
Programme 27I: Standardisation Report Router.

Central report routing for LEAF standardisation outputs.

Design rules:
- Route reports only.
- No repository repair.
- No deletion.
- No archive.
- No mutation outside LEAF_Reports.
- Keep standardisation reports in one canonical report location.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping


@dataclass(frozen=True)
class StandardisationRoutedReport:
    schema: str
    report_id: str
    txt_path: str
    json_path: str
    report_dir: str
    mutation_scope: str
    mutation_performed: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "report_id": self.report_id,
            "txt_path": self.txt_path,
            "json_path": self.json_path,
            "report_dir": self.report_dir,
            "mutation_scope": self.mutation_scope,
            "mutation_performed": self.mutation_performed,
        }


class StandardisationReportRouter:
    """
    Canonical report router for standardisation architecture.

    This is allowed to write report files only under:
        LEAF_Reports/standardisation_architecture

    It must not modify engineering, runtime, workflow, storage, or project files.
    """

    REPORT_SCHEMA = "LEAF_STANDARDISATION_REPORT_ROUTER_PHASE_27I_V1"

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.report_dir = self.root / "LEAF_Reports" / "standardisation_architecture"

    def route_report(
        self,
        report_id: str,
        payload: Mapping[str, Any],
        title: str = "LEAF Standardisation Routed Report",
    ) -> StandardisationRoutedReport:
        if not report_id or not report_id.strip():
            raise ValueError("report_id is empty")

        safe_report_id = self._safe_report_id(report_id)
        self.report_dir.mkdir(parents=True, exist_ok=True)

        txt_path = self.report_dir / f"{safe_report_id}.txt"
        json_path = self.report_dir / f"{safe_report_id}.json"

        routed_payload = {
            "schema": self.REPORT_SCHEMA,
            "report_id": safe_report_id,
            "payload": dict(payload),
            "router": {
                "report_dir": str(self.report_dir.relative_to(self.root)),
                "mutation_scope": "LEAF_Reports_only",
                "mutation_performed": False,
                "deletion_performed": False,
                "archive_performed": False,
            },
        }

        txt_path.write_text(
            self._render_text(title=title, report_id=safe_report_id, payload=routed_payload),
            encoding="utf-8",
        )
        json_path.write_text(json.dumps(routed_payload, indent=2), encoding="utf-8")

        return StandardisationRoutedReport(
            schema=self.REPORT_SCHEMA,
            report_id=safe_report_id,
            txt_path=str(txt_path.relative_to(self.root)),
            json_path=str(json_path.relative_to(self.root)),
            report_dir=str(self.report_dir.relative_to(self.root)),
            mutation_scope="LEAF_Reports_only",
            mutation_performed=False,
        )

    def _safe_report_id(self, report_id: str) -> str:
        allowed = []
        for char in report_id.strip():
            if char.isalnum() or char in {"_", "-", "."}:
                allowed.append(char)
            else:
                allowed.append("_")

        safe = "".join(allowed).strip("._-")
        if not safe:
            raise ValueError("report_id could not be converted to a safe filename")
        return safe

    def _render_text(
        self,
        title: str,
        report_id: str,
        payload: Mapping[str, Any],
    ) -> str:
        router = payload.get("router", {})
        body = [
            title,
            "=" * len(title),
            f"schema={payload.get('schema')}",
            f"report_id={report_id}",
            f"report_dir={router.get('report_dir')}",
            f"mutation_scope={router.get('mutation_scope')}",
            f"mutation_performed={router.get('mutation_performed')}",
            f"deletion_performed={router.get('deletion_performed')}",
            f"archive_performed={router.get('archive_performed')}",
        ]

        payload_data = payload.get("payload", {})
        for key in sorted(payload_data):
            value = payload_data[key]
            if isinstance(value, (str, int, float, bool)) or value is None:
                body.append(f"{key}={value}")

        return "\n".join(body) + "\n"

    def report(self) -> Dict[str, Any]:
        return {
            "schema": self.REPORT_SCHEMA,
            "report_dir": str(self.report_dir.relative_to(self.root)),
            "mutation_scope": "LEAF_Reports_only",
            "mutation_performed": False,
            "deletion_performed": False,
            "archive_performed": False,
        }


def build_standardisation_report_router(root: Path) -> StandardisationReportRouter:
    return StandardisationReportRouter(root=root)
