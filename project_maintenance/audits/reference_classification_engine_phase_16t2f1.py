from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.production_historical_artifacts.leaf_qt.root_level_review.codebase_safe_cleanup_plan_phase_16t2d import ARCHIVE, build_safe_cleanup_plan


PHASE = "16T.2F.1"

PASS_STATUS = "PASS_REFERENCE_CLASSIFICATION_ENGINE_PHASE_16T2F1"
WARN_STATUS = "WARN_REFERENCE_CLASSIFICATION_ENGINE_PHASE_16T2F1"
FAIL_STATUS = "FAIL_REFERENCE_CLASSIFICATION_ENGINE_PHASE_16T2F1"

REPORT_DIR = ROOT / "_leaf_artifacts" / "reports"

REF_RUNTIME_IMPORT = "RUNTIME_IMPORT"
REF_DYNAMIC_IMPORT = "DYNAMIC_IMPORT"
REF_SUBPROCESS_OR_SCRIPT = "SUBPROCESS_OR_SCRIPT"
REF_TEST = "TEST_REFERENCE"
REF_DOCUMENTATION = "DOCUMENTATION_REFERENCE"
REF_GENERATED_AUDIT_REPORT = "GENERATED_AUDIT_REPORT"
REF_STRING_MENTION = "STRING_MENTION"

BLOCKING_REFERENCE_TYPES = {
    REF_RUNTIME_IMPORT,
    REF_DYNAMIC_IMPORT,
    REF_SUBPROCESS_OR_SCRIPT,
}

TEXT_EXTENSIONS = {
    ".py", ".md", ".txt", ".sh", ".bash", ".zsh",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"
}

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    "_leaf_archive",
    "LEAF_UPLOAD",
}

GENERATED_REPORT_NAME_TOKENS = (
    "AUDIT",
    "REPORT",
    "CLEANUP",
    "INTELLIGENCE",
    "VERIFIED",
    "DEPENDENCY",
)

SCRIPT_HINTS = (
    "subprocess",
    "os.system",
    "python ",
    "python3 ",
    "bash ",
    "zsh ",
    "sh ",
)

DYNAMIC_IMPORT_HINTS = (
    "importlib.import_module",
    "__import__",
)


def _skip(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def _archive_candidates() -> list[str]:
    plan = build_safe_cleanup_plan(ROOT)
    return [
        item["path"]
        for item in plan.get("actions", [])
        if item.get("action") == ARCHIVE
    ]


def _tokens(candidate: str) -> set[str]:
    path = Path(candidate)
    return {
        path.as_posix(),
        path.name,
        path.stem,
        ".".join(path.with_suffix("").parts),
    }


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _iter_text_files() -> list[Path]:
    out: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if _skip(rel):
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS:
            out.append(path)
    return out


def _is_generated_report(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    name = path.name.upper()

    if "_leaf_artifacts" in rel.parts and "reports" in rel.parts:
        return True

    if path.suffix.lower() == ".txt" and any(token in name for token in GENERATED_REPORT_NAME_TOKENS):
        return True

    return False


def _is_test_file(path: Path) -> bool:
    return path.name.startswith("test_") or "/test_" in path.as_posix()


def _is_documentation(path: Path) -> bool:
    return path.suffix.lower() in {".md", ".txt"} and not _is_generated_report(path)


def _ast_import_hits(path: Path, candidate_stem: str) -> list[str]:
    if path.suffix.lower() != ".py":
        return []

    try:
        tree = ast.parse(_read(path))
    except Exception:
        return []

    hits: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] == candidate_stem:
                    hits.append(f"import {alias.name}")

        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] == candidate_stem:
                hits.append(f"from {node.module} import ...")

    return hits


def classify_reference(path: Path, text: str, candidate: str) -> tuple[str, list[str]]:
    candidate_stem = Path(candidate).stem
    candidate_tokens = sorted(token for token in _tokens(candidate) if token and token in text)
    ast_hits = _ast_import_hits(path, candidate_stem)

    if ast_hits:
        if _is_test_file(path):
            return REF_TEST, ast_hits
        return REF_RUNTIME_IMPORT, ast_hits

    if _is_generated_report(path):
        return REF_GENERATED_AUDIT_REPORT, candidate_tokens

    if _is_test_file(path):
        return REF_TEST, candidate_tokens

    if any(hint in text for hint in DYNAMIC_IMPORT_HINTS) and candidate_stem in text:
        return REF_DYNAMIC_IMPORT, candidate_tokens

    if any(hint in text for hint in SCRIPT_HINTS) and (Path(candidate).name in text or candidate_stem in text):
        return REF_SUBPROCESS_OR_SCRIPT, candidate_tokens

    if _is_documentation(path):
        return REF_DOCUMENTATION, candidate_tokens

    return REF_STRING_MENTION, candidate_tokens


