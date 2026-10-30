from __future__ import annotations

import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXECUTION = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c7g" / "sorter_legacy_removal_execution_phase_17c7g.json"
ARCHIVE_MANIFEST = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c7g" / "sorter_legacy_removal_archive_manifest_phase_17c7g.json"

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c7h"
OUT_TXT = OUT_DIR / "sorter_legacy_removal_validation_phase_17c7h.txt"
OUT_JSON = OUT_DIR / "sorter_legacy_removal_validation_phase_17c7h.json"

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "_leaf_artifacts",
    "_leaf_archive",
    "_external_repository_quarantine",
    "build",
    "dist",
}


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing required input: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def active_python_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*.py"):
        if set(path.relative_to(ROOT).parts) & EXCLUDED_DIRS:
            continue
        files.append(path)
    return sorted(files)


def compile_active_python() -> list[dict[str, str]]:
    failures = []
    for path in active_python_files():
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            failures.append({"path": str(path.relative_to(ROOT)), "error": repr(exc)})
    return failures


def module_name_from_path(path_text: str) -> str:
    return path_text[:-3].replace("/", ".").replace("\\", ".")


def scan_references(target_path: str) -> list[dict[str, str]]:
    module = module_name_from_path(target_path)
    tail = module.split(".")[-1]

    needles = [
        f"import {module}",
        f"from {module} import",
        f"import {tail}",
        f"from .{tail} import",
    ]

    hits = []

    for path in active_python_files():
        rel = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8", errors="replace")

        for needle in needles:
            if needle in text:
                hits.append({"file": rel, "reference": needle})

    return hits


def build_validation() -> dict:
    execution = load_json(EXECUTION)
    manifest = load_json(ARCHIVE_MANIFEST)

    archive_records = manifest.get("archive_records", [])
    removed_files = execution.get("removed_files", [])

    active_still_present = []
    archive_missing = []
    reference_blockers = []

    for record in archive_records:
        original = ROOT / record["original_path"]
        archived = ROOT / record["archived_path"]

        if original.exists():
            active_still_present.append(record)

        if not archived.exists():
            archive_missing.append(record)

        refs = scan_references(record["original_path"])
        if refs:
            reference_blockers.append(
                {
                    "original_path": record["original_path"],
                    "references": refs,
                }
            )

    compile_failures = compile_active_python()

    hard_blockers = (
        len(active_still_present)
        + len(archive_missing)
        + len(reference_blockers)
        + len(compile_failures)
    )

    passed = (
        execution.get("passed") is True
        and execution.get("rolled_back") is False
        and manifest.get("passed") is True
        and len(archive_records) == 3
        and len(removed_files) == 3
        and hard_blockers == 0
    )

    return {
        "phase": "17C.7H",
        "name": "Sorter Legacy Removal Validation",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "execution": str(EXECUTION.relative_to(ROOT)),
            "archive_manifest": str(ARCHIVE_MANIFEST.relative_to(ROOT)),
        },
        "policy": {
            "moves_files": False,
            "deletes_files": False,
            "rewrites_imports": False,
            "validation_only": True,
            "requires_execution_pass": True,
            "requires_no_rollback": True,
            "requires_active_files_absent": True,
            "requires_archive_files_present": True,
            "requires_no_active_references": True,
            "requires_compile_health": True,
            "authorises_next_phase": "17C.7I_SORTER_LEGACY_REMOVAL_CLOSEOUT",
        },
        "counts": {
            "archive_records": len(archive_records),
            "removed_files": len(removed_files),
            "active_still_present": len(active_still_present),
            "archive_missing": len(archive_missing),
            "reference_blockers": len(reference_blockers),
            "compile_failures": len(compile_failures),
            "hard_blockers": hard_blockers,
        },
        "archive_records": archive_records,
        "removed_files": removed_files,
        "active_still_present": active_still_present,
        "archive_missing": archive_missing,
        "reference_blockers": reference_blockers,
        "compile_failures": compile_failures,
        "validation_statement": (
            "Sorter legacy removal validation passed. Removed files are absent from active locations, present in archive, unreferenced, and compilation is clean."
            if passed
            else
            "Sorter legacy removal validation failed. Resolve blockers before closeout."
        ),
        "next_phase": "17C.7I_SORTER_LEGACY_REMOVAL_CLOSEOUT",
        "passed": passed,
    }


def write_report(result: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 17C.7H",
        "SORTER LEGACY REMOVAL VALIDATION",
        "=" * 43,
        "",
        "COUNTS",
        "------",
    ]

    for key, value in result["counts"].items():
        lines.append(f"{key}={value}")

    lines += ["", "REMOVED FILES", "-------------"]

    for item in result["removed_files"]:
        lines.append(item)

    lines += ["", "ARCHIVE RECORDS", "---------------"]

    for record in result["archive_records"]:
        lines.append(f"{record['original_path']} -> {record['archived_path']}")

    lines += [
        "",
        "VALIDATION STATEMENT",
        "--------------------",
        result["validation_statement"],
        "",
        "RESULT",
        "------",
        "PASS_PHASE_17C7H_SORTER_LEGACY_REMOVAL_VALIDATION" if result["passed"] else "FAIL_PHASE_17C7H_SORTER_LEGACY_REMOVAL_VALIDATION",
        "",
        f"report={OUT_TXT.relative_to(ROOT)}",
        f"json={OUT_JSON.relative_to(ROOT)}",
        "",
        f"next_phase={result['next_phase']}",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = build_validation()
    write_report(result)

    print("PASS_PHASE_17C7H_SORTER_LEGACY_REMOVAL_VALIDATION" if result["passed"] else "FAIL_PHASE_17C7H_SORTER_LEGACY_REMOVAL_VALIDATION")
    print(f"archive_records={result['counts']['archive_records']}")
    print(f"removed_files={result['counts']['removed_files']}")
    print(f"active_still_present={result['counts']['active_still_present']}")
    print(f"archive_missing={result['counts']['archive_missing']}")
    print(f"reference_blockers={result['counts']['reference_blockers']}")
    print(f"compile_failures={result['counts']['compile_failures']}")
    print(f"hard_blockers={result['counts']['hard_blockers']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
