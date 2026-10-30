from __future__ import annotations

from pathlib import Path
from collections import Counter
import json
import re


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u171b_wave2_patch_shape_diagnostic.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u171c_comparison_operand_diagnostic.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u171c_comparison_operand_diagnostic.txt"


COMPARE_RE = re.compile(
    r'(?P<left>.+?)\s*(?P<op>==|!=)\s*(?P<right>.+)'
)


def classify_operand_shape(statement: str) -> str:
    compact = " ".join(statement.split())

    if "status_severity(" in compact:
        return "ALREADY_SHARED_SEVERITY_COMPARE"

    if "_severity" in compact:
        return "LIKELY_SEVERITY_VARIABLE_COMPARE"

    if ".severity" in compact:
        return "LIKELY_SEVERITY_ATTRIBUTE_COMPARE"

    if "status" in compact.lower():
        return "LIKELY_STATUS_VARIABLE_COMPARE"

    return "UNKNOWN_COMPARE_OPERAND_SHAPE"


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))

    diagnostics = []
    counts = Counter()

    for item in data.get("diagnostics", []):
        statement = item["statement"]
        compact = " ".join(statement.split())
        shape = classify_operand_shape(statement)
        counts[shape] += 1

        match = COMPARE_RE.search(compact)

        diagnostics.append(
            {
                "path": item["path"],
                "line_number": item["line_number"],
                "shape": shape,
                "statement_start_line": item["statement_start_line"],
                "statement_end_line": item["statement_end_line"],
                "compact_statement": compact,
                "left_operand": match.group("left") if match else None,
                "operator": match.group("op") if match else None,
                "right_operand": match.group("right") if match else None,
                "statement": statement,
            }
        )

    result = {
        "phase": "16U.171C",
        "diagnostic_count": len(diagnostics),
        "operand_shape_counts": dict(counts),
        "diagnostics": diagnostics,
        "passed": True,
        "status": "PASS_PHASE_16U171C_COMPARISON_OPERAND_DIAGNOSTIC",
        "next_phase": "16U.171D_OPERAND_AWARE_LITERAL_CLEANUP_WAVE2",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.171C",
        "COMPARISON OPERAND DIAGNOSTIC",
        "=" * 39,
        f"status={result['status']}",
        f"diagnostic_count={result['diagnostic_count']}",
        "",
        "OPERAND SHAPE COUNTS",
        "-" * 21,
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "FIRST 40 COMPARISONS", "-" * 20])

    for item in diagnostics[:40]:
        lines.append("")
        lines.append(f"{item['path']}:{item['line_number']} [{item['shape']}]")
        lines.append(f"left={item['left_operand']}")
        lines.append(f"op={item['operator']}")
        lines.append(f"right={item['right_operand']}")
        lines.append(f"statement={item['compact_statement']}")

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"diagnostic_count={result['diagnostic_count']}")
    print(f"operand_shape_counts={result['operand_shape_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
