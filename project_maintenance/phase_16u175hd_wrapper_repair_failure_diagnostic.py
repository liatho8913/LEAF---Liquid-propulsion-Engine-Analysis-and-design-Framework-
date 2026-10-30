from __future__ import annotations

from pathlib import Path
from collections import Counter
import json


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u175hc_failed_subset_compatibility_wrapper_repair.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u175hd_wrapper_repair_failure_diagnostic.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u175hd_wrapper_repair_failure_diagnostic.txt"


def classify_error(error: str) -> str:
    if "__future__ imports must occur" in error:
        return "IMPORT_INSERTED_BEFORE_FUTURE"

    if "IndentationError" in error:
        return "WRAPPER_INDENTATION_ERROR"

    if "expected an indented block" in error:
        return "EMPTY_BLOCK_AFTER_WRAPPER"

    if "invalid syntax" in error:
        return "WRAPPER_SYNTAX_ERROR"

    return "OTHER"


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    failures = data.get("compile_failures", [])

    diagnostics = []
    counts = Counter()

    for failure in failures:
        rel_path = failure["path"]
        path = ROOT / rel_path
        error = failure.get("error", "")
        classification = classify_error(error)
        counts[classification] += 1

        context_lines = []

        if path.exists():
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

            interesting = []
            for idx, line in enumerate(lines, start=1):
                if (
                    "def status_severity" in line
                    or "_leaf_shared_status_severity" in line
                    or "from __future__ import" in line
                    or "status_presentation" in line
                ):
                    interesting.append(idx)

            for idx in interesting[:20]:
                start = max(1, idx - 3)
                end = min(len(lines), idx + 6)
                context_lines.append(f"--- context around line {idx} ---")
                for line_no in range(start, end + 1):
                    marker = ">>" if line_no == idx else "  "
                    context_lines.append(f"{marker} {line_no:5d}: {lines[line_no - 1]}")

        diagnostics.append(
            {
                "path": rel_path,
                "classification": classification,
                "error": error,
                "context": context_lines,
            }
        )

    result = {
        "phase": "16U.175H-D",
        "failure_count": len(failures),
        "classification_counts": dict(counts),
        "diagnostics": diagnostics,
        "passed": True,
        "status": "PASS_PHASE_16U175HD_WRAPPER_REPAIR_FAILURE_DIAGNOSTIC",
        "next_phase": "16U.175H-E_CONTEXT_AWARE_WRAPPER_REPAIR",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.175H-D",
        "WRAPPER REPAIR FAILURE DIAGNOSTIC",
        "=" * 43,
        f"status={result['status']}",
        f"failure_count={result['failure_count']}",
        "",
        "CLASSIFICATION COUNTS",
        "-" * 21,
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "DIAGNOSTICS", "-" * 11])

    for item in diagnostics:
        lines.append("")
        lines.append(f"{item['path']} :: {item['classification']}")
        lines.append(f"error={item['error']}")
        lines.extend(item["context"][:80])

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"failure_count={result['failure_count']}")
    print(f"classification_counts={result['classification_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

