from __future__ import annotations

from pathlib import Path
from collections import Counter
import ast
import json
import re


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u175d_local_status_severity_definition_equivalence_audit.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u175e_local_status_severity_semantic_variant_classifier.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u175e_local_status_severity_semantic_variant_classifier.txt"


def classify_source(source: str | None) -> str:
    if not source:
        return "NO_LOCAL_DEFINITION_SOURCE"

    upper = source.upper()

    has_pass = "PASS" in upper
    has_warn = "WARN" in upper
    has_fail = "FAIL" in upper

    uses_prefix = ".STARTSWITH" in upper or "STARTSWITH(" in upper
    uses_split = ".SPLIT" in upper or "SPLIT(" in upper
    uses_dict = "{" in source and ":" in source
    has_unknown = "UNKNOWN" in upper
    has_blocked = "BLOCKED" in upper
    has_error = "ERROR" in upper

    if has_pass and has_warn and has_fail and uses_prefix and not (has_unknown or has_blocked or has_error):
        return "CANONICAL_PREFIX_TRIPLE_VARIANT"

    if has_pass and has_warn and has_fail and uses_split:
        return "SPLIT_PREFIX_TRIPLE_VARIANT"

    if has_pass and has_warn and has_fail and uses_dict:
        return "MAPPING_BASED_TRIPLE_VARIANT"

    if has_pass and has_warn and has_fail and (has_unknown or has_blocked or has_error):
        return "EXTENDED_SEVERITY_VARIANT"

    if has_pass and has_warn and has_fail:
        return "TRIPLE_SEVERITY_VARIANT_UNKNOWN_FORM"

    return "NONSTANDARD_STATUS_SEVERITY_VARIANT"


def extract_returns(source: str | None) -> list[str]:
    if not source:
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    returns = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Return):
            try:
                returns.append(ast.unparse(node.value))
            except Exception:
                returns.append("<unparse_failed>")

    return returns


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))

    entries = []
    counts = Counter()

    for item in data.get("entries", []):
        source = item.get("local_source")
        variant = classify_source(source)
        returns = extract_returns(source)

        counts[variant] += 1

        entries.append(
            {
                "path": item["path"],
                "equivalence": item["equivalence"],
                "variant": variant,
                "local_start_line": item.get("local_start_line"),
                "local_end_line": item.get("local_end_line"),
                "returns": returns,
                "local_source_preview": source,
            }
        )

    result = {
        "phase": "16U.175E",
        "variant_count": len(entries),
        "variant_counts": dict(counts),
        "entries": entries,
        "passed": True,
        "status": "PASS_PHASE_16U175E_LOCAL_STATUS_SEVERITY_SEMANTIC_VARIANT_CLASSIFIER",
        "next_phase": "16U.175F_LOCAL_STATUS_SEVERITY_DEDUPLICATION_MANIFEST",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.175E",
        "LOCAL STATUS SEVERITY SEMANTIC VARIANT CLASSIFIER",
        "=" * 60,
        f"status={result['status']}",
        f"variant_count={result['variant_count']}",
        "",
        "VARIANT COUNTS",
        "-" * 14,
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "ENTRIES", "-" * 7])

    for item in entries:
        lines.append("")
        lines.append(
            f"{item['path']} :: {item['variant']} "
            f"lines={item['local_start_line']}-{item['local_end_line']}"
        )
        lines.append(f"returns={item['returns']}")

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"variant_count={result['variant_count']}")
    print(f"variant_counts={result['variant_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
