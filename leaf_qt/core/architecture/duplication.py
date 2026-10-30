from __future__ import annotations

from core.architecture.repository_metadata import iter_supported_files
from pathlib import Path
from typing import Any

from core.architecture.models import ArchitectureFinding, ArchitectureReport


DUPLICATION_PATTERNS = {
    "MANUAL_WRITE_TEXT": ".write_text(",
    "MANUAL_PARENT_MKDIR": ".parent.mkdir(",
}

JSON_ARTIFACT_PATTERNS = {
    "MANUAL_JSON_DUMPS_TO_ARTIFACT": "write_text(json.dumps(",
    "MANUAL_JSON_LOADS_FROM_ARTIFACT": "json.loads(",
}


def scan_file_for_architecture_duplication(path: Path, root: Path | None = None) -> list[ArchitectureFinding]:
    root = root or Path(".").resolve()
    text = path.read_text(encoding="utf-8", errors="replace")
    relative = path.relative_to(root).as_posix() if path.is_absolute() else path.as_posix()

    findings: list[ArchitectureFinding] = []

    for code, pattern in DUPLICATION_PATTERNS.items():
        count = text.count(pattern)
        if count:
            findings.append(
                ArchitectureFinding(
                    status="WARN",
                    code=code,
                    message=f"Found duplicated architecture IO/reporting pattern {pattern!r} {count} time(s).",
                    path=relative,
                    evidence={"pattern": pattern, "count": count},
                )
            )

    if "write_text(json.dumps(" in text:
        findings.append(
            ArchitectureFinding(
                status="WARN",
                code="MANUAL_JSON_DUMPS_TO_ARTIFACT",
                message="Found manual JSON artifact writing.",
                path=relative,
                evidence={"pattern": "write_text(json.dumps(", "count": text.count("write_text(json.dumps(")},
            )
        )

    if "json.loads(" in text and ".read_text(" in text:
        findings.append(
            ArchitectureFinding(
                status="WARN",
                code="MANUAL_JSON_LOADS_FROM_ARTIFACT",
                message="Found manual JSON artifact reading.",
                path=relative,
                evidence={"pattern": "json.loads(...read_text...)", "count": text.count("json.loads(")},
            )
        )

    return findings


def _should_skip_duplication_scan_path(
    relative_path: str,
    include_tests: bool = False,
) -> bool:
    lowered = relative_path.lower()
    filename = Path(relative_path).name.lower()

    if "__pycache__" in lowered:
        return True

    if lowered.startswith("leaf_qt/core/architecture/"):
        return True

    if not include_tests and (
        filename.startswith("test_")
        or "/test_" in lowered
        or lowered.endswith("_test.py")
    ):
        return True

    return False


def build_architecture_duplication_report(
    root: str | Path = ".",
    include_prefixes: tuple[str, ...] = ("leaf_qt/",),
    include_tests: bool = False,
) -> ArchitectureReport:
    root_path = Path(root).resolve()
    findings: list[ArchitectureFinding] = []

    for path in iter_supported_files(root_path):
        if path.suffix.lower() != ".py":
            continue

        rel = path.relative_to(root_path).as_posix()

        if not rel.startswith(include_prefixes):
            continue

        if _should_skip_duplication_scan_path(rel, include_tests=include_tests):
            continue

        file_findings = scan_file_for_architecture_duplication(path, root_path)
        findings.extend(file_findings)

    pattern_counts: dict[str, int] = {}
    files_with_findings: set[str] = set()

    for finding in findings:
        pattern_counts[finding.code] = pattern_counts.get(finding.code, 0) + 1
        if finding.path:
            files_with_findings.add(finding.path)

    return ArchitectureReport(
        schema="LEAF_ARCHITECTURE_DUPLICATION_REPORT_V1",
        title="LEAF ARCHITECTURE DUPLICATION REPORT",
        summary={
            "findings": len(findings),
            "files_with_findings": len(files_with_findings),
            "pattern_counts": dict(sorted(pattern_counts.items())),
        },
        findings=findings,
        payload={
            "patterns": DUPLICATION_PATTERNS,
            "files_with_findings": sorted(files_with_findings),
        },
        safe_to_modify_files=False,
    )


def build_duplication_text_report(report: ArchitectureReport, limit: int = 50) -> str:
    data = report.to_dict()
    summary = data["summary"]

    lines = [
        report.title,
        "=" * len(report.title),
        f"schema={report.schema}",
        f"passed={data['passed']}",
        f"safe_to_modify_files={report.safe_to_modify_files}",
        f"findings={summary['findings']}",
        f"files_with_findings={summary['files_with_findings']}",
        "",
        "PATTERN COUNTS",
        "--------------",
    ]

    for key, value in summary["pattern_counts"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", f"TOP {limit} FINDINGS", "---------------"])

    for finding in report.findings[:limit]:
        lines.append(
            f"{finding.status} | {finding.code} | {finding.path} | {finding.message}"
        )

    return "\n".join(lines)
