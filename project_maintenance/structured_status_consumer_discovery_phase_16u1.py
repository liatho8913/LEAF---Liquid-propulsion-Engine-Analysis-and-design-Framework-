from __future__ import annotations

import ast
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


PHASE = "16U.1"
PASS_BANNER = "PASS_PHASE_16U1_STRUCTURED_STATUS_CONSUMER_DISCOVERY"

ROOT = Path(".")
OUT_TXT = Path("project_maintenance/STRUCTURED_STATUS_CONSUMER_DISCOVERY_PHASE_16U1.txt")
OUT_JSON = Path("project_maintenance/structured_status_consumer_discovery_phase_16u1.json")

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "build",
    "dist",
    "LEAF_UPLOAD",
}

RAW_STATUS_TERMS = ("PASS", "WARN", "FAIL")

PATTERNS = [
    ("direct_status_equality", re.compile(r"""status\s*==\s*["'](?:PASS|WARN|FAIL)["']""")),
    ("direct_status_inequality", re.compile(r"""status\s*!=\s*["'](?:PASS|WARN|FAIL)["']""")),
    ("startswith_status", re.compile(r"""\.startswith\(\s*["'](?:PASS|WARN|FAIL)""")),
    ("contains_status", re.compile(r"""["'](?:PASS|WARN|FAIL)["']\s+in\s+""")),
    ("raw_status_literal", re.compile(r"""["'](?:PASS|WARN|FAIL)["']""")),
    ("pass_banner_literal", re.compile(r"""["']PASS_[A-Z0-9_]+["']""")),
]


@dataclass(frozen=True)
class ConsumerFinding:
    file: str
    line: int
    category: str
    pattern: str
    snippet: str


def iter_python_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.py")):
        parts = set(path.parts)
        if parts & EXCLUDED_DIRS:
            continue
        yield path


def classify_file(path: Path) -> str:
    name = path.name.lower()
    text = str(path).lower()

    if name.startswith("test_") or "/test_" in text:
        return "REGRESSION_TEST"
    if "master_gate" in text:
        return "MASTER_GATE"
    if "completion_audit" in text or "audit" in text:
        return "COMPLETION_AUDIT"
    if "report" in text:
        return "REPORT"
    if "viewer" in text or "window" in text or "panel" in text or "main_window" in text:
        return "GUI"
    if "validation" in text or "validator" in text:
        return "VALIDATION"
    if "export" in text:
        return "EXPORT"
    if "project_maintenance" in text:
        return "DEVELOPER_TOOL"
    if "solver" in text:
        return "SOLVER_CONSUMER"
    return "UTILITY"


def extract_ast_status_consumers(path: Path, source: str) -> list[ConsumerFinding]:
    findings: list[ConsumerFinding] = []
    category = classify_file(path)

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            left_name = ""
            if isinstance(node.left, ast.Name):
                left_name = node.left.id.lower()
            elif isinstance(node.left, ast.Attribute):
                left_name = node.left.attr.lower()

            for comparator in node.comparators:
                if isinstance(comparator, ast.Constant) and comparator.value in RAW_STATUS_TERMS:
                    if "status" in left_name or left_name in {"severity", "result"}:
                        line = getattr(node, "lineno", 0)
                        snippet = source.splitlines()[line - 1].strip() if line else ""
                        findings.append(
                            ConsumerFinding(
                                file=str(path),
                                line=line,
                                category=category,
                                pattern="ast_status_compare",
                                snippet=snippet,
                            )
                        )

        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in {"startswith", "endswith"}:
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if any(arg.value.startswith(term) for term in RAW_STATUS_TERMS):
                            line = getattr(node, "lineno", 0)
                            snippet = source.splitlines()[line - 1].strip() if line else ""
                            findings.append(
                                ConsumerFinding(
                                    file=str(path),
                                    line=line,
                                    category=category,
                                    pattern=f"ast_{func.attr}_status",
                                    snippet=snippet,
                                )
                            )

    return findings


