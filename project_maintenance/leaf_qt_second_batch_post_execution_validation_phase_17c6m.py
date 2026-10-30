from __future__ import annotations

import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

EXECUTION = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6l" / "leaf_qt_second_batch_execution_phase_17c6l.json"

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6m"
OUT_TXT = OUT_DIR / "leaf_qt_second_batch_post_execution_validation_phase_17c6m.txt"
OUT_JSON = OUT_DIR / "leaf_qt_second_batch_post_execution_validation_phase_17c6m.json"

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


def validate_second_batch() -> dict[str, Any]:
    execution = load_json(EXECUTION)
    executed_moves = execution.get("executed_moves", [])
    import_rewrites = execution.get("import_rewrites", [])

    destination_missing = []
    source_still_present = []
    old_import_references = []
    new_import_missing = []

    old_to_new_modules = {
        module_name_from_path(move["from"]): module_name_from_path(move["to"])
        for move in executed_moves
    }

    for move in executed_moves:
        src = ROOT / move["from"]
        dst = ROOT / move["to"]

        if src.exists():
            source_still_present.append(move)

        if not dst.exists():
            destination_missing.append(move)

    for file_path in active_python_files():
        text = file_path.read_text(encoding="utf-8", errors="replace")
        rel = str(file_path.relative_to(ROOT))

        for old_module, new_module in old_to_new_modules.items():
            old_needles = [
                f"from {old_module} import",
                f"import {old_module}",
            ]

            for needle in old_needles:
                if needle in text:
                    old_import_references.append(
                        {
                            "file": rel,
                            "reference": needle,
                            "old_module": old_module,
                            "new_module": new_module,
                        }
                    )

    for old_module, new_module in old_to_new_modules.items():
        new_path = ROOT / (new_module.replace(".", "/") + ".py")
        if not new_path.exists():
            new_import_missing.append(
                {
                    "old_module": old_module,
                    "new_module": new_module,
                    "expected_path": str(new_path.relative_to(ROOT)),
                }
            )

    compile_failures = compile_active_python()

    hard_blockers = (
        len(destination_missing)
        + len(source_still_present)
        + len(old_import_references)
        + len(new_import_missing)
        + len(compile_failures)
    )

    passed = (
        execution.get("passed") is True
        and execution.get("rolled_back") is False
        and len(executed_moves) == 25
        and hard_blockers == 0
    )

    return {
        "phase": "17C.6M",
        "name": "leaf_qt Second Batch Post-Execution Validation",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "execution": str(EXECUTION.relative_to(ROOT)),
        },
        "policy": {
            "moves_files": False,
            "deletes_files": False,
            "rewrites_imports": False,
            "post_execution_validation_only": True,
            "requires_execution_pass": True,
            "requires_no_rollback": True,
            "requires_destinations_present": True,
            "requires_sources_absent": True,
            "requires_old_imports_absent": True,
            "requires_new_module_paths_present": True,
            "requires_compile_health": True,
            "authorises_next_phase": "17C.6N_SECOND_BATCH_CLOSEOUT_CERTIFICATE",
        },
        "counts": {
            "executed_moves": len(executed_moves),
            "import_rewrites": len(import_rewrites),
            "destination_missing": len(destination_missing),
            "source_still_present": len(source_still_present),
            "old_import_references": len(old_import_references),
            "new_import_missing": len(new_import_missing),
            "compile_failures": len(compile_failures),
            "hard_blockers": hard_blockers,
        },
        "executed_moves": executed_moves,
        "destination_missing": destination_missing,
        "source_still_present": source_still_present,
        "old_import_references": old_import_references,
        "new_import_missing": new_import_missing,
        "compile_failures": compile_failures,
        "validation_statement": (
            "Second controlled movement batch passed post-execution validation. "
            "Destinations exist, old source paths are absent, old absolute import references are absent, "
            "new module paths exist, and active Python compilation is clean."
            if passed
            else
            "Second controlled movement batch failed post-execution validation. "
            "Resolve blockers before closeout certification."
        ),
        "next_phase": "17C.6N_LEAF_QT_SECOND_BATCH_CLOSEOUT_CERTIFICATE",
        "passed": passed,
    }


def write_report(result: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 17C.6M",
        "LEAF_QT SECOND BATCH POST-EXECUTION VALIDATION",
        "=" * 58,
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

    lines += ["", "VALIDATED MOVES", "---------------"]

    for move in result["executed_moves"]:
        lines.append(f"{move['move_id']} :: {move['from']} -> {move['to']}")

    lines += ["", "BLOCKERS", "--------"]

    blocker_sections = [
        ("destination_missing", result["destination_missing"]),
        ("source_still_present", result["source_still_present"]),
        ("old_import_references", result["old_import_references"]),
        ("new_import_missing", result["new_import_missing"]),
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
        "VALIDATION STATEMENT",
        "--------------------",
        result["validation_statement"],
        "",
        "RESULT",
        "------",
        "PASS_PHASE_17C6M_LEAF_QT_SECOND_BATCH_POST_EXECUTION_VALIDATION" if result["passed"] else "FAIL_PHASE_17C6M_LEAF_QT_SECOND_BATCH_POST_EXECUTION_VALIDATION",
        "",
        f"report={OUT_TXT.relative_to(ROOT)}",
        f"json={OUT_JSON.relative_to(ROOT)}",
        "",
        f"next_phase={result['next_phase']}",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = validate_second_batch()
    write_report(result)

    print("PASS_PHASE_17C6M_LEAF_QT_SECOND_BATCH_POST_EXECUTION_VALIDATION" if result["passed"] else "FAIL_PHASE_17C6M_LEAF_QT_SECOND_BATCH_POST_EXECUTION_VALIDATION")
    print(f"executed_moves={result['counts']['executed_moves']}")
    print(f"import_rewrites={result['counts']['import_rewrites']}")
    print(f"destination_missing={result['counts']['destination_missing']}")
    print(f"source_still_present={result['counts']['source_still_present']}")
    print(f"old_import_references={result['counts']['old_import_references']}")
    print(f"new_import_missing={result['counts']['new_import_missing']}")
    print(f"compile_failures={result['counts']['compile_failures']}")
    print(f"hard_blockers={result['counts']['hard_blockers']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
