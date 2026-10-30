from __future__ import annotations

from core.architecture.repository_metadata import iter_supported_files
from dataclasses import dataclass, asdict
from pathlib import Path

from core.architecture.io import write_json_artifact, write_text_artifact
from typing import Iterable
import json
import re


LEGACY_PRESENTATION_PATTERNS = {
    "inline_pass_fail_warn_literal": re.compile(r'["\'](?:PASS|FAIL|WARN)_[A-Z0-9_]+["\']'),
    "inline_status_prefix_check": re.compile(r'\.startswith\(["\'](?:PASS|FAIL|WARN)'),
    "inline_status_contains_check": re.compile(r'(?:PASS|FAIL|WARN)_'),
    "legacy_status_suffix_check": re.compile(r'\.endswith\(["\']_(?:PASS|FAIL|WARN)["\']\)'),
}

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    ".idea",
    ".vscode",
}

AUDIT_EXEMPT_FILE_FRAGMENTS = {
    "presentation_layer_repository_audit_owner.py",
    "phase_16u162_global_repository_presentation_layer_sanity_audit.py",
}


@dataclass(frozen=True)
class PresentationLayerFinding:
    path: str
    line_number: int
    pattern: str
    line: str


def _is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)


def _is_audit_exempt(path: Path) -> bool:
    return any(fragment in str(path) for fragment in AUDIT_EXEMPT_FILE_FRAGMENTS)


def iter_python_files(root: Path) -> Iterable[Path]:
    """Yield current Python source files relevant to presentation auditing."""
    for path in iter_supported_files(root):
        if path.suffix.lower() != ".py":
            continue
        if _is_excluded(path):
            continue
        if _is_audit_exempt(path):
            continue
        yield path


def audit_repository_presentation_layer(root: Path) -> dict:
    root = root.resolve()
    findings: list[PresentationLayerFinding] = []
    scanned_files = 0
    compile_failures: list[str] = []

    for path in iter_python_files(root):
        scanned_files += 1

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")

        try:
            compile(text, str(path), "exec")
        except SyntaxError as exc:
            compile_failures.append(f"{path.relative_to(root)}:{exc.lineno}:{exc.msg}")

        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            for pattern_name, pattern in LEGACY_PRESENTATION_PATTERNS.items():
                if pattern.search(stripped):
                    findings.append(
                        PresentationLayerFinding(
                            path=str(path.relative_to(root)),
                            line_number=line_number,
                            pattern=pattern_name,
                            line=stripped[:240],
                        )
                    )

    passed = not findings and not compile_failures

    return {
        "phase": "16U.162",
        "audit": "GLOBAL_REPOSITORY_PRESENTATION_LAYER_SANITY_AUDIT",
        "root": str(root),
        "scanned_files": scanned_files,
        "finding_count": len(findings),
        "compile_failure_count": len(compile_failures),
        "compile_failures": compile_failures,
        "findings": [asdict(f) for f in findings],
        "passed": passed,
        "status": (
            "PASS_PHASE_16U162_GLOBAL_REPOSITORY_PRESENTATION_LAYER_SANITY_AUDIT"
            if passed
            else "FAIL_PHASE_16U162_GLOBAL_REPOSITORY_PRESENTATION_LAYER_SANITY_AUDIT"
        ),
    }


def write_audit_outputs(root: Path, output_dir: Path | None = None) -> dict:
    result = audit_repository_presentation_layer(root)

    if output_dir is None:
        output_dir = root / "project_maintenance"

    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "phase_16u162_global_repository_presentation_layer_sanity_audit.json"
    txt_path = output_dir / "phase_16u162_global_repository_presentation_layer_sanity_audit.txt"

    write_json_artifact(result, json_path)

    lines = [
        "LEAF PHASE 16U.162",
        "GLOBAL REPOSITORY PRESENTATION LAYER SANITY AUDIT",
        "=" * 58,
        f"status={result['status']}",
        f"scanned_files={result['scanned_files']}",
        f"finding_count={result['finding_count']}",
        f"compile_failure_count={result['compile_failure_count']}",
        "",
    ]

    if result["compile_failures"]:
        lines.append("COMPILE FAILURES")
        lines.append("-" * 16)
        lines.extend(result["compile_failures"])
        lines.append("")

    if result["findings"]:
        lines.append("FINDINGS")
        lines.append("-" * 8)
        for finding in result["findings"][:500]:
            lines.append(
                f"{finding['path']}:{finding['line_number']} "
                f"[{finding['pattern']}] {finding['line']}"
            )

        if len(result["findings"]) > 500:
            lines.append("")
            lines.append(f"... truncated: {len(result['findings']) - 500} additional findings in JSON report")

    write_text_artifact("\n".join(lines), txt_path)

    result["json_report"] = str(json_path)
    result["text_report"] = str(txt_path)

    return result
