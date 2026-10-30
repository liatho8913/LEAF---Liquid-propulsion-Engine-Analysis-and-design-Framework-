from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json


REPORT_ONLY_DIR_MARKERS = (
    "LEAF_Reports/",
    "reports/",
    "audit",
    "completion",
)

DO_NOT_TOUCH_DIR_MARKERS = (
    ".venv/",
    "venv/",
    ".git/",
    "__pycache__/",
    "_leaf_repository_cleanup_candidates/",
)

SAFE_CODE_SUFFIXES = (
    ".py",
    ".json",
)

REVIEW_SUFFIXES = (
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
)


@dataclass(frozen=True)
class ReplacementPlanningItem:
    file: str
    line_number: int
    category: str
    pattern: str
    classification: str
    reason: str
    line: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "line_number": self.line_number,
            "category": self.category,
            "pattern": self.pattern,
            "classification": self.classification,
            "reason": self.reason,
            "line": self.line,
        }


@dataclass(frozen=True)
class ReferenceReplacementPlan:
    status: str
    source_audit: str
    total_items: int
    classification_counts: dict[str, int]
    samples: dict[str, list[dict[str, Any]]]
    mutation_performed: bool
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "source_audit": self.source_audit,
            "total_items": self.total_items,
            "classification_counts": self.classification_counts,
            "samples": self.samples,
            "mutation_performed": self.mutation_performed,
            "next_action": self.next_action,
        }


class ReferenceReplacementPlanner:
    """
    Classifies repository reference audit hits before replacement.

    This is intentionally read-only.

    It prevents blind mutation by separating:
    - safe_to_replace
    - needs_manual_review
    - report_only_historical
    - do_not_touch
    """

    def __init__(self, root: Path, audit_json: Path):
        self.root = Path(root)
        self.audit_json = Path(audit_json)

    def load_hits(self) -> list[dict[str, Any]]:
        payload = json.loads(self.audit_json.read_text(encoding="utf-8"))
        return payload.get("audit", {}).get("hits", [])

    def classify_hit(self, hit: dict[str, Any]) -> ReplacementPlanningItem:
        file = hit.get("file", "")
        suffix = Path(file).suffix

        if any(marker in file for marker in DO_NOT_TOUCH_DIR_MARKERS):
            classification = "do_not_touch"
            reason = "Path is excluded from repository mutation."
        elif any(marker in file for marker in REPORT_ONLY_DIR_MARKERS):
            classification = "report_only_historical"
            reason = "Reference appears inside report/audit/history output."
        elif suffix in SAFE_CODE_SUFFIXES and "project_maintenance/" in file:
            classification = "needs_manual_review"
            reason = "Maintenance code may contain phase history or active gates."
        elif suffix in SAFE_CODE_SUFFIXES:
            classification = "safe_to_replace_candidate"
            reason = "Code/config reference outside report-only areas."
        elif suffix in REVIEW_SUFFIXES:
            classification = "needs_manual_review"
            reason = "Documentation/config text must be reviewed before replacement."
        else:
            classification = "needs_manual_review"
            reason = "Unknown file type or unclear ownership."

        return ReplacementPlanningItem(
            file=file,
            line_number=int(hit.get("line_number", 0)),
            category=hit.get("category", ""),
            pattern=hit.get("pattern", ""),
            classification=classification,
            reason=reason,
            line=hit.get("line", ""),
        )

    def build_plan(self, sample_limit: int = 25) -> ReferenceReplacementPlan:
        hits = self.load_hits()
        items = [self.classify_hit(hit) for hit in hits]

        counts: dict[str, int] = {}
        samples: dict[str, list[dict[str, Any]]] = {}

        for item in items:
            counts[item.classification] = counts.get(item.classification, 0) + 1
            samples.setdefault(item.classification, [])
            if len(samples[item.classification]) < sample_limit:
                samples[item.classification].append(item.to_dict())

        return ReferenceReplacementPlan(
            status="PASS",
            source_audit=str(self.audit_json.relative_to(self.root)),
            total_items=len(items),
            classification_counts=dict(sorted(counts.items())),
            samples=samples,
            mutation_performed=False,
            next_action="Targeted safe replacement candidates only after review.",
        )
