from __future__ import annotations

from pathlib import Path
from collections import Counter
import json


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u169_active_control_flow_presentation_debt_manifest.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u170_structural_predicate_patchability_audit.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u170_structural_predicate_patchability_audit.txt"


STATUS_TOKENS = ("PASS", "WARN", "FAIL")


def load_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def extract_statement(lines: list[str], line_number: int) -> dict:
    idx = line_number - 1
    start = idx
    end = idx

    while start > 0:
        prev = lines[start - 1]
        current = lines[start]

        if current.startswith((" ", "\t")) and not current.lstrip().startswith(("if ", "elif ", "return ", "assert ")):
            start -= 1
            continue

        if prev.rstrip().endswith(("\\", "(", "[", "{", "and", "or")):
            start -= 1
            continue

        break

    paren_balance = 0
    for j in range(start, min(len(lines), start + 20)):
        text = lines[j]
        paren_balance += text.count("(") - text.count(")")
        end = j

        if j >= idx and paren_balance <= 0 and not text.rstrip().endswith(("\\", "and", "or")):
            break

    statement = "\n".join(lines[start:end + 1])

    return {
        "start_line": start + 1,
        "end_line": end + 1,
        "statement": statement,
    }


def classify_patchability(statement: str) -> str:
    if "status_severity(" in statement:
        return "ALREADY_SHARED_SEVERITY"

    if any(token in statement for token in STATUS_TOKENS) and "==" in statement:
        return "SAFE_EQUALITY_LITERAL_CANDIDATE"

    if any(token in statement for token in STATUS_TOKENS) and "!=" in statement:
        return "SAFE_INEQUALITY_LITERAL_CANDIDATE"

    if any(token in statement for token in STATUS_TOKENS) and " in " in statement:
        return "MEMBERSHIP_REVIEW_CANDIDATE"

    return "MANUAL_REVIEW_REQUIRED"


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    entries = data.get("entries", [])

    audited = []
    counts = Counter()

    for entry in entries:
        path = ROOT / entry["path"]

        if not path.exists():
            patchability = "MISSING_FILE"
            statement = {
                "start_line": entry["line_number"],
                "end_line": entry["line_number"],
                "statement": "",
            }
        else:
            lines = load_lines(path)
            statement = extract_statement(lines, entry["line_number"])
            patchability = classify_patchability(statement["statement"])

        counts[patchability] += 1

        audited.append(
            {
                **entry,
                "statement_start_line": statement["start_line"],
                "statement_end_line": statement["end_line"],
                "statement": statement["statement"],
                "patchability": patchability,
            }
        )

    result = {
        "phase": "16U.170",
        "audited_predicate_count": len(audited),
        "patchability_counts": dict(counts),
        "audited_predicates": audited,
        "passed": True,
        "status": "PASS_PHASE_16U170_STRUCTURAL_PREDICATE_PATCHABILITY_AUDIT",
        "next_phase": "16U.171_EQUALITY_INEQUALITY_LITERAL_CLEANUP_WAVE_2",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines_out = [
        "LEAF PHASE 16U.170",
        "STRUCTURAL PREDICATE PATCHABILITY AUDIT",
        "=" * 48,
        f"status={result['status']}",
        f"audited_predicate_count={result['audited_predicate_count']}",
        "",
        "PATCHABILITY COUNTS",
        "-" * 20,
    ]

    for key, value in sorted(counts.items()):
        lines_out.append(f"{key}={value}")

    lines_out.extend(["", "AUDITED PREDICATES", "-" * 18])

    for item in audited:
        lines_out.append("")
        lines_out.append(
            f"{item['path']}:{item['line_number']} "
            f"[{item['patchability']}]"
        )
        lines_out.append(
            f"statement_lines={item['statement_start_line']}-{item['statement_end_line']}"
        )
        for offset, line in enumerate(item["statement"].splitlines(), start=item["statement_start_line"]):
            marker = ">>" if offset == item["line_number"] else "  "
            lines_out.append(f"{marker} {offset:5d}: {line}")

    lines_out.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines_out), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"audited_predicate_count={result['audited_predicate_count']}")
    print(f"patchability_counts={result['patchability_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
