"""
Programme 27D: Standardisation Finding Report Owner.

Owned reporting layer for standardisation scanner findings.

Design rules:
- Report only.
- No mutation.
- No deletion.
- No automatic repair.
- Organise findings so later phases can prioritise real architectural debt.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .scanner import (
    StandardisationFinding,
    StandardisationFindingLevel,
    StandardisationScanResult,
)


@dataclass(frozen=True)
class StandardisationFindingReportPackage:
    schema: str
    report_id: str
    summary: Dict[str, Any]
    sections: Dict[str, Any]
    mutation_performed: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "report_id": self.report_id,
            "summary": dict(self.summary),
            "sections": dict(self.sections),
            "mutation_performed": self.mutation_performed,
        }


class StandardisationFindingReportOwner:
    """
    Authoritative report owner for standardisation findings.
    """

    def __init__(self, scan_result: StandardisationScanResult) -> None:
        self.scan_result = scan_result
        self.findings: Tuple[StandardisationFinding, ...] = scan_result.findings

    def build_report(self) -> StandardisationFindingReportPackage:
        summary = self._summary()
        sections = {
            "finding_counts": self.scan_result.finding_counts(),
            "top_rules": self._top_rules(),
            "top_paths": self._top_paths(),
            "errors": self._findings_by_level(StandardisationFindingLevel.ERROR),
            "warnings": self._findings_by_level(StandardisationFindingLevel.WARNING),
            "infos": self._findings_by_level(StandardisationFindingLevel.INFO),
            "actionable_priority": self._actionable_priority(),
        }

        return StandardisationFindingReportPackage(
            schema="LEAF_STANDARDISATION_FINDING_REPORT_OWNER_PHASE_27D_V1",
            report_id="standardisation_finding_report_owner",
            summary=summary,
            sections=sections,
            mutation_performed=False,
        )

    def _summary(self) -> Dict[str, Any]:
        counts = self.scan_result.finding_counts()
        total_findings = len(self.findings)

        return {
            "root": self.scan_result.root,
            "scanned_python_files": self.scan_result.scanned_python_files,
            "scanned_report_files": self.scan_result.scanned_report_files,
            "total_findings": total_findings,
            "info_findings": counts["INFO"],
            "warning_findings": counts["WARNING"],
            "error_findings": counts["ERROR"],
            "has_errors": counts["ERROR"] > 0,
            "has_warnings": counts["WARNING"] > 0,
            "mutation_performed": False,
            "owner": "standardisation_finding_report_owner",
            "phase": "27D",
            "programme": "27",
        }

    def _top_rules(self, limit: int = 10) -> List[Dict[str, Any]]:
        counter = Counter(finding.rule_id for finding in self.findings)
        return [
            {"rule_id": rule_id, "count": count}
            for rule_id, count in counter.most_common(limit)
        ]

    def _top_paths(self, limit: int = 10) -> List[Dict[str, Any]]:
        counter = Counter(finding.path for finding in self.findings)
        return [
            {"path": path, "count": count}
            for path, count in counter.most_common(limit)
        ]

    def _findings_by_level(
        self,
        level: StandardisationFindingLevel,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        selected = [
            finding.as_dict()
            for finding in self.findings
            if finding.level == level
        ]
        return selected[:limit]

    def _actionable_priority(self, limit: int = 25) -> List[Dict[str, Any]]:
        priority_order = {
            StandardisationFindingLevel.ERROR: 0,
            StandardisationFindingLevel.WARNING: 1,
            StandardisationFindingLevel.INFO: 2,
        }

        ordered = sorted(
            self.findings,
            key=lambda finding: (
                priority_order[finding.level],
                finding.rule_id,
                finding.path,
            ),
        )

        return [finding.as_dict() for finding in ordered[:limit]]


def build_standardisation_finding_report_owner(
    scan_result: StandardisationScanResult,
) -> StandardisationFindingReportOwner:
    return StandardisationFindingReportOwner(scan_result)
