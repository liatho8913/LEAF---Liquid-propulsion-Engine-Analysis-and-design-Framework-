from __future__ import annotations

from pathlib import Path
from collections import Counter
import json
import re


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u171c_comparison_operand_diagnostic.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u171d_exact_status_code_guardrail_audit.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u171d_exact_status_code_guardrail_audit.txt"

STATUS_LITERAL_RE = re.compile(r'["\'](?P<literal>(PASS|WARN|FAIL)(?:_[A-Z0-9]+)+)["\']')


def classify_literal(literal: str) -> str:
    parts = literal.split("_")

    if len(parts) == 1:
        return "PURE_SEVERITY_LITERAL"

    if len(parts) == 2 and parts[1] in {"PASS", "WARN", "FAIL"}:
        return "SUFFIX_SEVERITY_LITERAL"

    return "EXACT_STATUS_CODE_LITERAL"


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))

    entries = []
    counts = Counter()

    for item in data.get("diagnostics", []):
        statement = item.get("compact_statement", "")
        literals = [m.group("literal") for m in STATUS_LITERAL_RE.finditer(statement)]

        if not literals:
            classification = "NO_STATUS_CODE_LITERAL"
        else:
            literal_classes = [classify_literal(literal) for literal in literals]
            if all(cls == "EXACT_STATUS_CODE_LITERAL" for cls in literal_classes):
                classification = "EXACT_STATUS_CODE_LOGIC_REQUIRED"
            elif any(cls == "EXACT_STATUS_CODE_LITERAL" for cls in literal_classes):
                classification = "MIXED_EXACT_AND_SEVERITY_REVIEW_REQUIRED"
            else:
                classification = "SEVERITY_ONLY_LOGIC_CANDIDATE"

        counts[classification] += 1

        entries.append(
            {
                "path": item["path"],
                "line_number": item["line_number"],
                "statement_start_line": item["statement_start_line"],
                "statement_end_line": item["statement_end_line"],
                "statement": item["statement"],
                "compact_statement": statement,
                "status_literals": literals,
                "guardrail_classification": classification,
            }
        )

    result = {
        "phase": "16U.171D",
        "audited_count": len(entries),
        "guardrail_counts": dict(counts),
        "entries": entries,
        "passed": True,
        "status": "PASS_PHASE_16U171D_EXACT_STATUS_CODE_GUARDRAIL_AUDIT",
        "next_phase": "16U.171E_EXACT_STATUS_CODE_OWNERSHIP_MANIFEST",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.171D",
        "EXACT STATUS CODE GUARDRAIL AUDIT",
        "=" * 43,
        f"status={result['status']}",
        f"audited_count={result['audited_count']}",
        "",
        "GUARDRAIL COUNTS",
        "-" * 17,
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "ENTRIES", "-" * 7])

    for item in entries:
        lines.append("")
        lines.append(
            f"{item['path']}:{item['line_number']} "
            f"[{item['guardrail_classification']}]"
        )
        lines.append(f"status_literals={item['status_literals']}")
        lines.append(f"statement={item['compact_statement']}")

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"audited_count={result['audited_count']}")
    print(f"guardrail_counts={result['guardrail_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
