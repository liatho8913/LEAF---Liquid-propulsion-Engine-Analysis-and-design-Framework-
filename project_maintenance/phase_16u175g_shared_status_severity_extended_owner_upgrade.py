from __future__ import annotations

from pathlib import Path
import json
import py_compile
import shutil
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]

TARGET = ROOT / "leaf_qt" / "status_presentation.py"

OUT_JSON = ROOT / "project_maintenance" / "phase_16u175g_shared_status_severity_extended_owner_upgrade.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u175g_shared_status_severity_extended_owner_upgrade.txt"
BACKUP_DIR = ROOT / "project_maintenance" / "phase_16u175g_backups"


NEW_FUNCTION = '''
def status_severity(status: object) -> str:
    """Return the presentation severity for an exact LEAF status code.

    This is intentionally broader than the original PASS/WARN/FAIL-only helper.

    It preserves exact status-code ownership while allowing presentation code to
    ask only for the display severity. Exact codes such as
    PASS_REGEN_CONVERGENCE_MASTER_GATE_CONVERGED must remain exact-code logic
    when state-machine decisions depend on them.

    Returned severities:
        PASS
        WARN
        FAIL
        BLOCKED
        ERROR
        UNKNOWN
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


def replace_status_severity_function(source: str) -> tuple[str, bool]:
    marker = "def status_severity("
    start = source.find(marker)

    if start == -1:
        return source.rstrip() + "\n\n" + NEW_FUNCTION + "\n", True

    lines = source.splitlines()
    start_line = None

    for idx, line in enumerate(lines):
        if line.startswith(marker):
            start_line = idx
            break

    if start_line is None:
        return source, False

    end_line = len(lines)

    for idx in range(start_line + 1, len(lines)):
        line = lines[idx]
        if line.startswith("def ") or line.startswith("class "):
            end_line = idx
            break

    new_lines = lines[:start_line] + NEW_FUNCTION.splitlines() + lines[end_line:]
    return "\n".join(new_lines) + "\n", True


def self_test() -> list[str]:
    namespace = {}
    exec(NEW_FUNCTION, namespace)
    fn = namespace["status_severity"]

    cases = {
        "PASS": "PASS",
        "PASS_REGEN_CONVERGED": "PASS",
        "WARN_REGEN_RUNNING": "WARN",
        "WARNING_SOMETHING": "WARN",
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
        actual = fn(raw)
        if actual != expected:
            failures.append(f"{raw!r}: expected {expected}, got {actual}")

    return failures


def main() -> dict:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    original = TARGET.read_text(encoding="utf-8", errors="replace")
    patched, applied = replace_status_severity_function(original)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"{timestamp}__status_presentation.py.bak"
    shutil.copy2(TARGET, backup)

    TARGET.write_text(patched, encoding="utf-8")

    compile_error = None
    test_failures = self_test()

    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as exc:
        compile_error = repr(exc)

    passed = applied and compile_error is None and not test_failures

    if not passed:
        shutil.copy2(backup, TARGET)

    result = {
        "phase": "16U.175G",
        "target": str(TARGET.relative_to(ROOT)),
        "backup": str(backup),
        "function_replaced_or_added": applied,
        "compile_error": compile_error,
        "self_test_failures": test_failures,
        "rolled_back": not passed,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U175G_SHARED_STATUS_SEVERITY_EXTENDED_OWNER_UPGRADE"
            if passed
            else "FAIL_PHASE_16U175G_SHARED_STATUS_SEVERITY_EXTENDED_OWNER_UPGRADE"
        ),
        "next_phase": "16U.175H_LOCAL_STATUS_SEVERITY_DEDUPLICATION_WAVE",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.175G",
        "SHARED STATUS SEVERITY EXTENDED OWNER UPGRADE",
        "=" * 56,
        f"status={result['status']}",
        f"target={result['target']}",
        f"function_replaced_or_added={result['function_replaced_or_added']}",
        f"compile_error={result['compile_error']}",
        f"self_test_failures={result['self_test_failures']}",
        f"rolled_back={result['rolled_back']}",
        f"backup={result['backup']}",
        "",
        "SUPPORTED SHARED SEVERITIES",
        "-" * 27,
        "PASS",
        "WARN",
        "FAIL",
        "BLOCKED",
        "ERROR",
        "UNKNOWN",
        "",
        f"json={OUT_JSON}",
        f"text={OUT_TXT}",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"target={result['target']}")
    print(f"function_replaced_or_added={result['function_replaced_or_added']}")
    print(f"compile_error={result['compile_error']}")
    print(f"self_test_failures={result['self_test_failures']}")
    print(f"rolled_back={result['rolled_back']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
