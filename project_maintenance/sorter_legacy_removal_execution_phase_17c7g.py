from __future__ import annotations

import json
import py_compile
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REMOVAL_PROOF = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c7f" / "sorter_legacy_removal_proof_phase_17c7f.json"

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c7g"
ARCHIVE_DIR = ROOT / "_leaf_archive" / "repository_architecture" / "sorter_legacy_retirement" / "phase_17c7g"
OUT_TXT = OUT_DIR / "sorter_legacy_removal_execution_phase_17c7g.txt"
OUT_JSON = OUT_DIR / "sorter_legacy_removal_execution_phase_17c7g.json"
ARCHIVE_MANIFEST = OUT_DIR / "sorter_legacy_removal_archive_manifest_phase_17c7g.json"

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


def restore_from_archive(archive_records: list[dict]) -> list[str]:
    errors = []

    for record in archive_records:
        source = ROOT / record["original_path"]
        archived = ROOT / record["archived_path"]

        try:
            if not source.exists() and archived.exists():
                source.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(archived, source)
        except Exception as exc:
            errors.append(f"restore_failed:{record['original_path']}:{exc!r}")

    return errors


def execute_removal() -> dict:
    proof = load_json(REMOVAL_PROOF)
    removal_proofs = proof.get("removal_proofs", [])

    safe_candidates = [
        item for item in removal_proofs
        if item.get("removal_safe_later") is True
    ]

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    archive_records = []
    missing_targets = []
    archive_failures = []
    removal_failures = []

    if proof.get("passed") is not True:
        return {
            "phase": "17C.7G",
            "name": "Sorter Legacy Removal Execution",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "passed": False,
            "rolled_back": False,
            "rollback_errors": [],
            "counts": {
                "safe_candidates": len(safe_candidates),
                "archived_files": 0,
                "removed_files": 0,
                "missing_targets": 0,
                "archive_failures": 0,
                "removal_failures": 0,
                "compile_failures": 0,
                "hard_blockers": 1,
            },
            "execution_statement": "Removal proof did not pass. Execution refused.",
            "next_phase": "17C.7H_SORTER_LEGACY_REMOVAL_VALIDATION",
        }

    for item in safe_candidates:
        source = ROOT / item["path"]

        if not source.exists():
            missing_targets.append(item)
            continue

        archive_name = item["path"].replace("/", "__").replace("\\", "__")
        archived = ARCHIVE_DIR / archive_name

        try:
            shutil.copy2(source, archived)
            archive_records.append(
                {
                    "original_path": item["path"],
                    "archived_path": str(archived.relative_to(ROOT)),
                    "backup_path": item.get("backup"),
                    "reason": "removed_from_active_tree_after_replacement_proof",
                }
            )
        except Exception as exc:
            archive_failures.append({"path": item["path"], "error": repr(exc)})

    if missing_targets or archive_failures:
        hard_blockers = len(missing_targets) + len(archive_failures)
        return {
            "phase": "17C.7G",
            "name": "Sorter Legacy Removal Execution",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "passed": False,
            "rolled_back": False,
            "rollback_errors": [],
            "archive_records": archive_records,
            "missing_targets": missing_targets,
            "archive_failures": archive_failures,
            "removal_failures": [],
            "compile_failures": [],
            "counts": {
                "safe_candidates": len(safe_candidates),
                "archived_files": len(archive_records),
                "removed_files": 0,
                "missing_targets": len(missing_targets),
                "archive_failures": len(archive_failures),
                "removal_failures": 0,
                "compile_failures": 0,
                "hard_blockers": hard_blockers,
            },
            "execution_statement": "Removal refused because archive coverage was incomplete.",
            "next_phase": "17C.7H_SORTER_LEGACY_REMOVAL_VALIDATION",
        }

    removed_files = []

    for record in archive_records:
        source = ROOT / record["original_path"]

        try:
            source.unlink()
            removed_files.append(record["original_path"])
        except Exception as exc:
            removal_failures.append({"path": record["original_path"], "error": repr(exc)})

    compile_failures = compile_active_python()

    if removal_failures or compile_failures:
        rollback_errors = restore_from_archive(archive_records)
        hard_blockers = len(removal_failures) + len(compile_failures) + len(rollback_errors)

        return {
            "phase": "17C.7G",
            "name": "Sorter Legacy Removal Execution",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "passed": False,
            "rolled_back": True,
            "rollback_errors": rollback_errors,
            "archive_records": archive_records,
            "removed_files": removed_files,
            "missing_targets": missing_targets,
            "archive_failures": archive_failures,
            "removal_failures": removal_failures,
            "compile_failures": compile_failures,
            "counts": {
                "safe_candidates": len(safe_candidates),
                "archived_files": len(archive_records),
                "removed_files": len(removed_files),
                "missing_targets": len(missing_targets),
                "archive_failures": len(archive_failures),
                "removal_failures": len(removal_failures),
                "compile_failures": len(compile_failures),
                "hard_blockers": hard_blockers,
            },
            "execution_statement": "Removal produced blockers. Active files were restored from archive where possible.",
            "next_phase": "17C.7H_SORTER_LEGACY_REMOVAL_VALIDATION",
        }

    archive_manifest = {
        "phase": "17C.7G",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "archive_records": archive_records,
        "removed_files": removed_files,
        "passed": True,
    }
    ARCHIVE_MANIFEST.write_text(json.dumps(archive_manifest, indent=2), encoding="utf-8")

    return {
        "phase": "17C.7G",
        "name": "Sorter Legacy Removal Execution",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "removal_proof": str(REMOVAL_PROOF.relative_to(ROOT)),
        },
        "outputs": {
            "archive_manifest": str(ARCHIVE_MANIFEST.relative_to(ROOT)),
            "archive_dir": str(ARCHIVE_DIR.relative_to(ROOT)),
        },
        "policy": {
            "moves_files": False,
            "deletes_files": True,
            "archives_before_removal": True,
            "removes_from_active_tree": True,
            "rolls_back_on_compile_failure": True,
            "requires_removal_proof_pass": True,
            "requires_archive_copy_before_unlink": True,
            "requires_compile_health_after_removal": True,
        },
        "archive_records": archive_records,
        "removed_files": removed_files,
        "missing_targets": missing_targets,
        "archive_failures": archive_failures,
        "removal_failures": removal_failures,
        "compile_failures": compile_failures,
        "rolled_back": False,
        "rollback_errors": [],
        "counts": {
            "safe_candidates": len(safe_candidates),
            "archived_files": len(archive_records),
            "removed_files": len(removed_files),
            "missing_targets": len(missing_targets),
            "archive_failures": len(archive_failures),
            "removal_failures": len(removal_failures),
            "compile_failures": len(compile_failures),
            "hard_blockers": 0,
        },
        "execution_statement": (
            "Sorter legacy removal execution passed. Proven-safe legacy files were archived, removed from the active tree, and active Python compilation remained clean."
        ),
        "next_phase": "17C.7H_SORTER_LEGACY_REMOVAL_VALIDATION",
        "passed": True,
    }


