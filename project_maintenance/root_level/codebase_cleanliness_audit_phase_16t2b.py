from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PHASE = "16T.2B"

PASS_STATUS = "PASS_CODEBASE_CLEANLINESS_AUDIT_PHASE_16T2B"
WARN_STATUS = "WARN_CODEBASE_CLEANLINESS_AUDIT_PHASE_16T2B"
FAIL_STATUS = "FAIL_CODEBASE_CLEANLINESS_AUDIT_PHASE_16T2B"

DEFAULT_EXCLUDED_DIRS = {
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

ENTRYPOINT_MODULES = {
    "main",
    "main_window",
    "engine_solver",
    "run_foundation_verification",
}

EXPECTED_STANDALONE_PREFIXES = (
    "test_",
    "run_",
    "verify_",
    "stage_",
)

SUSPICIOUS_NAME_TOKENS = (
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
class PythonFileRecord:
    path: str
    module: str
    sha256: str
    imports: tuple[str, ...]
    parse_error: str | None


def _should_skip(path: Path) -> bool:
    return any(part in DEFAULT_EXCLUDED_DIRS for part in path.parts)


def _module_name(path: Path, root: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    return ".".join(rel.parts)


def _top_level_module(module: str) -> str:
    return module.split(".")[0]


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_imports(path: Path) -> tuple[tuple[str, ...], str | None]:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except Exception as exc:
        return (), f"{type(exc).__name__}: {exc}"

    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(_top_level_module(alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(_top_level_module(node.module))

    return tuple(sorted(imports)), None


def collect_python_files(root: str | Path = ".") -> list[PythonFileRecord]:
    root_path = Path(root).resolve()
    records: list[PythonFileRecord] = []

    for path in sorted(root_path.rglob("*.py")):
        if _should_skip(path):
            continue

        imports, parse_error = _extract_imports(path)

        records.append(
            PythonFileRecord(
                path=path.relative_to(root_path).as_posix(),
                module=_module_name(path, root_path),
                sha256=_hash_file(path),
                imports=imports,
                parse_error=parse_error,
            )
        )

    return records


def build_codebase_cleanliness_audit(root: str | Path = ".") -> dict[str, Any]:
    records = collect_python_files(root)

    module_to_paths: dict[str, list[str]] = {}
    hash_to_paths: dict[str, list[str]] = {}
    imported_top_modules: set[str] = set()

    for record in records:
        module_to_paths.setdefault(record.module.split(".")[-1], []).append(record.path)
        hash_to_paths.setdefault(record.sha256, []).append(record.path)
        imported_top_modules.update(record.imports)

    exact_duplicate_groups = [
        paths for paths in hash_to_paths.values()
        if len(paths) > 1
    ]

    duplicate_module_name_groups = {
        module: paths
        for module, paths in module_to_paths.items()
        if len(paths) > 1
    }

    parse_errors = [
        {"path": record.path, "error": record.parse_error}
        for record in records
        if record.parse_error
    ]

    suspicious_files = [
        record.path
        for record in records
        if any(token in Path(record.path).stem.lower() for token in SUSPICIOUS_NAME_TOKENS)
    ]

    local_module_names = {record.module.split(".")[-1] for record in records}

    likely_unreferenced_modules = []

    for record in records:
        short_name = record.module.split(".")[-1]

        if short_name in ENTRYPOINT_MODULES:
            continue

        if short_name.startswith(EXPECTED_STANDALONE_PREFIXES):
            continue

        if short_name not in imported_top_modules:
            likely_unreferenced_modules.append(record.path)

    missing_internal_imports = []

    for record in records:
        for imported in record.imports:
            if imported.startswith("_"):
                continue
            if imported in {"PySide6", "numpy", "scipy", "matplotlib", "rocketcea", "pytest"}:
                continue
            if imported.startswith("typing"):
                continue
            if imported in local_module_names:
                continue

    blockers = []
    warnings = []

    if parse_errors:
        blockers.append(f"{len(parse_errors)} Python files could not be parsed.")

    if exact_duplicate_groups:
        warnings.append(f"{len(exact_duplicate_groups)} exact duplicate Python file groups found.")

    if duplicate_module_name_groups:
        warnings.append(f"{len(duplicate_module_name_groups)} duplicate module-name groups found.")

    if suspicious_files:
        warnings.append(f"{len(suspicious_files)} suspicious backup/temp/copy-style file names found.")

    if likely_unreferenced_modules:
        warnings.append(f"{len(likely_unreferenced_modules)} likely unreferenced non-test modules found.")

    if blockers:
        status = FAIL_STATUS
        passed = False
    elif warnings:
        status = WARN_STATUS
        passed = True
    else:
        status = PASS_STATUS
        passed = True

    return {
        "phase": PHASE,
        "status": status,
        "passed": passed,
        "python_file_count": len(records),
        "test_file_count": sum(1 for record in records if Path(record.path).name.startswith("test_")),
        "exact_duplicate_group_count": len(exact_duplicate_groups),
        "exact_duplicate_groups": exact_duplicate_groups,
        "duplicate_module_name_group_count": len(duplicate_module_name_groups),
        "duplicate_module_name_groups": duplicate_module_name_groups,
        "parse_error_count": len(parse_errors),
        "parse_errors": parse_errors,
        "suspicious_file_count": len(suspicious_files),
        "suspicious_files": suspicious_files,
        "likely_unreferenced_module_count": len(likely_unreferenced_modules),
        "likely_unreferenced_modules": likely_unreferenced_modules,
        "blockers": blockers,
        "warnings": warnings,
        "summary": (
            f"{len(records)} Python files audited; "
            f"{len(exact_duplicate_groups)} exact duplicate groups; "
            f"{len(likely_unreferenced_modules)} likely unreferenced non-test modules."
        ),
    }


def build_codebase_cleanliness_report(root: str | Path = ".") -> str:
    audit = build_codebase_cleanliness_audit(root)

    lines = [
        "PYTHON CODEBASE CLEANLINESS AUDIT",
        "=================================",
        f"Phase: {audit['phase']}",
        f"Status: {audit['status']}",
        f"Passed: {audit['passed']}",
        f"Summary: {audit['summary']}",
        "",
        "COUNTS",
        "------",
        f"Python files: {audit['python_file_count']}",
        f"Test files: {audit['test_file_count']}",
        f"Exact duplicate groups: {audit['exact_duplicate_group_count']}",
        f"Duplicate module-name groups: {audit['duplicate_module_name_group_count']}",
        f"Parse errors: {audit['parse_error_count']}",
        f"Suspicious files: {audit['suspicious_file_count']}",
        f"Likely unreferenced modules: {audit['likely_unreferenced_module_count']}",
    ]

    if audit["exact_duplicate_groups"]:
        lines.extend(["", "EXACT DUPLICATE GROUPS", "----------------------"])
        for group in audit["exact_duplicate_groups"]:
            lines.append("- " + " | ".join(group))

    if audit["duplicate_module_name_groups"]:
        lines.extend(["", "DUPLICATE MODULE NAMES", "----------------------"])
        for module, paths in audit["duplicate_module_name_groups"].items():
            lines.append(f"- {module}: " + " | ".join(paths))

    if audit["suspicious_files"]:
        lines.extend(["", "SUSPICIOUS FILE NAMES", "---------------------"])
        for path in audit["suspicious_files"]:
            lines.append(f"- {path}")

    if audit["likely_unreferenced_modules"]:
        lines.extend(["", "LIKELY UNREFERENCED NON-TEST MODULES", "------------------------------------"])
        for path in audit["likely_unreferenced_modules"]:
            lines.append(f"- {path}")

    if audit["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in audit["warnings"])

    if audit["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in audit["blockers"])

    return "\n".join(lines)


def write_codebase_cleanliness_report(
    root: str | Path = ".",
    output_path: str | Path = "CODEBASE_CLEANLINESS_AUDIT_PHASE_16T2B.txt",
) -> Path:
    output = Path(output_path)
    output.write_text(build_codebase_cleanliness_report(root), encoding="utf-8")
    return output


if __name__ == "__main__":
    path = write_codebase_cleanliness_report(".")
    audit = build_codebase_cleanliness_audit(".")
    print(audit["status"])
    print(path)
