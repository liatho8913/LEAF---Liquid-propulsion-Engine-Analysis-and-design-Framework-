from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


PHASE = "16U.2"
PASS_BANNER = "PASS_PHASE_16U2_STRUCTURED_STATUS_CONSUMER_CLASSIFICATION"

IN_JSON = Path("project_maintenance/structured_status_consumer_discovery_phase_16u1.json")
OUT_JSON = Path("project_maintenance/structured_status_consumer_classification_phase_16u2.json")
OUT_TXT = Path("project_maintenance/STRUCTURED_STATUS_CONSUMER_CLASSIFICATION_PHASE_16U2.txt")


@dataclass(frozen=True)
class ClassifiedFinding:
    file: str
    line: int
    source_category: str
    pattern: str
    classification: str
    migration_required: bool
    priority: str
    reason: str
    snippet: str


def _is_test_file(file_path: str, source_category: str) -> bool:
    lower = file_path.lower()
    return (
        source_category == "REGRESSION_TEST"
        or "/test_" in lower
        or lower.startswith("test_")
        or "/tests/" in lower
        or lower.endswith("_test.py")
    )


def _is_project_maintenance(file_path: str) -> bool:
    return "project_maintenance/" in file_path.lower()


def _is_pass_banner(snippet: str, pattern: str) -> bool:
    return pattern == "pass_banner_literal" or bool(re.search(r"PASS_[A-Z0-9_]+", snippet))


def _looks_like_assignment(snippet: str) -> bool:
    return bool(
        re.search(
            r"(^|\s)(status|.*_status|severity|gate|.*_gate|diagnostic_note)\s*=",
            snippet,
        )
    )


def _looks_like_output_payload_write(snippet: str) -> bool:
    return bool(
        re.search(
            r"""(\[["'][^"']*(status|gate|severity)[^"']*["']\]\s*=|["'](status|severity|.*_status|.*_gate)["']\s*:)""",
            snippet,
        )
    )


def _looks_like_consumer(snippet: str, pattern: str) -> bool:
    if pattern in {
        "ast_status_compare",
        "direct_status_equality",
        "direct_status_inequality",
        "startswith_status",
        "contains_status",
        "ast_startswith_status",
        "ast_endswith_status",
    }:
        return True

    consumer_tokens = [
        " if ",
        "if ",
        "elif ",
        "while ",
        "assert ",
        "not in",
        " in ",
        "==",
        "!=",
        ".startswith",
        ".endswith",
    ]
    return any(token in snippet for token in consumer_tokens)


def _looks_like_presentation_only(snippet: str) -> bool:
    return any(
        token in snippet
        for token in [
            "setText",
            "append(",
            "report_lines.append",
            "lines.append",
            "print(",
            "f\"",
            "f'",
        ]
    )


def classify_finding(raw: dict) -> ClassifiedFinding:
    file_path = raw.get("file", "")
    line = int(raw.get("line", 0))
    source_category = raw.get("category", "UNKNOWN")
    pattern = raw.get("pattern", "unknown")
    snippet = raw.get("snippet", "").strip()

    lower_file = file_path.lower()

    if _is_test_file(file_path, source_category):
        return ClassifiedFinding(
            file=file_path,
            line=line,
            source_category=source_category,
            pattern=pattern,
            classification="TEST_ASSERTION_OR_REGRESSION_EVIDENCE",
            migration_required=False,
            priority="NONE",
            reason="Regression tests may assert legacy strings while compatibility is preserved.",
            snippet=snippet,
        )

    if _is_pass_banner(snippet, pattern):
        return ClassifiedFinding(
            file=file_path,
            line=line,
            source_category=source_category,
            pattern=pattern,
            classification="PASS_BANNER_OR_COMPLETION_EVIDENCE",
            migration_required=False,
            priority="NONE",
            reason="Phase completion banners are historical evidence and should not be migrated.",
            snippet=snippet,
        )

    if _is_project_maintenance(file_path) and _looks_like_presentation_only(snippet):
        return ClassifiedFinding(
            file=file_path,
            line=line,
            source_category=source_category,
            pattern=pattern,
            classification="DEVELOPER_REPORT_PRESENTATION",
            migration_required=False,
            priority="LOW",
            reason="Developer-facing report text can remain legacy-compatible unless it drives a gate.",
            snippet=snippet,
        )

    if _looks_like_assignment(snippet) or _looks_like_output_payload_write(snippet):
        return ClassifiedFinding(
            file=file_path,
            line=line,
            source_category=source_category,
            pattern=pattern,
            classification="STATUS_PRODUCER",
            migration_required=False,
            priority="NONE",
            reason="This appears to produce status data rather than consume it.",
            snippet=snippet,
        )

    if _looks_like_consumer(snippet, pattern):
        if source_category in {"MASTER_GATE", "COMPLETION_AUDIT", "VALIDATION"}:
            priority = "HIGH"
        elif source_category in {"GUI", "REPORT", "EXPORT"}:
            priority = "MEDIUM"
        elif source_category == "SOLVER_CONSUMER":
            priority = "HIGH"
        else:
            priority = "LOW"

        return ClassifiedFinding(
            file=file_path,
            line=line,
            source_category=source_category,
            pattern=pattern,
            classification="STATUS_CONSUMER_REQUIRES_REVIEW",
            migration_required=True,
            priority=priority,
            reason="This appears to branch, compare, filter, or decide using a raw status value.",
            snippet=snippet,
        )

    if _looks_like_presentation_only(snippet):
        return ClassifiedFinding(
            file=file_path,
            line=line,
            source_category=source_category,
            pattern=pattern,
            classification="PRESENTATION_ONLY",
            migration_required=False,
            priority="LOW",
            reason="This appears to render status text rather than make engineering decisions.",
            snippet=snippet,
        )

    if "legacy" in lower_file or "adapter" in lower_file:
        return ClassifiedFinding(
            file=file_path,
            line=line,
            source_category=source_category,
            pattern=pattern,
            classification="LEGACY_COMPATIBILITY",
            migration_required=False,
            priority="LOW",
            reason="Legacy compatibility/adapters may intentionally preserve raw status values.",
            snippet=snippet,
        )

    return ClassifiedFinding(
        file=file_path,
        line=line,
        source_category=source_category,
        pattern=pattern,
        classification="UNCLASSIFIED_REVIEW_REQUIRED",
        migration_required=True,
        priority="MEDIUM",
        reason="Could not confidently classify this finding; manual review required.",
        snippet=snippet,
    )


