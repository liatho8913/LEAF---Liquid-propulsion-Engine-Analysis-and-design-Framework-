from __future__ import annotations

from pathlib import Path
import py_compile
import shutil
import json
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "leaf_qt" / "regen_viewer_integration_report_owner.py"

OUT_JSON = ROOT / "project_maintenance" / "phase_16u165d_surgical_failed_file_repair.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u165d_surgical_failed_file_repair.txt"
BACKUP_DIR = ROOT / "project_maintenance" / "phase_16u165d_backups"


OLD = 'if not check.status.startswith("PASS")'
NEW = 'if status_severity(check.status) != "PASS"'


def insert_import_safely(text: str) -> str:
    import_line = "from leaf_qt.status_presentation import status_severity"

    if import_line in text:
        return text

    lines = text.splitlines()

    insert_at = 0

    if lines and lines[0].startswith("#!"):
        insert_at = 1

    while insert_at < len(lines) and lines[insert_at].startswith("from __future__ import"):
        insert_at += 1

    lines.insert(insert_at, import_line)

    return "\n".join(lines) + "\n"


def main() -> dict:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    original = TARGET.read_text(encoding="utf-8", errors="replace")

    if OLD not in original:
        result = {
            "phase": "16U.165D",
            "target": str(TARGET.relative_to(ROOT)),
            "replacement_applied": False,
            "reason": "target_legacy_line_not_found",
            "passed": False,
            "status": "FAIL_PHASE_16U165D_SURGICAL_FAILED_FILE_REPAIR",
        }
        OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
        OUT_TXT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"{timestamp}__regen_viewer_integration_report_owner.py.bak"
    shutil.copy2(TARGET, backup)

    patched = original.replace(OLD, NEW, 1)
    patched = insert_import_safely(patched)

    TARGET.write_text(patched, encoding="utf-8")

    try:
        py_compile.compile(str(TARGET), doraise=True)
        passed = True
        error = None
    except Exception as exc:
        shutil.copy2(backup, TARGET)
        passed = False
        error = repr(exc)

    result = {
        "phase": "16U.165D",
        "target": str(TARGET.relative_to(ROOT)),
        "backup": str(backup),
        "replacement_applied": passed,
        "old": OLD,
        "new": NEW,
        "compile_error": error,
        "rolled_back": not passed,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U165D_SURGICAL_FAILED_FILE_REPAIR"
            if passed
            else "FAIL_PHASE_16U165D_SURGICAL_FAILED_FILE_REPAIR"
        ),
        "next_phase": "16U.166_SAFE_WAVE_REGRESSION_AND_RECLASSIFICATION",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    OUT_TXT.write_text(
        "\n".join(
            [
                "LEAF PHASE 16U.165D",
                "SURGICAL FAILED-FILE REPAIR",
                "=" * 34,
                f"status={result['status']}",
                f"target={result['target']}",
                f"replacement_applied={result['replacement_applied']}",
                f"rolled_back={result['rolled_back']}",
                f"compile_error={result['compile_error']}",
                f"backup={result['backup']}",
                f"json={OUT_JSON}",
                f"text={OUT_TXT}",
            ]
        ),
        encoding="utf-8",
    )

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"target={result['target']}")
    print(f"replacement_applied={result['replacement_applied']}")
    print(f"rolled_back={result['rolled_back']}")
    print(f"compile_error={result['compile_error']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
