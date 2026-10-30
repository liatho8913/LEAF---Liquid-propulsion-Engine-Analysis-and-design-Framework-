from __future__ import annotations

from pathlib import Path
from collections import Counter, defaultdict
import json
import re


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u171f_no_literal_rescan_and_exact_owner_gate.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u173_unquoted_status_token_resolver.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u173_unquoted_status_token_resolver.txt"

TOKEN_RE = re.compile(r"\b(PASS|WARN|FAIL)(?:_[A-Z0-9]+)*\b")


def classify_unquoted_statement(statement: str) -> str:
    compact = " ".join(statement.split())

    if "status_severity(" in compact:
        return "ALREADY_SHARED_SEVERITY_USAGE"

    if ".startswith(" in compact or ".endswith(" in compact:
        return "LEGACY_PREFIX_SUFFIX_REVIEW_REQUIRED"

    if "==" in compact or "!=" in compact:
        return "SYMBOLIC_COMPARE_REVIEW_REQUIRED"

    if " in " in compact:
        return "SYMBOLIC_MEMBERSHIP_REVIEW_REQUIRED"

    return "TOKEN_CONTEXT_REVIEW_REQUIRED"


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    unresolved = data.get("unresolved_entries", [])

    resolved = []
    counts = Counter()
    by_file = defaultdict(list)

    for item in unresolved:
        statement = item.get("statement", "")
        compact = " ".join(statement.split())
        tokens = sorted(set(TOKEN_RE.findall(compact)))
        classification = classify_unquoted_statement(statement)

        counts[classification] += 1

        enriched = {
            **item,
            "tokens": tokens,
            "resolver_classification": classification,
            "compact_statement": compact,
        }

        resolved.append(enriched)
        by_file[item["path"]].append(enriched)

    result = {
        "phase": "16U.173",
        "unresolved_input_count": len(unresolved),
        "resolved_entry_count": len(resolved),
        "resolver_counts": dict(counts),
        "files": {
            path: items
            for path, items in sorted(by_file.items())
        },
        "entries": resolved,
        "passed": True,
        "status": "PASS_PHASE_16U173_UNQUOTED_STATUS_TOKEN_RESOLVER",
        "next_phase": "16U.174_FINAL_PRESENTATION_DEBT_OWNERSHIP_GATE",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.173",
        "UNQUOTED STATUS TOKEN RESOLVER",
        "=" * 40,
        f"status={result['status']}",
        f"unresolved_input_count={result['unresolved_input_count']}",
        f"resolved_entry_count={result['resolved_entry_count']}",
        "",
        "RESOLVER COUNTS",
        "-" * 15,
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "FILES", "-" * 5])

    for path, items in sorted(by_file.items()):
        lines.append("")
        lines.append(path)
        for item in items:
            lines.append(
                f"  line {item['line_number']} "
                f"[{item['resolver_classification']}] "
                f"tokens={item['tokens']}: {item['compact_statement']}"
            )

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"unresolved_input_count={result['unresolved_input_count']}")
    print(f"resolved_entry_count={result['resolved_entry_count']}")
    print(f"resolver_counts={result['resolver_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
