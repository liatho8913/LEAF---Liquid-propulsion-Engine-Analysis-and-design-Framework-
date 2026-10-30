from __future__ import annotations

import json
import py_compile
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

APPROVAL = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6j" / "leaf_qt_second_batch_approval_phase_17c6j.json"

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6k"
ROLLBACK_DIR = OUT_DIR / "rollback_snapshots"
OUT_TXT = OUT_DIR / "leaf_qt_second_batch_readiness_phase_17c6k.txt"
OUT_JSON = OUT_DIR / "leaf_qt_second_batch_readiness_phase_17c6k.json"
ROLLBACK_JSON = OUT_DIR / "leaf_qt_second_batch_rollback_manifest_phase_17c6k.json"

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


def import_reference_scan(moves: list[dict[str, Any]]) -> dict[str, list[str]]:
    active_files = active_python_files()
    references: dict[str, list[str]] = {}

    old_modules = {
        move["from"]: module_name_from_path(move["from"])
        for move in moves
    }

    for source_path, module_name in old_modules.items():
        hits: list[str] = []
        import_tail = module_name.split(".")[-1]

        for file_path in active_files:
            text = file_path.read_text(encoding="utf-8", errors="replace")
            rel = str(file_path.relative_to(ROOT))

            needles = [
                f"import {module_name}",
                f"from {module_name} import",
                f"from .{import_tail} import",
                f"import {import_tail}",
            ]

            if any(needle in text for needle in needles):
                hits.append(rel)

        references[source_path] = sorted(set(hits))

    return references


def build_readiness() -> dict[str, Any]:
    approval = load_json(APPROVAL)
    approved_moves = approval.get("approved_moves", [])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ROLLBACK_DIR.mkdir(parents=True, exist_ok=True)

    source_missing = []
    destination_exists = []
    rollback_snapshots: dict[str, str] = {}
    snapshot_failures = []

    for move in approved_moves:
        src = ROOT / move["from"]
        dst = ROOT / move["to"]

        if not src.exists():
            source_missing.append(move)
            continue

        if dst.exists():
            destination_exists.append(move)

        snapshot_name = move["from"].replace("/", "__").replace("\\", "__")
        snapshot_path = ROLLBACK_DIR / snapshot_name

        try:
            shutil.copy2(src, snapshot_path)
            rollback_snapshots[move["from"]] = str(snapshot_path.relative_to(ROOT))
        except Exception as exc:
            snapshot_failures.append(
                {
                    "move": move,
                    "error": repr(exc),
                }
            )

    import_references = import_reference_scan(approved_moves)
    compile_failures = compile_active_python()

    hard_blockers = (
        len(source_missing)
        + len(destination_exists)
        + len(snapshot_failures)
        + len(compile_failures)
    )

    passed = (
        approval.get("passed") is True
        and len(approved_moves) == 25
        and len(rollback_snapshots) == len(approved_moves)
        and hard_blockers == 0
    )

    rollback_manifest = {
        "phase": "17C.6K",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "snapshots": rollback_snapshots,
        "approved_moves": approved_moves,
        "passed": len(snapshot_failures) == 0 and len(rollback_snapshots) == len(approved_moves),
    }
    ROLLBACK_JSON.write_text(json.dumps(rollback_manifest, indent=2), encoding="utf-8")

    return {
        "phase": "17C.6K",
        "name": "leaf_qt Second Batch Readiness",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "approval": str(APPROVAL.relative_to(ROOT)),
        },
        "outputs": {
            "rollback_manifest": str(ROLLBACK_JSON.relative_to(ROOT)),
            "rollback_snapshots": str(ROLLBACK_DIR.relative_to(ROOT)),
        },
        "policy": {
            "moves_files": False,
            "deletes_files": False,
            "rewrites_imports": False,
            "readiness_only": True,
            "requires_approval_pass": True,
            "requires_rollback_snapshots": True,
            "requires_source_presence": True,
            "requires_empty_destinations": True,
            "requires_import_reference_scan": True,
            "requires_compile_health": True,
            "authorises_next_phase": "17C.6L_SECOND_BATCH_EXECUTION",
        },
        "counts": {
            "approved_moves": len(approved_moves),
            "rollback_snapshots": len(rollback_snapshots),
            "source_missing": len(source_missing),
            "destination_exists": len(destination_exists),
            "snapshot_failures": len(snapshot_failures),
            "import_reference_groups": len(import_references),
            "compile_failures": len(compile_failures),
            "hard_blockers": hard_blockers,
        },
        "approved_moves": approved_moves,
        "rollback_snapshots": rollback_snapshots,
        "import_references": import_references,
        "source_missing": source_missing,
        "destination_exists": destination_exists,
        "snapshot_failures": snapshot_failures,
        "compile_failures": compile_failures,
        "readiness_statement": (
            "Second controlled movement batch is ready for execution. "
            "Rollback snapshots exist, source/destination checks are clean, import references are mapped, and compilation is clean."
            if passed
            else
            "Second controlled movement batch is not ready for execution. Resolve blockers before movement."
        ),
        "next_phase": "17C.6L_LEAF_QT_SECOND_BATCH_EXECUTION",
        "passed": passed,
    }


def write_report(result: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 17C.6K",
        "LEAF_QT SECOND BATCH READINESS",
        "=" * 41,
        "",
        "INPUTS",
        "------",
    ]

    for key, value in result["inputs"].items():
        lines.append(f"{key}={value}")

    lines += ["", "OUTPUTS", "-------"]

    for key, value in result["outputs"].items():
        lines.append(f"{key}={value}")

    lines += ["", "COUNTS", "------"]

    for key, value in result["counts"].items():
        lines.append(f"{key}={value}")

    lines += ["", "APPROVED MOVES", "--------------"]

    for move in result["approved_moves"]:
        lines.append(f"{move['move_id']} :: {move['from']} -> {move['to']}")

    lines += ["", "BLOCKERS", "--------"]

    blocker_sections = [
        ("source_missing", result["source_missing"]),
        ("destination_exists", result["destination_exists"]),
        ("snapshot_failures", result["snapshot_failures"]),
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
        "READINESS STATEMENT",
        "-------------------",
        result["readiness_statement"],
        "",
        "RESULT",
        "------",
        "PASS_PHASE_17C6K_LEAF_QT_SECOND_BATCH_READINESS" if result["passed"] else "FAIL_PHASE_17C6K_LEAF_QT_SECOND_BATCH_READINESS",
        "",
        f"report={OUT_TXT.relative_to(ROOT)}",
        f"json={OUT_JSON.relative_to(ROOT)}",
        f"rollback_manifest={ROLLBACK_JSON.relative_to(ROOT)}",
        "",
        f"next_phase={result['next_phase']}",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = build_readiness()
    write_report(result)

    print("PASS_PHASE_17C6K_LEAF_QT_SECOND_BATCH_READINESS" if result["passed"] else "FAIL_PHASE_17C6K_LEAF_QT_SECOND_BATCH_READINESS")
    print(f"approved_moves={result['counts']['approved_moves']}")
    print(f"rollback_snapshots={result['counts']['rollback_snapshots']}")
    print(f"source_missing={result['counts']['source_missing']}")
    print(f"destination_exists={result['counts']['destination_exists']}")
    print(f"snapshot_failures={result['counts']['snapshot_failures']}")
    print(f"import_reference_groups={result['counts']['import_reference_groups']}")
    print(f"compile_failures={result['counts']['compile_failures']}")
    print(f"hard_blockers={result['counts']['hard_blockers']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")
    print(f"rollback_manifest={ROLLBACK_JSON.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
