from __future__ import annotations

from pathlib import Path
import json
import py_compile
import shutil
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]

TARGET = ROOT / "leaf_qt" / "structured_status_access.py"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u175ic_status_presentation_circular_import_break.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u175ic_status_presentation_circular_import_break.txt"
BACKUP_DIR = ROOT / "project_maintenance" / "phase_16u175ic_backups"

OLD_IMPORT = "from leaf_qt.status_presentation import status_severity"

LOCAL_STATUS_SEVERITY = '''
def status_severity(status: object) -> str:
    """Return canonical severity without importing status_presentation.

    This deliberately lives here to avoid a circular import:

        status_presentation -> structured_status_access
        structured_status_access -> status_presentation

    The public shared owner may re-export or reuse this behaviour, but this
    low-level access module must not import back upward.
    """
    text = str(status or "").strip().upper()

    if not text:
        return "UNKNOWN"

    if text.startswith("PASS"):
        return "PASS"

    if text.startswith("WARN") or text.startswith("WARNING"):
        return "WARN"

    if text.startswith("FAIL") or text.startswith("FAILED"):
        return "FAIL"

    if text.startswith("BLOCKED"):
        return "BLOCKED"

    if text.startswith("ERROR") or text.startswith("EXCEPTION"):
        return "ERROR"

    return "UNKNOWN"
'''.strip()


def patch_text(text: str) -> tuple[str, bool]:
    changed = False

    if OLD_IMPORT in text:
        text = text.replace(OLD_IMPORT, LOCAL_STATUS_SEVERITY, 1)
        changed = True

    if "def status_severity(" not in text:
        text = LOCAL_STATUS_SEVERITY + "\n\n" + text
        changed = True

    return text, changed


def main() -> dict:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    original = TARGET.read_text(encoding="utf-8", errors="replace")
    patched, changed = patch_text(original)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"{timestamp}__structured_status_access.py.bak"
    shutil.copy2(TARGET, backup)

    TARGET.write_text(patched, encoding="utf-8")

    compile_error = None
    import_error = None
    self_test_failures = []

    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as exc:
        compile_error = repr(exc)

    if compile_error is None:
        try:
            import sys
            sys.path.insert(0, str(ROOT))

            from leaf_qt.structured_status_access import status_severity

            cases = {
                "PASS_REGEN": "PASS",
                "WARN_REGEN": "WARN",
                "FAIL_REGEN": "FAIL",
                "BLOCKED_REGEN": "BLOCKED",
                "ERROR_REGEN": "ERROR",
                "": "UNKNOWN",
                None: "UNKNOWN",
            }

            for raw, expected in cases.items():
                actual = status_severity(raw)
                if actual != expected:
                    self_test_failures.append(f"{raw!r}: expected {expected}, got {actual}")

        except Exception as exc:
            import_error = repr(exc)

    passed = changed and compile_error is None and import_error is None and not self_test_failures

    if not passed:
        shutil.copy2(backup, TARGET)

    result = {
        "phase": "16U.175I-C",
        "target": str(TARGET.relative_to(ROOT)),
        "changed": changed,
        "compile_error": compile_error,
        "import_error": import_error,
        "self_test_failures": self_test_failures,
        "rolled_back": not passed,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U175IC_STATUS_PRESENTATION_CIRCULAR_IMPORT_BREAK"
            if passed
            else "FAIL_PHASE_16U175IC_STATUS_PRESENTATION_CIRCULAR_IMPORT_BREAK"
        ),
        "next_phase": "16U.175I_DEDUPLICATION_REGRESSION_AND_COMPATIBILITY_AUDIT",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_TXT.write_text(
        "\n".join(
            [
                "LEAF PHASE 16U.175I-C",
                "STATUS PRESENTATION CIRCULAR IMPORT BREAK",
                "=" * 49,
                f"status={result['status']}",
                f"target={result['target']}",
                f"changed={result['changed']}",
                f"compile_error={result['compile_error']}",
                f"import_error={result['import_error']}",
                f"self_test_failures={result['self_test_failures']}",
                f"rolled_back={result['rolled_back']}",
                f"backup={backup}",
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
    print(f"changed={result['changed']}")
    print(f"compile_error={result['compile_error']}")
    print(f"import_error={result['import_error']}")
    print(f"self_test_failures={result['self_test_failures']}")
    print(f"rolled_back={result['rolled_back']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
