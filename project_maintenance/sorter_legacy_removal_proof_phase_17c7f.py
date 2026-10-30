from __future__ import annotations

import ast
import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path

from repository_architecture.universal_repository_sorter_engine import (
    classify_repository,
    compile_active_python,
    select_safe_moves,
)


ROOT = Path(__file__).resolve().parents[1]

ARCHIVE_READINESS = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c7e" / "sorter_legacy_archive_readiness_phase_17c7e.json"
ENGINE = ROOT / "project_maintenance" / "repository_architecture" / "universal_repository_sorter_engine.py"

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c7f"
OUT_TXT = OUT_DIR / "sorter_legacy_removal_proof_phase_17c7f.txt"
OUT_JSON = OUT_DIR / "sorter_legacy_removal_proof_phase_17c7f.json"

ENGINE_IMPORT = "repository_architecture.universal_repository_sorter_engine"

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


REQUIRED_ENGINE_CAPABILITIES = {
    "classify_repository",
    "compile_active_python",
    "select_safe_moves",
    "classify_file",
    "is_safe_movement_candidate",
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


def compile_file(path: Path) -> dict | None:
    try:
        py_compile.compile(str(path), doraise=True)
        return None
    except Exception as exc:
        return {"path": str(path.relative_to(ROOT)), "error": repr(exc)}


def parse_ast(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None


def defined_functions(path: Path) -> set[str]:
    tree = parse_ast(path)
    if tree is None:
        return set()

    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


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

        if rel == target_path:
            continue

        text = path.read_text(encoding="utf-8", errors="replace")

        for needle in needles:
            if needle in text:
                hits.append({"file": rel, "reference": needle})

    return hits


def has_engine_replacement_access(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    return ENGINE_IMPORT in text


def build_removal_proof() -> dict:
    readiness = load_json(ARCHIVE_READINESS)
    candidates = readiness.get("removal_prep_candidates", [])

    classifications = classify_repository(ROOT)
    selected_moves, deferred, rejected = select_safe_moves(ROOT, classifications)

    engine_functions = defined_functions(ENGINE)
    missing_engine_capabilities = sorted(REQUIRED_ENGINE_CAPABILITIES - engine_functions)

    removal_proofs = []
    missing_targets = []
    missing_backups = []
    target_compile_failures = []
    active_dependency_blockers = []
    missing_engine_replacement = []

    for item in candidates:
        path_text = item["path"]
        target = ROOT / path_text
        backup = ROOT / item["backup"]

        if not target.exists():
            missing_targets.append(item)
            continue

        if not backup.exists():
            missing_backups.append(item)

        failure = compile_file(target)
        if failure:
            target_compile_failures.append(failure)

        references = scan_references(path_text)
        if references:
            active_dependency_blockers.append(
                {
                    "path": path_text,
                    "references": references,
                }
            )

        replacement_access = has_engine_replacement_access(target)
        if not replacement_access:
            missing_engine_replacement.append(item)

        removal_proofs.append(
            {
                "path": path_text,
                "backup": item["backup"],
                "reference_count": len(references),
                "references": references,
                "compile_clean": failure is None,
                "has_engine_replacement_access": replacement_access,
                "removal_safe_later": (
                    len(references) == 0
                    and failure is None
                    and replacement_access
                ),
            }
        )

    compile_failures = compile_active_python(ROOT)
    engine_failure = compile_file(ENGINE)
    engine_compile_failures = [engine_failure] if engine_failure else []

    hard_blockers = (
        len(missing_targets)
        + len(missing_backups)
        + len(target_compile_failures)
        + len(active_dependency_blockers)
        + len(missing_engine_replacement)
        + len(missing_engine_capabilities)
        + len(compile_failures)
        + len(engine_compile_failures)
    )

    passed = (
        readiness.get("passed") is True
        and len(candidates) == 3
        and len(removal_proofs) == 3
        and len(selected_moves) > 0
        and hard_blockers == 0
    )

    return {
        "phase": "17C.7F",
        "name": "Sorter Legacy Removal Proof",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "archive_readiness": str(ARCHIVE_READINESS.relative_to(ROOT)),
            "engine": str(ENGINE.relative_to(ROOT)),
        },
        "policy": {
            "moves_files": False,
            "deletes_files": False,
            "rewrites_imports": False,
            "removal_proof_only": True,
            "requires_archive_readiness_pass": True,
            "requires_no_active_references": True,
            "requires_backups_present": True,
            "requires_engine_replacement_access": True,
            "requires_engine_capabilities": True,
            "requires_compile_health": True,
            "does_not_delete_yet": True,
            "authorises_next_phase": "17C.7G_SORTER_LEGACY_REMOVAL_EXECUTION",
        },
        "counts": {
            "removal_candidates": len(candidates),
            "removal_proofs": len(removal_proofs),
            "removal_safe_later": len([item for item in removal_proofs if item["removal_safe_later"]]),
            "missing_targets": len(missing_targets),
            "missing_backups": len(missing_backups),
            "target_compile_failures": len(target_compile_failures),
            "active_dependency_blockers": len(active_dependency_blockers),
            "missing_engine_replacement": len(missing_engine_replacement),
            "missing_engine_capabilities": len(missing_engine_capabilities),
            "classified_files": len(classifications),
            "selected_moves_from_engine": len(selected_moves),
            "compile_failures": len(compile_failures),
            "engine_compile_failures": len(engine_compile_failures),
            "hard_blockers": hard_blockers,
        },
        "removal_proofs": removal_proofs,
        "missing_targets": missing_targets,
        "missing_backups": missing_backups,
        "target_compile_failures": target_compile_failures,
        "active_dependency_blockers": active_dependency_blockers,
        "missing_engine_replacement": missing_engine_replacement,
        "missing_engine_capabilities": missing_engine_capabilities,
        "compile_failures": compile_failures,
        "engine_compile_failures": engine_compile_failures,
        "proof_statement": (
            "Sorter legacy removal proof passed. The 3 removal-prep files have no active references, have backups, compile cleanly, and have replacement access through the shared sorter engine."
            if passed
            else
            "Sorter legacy removal proof failed. Resolve references, backups, replacement access, or compile blockers before deletion."
        ),
        "next_phase": "17C.7G_SORTER_LEGACY_REMOVAL_EXECUTION",
        "passed": passed,
    }


def write_report(result: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 17C.7F",
        "SORTER LEGACY REMOVAL PROOF",
        "=" * 38,
        "",
        "COUNTS",
        "------",
    ]

    for key, value in result["counts"].items():
        lines.append(f"{key}={value}")

    lines += ["", "REMOVAL PROOFS", "--------------"]

    for item in result["removal_proofs"]:
        lines.append(
            f"{item['path']} :: safe_later={item['removal_safe_later']} "
            f"references={item['reference_count']} engine_replacement={item['has_engine_replacement_access']} backup={item['backup']}"
        )

    lines += [
        "",
        "PROOF STATEMENT",
        "---------------",
        result["proof_statement"],
        "",
        "RESULT",
        "------",
        "PASS_PHASE_17C7F_SORTER_LEGACY_REMOVAL_PROOF" if result["passed"] else "FAIL_PHASE_17C7F_SORTER_LEGACY_REMOVAL_PROOF",
        "",
        f"report={OUT_TXT.relative_to(ROOT)}",
        f"json={OUT_JSON.relative_to(ROOT)}",
        "",
        f"next_phase={result['next_phase']}",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = build_removal_proof()
    write_report(result)

    print("PASS_PHASE_17C7F_SORTER_LEGACY_REMOVAL_PROOF" if result["passed"] else "FAIL_PHASE_17C7F_SORTER_LEGACY_REMOVAL_PROOF")
    print(f"removal_candidates={result['counts']['removal_candidates']}")
    print(f"removal_safe_later={result['counts']['removal_safe_later']}")
    print(f"missing_targets={result['counts']['missing_targets']}")
    print(f"missing_backups={result['counts']['missing_backups']}")
    print(f"active_dependency_blockers={result['counts']['active_dependency_blockers']}")
    print(f"missing_engine_replacement={result['counts']['missing_engine_replacement']}")
    print(f"missing_engine_capabilities={result['counts']['missing_engine_capabilities']}")
    print(f"compile_failures={result['counts']['compile_failures']}")
    print(f"engine_compile_failures={result['counts']['engine_compile_failures']}")
    print(f"hard_blockers={result['counts']['hard_blockers']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
