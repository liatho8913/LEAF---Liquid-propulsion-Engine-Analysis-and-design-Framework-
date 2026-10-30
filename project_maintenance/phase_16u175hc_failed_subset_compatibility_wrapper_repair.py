from __future__ import annotations

from pathlib import Path
import ast
import json
import py_compile
import shutil
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u175hb_deduplication_failed_subset_diagnostic.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u175hc_failed_subset_compatibility_wrapper_repair.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u175hc_failed_subset_compatibility_wrapper_repair.txt"
BACKUP_DIR = ROOT / "project_maintenance" / "phase_16u175hc_backups"

SHARED_IMPORT = "from leaf_qt.status_presentation import status_severity as _leaf_shared_status_severity"

WRAPPER = '''def status_severity(status):
    return _leaf_shared_status_severity(status)
'''


def find_status_function_range(text: str) -> tuple[int, int] | None:
    tree = ast.parse(text)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "status_severity":
            return node.lineno, getattr(node, "end_lineno", node.lineno)

    return None


def insert_shared_import(text: str) -> str:
    if SHARED_IMPORT in text:
        return text

    lines = text.splitlines()
    insert_at = 0

    if lines and lines[0].startswith("#!"):
        insert_at = 1

    while insert_at < len(lines) and lines[insert_at].startswith("from __future__ import"):
        insert_at += 1

    lines.insert(insert_at, SHARED_IMPORT)
    return "\n".join(lines) + "\n"


def replace_with_wrapper(text: str) -> tuple[str, bool]:
    function_range = find_status_function_range(text)

    if not function_range:
        return text, False

    start, end = function_range
    lines = text.splitlines()

    new_lines = (
        lines[: start - 1]
        + WRAPPER.rstrip().splitlines()
        + lines[end:]
    )

    patched = "\n".join(new_lines) + "\n"
    patched = insert_shared_import(patched)

    return patched, True


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    diagnostics = data.get("diagnostics", [])

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    repaired = []
    skipped = []
    compile_failures = []

    for item in diagnostics:
        rel_path = item["path"]
        path = ROOT / rel_path

        if not path.exists():
            skipped.append({"path": rel_path, "reason": "missing_file"})
            continue

        original = path.read_text(encoding="utf-8", errors="replace")

        try:
            patched, applied = replace_with_wrapper(original)
        except Exception as exc:
            skipped.append({"path": rel_path, "reason": f"patch_error:{exc!r}"})
            continue

        if not applied:
            skipped.append({"path": rel_path, "reason": "local_status_severity_not_found"})
            continue

        backup = BACKUP_DIR / f"{timestamp}__{rel_path.replace('/', '__')}.bak"
        shutil.copy2(path, backup)

        path.write_text(patched, encoding="utf-8")

        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            shutil.copy2(backup, path)
            compile_failures.append(
                {
                    "path": rel_path,
                    "error": repr(exc),
                    "backup": str(backup),
                    "rolled_back": True,
                }
            )
            continue

        repaired.append(
            {
                "path": rel_path,
                "backup": str(backup),
                "wrapper_applied": True,
            }
        )

    passed = len(repaired) == len(diagnostics) and not skipped and not compile_failures

    result = {
        "phase": "16U.175H-C",
        "failed_subset_count": len(diagnostics),
        "repaired_count": len(repaired),
        "skipped_count": len(skipped),
        "compile_failure_count": len(compile_failures),
        "repaired": repaired,
        "skipped": skipped,
        "compile_failures": compile_failures,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U175HC_FAILED_SUBSET_COMPATIBILITY_WRAPPER_REPAIR"
            if passed
            else "FAIL_PHASE_16U175HC_FAILED_SUBSET_COMPATIBILITY_WRAPPER_REPAIR"
        ),
        "next_phase": "16U.175I_DEDUPLICATION_REGRESSION_AND_COMPATIBILITY_AUDIT",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.175H-C",
        "FAILED-SUBSET COMPATIBILITY WRAPPER REPAIR",
        "=" * 54,
        f"status={result['status']}",
        f"failed_subset_count={result['failed_subset_count']}",
        f"repaired_count={result['repaired_count']}",
        f"skipped_count={result['skipped_count']}",
        f"compile_failure_count={result['compile_failure_count']}",
        "",
        "REPAIRED FILES",
        "-" * 14,
    ]

    for item in repaired:
        lines.append(item["path"])

    lines.extend(["", "SKIPPED FILES", "-" * 13])
    if skipped:
        for item in skipped:
            lines.append(f"{item['path']} :: {item['reason']}")
    else:
        lines.append("None.")

    lines.extend(["", "COMPILE FAILURES", "-" * 16])
    if compile_failures:
        for item in compile_failures:
            lines.append(f"{item['path']} :: {item['error']}")
    else:
        lines.append("None.")

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"failed_subset_count={result['failed_subset_count']}")
    print(f"repaired_count={result['repaired_count']}")
    print(f"skipped_count={result['skipped_count']}")
    print(f"compile_failure_count={result['compile_failure_count']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
