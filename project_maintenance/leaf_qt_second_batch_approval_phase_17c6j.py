from __future__ import annotations

import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SELECTION = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6i" / "leaf_qt_second_batch_selection_phase_17c6i.json"

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6j"
OUT_TXT = OUT_DIR / "leaf_qt_second_batch_approval_phase_17c6j.txt"
OUT_JSON = OUT_DIR / "leaf_qt_second_batch_approval_phase_17c6j.json"

EXPECTED_BATCH_SIZE = 25

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


def approve_second_batch() -> dict[str, Any]:
    selection = load_json(SELECTION)
    selected_moves = selection.get("selected_moves", [])

    source_missing = []
    destination_exists = []
    invalid_paths = []
    duplicate_sources = []
    duplicate_destinations = []

    seen_sources = set()
    seen_destinations = set()

    for move in selected_moves:
        src_raw = move.get("from")
        dst_raw = move.get("to")

        if not src_raw or not dst_raw:
            invalid_paths.append(move)
            continue

        src = ROOT / src_raw
        dst = ROOT / dst_raw

        if src_raw in seen_sources:
            duplicate_sources.append(move)
        seen_sources.add(src_raw)

        if dst_raw in seen_destinations:
            duplicate_destinations.append(move)
        seen_destinations.add(dst_raw)

        if not src.exists():
            source_missing.append(move)

        if dst.exists():
            destination_exists.append(move)

    compile_failures = compile_active_python()

    hard_blockers = (
        len(source_missing)
        + len(destination_exists)
        + len(invalid_paths)
        + len(duplicate_sources)
        + len(duplicate_destinations)
        + len(compile_failures)
    )

    passed = (
        selection.get("passed") is True
        and len(selected_moves) == EXPECTED_BATCH_SIZE
        and hard_blockers == 0
    )

    return {
        "phase": "17C.6J",
        "name": "leaf_qt Second Batch Approval",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "selection": str(SELECTION.relative_to(ROOT)),
        },
        "policy": {
            "moves_files": False,
            "deletes_files": False,
            "rewrites_imports": False,
            "approval_only": True,
            "requires_selection_pass": True,
            "requires_exact_batch_size": EXPECTED_BATCH_SIZE,
            "requires_existing_sources": True,
            "requires_empty_destinations": True,
            "requires_unique_sources": True,
            "requires_unique_destinations": True,
            "requires_compile_health": True,
            "authorises_next_phase": "17C.6K_SECOND_BATCH_READINESS",
        },
        "counts": {
            "selected_moves": len(selected_moves),
            "source_missing": len(source_missing),
            "destination_exists": len(destination_exists),
            "invalid_paths": len(invalid_paths),
            "duplicate_sources": len(duplicate_sources),
            "duplicate_destinations": len(duplicate_destinations),
            "compile_failures": len(compile_failures),
            "hard_blockers": hard_blockers,
        },
        "approved_moves": selected_moves if passed else [],
        "source_missing": source_missing,
        "destination_exists": destination_exists,
        "invalid_paths": invalid_paths,
        "duplicate_sources": duplicate_sources,
        "duplicate_destinations": duplicate_destinations,
        "compile_failures": compile_failures,
        "approval_statement": (
            "Second controlled movement batch is approved. "
            "No files were moved. The selected batch is source-backed, destination-safe, unique, compile-clean, and ready for readiness validation."
            if passed
            else
            "Second controlled movement batch is not approved. Resolve blockers before readiness or execution."
        ),
        "next_phase": "17C.6K_LEAF_QT_SECOND_BATCH_READINESS",
        "passed": passed,
    }


def write_report(result: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 17C.6J",
        "LEAF_QT SECOND BATCH APPROVAL",
        "=" * 41,
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

    lines += ["", "APPROVED MOVES", "--------------"]

    if result["approved_moves"]:
        for move in result["approved_moves"]:
            lines.append(f"{move['move_id']} :: {move['from']} -> {move['to']}")
    else:
        lines.append("none")

    lines += ["", "BLOCKERS", "--------"]

    blocker_sections = [
        ("source_missing", result["source_missing"]),
        ("destination_exists", result["destination_exists"]),
        ("invalid_paths", result["invalid_paths"]),
        ("duplicate_sources", result["duplicate_sources"]),
        ("duplicate_destinations", result["duplicate_destinations"]),
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
        "APPROVAL STATEMENT",
        "------------------",
        result["approval_statement"],
        "",
        "RESULT",
        "------",
        "PASS_PHASE_17C6J_LEAF_QT_SECOND_BATCH_APPROVAL" if result["passed"] else "FAIL_PHASE_17C6J_LEAF_QT_SECOND_BATCH_APPROVAL",
        "",
        f"report={OUT_TXT.relative_to(ROOT)}",
        f"json={OUT_JSON.relative_to(ROOT)}",
        "",
        f"next_phase={result['next_phase']}",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = approve_second_batch()
    write_report(result)

    print("PASS_PHASE_17C6J_LEAF_QT_SECOND_BATCH_APPROVAL" if result["passed"] else "FAIL_PHASE_17C6J_LEAF_QT_SECOND_BATCH_APPROVAL")
    print(f"selected_moves={result['counts']['selected_moves']}")
    print(f"source_missing={result['counts']['source_missing']}")
    print(f"destination_exists={result['counts']['destination_exists']}")
    print(f"invalid_paths={result['counts']['invalid_paths']}")
    print(f"duplicate_sources={result['counts']['duplicate_sources']}")
    print(f"duplicate_destinations={result['counts']['duplicate_destinations']}")
    print(f"compile_failures={result['counts']['compile_failures']}")
    print(f"hard_blockers={result['counts']['hard_blockers']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
