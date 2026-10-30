from __future__ import annotations

import json
import py_compile
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

READINESS = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6k" / "leaf_qt_second_batch_readiness_phase_17c6k.json"
ROLLBACK_MANIFEST = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6k" / "leaf_qt_second_batch_rollback_manifest_phase_17c6k.json"

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6l"
OUT_TXT = OUT_DIR / "leaf_qt_second_batch_execution_phase_17c6l.txt"
OUT_JSON = OUT_DIR / "leaf_qt_second_batch_execution_phase_17c6l.json"

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


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required input: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def active_python_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.py"):
        rel_parts = set(path.relative_to(ROOT).parts)
        if rel_parts & EXCLUDED_DIRS:
            continue
        files.append(path)
    return sorted(files)


def compile_active_python() -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for path in active_python_files():
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            failures.append({"path": str(path.relative_to(ROOT)), "error": repr(exc)})
    return failures


def module_name_from_path(path_text: str) -> str:
    return path_text[:-3].replace("/", ".").replace("\\", ".")


def rollback(executed_moves: list[dict[str, Any]], modified_files: dict[str, str], rollback_manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for rel_path, original_text in modified_files.items():
        try:
            (ROOT / rel_path).write_text(original_text, encoding="utf-8")
        except Exception as exc:
            errors.append(f"restore_import_file_failed:{rel_path}:{exc!r}")

    for move in reversed(executed_moves):
        src = ROOT / move["from"]
        dst = ROOT / move["to"]
        snapshot_rel = rollback_manifest.get("snapshots", {}).get(move["from"])
        snapshot = ROOT / snapshot_rel if snapshot_rel else None

        try:
            if dst.exists():
                dst.unlink()
            if snapshot and snapshot.exists():
                src.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(snapshot, src)
        except Exception as exc:
            errors.append(f"restore_move_failed:{move['from']}:{move['to']}:{exc!r}")

    return errors


def execute_second_batch() -> dict[str, Any]:
    readiness = load_json(READINESS)
    rollback_manifest = load_json(ROLLBACK_MANIFEST)

    approved_moves = readiness.get("approved_moves", [])

    source_missing = []
    destination_exists = []
    executed_moves: list[dict[str, Any]] = []
    modified_import_files: list[dict[str, Any]] = []
    modified_file_originals: dict[str, str] = {}
    import_rewrites: list[dict[str, str]] = []

    if readiness.get("passed") is not True:
        return {
            "phase": "17C.6L",
            "name": "leaf_qt Second Batch Execution",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "passed": False,
            "rolled_back": False,
            "rollback_errors": [],
            "counts": {
                "approved_moves": len(approved_moves),
                "executed_moves": 0,
                "modified_import_files": 0,
                "import_rewrites": 0,
                "source_missing": 0,
                "destination_exists": 0,
                "compile_failures": 0,
                "hard_blockers": 1,
            },
            "execution_statement": "Readiness did not pass. Execution refused.",
            "next_phase": "17C.6M_LEAF_QT_SECOND_BATCH_POST_EXECUTION_VALIDATION",
        }

    already_moved: list[dict[str, Any]] = []

    for move in approved_moves:
        src = ROOT / move["from"]
        dst = ROOT / move["to"]

        if src.exists() and dst.exists():
            destination_exists.append(move)
        elif not src.exists() and dst.exists():
            already_moved.append(move)
        elif not src.exists() and not dst.exists():
            source_missing.append(move)

    if source_missing or destination_exists:
        return {
            "phase": "17C.6L",
            "name": "leaf_qt Second Batch Execution",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "passed": False,
            "rolled_back": False,
            "rollback_errors": [],
            "source_missing": source_missing,
            "destination_exists": destination_exists,
            "already_moved": already_moved,
            "counts": {
                "approved_moves": len(approved_moves),
                "executed_moves": len(already_moved),
                "modified_import_files": 0,
                "import_rewrites": 0,
                "source_missing": len(source_missing),
                "destination_exists": len(destination_exists),
                "compile_failures": 0,
                "hard_blockers": len(source_missing) + len(destination_exists),
            },
            "execution_statement": "Execution refused because sources/destinations are in an unsafe mixed state.",
            "next_phase": "17C.6M_LEAF_QT_SECOND_BATCH_POST_EXECUTION_VALIDATION",
        }

    old_to_new_modules = {
        module_name_from_path(move["from"]): module_name_from_path(move["to"])
        for move in approved_moves
    }

    try:
        for move in approved_moves:
            src = ROOT / move["from"]
            dst = ROOT / move["to"]

            if dst.exists() and not src.exists():
                executed_moves.append(move)
                continue

            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            executed_moves.append(move)

        for file_path in active_python_files():
            rel = str(file_path.relative_to(ROOT))
            text = file_path.read_text(encoding="utf-8", errors="replace")
            original = text

            for old_module, new_module in old_to_new_modules.items():
                replacements = [
                    (f"from {old_module} import", f"from {new_module} import"),
                    (f"import {old_module}", f"import {new_module}"),
                ]

                old_tail = old_module.split(".")[-1]
                new_tail = new_module.split(".")[-1]

                if file_path.parent == (ROOT / "/".join(new_module.split(".")[:-1])):
                    replacements.append((f"from .{old_tail} import", f"from .{new_tail} import"))

                for before, after in replacements:
                    if before in text:
                        text = text.replace(before, after)
                        import_rewrites.append({"file": rel, "from": before, "to": after})

            if text != original:
                modified_file_originals[rel] = original
                file_path.write_text(text, encoding="utf-8")
                modified_import_files.append({"path": rel})

        compile_failures = compile_active_python()

        if compile_failures:
            rollback_errors = rollback(executed_moves, modified_file_originals, rollback_manifest)
            return {
                "phase": "17C.6L",
                "name": "leaf_qt Second Batch Execution",
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "inputs": {
                    "readiness": str(READINESS.relative_to(ROOT)),
                    "rollback_manifest": str(ROLLBACK_MANIFEST.relative_to(ROOT)),
                },
                "approved_moves": approved_moves,
                "executed_moves": executed_moves,
                "modified_import_files": modified_import_files,
                "import_rewrites": import_rewrites,
                "compile_failures": compile_failures,
                "rolled_back": True,
                "rollback_errors": rollback_errors,
                "counts": {
                    "approved_moves": len(approved_moves),
                    "executed_moves": len(executed_moves),
                    "modified_import_files": len(modified_import_files),
                    "import_rewrites": len(import_rewrites),
                    "source_missing": 0,
                    "destination_exists": 0,
                    "compile_failures": len(compile_failures),
                    "hard_blockers": len(compile_failures) + len(rollback_errors),
                },
                "passed": False,
                "execution_statement": "Execution produced compile failures. Rollback was triggered.",
                "next_phase": "17C.6M_LEAF_QT_SECOND_BATCH_POST_EXECUTION_VALIDATION",
            }

        return {
            "phase": "17C.6L",
            "name": "leaf_qt Second Batch Execution",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "inputs": {
                "readiness": str(READINESS.relative_to(ROOT)),
                "rollback_manifest": str(ROLLBACK_MANIFEST.relative_to(ROOT)),
            },
            "policy": {
                "moves_files": True,
                "deletes_files": False,
                "rewrites_imports": True,
                "requires_readiness_pass": True,
                "uses_rollback_manifest": True,
                "rolls_back_on_compile_failure": True,
                "requires_compile_health_after_execution": True,
            },
            "approved_moves": approved_moves,
            "executed_moves": executed_moves,
            "modified_import_files": modified_import_files,
            "import_rewrites": import_rewrites,
            "compile_failures": compile_failures,
            "rolled_back": False,
            "rollback_errors": [],
            "counts": {
                "approved_moves": len(approved_moves),
                "executed_moves": len(executed_moves),
                "modified_import_files": len(modified_import_files),
                "import_rewrites": len(import_rewrites),
                "source_missing": 0,
                "destination_exists": 0,
                "compile_failures": len(compile_failures),
                "hard_blockers": 0,
            },
            "passed": True,
            "execution_statement": "Second controlled movement batch executed successfully. Files were moved, imports were rewritten, compilation remained clean, and rollback was not required.",
            "next_phase": "17C.6M_LEAF_QT_SECOND_BATCH_POST_EXECUTION_VALIDATION",
        }

    except Exception as exc:
        rollback_errors = rollback(executed_moves, modified_file_originals, rollback_manifest)
        return {
            "phase": "17C.6L",
            "name": "leaf_qt Second Batch Execution",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "approved_moves": approved_moves,
            "executed_moves": executed_moves,
            "modified_import_files": modified_import_files,
            "import_rewrites": import_rewrites,
            "rolled_back": True,
            "rollback_errors": rollback_errors,
            "counts": {
                "approved_moves": len(approved_moves),
                "executed_moves": len(executed_moves),
                "modified_import_files": len(modified_import_files),
                "import_rewrites": len(import_rewrites),
                "source_missing": 0,
                "destination_exists": 0,
                "compile_failures": 0,
                "hard_blockers": 1 + len(rollback_errors),
            },
            "passed": False,
            "execution_statement": f"Execution failed and rollback was triggered: {exc!r}",
            "next_phase": "17C.6M_LEAF_QT_SECOND_BATCH_POST_EXECUTION_VALIDATION",
        }


def write_report(result: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 17C.6L",
        "LEAF_QT SECOND BATCH EXECUTION",
        "=" * 41,
        "",
        "COUNTS",
        "------",
    ]

    for key, value in result["counts"].items():
        lines.append(f"{key}={value}")

    lines += ["", "EXECUTED MOVES", "--------------"]

    for move in result.get("executed_moves", []):
        lines.append(f"{move['move_id']} :: {move['from']} -> {move['to']}")

    lines += ["", "MODIFIED IMPORT FILES", "---------------------"]

    if result.get("modified_import_files"):
        for item in result["modified_import_files"]:
            lines.append(item["path"])
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
        "PASS_PHASE_17C6L_LEAF_QT_SECOND_BATCH_EXECUTION" if result["passed"] else "FAIL_PHASE_17C6L_LEAF_QT_SECOND_BATCH_EXECUTION",
        "",
        f"report={OUT_TXT.relative_to(ROOT)}",
        f"json={OUT_JSON.relative_to(ROOT)}",
        "",
        f"next_phase={result['next_phase']}",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = execute_second_batch()
    write_report(result)

    print("PASS_PHASE_17C6L_LEAF_QT_SECOND_BATCH_EXECUTION" if result["passed"] else "FAIL_PHASE_17C6L_LEAF_QT_SECOND_BATCH_EXECUTION")
    print(f"approved_moves={result['counts']['approved_moves']}")
    print(f"executed_moves={result['counts']['executed_moves']}")
    print(f"modified_import_files={result['counts']['modified_import_files']}")
    print(f"import_rewrites={result['counts']['import_rewrites']}")
    print(f"source_missing={result['counts']['source_missing']}")
    print(f"destination_exists={result['counts']['destination_exists']}")
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