def build_structured_status_consumer_classification() -> dict:
    if not IN_JSON.exists():
        raise FileNotFoundError(
            f"Missing {IN_JSON}. Run Phase 16U.1 discovery before Phase 16U.2 classification."
        )

    source = json.loads(IN_JSON.read_text(encoding="utf-8"))
    raw_findings = source.get("findings", [])

    classified = [classify_finding(item) for item in raw_findings]

    by_classification: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    migration_required = []

    for item in classified:
        by_classification[item.classification] = by_classification.get(item.classification, 0) + 1
        by_priority[item.priority] = by_priority.get(item.priority, 0) + 1
        if item.migration_required:
            migration_required.append(item)

    high_priority = [item for item in migration_required if item.priority == "HIGH"]
    medium_priority = [item for item in migration_required if item.priority == "MEDIUM"]
    low_priority = [item for item in migration_required if item.priority == "LOW"]

    payload = {
        "phase": PHASE,
        "status": PASS_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "source_discovery_status": source.get("status"),
        "source_finding_count": len(raw_findings),
        "classified_finding_count": len(classified),
        "migration_required_count": len(migration_required),
        "high_priority_migration_count": len(high_priority),
        "medium_priority_migration_count": len(medium_priority),
        "low_priority_migration_count": len(low_priority),
        "by_classification": dict(sorted(by_classification.items())),
        "by_priority": dict(sorted(by_priority.items())),
        "migration_required_findings": [asdict(item) for item in migration_required],
        "classified_findings": [asdict(item) for item in classified],
        "phase_16u2_structured_status_consumer_classification_complete": True,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.2",
        "STRUCTURED STATUS CONSUMER CLASSIFICATION",
        "===========================================",
        "",
        f"STATUS: {PASS_BANNER}",
        f"Generated: {payload['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase classifies Phase 16U.1 discovery findings.",
        "No engineering logic is modified.",
        "No solver logic is modified.",
        "No GUI behaviour is modified.",
        "",
        "SUMMARY",
        "-------",
        f"Source findings: {payload['source_finding_count']}",
        f"Classified findings: {payload['classified_finding_count']}",
        f"Migration required: {payload['migration_required_count']}",
        f"High-priority migrations: {payload['high_priority_migration_count']}",
        f"Medium-priority migrations: {payload['medium_priority_migration_count']}",
        f"Low-priority migrations: {payload['low_priority_migration_count']}",
        "",
        "CLASSIFICATION BREAKDOWN",
        "------------------------",
    ]

    for key, value in payload["by_classification"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "PRIORITY BREAKDOWN", "------------------"])
    for key, value in payload["by_priority"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "HIGH-PRIORITY MIGRATION TARGETS", "-------------------------------"])
    for item in high_priority[:150]:
        lines.append(
            f"{item.file}:{item.line} "
            f"[{item.source_category}/{item.pattern}] "
            f"{item.snippet}"
        )

    if len(high_priority) > 150:
        lines.append(f"... truncated {len(high_priority) - 150} additional high-priority targets")

    lines.extend(
        [
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.3 — STRUCTURED STATUS MIGRATION ROADMAP",
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.2 COMPLETE.",
            "Status discovery findings have been classified.",
            "The project may now create a migration roadmap from the true consumer list.",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = build_structured_status_consumer_classification()
    print(result["status"])
    print(f"source_finding_count={result['source_finding_count']}")
    print(f"classified_finding_count={result['classified_finding_count']}")
    print(f"migration_required_count={result['migration_required_count']}")
    print(f"high_priority_migration_count={result['high_priority_migration_count']}")
    print(f"medium_priority_migration_count={result['medium_priority_migration_count']}")
    print(f"low_priority_migration_count={result['low_priority_migration_count']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
