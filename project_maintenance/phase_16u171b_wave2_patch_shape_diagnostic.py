from __future__ import annotations

from pathlib import Path
from collections import Counter
import json
import re


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u170_structural_predicate_patchability_audit.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u171b_wave2_patch_shape_diagnostic.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u171b_wave2_patch_shape_diagnostic.txt"

TARGET_PATCHABILITIES = {
    "SAFE_EQUALITY_LITERAL_CANDIDATE",
    "SAFE_INEQUALITY_LITERAL_CANDIDATE",
}

PATTERNS = {
    "RIGHT_LITERAL_SIMPLE_EXPR": re.compile(
        r'(?P<expr>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*|\[[^\]]+\])*)\s*(==|!=)\s*["\'](?:PASS|WARN|FAIL)["\']'
    ),
    "LEFT_LITERAL_SIMPLE_EXPR": re.compile(
        r'["\'](?:PASS|WARN|FAIL)["\']\s*(==|!=)\s*(?P<expr>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*|\[[^\]]+\])*)'
    ),
    "CONTAINS_STATUS_WORD": re.compile(r'(PASS|WARN|FAIL)'),
}


def classify_statement(statement: str) -> str:
    if PATTERNS["RIGHT_LITERAL_SIMPLE_EXPR"].search(statement):
        return "PATCHABLE_RIGHT_LITERAL_SIMPLE_EXPR"

    if PATTERNS["LEFT_LITERAL_SIMPLE_EXPR"].search(statement):
        return "PATCHABLE_LEFT_LITERAL_SIMPLE_EXPR"

    if "==" in statement or "!=" in statement:
        return "COMPARE_SHAPE_NOT_YET_SUPPORTED"

    if PATTERNS["CONTAINS_STATUS_WORD"].search(statement):
        return "STATUS_WORD_WITHOUT_DIRECT_COMPARE"

    return "NO_STATUS_COMPARE_FOUND"


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))

    diagnostics = []
    counts = Counter()

    for entry in data.get("audited_predicates", []):
        if entry.get("patchability") not in TARGET_PATCHABILITIES:
            continue

        statement = entry.get("statement", "")
        shape = classify_statement(statement)
        counts[shape] += 1

        diagnostics.append(
            {
                "path": entry["path"],
                "line_number": entry["line_number"],
                "patchability": entry["patchability"],
                "shape": shape,
                "statement_start_line": entry["statement_start_line"],
                "statement_end_line": entry["statement_end_line"],
                "statement": statement,
            }
        )

    result = {
        "phase": "16U.171B",
        "diagnostic_count": len(diagnostics),
        "shape_counts": dict(counts),
        "diagnostics": diagnostics,
        "passed": True,
        "status": "PASS_PHASE_16U171B_WAVE2_PATCH_SHAPE_DIAGNOSTIC",
        "next_phase": "16U.171C_STATEMENT_LEVEL_LITERAL_CLEANUP_WAVE2",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.171B",
        "WAVE 2 PATCH SHAPE DIAGNOSTIC",
        "=" * 40,
        f"status={result['status']}",
        f"diagnostic_count={result['diagnostic_count']}",
        "",
        "SHAPE COUNTS",
        "-" * 12,
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "DIAGNOSTICS", "-" * 11])

    for item in diagnostics:
        lines.append("")
        lines.append(
            f"{item['path']}:{item['line_number']} "
            f"[{item['shape']}]"
        )
        lines.append(
            f"statement_lines={item['statement_start_line']}-{item['statement_end_line']}"
        )
        for offset, line in enumerate(item["statement"].splitlines(), start=item["statement_start_line"]):
            marker = ">>" if offset == item["line_number"] else "  "
            lines.append(f"{marker} {offset:5d}: {line}")

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"diagnostic_count={result['diagnostic_count']}")
    print(f"shape_counts={result['shape_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
