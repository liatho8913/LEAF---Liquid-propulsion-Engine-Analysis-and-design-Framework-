from __future__ import annotations

import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

EXECUTION = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6l" / "leaf_qt_second_batch_execution_phase_17c6l.json"
READINESS = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6k" / "leaf_qt_second_batch_readiness_phase_17c6k.json"
VALIDATION = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6m" / "leaf_qt_second_batch_post_execution_validation_phase_17c6m.json"
ROLLBACK = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6k" / "leaf_qt_second_batch_rollback_manifest_phase_17c6k.json"

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6n"
OUT_TXT = OUT_DIR / "leaf_qt_second_batch_closeout_certificate_phase_17c6n.txt"
OUT_JSON = OUT_DIR / "leaf_qt_second_batch_closeout_certificate_phase_17c6n.json"

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


def build_closeout() -> dict[str, Any]:
    execution = load_json(EXECUTION)
    readiness = load_json(READINESS)
    validation = load_json(VALIDATION)
    rollback = load_json(ROLLBACK)

    executed_moves = execution.get("executed_moves", [])
    rollback_snapshots = rollback.get("snapshots", {})
    modified_import_files = execution.get("modified_import_files", [])
    import_rewrites = execution.get("import_rewrites", [])

    destination_missing = []
    source_still_present = []
    rollback_snapshot_missing = []

    for move in executed_moves:
        src = ROOT / move["from"]
        dst = ROOT / move["to"]

        if src.exists():
            source_still_present.append(move)

        if not dst.exists():
            destination_missing.append(move)

    for original, snapshot in rollback_snapshots.items():
        if not (ROOT / snapshot).exists():
            rollback_snapshot_missing.append(
                {
                    "original": original,
                    "snapshot": snapshot,
                }
            )

    compile_failures = compile_active_python()

    hard_blockers = (
        len(destination_missing)
        + len(source_still_present)
        + len(rollback_snapshot_missing)
        + len(compile_failures)
    )

    passed = (
        readiness.get("passed") is True
        and execution.get("passed") is True
        and execution.get("rolled_back") is False
        and validation.get("passed") is True
        and len(executed_moves) == 25
        and len(rollback_snapshots) == 25
        and hard_blockers == 0
    )

    return {
        "phase": "17C.6N",
        "name": "leaf_qt Second Batch Closeout Certificate",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "readiness": str(READINESS.relative_to(ROOT)),
            "execution": str(EXECUTION.relative_to(ROOT)),
            "validation": str(VALIDATION.relative_to(ROOT)),
            "rollback": str(ROLLBACK.relative_to(ROOT)),
        },
        "policy": {
            "moves_files": False,
            "deletes_files": False,
            "rewrites_imports": False,
            "closeout_only": True,
            "requires_readiness_pass": True,
            "requires_execution_pass": True,
            "requires_validation_pass": True,
            "requires_no_rollback": True,
            "requires_rollback_manifest": True,
            "requires_compile_health": True,
            "authorises_next_phase": "17C.6O_THIRD_BATCH_SELECTION_OR_UNIVERSAL_SORTER_FOUNDATION",
        },
        "counts": {
            "executed_moves": len(executed_moves),
            "modified_import_files": len(modified_import_files),
            "import_rewrites": len(import_rewrites),
            "rollback_snapshots": len(rollback_snapshots),
            "destination_missing": len(destination_missing),
            "source_still_present": len(source_still_present),
            "rollback_snapshot_missing": len(rollback_snapshot_missing),
            "compile_failures": len(compile_failures),
            "hard_blockers": hard_blockers,
        },
        "certified_moves": executed_moves,
        "modified_import_files": modified_import_files,
        "import_rewrites": import_rewrites,
        "destination_missing": destination_missing,
        "source_still_present": source_still_present,
        "rollback_snapshot_missing": rollback_snapshot_missing,
        "compile_failures": compile_failures,
        "closeout_statement": (
            "Second controlled leaf_qt movement batch is certified complete. "
            "Readiness, execution, rollback coverage, post-execution validation, and active Python compilation are clean. "
            "The repository is authorised to proceed to the next controlled structural step."
            if passed
            else
            "Second controlled leaf_qt movement batch is not certified. Resolve blockers before any further movement selection."
        ),
        "next_phase": "17C.6O_THIRD_BATCH_SELECTION_OR_UNIVERSAL_SORTER_FOUNDATION",
        "passed": passed,
    }


def write_report(result: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 17C.6N",
        "LEAF_QT SECOND BATCH CLOSEOUT CERTIFICATE",
        "=" * 51,
        "",
        "INPUTS",
        "------",
    ]

    for key, value in result["inputs"].items():
        lines.append(f"{key}={value}")

    lines += ["", "POLICY", "------"]

    for key, value in result["policy"].items():
        lines.append(f"{key}={value}")

    lines += ["", "COUNTS", "------"]

    for key, value in result["counts"].items():
        lines.append(f"{key}={value}")

    lines += ["", "CERTIFIED MOVES", "---------------"]

    for move in result["certified_moves"]:
        lines.append(f"{move['move_id']} :: {move['from']} -> {move['to']}")

    lines += ["", "BLOCKERS", "--------"]

    blocker_sections = [
        ("destination_missing", result["destination_missing"]),
        ("source_still_present", result["source_still_present"]),
        ("rollback_snapshot_missing", result["rollback_snapshot_missing"]),
        ("compile_failures", result["compile_failures"]),
    ]

    any_blockers = False
    for name, items in blocker_sections:
        if items:
            any_blockers = True
            lines.append(name)
            for item in items[:100]:
                lines.append(f"  {item}")

    if not any_blockers:
        lines.append("none")

    lines += [
        "",
        "CLOSEOUT STATEMENT",
        "------------------",
        result["closeout_statement"],
        "",
        "RESULT",
        "------",
        "PASS_PHASE_17C6N_LEAF_QT_SECOND_BATCH_CLOSEOUT_CERTIFICATE" if result["passed"] else "FAIL_PHASE_17C6N_LEAF_QT_SECOND_BATCH_CLOSEOUT_CERTIFICATE",
        "",
        f"report={OUT_TXT.relative_to(ROOT)}",
        f"json={OUT_JSON.relative_to(ROOT)}",
        "",
        f"next_phase={result['next_phase']}",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = build_closeout()
    write_report(result)

    print("PASS_PHASE_17C6N_LEAF_QT_SECOND_BATCH_CLOSEOUT_CERTIFICATE" if result["passed"] else "FAIL_PHASE_17C6N_LEAF_QT_SECOND_BATCH_CLOSEOUT_CERTIFICATE")
    print(f"executed_moves={result['counts']['executed_moves']}")
    print(f"modified_import_files={result['counts']['modified_import_files']}")
    print(f"import_rewrites={result['counts']['import_rewrites']}")
    print(f"rollback_snapshots={result['counts']['rollback_snapshots']}")
    print(f"destination_missing={result['counts']['destination_missing']}")
    print(f"source_still_present={result['counts']['source_still_present']}")
    print(f"rollback_snapshot_missing={result['counts']['rollback_snapshot_missing']}")
    print(f"compile_failures={result['counts']['compile_failures']}")
    print(f"hard_blockers={result['counts']['hard_blockers']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
