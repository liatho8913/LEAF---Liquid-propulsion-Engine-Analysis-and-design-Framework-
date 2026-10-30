from __future__ import annotations

from pathlib import Path
import py_compile
import shutil
import json
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "leaf_qt" / "regen_viewer_integration_report_owner.py"

OUT_JSON = ROOT / "project_maintenance" / "phase_16u165e_import_order_normalise_and_repair.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u165e_import_order_normalise_and_repair.txt"
BACKUP_DIR = ROOT / "project_maintenance" / "phase_16u165e_backups"

STATUS_IMPORT = "from leaf_qt.status_presentation import status_severity"

REPLACEMENTS = {
    'if not check.status.startswith("PASS")': 'if status_severity(check.status) != "PASS"',
}


def normalise_import_order(text: str) -> str:
    lines = text.splitlines()

    shebang = []
    if lines and lines[0].startswith("#!"):
        shebang = [lines.pop(0)]

    future_lines = []
    status_lines = []
    remaining = []

    for line in lines:
        stripped = line.strip()

        if stripped == "from __future__ import annotations":
            if stripped not in future_lines:
                future_lines.append(stripped)
            continue

        if stripped == STATUS_IMPORT:
            if stripped not in status_lines:
                status_lines.append(stripped)
            continue

        remaining.append(line)

    if not future_lines:
        future_lines = ["from __future__ import annotations"]

    if not status_lines:
        status_lines = [STATUS_IMPORT]

    final_lines = []
    final_lines.extend(shebang)
    final_lines.extend(future_lines)
    final_lines.extend(status_lines)
    final_lines.extend(remaining)

    while len(final_lines) > 2 and final_lines[2] == "" and final_lines[3] == "":
        del final_lines[3]

    return "\n".join(final_lines) + "\n"


def main() -> dict:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"{timestamp}__regen_viewer_integration_report_owner.py.bak"
    shutil.copy2(TARGET, backup)

    text = TARGET.read_text(encoding="utf-8", errors="replace")

    replacement_count = 0
    for old, new in REPLACEMENTS.items():
        if old in text:
            text = text.replace(old, new, 1)
            replacement_count += 1

    text = normalise_import_order(text)

    TARGET.write_text(text, encoding="utf-8")

    try:
        py_compile.compile(str(TARGET), doraise=True)
        passed = True
        error = None
    except Exception as exc:
        shutil.copy2(backup, TARGET)
        passed = False
        error = repr(exc)

    result = {
        "phase": "16U.165E",
        "target": str(TARGET.relative_to(ROOT)),
        "backup": str(backup),
        "replacement_count": replacement_count,
        "import_order_normalised": True,
        "rolled_back": not passed,
        "compile_error": error,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U165E_IMPORT_ORDER_NORMALISE_AND_REPAIR"
            if passed
            else "FAIL_PHASE_16U165E_IMPORT_ORDER_NORMALISE_AND_REPAIR"
        ),
        "next_phase": "16U.166_SAFE_WAVE_REGRESSION_AND_RECLASSIFICATION",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_TXT.write_text(
        "\n".join(
            [
                "LEAF PHASE 16U.165E",
                "IMPORT ORDER NORMALISATION + SURGICAL STATUS REPAIR",
                "=" * 58,
                f"status={result['status']}",
                f"target={result['target']}",
                f"replacement_count={result['replacement_count']}",
                f"import_order_normalised={result['import_order_normalised']}",
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
    print(f"replacement_count={result['replacement_count']}")
    print(f"rolled_back={result['rolled_back']}")
    print(f"compile_error={result['compile_error']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
