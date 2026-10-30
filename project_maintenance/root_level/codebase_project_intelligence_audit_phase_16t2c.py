from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PHASE = "16T.2C"

PASS_STATUS = "PASS_CODEBASE_PROJECT_INTELLIGENCE_AUDIT_PHASE_16T2C"
WARN_STATUS = "WARN_CODEBASE_PROJECT_INTELLIGENCE_AUDIT_PHASE_16T2C"
FAIL_STATUS = "FAIL_CODEBASE_PROJECT_INTELLIGENCE_AUDIT_PHASE_16T2C"

ACTIVE_SOURCE = "ACTIVE_SOURCE"
ARCHIVE_OR_UPLOAD_COPY = "ARCHIVE_OR_UPLOAD_COPY"
TEST = "TEST"
SCRIPT = "SCRIPT"
SUSPICIOUS = "SUSPICIOUS"
LIKELY_UNUSED = "LIKELY_UNUSED"

ARCHIVE_DIR_TOKENS = {
    "LEAF_UPLOAD",
    "archive",
    "archives",
    "backup",
    "backups",
    "history",
    "old",
    "snapshot",
    "snapshots",
}

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    "build",
    "dist",
}

ENTRYPOINTS = {
    "main",
    "main_window",
    "engine_solver",
    "run_foundation_verification",
}

SCRIPT_PREFIXES = (
    "run_",
    "verify_",
    "integrate_",
    "fix_",
    "dump_",
    "find_",
    "inspect_",
    "full_",
)

SUSPICIOUS_TOKENS = (
    "copy",
    "backup",
    "old",
    "temp",
    "tmp",
    "unused",
    "broken",
    "duplicate",
)


@dataclass(frozen=True)
class ModuleRecord:
    path: str
    module: str
    name: str
    sha256: str
    imports: tuple[str, ...]
    category: str
    parse_error: str | None


def _skip(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)


def _is_archive_path(path: Path) -> bool:
    return any(part in ARCHIVE_DIR_TOKENS for part in path.parts)


def _module_name(path: Path, root: Path) -> str:
    return ".".join(path.relative_to(root).with_suffix("").parts)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _imports(path: Path) -> tuple[tuple[str, ...], str | None]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)
    except Exception as exc:
        return (), f"{type(exc).__name__}: {exc}"

    found: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])

    return tuple(sorted(found)), None


def _category(path: Path) -> str:
    name = path.stem

    if _is_archive_path(path):
        return ARCHIVE_OR_UPLOAD_COPY

    if name.startswith("test_"):
        return TEST

    if name.startswith(SCRIPT_PREFIXES):
        return SCRIPT

    if any(token in name.lower() for token in SUSPICIOUS_TOKENS):
        return SUSPICIOUS

    return ACTIVE_SOURCE


def collect_project_records(root: str | Path = ".") -> list[ModuleRecord]:
    root_path = Path(root).resolve()
    records: list[ModuleRecord] = []

    for path in sorted(root_path.rglob("*.py")):
        if _skip(path):
            continue

        imports, parse_error = _imports(path)

        records.append(
            ModuleRecord(
                path=path.relative_to(root_path).as_posix(),
                module=_module_name(path, root_path),
                name=path.stem,
                sha256=_hash(path),
                imports=imports,
                category=_category(path.relative_to(root_path)),
                parse_error=parse_error,
            )
        )

    return records


