from __future__ import annotations

from pathlib import Path
import ast
import json
import py_compile
import shutil
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u175f_local_status_severity_deduplication_manifest.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u175h_local_status_severity_deduplication_wave.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u175h_local_status_severity_deduplication_wave.txt"
BACKUP_DIR = ROOT / "project_maintenance" / "phase_16u175h_backups"

STATUS_IMPORT = "from leaf_qt.status_presentation import status_severity"


def find_function_range(text: str, name: str) -> tuple[int, int] | None:
    tree = ast.parse(text)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node.lineno, getattr(node, "end_lineno", node.lineno)

    return None


def insert_import(text: str) -> str:
    if STATUS_IMPORT in text:
        return text

    lines = text.splitlines()
    insert_at = 0

    if lines and lines[0].startswith("#!"):
        insert_at = 1

    while insert_at < len(lines) and lines[insert_at].startswith("from __future__ import"):
        insert_at += 1

    lines.insert(insert_at, STATUS_IMPORT)
    return "\n".join(lines) + "\n"


def remove_local_status_severity(text: str) -> tuple[str, bool]:
    function_range = find_function_range(text, "status_severity")

    if function_range is None:
        return text, False

    start, end = function_range
    lines = text.splitlines()

    del lines[start - 1:end]

    while start - 1 < len(lines) and lines[start - 1].strip() == "":
        del lines[start - 1]

    patched = "\n".join(lines) + "\n"
    patched = insert_import(patched)

    return patched, True


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))

    candidates = [
        entry for entry in data.get("entries", [])
        if entry.get("deduplication_action") == "UPGRADE_SHARED_OWNER_THEN_DEDUPLICATE"
    ]

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    touched = []
    skipped = []
    compile_failures = []

    for entry in candidates:
        rel_path = entry["path"]
        path = ROOT / rel_path

        if not path.exists():
            skipped.append({"path": rel_path, "reason": "missing_file"})
            continue

        original = path.read_text(encoding="utf-8", errors="replace")

        try:
            patched, removed = remove_local_status_severity(original)
        except Exception as exc:
            skipped.append({"path": rel_path, "reason": f"parse_or_patch_error:{exc!r}"})
            continue

        if not removed:
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

        touched.append(
            {
                "path": rel_path,
                "backup": str(backup),
                "local_definition_removed": True,
                "shared_import_inserted": STATUS_IMPORT in patched,
            }
        )

    passed = bool(touched) and not compile_failures

    result = {
        "phase": "16U.175H",
        "candidate_count": len(candidates),
        "touched_count": len(touched),
        "skipped_count": len(skipped),
        "compile_failure_count": len(compile_failures),
        "touched": touched,
        "skipped": skipped,
        "compile_failures": compile_failures,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U175H_LOCAL_STATUS_SEVERITY_DEDUPLICATION_WAVE"
            if passed
            else "FAIL_PHASE_16U175H_LOCAL_STATUS_SEVERITY_DEDUPLICATION_WAVE"
        ),
        "next_phase": "16U.175I_DEDUPLICATION_REGRESSION_AND_COMPATIBILITY_AUDIT",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.175H",
        "LOCAL STATUS SEVERITY DEDUPLICATION WAVE",
        "=" * 50,
        f"status={result['status']}",
        f"candidate_count={result['candidate_count']}",
        f"touched_count={result['touched_count']}",
        f"skipped_count={result['skipped_count']}",
        f"compile_failure_count={result['compile_failure_count']}",
        "",
        "TOUCHED FILES",
        "-" * 13,
    ]

    for item in touched:
        lines.append(f"{item['path']}")

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
    print(f"candidate_count={result['candidate_count']}")
    print(f"touched_count={result['touched_count']}")
    print(f"skipped_count={result['skipped_count']}")
    print(f"compile_failure_count={result['compile_failure_count']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
