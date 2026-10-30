from __future__ import annotations

from pathlib import Path
import json
import py_compile
import shutil
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u175hd_wrapper_repair_failure_diagnostic.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u175he_context_aware_try_except_fallback_repair.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u175he_context_aware_try_except_fallback_repair.txt"
BACKUP_DIR = ROOT / "project_maintenance" / "phase_16u175he_backups"

FALLBACK_FUNCTION_HEADER = "def status_severity"
SHARED_IMPORT = "from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity"


def replace_except_fallback(text: str) -> tuple[str, bool]:
    lines = text.splitlines()
    changed = False

    for i, line in enumerate(lines):
        if line.strip().startswith("except"):
            j = i + 1

            while j < len(lines) and lines[j].strip() == "":
                j += 1

            if j < len(lines) and lines[j].lstrip().startswith(FALLBACK_FUNCTION_HEADER):
                indent = line[: len(line) - len(line.lstrip())] + "    "
                lines[j] = indent + "from leaf_qt.status_presentation import status_severity"

                k = j + 1
                while k < len(lines):
                    current = lines[k]

                    if current.strip() == "":
                        k += 1
                        continue

                    current_indent_len = len(current) - len(current.lstrip())

                    if current_indent_len <= len(line) - len(line.lstrip()):
                        break

                    del lines[k]

                changed = True
                break

    if not changed:
        return text, False

    return "\n".join(lines) + "\n", True


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
        patched, changed = replace_except_fallback(original)

        if not changed:
            skipped.append({"path": rel_path, "reason": "try_except_fallback_pattern_not_found"})
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
                "fallback_replaced": True,
            }
        )

    passed = len(repaired) == len(diagnostics) and not skipped and not compile_failures

    result = {
        "phase": "16U.175H-E",
        "input_failed_subset_count": len(diagnostics),
        "repaired_count": len(repaired),
        "skipped_count": len(skipped),
        "compile_failure_count": len(compile_failures),
        "repaired": repaired,
        "skipped": skipped,
        "compile_failures": compile_failures,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U175HE_CONTEXT_AWARE_TRY_EXCEPT_FALLBACK_REPAIR"
            if passed
            else "FAIL_PHASE_16U175HE_CONTEXT_AWARE_TRY_EXCEPT_FALLBACK_REPAIR"
        ),
        "next_phase": "16U.175I_DEDUPLICATION_REGRESSION_AND_COMPATIBILITY_AUDIT",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.175H-E",
        "CONTEXT-AWARE TRY/EXCEPT FALLBACK REPAIR",
        "=" * 52,
        f"status={result['status']}",
        f"input_failed_subset_count={result['input_failed_subset_count']}",
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
    print(f"input_failed_subset_count={result['input_failed_subset_count']}")
    print(f"repaired_count={result['repaired_count']}")
    print(f"skipped_count={result['skipped_count']}")
    print(f"compile_failure_count={result['compile_failure_count']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