def build_project_intelligence_audit(root: str | Path = ".") -> dict[str, Any]:
    records = collect_project_records(root)

    active_records = [r for r in records if r.category == ACTIVE_SOURCE]
    non_archive_records = [r for r in records if r.category != ARCHIVE_OR_UPLOAD_COPY]

    imported_names = set()
    for record in non_archive_records:
        imported_names.update(record.imports)

    hash_to_paths: dict[str, list[str]] = {}
    active_hash_to_paths: dict[str, list[str]] = {}

    for record in records:
        hash_to_paths.setdefault(record.sha256, []).append(record.path)
        if record.category == ACTIVE_SOURCE:
            active_hash_to_paths.setdefault(record.sha256, []).append(record.path)

    all_duplicate_groups = [paths for paths in hash_to_paths.values() if len(paths) > 1]
    active_duplicate_groups = [paths for paths in active_hash_to_paths.values() if len(paths) > 1]

    parse_errors = [
        {"path": r.path, "error": r.parse_error}
        for r in records
        if r.parse_error
    ]

    likely_unused = []

    for record in active_records:
        if record.name in ENTRYPOINTS:
            continue

        if record.name not in imported_names:
            likely_unused.append(record.path)

    category_counts: dict[str, int] = {
        ACTIVE_SOURCE: 0,
        ARCHIVE_OR_UPLOAD_COPY: 0,
        TEST: 0,
        SCRIPT: 0,
        SUSPICIOUS: 0,
        LIKELY_UNUSED: len(likely_unused),
    }

    for record in records:
        category_counts[record.category] = category_counts.get(record.category, 0) + 1

    blockers = []
    warnings = []

    if parse_errors:
        blockers.append(f"{len(parse_errors)} Python files could not be parsed.")

    if active_duplicate_groups:
        warnings.append(f"{len(active_duplicate_groups)} duplicate groups exist inside active source.")

    if likely_unused:
        warnings.append(f"{len(likely_unused)} active modules appear likely unreferenced.")

    if category_counts[SUSPICIOUS]:
        warnings.append(f"{category_counts[SUSPICIOUS]} suspicious active filenames found.")

    status = FAIL_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not blockers,
        "python_file_count": len(records),
        "category_counts": category_counts,
        "all_duplicate_group_count": len(all_duplicate_groups),
        "active_duplicate_group_count": len(active_duplicate_groups),
        "active_duplicate_groups": active_duplicate_groups,
        "archive_or_upload_duplicate_count": len(all_duplicate_groups) - len(active_duplicate_groups),
        "likely_unused_active_modules": likely_unused,
        "likely_unused_active_module_count": len(likely_unused),
        "parse_errors": parse_errors,
        "parse_error_count": len(parse_errors),
        "warnings": warnings,
        "blockers": blockers,
        "summary": (
            f"{len(records)} Python files classified; "
            f"{category_counts[ARCHIVE_OR_UPLOAD_COPY]} archive/upload files ignored for active duplicate decisions; "
            f"{len(active_duplicate_groups)} active duplicate groups found."
        ),
    }


def build_project_intelligence_report(root: str | Path = ".") -> str:
    audit = build_project_intelligence_audit(root)

    lines = [
        "PROJECT-AWARE CODE INTELLIGENCE AUDIT",
        "=====================================",
        f"Phase: {audit['phase']}",
        f"Status: {audit['status']}",
        f"Passed: {audit['passed']}",
        f"Summary: {audit['summary']}",
        "",
        "CATEGORY COUNTS",
        "---------------",
    ]

    for key, value in audit["category_counts"].items():
        lines.append(f"{key}: {value}")

    lines.extend([
        "",
        "DUPLICATE INTELLIGENCE",
        "----------------------",
        f"All duplicate groups: {audit['all_duplicate_group_count']}",
        f"Active-source duplicate groups: {audit['active_duplicate_group_count']}",
        f"Archive/upload duplicate groups ignored: {audit['archive_or_upload_duplicate_count']}",
    ])

    if audit["active_duplicate_groups"]:
        lines.extend(["", "ACTIVE-SOURCE DUPLICATE GROUPS", "------------------------------"])
        for group in audit["active_duplicate_groups"]:
            lines.append("- " + " | ".join(group))

    if audit["likely_unused_active_modules"]:
        lines.extend(["", "LIKELY UNUSED ACTIVE MODULES", "----------------------------"])
        for path in audit["likely_unused_active_modules"]:
            lines.append(f"- {path}")

    if audit["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in audit["warnings"])

    if audit["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in audit["blockers"])

    return "\n".join(lines)


def write_project_intelligence_report(
    root: str | Path = ".",
    output_path: str | Path = "PROJECT_INTELLIGENCE_AUDIT_PHASE_16T2C.txt",
) -> Path:
    output = Path(output_path)
    output.write_text(build_project_intelligence_report(root), encoding="utf-8")
    return output


if __name__ == "__main__":
    output = write_project_intelligence_report(".")
    audit = build_project_intelligence_audit(".")
    print(audit["status"])
    print(output)