def extract_regex_status_consumers(path: Path, source: str) -> list[ConsumerFinding]:
    findings: list[ConsumerFinding] = []
    category = classify_file(path)
    lines = source.splitlines()

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        for pattern_name, pattern in PATTERNS:
            if pattern.search(stripped):
                findings.append(
                    ConsumerFinding(
                        file=str(path),
                        line=idx,
                        category=category,
                        pattern=pattern_name,
                        snippet=stripped,
                    )
                )

    return findings


def deduplicate(findings: list[ConsumerFinding]) -> list[ConsumerFinding]:
    seen = set()
    unique: list[ConsumerFinding] = []

    for finding in findings:
        key = (finding.file, finding.line, finding.pattern, finding.snippet)
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)

    return sorted(unique, key=lambda item: (item.file, item.line, item.pattern))


def build_consumer_discovery() -> dict:
    all_findings: list[ConsumerFinding] = []
    files_scanned = 0

    for path in iter_python_files(ROOT):
        files_scanned += 1
        source = path.read_text(encoding="utf-8", errors="replace")
        all_findings.extend(extract_ast_status_consumers(path, source))
        all_findings.extend(extract_regex_status_consumers(path, source))

    findings = deduplicate(all_findings)

    by_category: dict[str, int] = {}
    by_pattern: dict[str, int] = {}

    for finding in findings:
        by_category[finding.category] = by_category.get(finding.category, 0) + 1
        by_pattern[finding.pattern] = by_pattern.get(finding.pattern, 0) + 1

    high_priority = [
        finding
        for finding in findings
        if finding.category in {
            "GUI",
            "REPORT",
            "VALIDATION",
            "COMPLETION_AUDIT",
            "MASTER_GATE",
            "SOLVER_CONSUMER",
            "EXPORT",
        }
    ]

    payload = {
        "phase": PHASE,
        "status": PASS_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "files_scanned": files_scanned,
        "finding_count": len(findings),
        "high_priority_finding_count": len(high_priority),
        "by_category": dict(sorted(by_category.items())),
        "by_pattern": dict(sorted(by_pattern.items())),
        "findings": [asdict(item) for item in findings],
        "high_priority_findings": [asdict(item) for item in high_priority],
        "phase_16u1_structured_status_consumer_discovery_complete": True,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    report_lines = [
        "LEAF PHASE 16U.1",
        "STRUCTURED STATUS CONSUMER DISCOVERY",
        "======================================",
        "",
        f"STATUS: {PASS_BANNER}",
        f"Generated: {payload['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase performs discovery only.",
        "No engineering logic is modified.",
        "No solver logic is modified.",
        "No GUI behaviour is modified.",
        "",
        "SUMMARY",
        "-------",
        f"Python files scanned: {files_scanned}",
        f"Raw status consumer findings: {len(findings)}",
        f"High-priority migration findings: {len(high_priority)}",
        "",
        "FINDINGS BY CATEGORY",
        "--------------------",
    ]

    for category, count in sorted(by_category.items()):
        report_lines.append(f"{category}: {count}")

    report_lines.extend(["", "FINDINGS BY PATTERN", "-------------------"])

    for pattern, count in sorted(by_pattern.items()):
        report_lines.append(f"{pattern}: {count}")

    report_lines.extend(
        [
            "",
            "HIGH PRIORITY MIGRATION TARGETS",
            "-------------------------------",
        ]
    )

    for finding in high_priority[:200]:
        report_lines.append(
            f"{finding.file}:{finding.line} "
            f"[{finding.category}/{finding.pattern}] "
            f"{finding.snippet}"
        )

    if len(high_priority) > 200:
        report_lines.append(f"... truncated {len(high_priority) - 200} additional high-priority findings")

    report_lines.extend(
        [
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.2 — STRUCTURED STATUS CONSUMER CLASSIFICATION",
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.1 COMPLETE.",
            "Consumer discovery is complete.",
            "The project may now classify and prioritise these consumers before migration.",
        ]
    )

    OUT_TXT.write_text("\n".join(report_lines), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = build_consumer_discovery()
    print(result["status"])
    print(f"files_scanned={result['files_scanned']}")
    print(f"finding_count={result['finding_count']}")
    print(f"high_priority_finding_count={result['high_priority_finding_count']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