def write_report(result: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 17C.7G",
        "SORTER LEGACY REMOVAL EXECUTION",
        "=" * 42,
        "",
        "COUNTS",
        "------",
    ]

    for key, value in result["counts"].items():
        lines.append(f"{key}={value}")

    lines += ["", "REMOVED FILES", "-------------"]

    if result.get("removed_files"):
        for item in result["removed_files"]:
            lines.append(item)
    else:
        lines.append("none")

    lines += ["", "ARCHIVE RECORDS", "---------------"]

    if result.get("archive_records"):
        for item in result["archive_records"]:
            lines.append(f"{item['original_path']} -> {item['archived_path']}")
    else:
        lines.append("none")

    lines += [
        "",
        "ROLLBACK",
        "--------",
        f"rolled_back={result.get('rolled_back')}",
        f"rollback_errors={len(result.get('rollback_errors', []))}",
        "",
        "EXECUTION STATEMENT",
        "-------------------",
        result["execution_statement"],
        "",
        "RESULT",
        "------",
        "PASS_PHASE_17C7G_SORTER_LEGACY_REMOVAL_EXECUTION" if result["passed"] else "FAIL_PHASE_17C7G_SORTER_LEGACY_REMOVAL_EXECUTION",
        "",
        f"report={OUT_TXT.relative_to(ROOT)}",
        f"json={OUT_JSON.relative_to(ROOT)}",
        "",
        f"next_phase={result['next_phase']}",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = execute_removal()
    write_report(result)

    print("PASS_PHASE_17C7G_SORTER_LEGACY_REMOVAL_EXECUTION" if result["passed"] else "FAIL_PHASE_17C7G_SORTER_LEGACY_REMOVAL_EXECUTION")
    print(f"safe_candidates={result['counts']['safe_candidates']}")
    print(f"archived_files={result['counts']['archived_files']}")
    print(f"removed_files={result['counts']['removed_files']}")
    print(f"missing_targets={result['counts']['missing_targets']}")
    print(f"archive_failures={result['counts']['archive_failures']}")
    print(f"removal_failures={result['counts']['removal_failures']}")
    print(f"compile_failures={result['counts']['compile_failures']}")
    print(f"rolled_back={result.get('rolled_back')}")
    print(f"rollback_errors={len(result.get('rollback_errors', []))}")
    print(f"hard_blockers={result['counts']['hard_blockers']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