def build_reference_classification_audit() -> dict[str, Any]:
    candidates = _archive_candidates()
    references: dict[str, list[dict[str, Any]]] = {candidate: [] for candidate in candidates}

    files = _iter_text_files()

    for file_path in files:
        text = _read(file_path)
        rel = file_path.relative_to(ROOT).as_posix()

        for candidate in candidates:
            candidate_tokens = _tokens(candidate)
            if not any(token and token in text for token in candidate_tokens):
                continue

            ref_type, evidence = classify_reference(file_path, text, candidate)

            references[candidate].append(
                {
                    "referenced_by": rel,
                    "reference_type": ref_type,
                    "blocking": ref_type in BLOCKING_REFERENCE_TYPES,
                    "evidence": evidence[:8],
                }
            )

    blocking_candidates: dict[str, list[dict[str, Any]]] = {}
    nonblocking_only_candidates: dict[str, list[dict[str, Any]]] = {}
    unreferenced_candidates: list[str] = []

    type_counts: dict[str, int] = {
        REF_RUNTIME_IMPORT: 0,
        REF_DYNAMIC_IMPORT: 0,
        REF_SUBPROCESS_OR_SCRIPT: 0,
        REF_TEST: 0,
        REF_DOCUMENTATION: 0,
        REF_GENERATED_AUDIT_REPORT: 0,
        REF_STRING_MENTION: 0,
    }

    for candidate, refs in references.items():
        if not refs:
            unreferenced_candidates.append(candidate)
            continue

        for ref in refs:
            type_counts[ref["reference_type"]] = type_counts.get(ref["reference_type"], 0) + 1

        blocking_refs = [ref for ref in refs if ref["blocking"]]
        if blocking_refs:
            blocking_candidates[candidate] = blocking_refs
        else:
            nonblocking_only_candidates[candidate] = refs

    warnings = []
    blockers = []

    if blocking_candidates:
        warnings.append(f"{len(blocking_candidates)} archive candidates have blocking operational references.")

    status = FAIL_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not blockers,
        "candidate_count": len(candidates),
        "blocking_candidate_count": len(blocking_candidates),
        "nonblocking_only_candidate_count": len(nonblocking_only_candidates),
        "unreferenced_candidate_count": len(unreferenced_candidates),
        "blocking_candidates": blocking_candidates,
        "nonblocking_only_candidates": nonblocking_only_candidates,
        "unreferenced_candidates": unreferenced_candidates,
        "reference_type_counts": type_counts,
        "warnings": warnings,
        "blockers": blockers,
        "summary": (
            f"{len(candidates)} archive candidates classified; "
            f"{len(blocking_candidates)} blocking; "
            f"{len(nonblocking_only_candidates)} nonblocking-only; "
            f"{len(unreferenced_candidates)} unreferenced."
        ),
    }


def build_reference_classification_report() -> str:
    audit = build_reference_classification_audit()

    lines = [
        "REFERENCE CLASSIFICATION ENGINE",
        "===============================",
        f"Phase: {audit['phase']}",
        f"Status: {audit['status']}",
        f"Passed: {audit['passed']}",
        f"Summary: {audit['summary']}",
        "",
        "COUNTS",
        "------",
        f"Archive candidates: {audit['candidate_count']}",
        f"Blocking candidates: {audit['blocking_candidate_count']}",
        f"Nonblocking-only candidates: {audit['nonblocking_only_candidate_count']}",
        f"Unreferenced candidates: {audit['unreferenced_candidate_count']}",
        "",
        "REFERENCE TYPE COUNTS",
        "---------------------",
    ]

    for key, value in audit["reference_type_counts"].items():
        lines.append(f"{key}: {value}")

    if audit["blocking_candidates"]:
        lines.extend(["", "BLOCKING OPERATIONAL REFERENCES", "-------------------------------"])
        for candidate, refs in audit["blocking_candidates"].items():
            lines.append(f"- {candidate}")
            for ref in refs[:10]:
                evidence = ", ".join(ref["evidence"]) if ref["evidence"] else "no evidence payload"
                lines.append(f"    {ref['reference_type']} by {ref['referenced_by']} :: {evidence}")

    if audit["nonblocking_only_candidates"]:
        lines.extend(["", "NONBLOCKING-ONLY CANDIDATES", "---------------------------"])
        for candidate, refs in audit["nonblocking_only_candidates"].items():
            types = sorted({ref["reference_type"] for ref in refs})
            lines.append(f"- {candidate} :: {', '.join(types)}")

    if audit["unreferenced_candidates"]:
        lines.extend(["", "UNREFERENCED CANDIDATES", "-----------------------"])
        for candidate in audit["unreferenced_candidates"]:
            lines.append(f"- {candidate}")

    if audit["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in audit["warnings"])

    if audit["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in audit["blockers"])

    lines.extend([
        "",
        "SAFETY RULE",
        "-----------",
        "Generated reports and plain filename mentions do not block archival. Runtime imports, dynamic imports, and subprocess/script calls do block archival.",
    ])

    return "\n".join(lines)


def write_reference_classification_report() -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output = REPORT_DIR / "REFERENCE_CLASSIFICATION_ENGINE_PHASE_16T2F1.txt"
    output.write_text(build_reference_classification_report(), encoding="utf-8")
    return output


if __name__ == "__main__":
    output = write_reference_classification_report()
    audit = build_reference_classification_audit()
    print(audit["status"])
    print(output)
