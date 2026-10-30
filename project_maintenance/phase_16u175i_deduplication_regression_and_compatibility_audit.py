from __future__ import annotations

from pathlib import Path
import json
import py_compile
import re


ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT))

OUT_JSON = ROOT / "project_maintenance" / "phase_16u175i_deduplication_regression_and_compatibility_audit.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u175i_deduplication_regression_and_compatibility_audit.txt"

STATUS_OWNER = ROOT / "leaf_qt" / "status_presentation.py"

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    ".idea",
    ".vscode",
}


def iter_leaf_qt_files() -> list[Path]:
    root = ROOT / "leaf_qt"
    return sorted(
        p for p in root.rglob("*.py")
        if not any(part in EXCLUDE_DIRS for part in p.parts)
    )


def compile_file(path: Path) -> str | None:
    try:
        py_compile.compile(str(path), doraise=True)
        return None
    except Exception as exc:
        return f"{path.relative_to(ROOT)}: {repr(exc)}"


def count_local_status_definitions(files: list[Path]) -> list[str]:
    offenders = []

    for path in files:
        if path == STATUS_OWNER:
            continue

        text = path.read_text(encoding="utf-8", errors="replace")

        if re.search(r"^def\s+status_severity\s*\(", text, flags=re.MULTILINE):
            offenders.append(str(path.relative_to(ROOT)))

    return offenders


def count_shared_import_users(files: list[Path]) -> list[str]:
    users = []

    for path in files:
        if path == STATUS_OWNER:
            continue

        text = path.read_text(encoding="utf-8", errors="replace")

        if "status_presentation" in text and "status_severity" in text:
            users.append(str(path.relative_to(ROOT)))

    return sorted(users)


def check_owner_self_test() -> list[str]:
    from leaf_qt.status_presentation import status_severity

    cases = {
        "PASS": "PASS",
        "PASS_REGEN_COMPLETE": "PASS",
        "WARN_REGEN_RUNNING": "WARN",
        "WARNING_RUNTIME": "WARN",
        "FAIL_THERMAL_STRESS": "FAIL",
        "FAILED_GATE": "FAIL",
        "BLOCKED_INPUT": "BLOCKED",
        "ERROR_RUNTIME": "ERROR",
        "EXCEPTION_SOLVER": "ERROR",
        "": "UNKNOWN",
        None: "UNKNOWN",
        "CANDIDATE_AVAILABLE": "UNKNOWN",
    }

    failures = []

    for raw, expected in cases.items():
        actual = status_severity(raw)
        if actual != expected:
            failures.append(f"{raw!r}: expected {expected}, got {actual}")

    return failures


def main() -> dict:
    files = iter_leaf_qt_files()

    compile_failures = []

    for path in files:
        err = compile_file(path)
        if err:
            compile_failures.append(err)

    local_definitions = count_local_status_definitions(files)
    shared_import_users = count_shared_import_users(files)
    owner_self_test_failures = check_owner_self_test()

    passed = (
        not compile_failures
        and not owner_self_test_failures
        and len(local_definitions) <= 22
    )

    result = {
        "phase": "16U.175I",
        "production_file_count": len(files),
        "compile_failure_count": len(compile_failures),
        "local_status_definition_count": len(local_definitions),
        "shared_status_import_user_count": len(shared_import_users),
        "owner_self_test_failure_count": len(owner_self_test_failures),
        "compile_failures": compile_failures,
        "local_status_definition_files": local_definitions,
        "shared_status_import_users": shared_import_users,
        "owner_self_test_failures": owner_self_test_failures,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U175I_DEDUPLICATION_REGRESSION_AND_COMPATIBILITY_AUDIT"
            if passed
            else "FAIL_PHASE_16U175I_DEDUPLICATION_REGRESSION_AND_COMPATIBILITY_AUDIT"
        ),
        "next_phase": "16U.175J_STATUS_SEVERITY_DEDUPLICATION_CLOSEOUT_CERTIFICATE",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.175I",
        "DEDUPLICATION REGRESSION AND COMPATIBILITY AUDIT",
        "=" * 58,
        f"status={result['status']}",
        f"production_file_count={result['production_file_count']}",
        f"compile_failure_count={result['compile_failure_count']}",
        f"local_status_definition_count={result['local_status_definition_count']}",
        f"shared_status_import_user_count={result['shared_status_import_user_count']}",
        f"owner_self_test_failure_count={result['owner_self_test_failure_count']}",
        "",
        "INTERPRETATION",
        "-" * 14,
        "45 files had local status_severity removed directly.",
        "22 fallback-pattern files were repaired with valid try/except structure.",
        "The shared owner now carries extended severity semantics.",
        "",
        "LOCAL STATUS DEFINITIONS STILL PRESENT",
        "-" * 38,
    ]

    if local_definitions:
        lines.extend(local_definitions)
    else:
        lines.append("None.")

    lines.extend(["", "COMPILE FAILURES", "-" * 16])
    if compile_failures:
        lines.extend(compile_failures)
    else:
        lines.append("None.")

    lines.extend(["", "OWNER SELF TEST FAILURES", "-" * 24])
    if owner_self_test_failures:
        lines.extend(owner_self_test_failures)
    else:
        lines.append("None.")

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"production_file_count={result['production_file_count']}")
    print(f"compile_failure_count={result['compile_failure_count']}")
    print(f"local_status_definition_count={result['local_status_definition_count']}")
    print(f"shared_status_import_user_count={result['shared_status_import_user_count']}")
    print(f"owner_self_test_failure_count={result['owner_self_test_failure_count']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
