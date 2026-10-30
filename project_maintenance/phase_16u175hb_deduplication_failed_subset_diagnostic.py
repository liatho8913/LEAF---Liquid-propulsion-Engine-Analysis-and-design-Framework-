from __future__ import annotations

from pathlib import Path
from collections import Counter
import json
import re


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u175h_local_status_severity_deduplication_wave.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u175hb_deduplication_failed_subset_diagnostic.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u175hb_deduplication_failed_subset_diagnostic.txt"


def classify_compile_error(error: str) -> str:
    if "NameError" in error and "status_severity" in error:
        return "RUNTIME_NAME_ERROR_STATUS_SEVERITY"

    if "SyntaxError" in error and "__future__" in error:
        return "FUTURE_IMPORT_ORDER_ERROR"

    if "IndentationError" in error:
        return "INDENTATION_ERROR_AFTER_FUNCTION_REMOVAL"

    if "expected an indented block" in error:
        return "EMPTY_BLOCK_AFTER_FUNCTION_REMOVAL"

    if "invalid syntax" in error:
        return "SYNTAX_ERROR_AFTER_FUNCTION_REMOVAL"

    return "OTHER_COMPILE_ERROR"


def extract_status_function_context(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    function_line = None
    for idx, line in enumerate(lines, start=1):
        if re.match(r"^def status_severity\s*\(", line):
            function_line = idx
            break

    import_lines = [
        idx for idx, line in enumerate(lines, start=1)
        if "status_severity" in line
    ]

    return {
        "has_local_definition": function_line is not None,
        "local_definition_line": function_line,
        "status_severity_line_numbers": import_lines[:40],
    }


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    failures = data.get("compile_failures", [])

    diagnostics = []
    counts = Counter()

    for failure in failures:
        rel_path = failure["path"]
        path = ROOT / rel_path
        error = failure.get("error", "")
        classification = classify_compile_error(error)

        if path.exists():
            context = extract_status_function_context(path)
        else:
            context = {
                "has_local_definition": False,
                "local_definition_line": None,
                "status_severity_line_numbers": [],
            }

        counts[classification] += 1

        diagnostics.append(
            {
                "path": rel_path,
                "error_classification": classification,
                "error": error,
                "context": context,
                "backup": failure.get("backup"),
                "rolled_back": failure.get("rolled_back"),
            }
        )

    result = {
        "phase": "16U.175H-B",
        "failed_subset_count": len(failures),
        "error_classification_counts": dict(counts),
        "diagnostics": diagnostics,
        "passed": True,
        "status": "PASS_PHASE_16U175HB_DEDUPLICATION_FAILED_SUBSET_DIAGNOSTIC",
        "next_phase": "16U.175H-C_FAILED_SUBSET_DEDUPLICATION_REPAIR_MANIFEST",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.175H-B",
        "DEDUPLICATION FAILED-SUBSET DIAGNOSTIC",
        "=" * 48,
        f"status={result['status']}",
        f"failed_subset_count={result['failed_subset_count']}",
        "",
        "ERROR CLASSIFICATION COUNTS",
        "-" * 28,
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "FAILED SUBSET", "-" * 13])

    for item in diagnostics:
        ctx = item["context"]
        lines.append("")
        lines.append(f"{item['path']} :: {item['error_classification']}")
        lines.append(f"has_local_definition={ctx['has_local_definition']}")
        lines.append(f"local_definition_line={ctx['local_definition_line']}")
        lines.append(f"status_severity_lines={ctx['status_severity_line_numbers']}")
        lines.append(f"error={item['error']}")

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"failed_subset_count={result['failed_subset_count']}")
    print(f"error_classification_counts={result['error_classification_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
