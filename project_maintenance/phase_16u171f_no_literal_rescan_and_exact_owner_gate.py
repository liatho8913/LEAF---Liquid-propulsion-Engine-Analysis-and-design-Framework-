from __future__ import annotations

from pathlib import Path
from collections import Counter
import json
import re


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u171e_exact_status_code_ownership_manifest.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u171f_no_literal_rescan_and_exact_owner_gate.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u171f_no_literal_rescan_and_exact_owner_gate.txt"

STATUS_CODE_RE = re.compile(r'["\']((PASS|WARN|FAIL)(?:_[A-Z0-9]+)+)["\']')
SEVERITY_RE = re.compile(r'["\'](PASS|WARN|FAIL)["\']')


def rescan_statement(statement: str) -> str:
    if STATUS_CODE_RE.search(statement):
        return "EXACT_STATUS_CODE_FOUND_ON_RESCAN"

    if SEVERITY_RE.search(statement):
        return "PURE_SEVERITY_LITERAL_FOUND_ON_RESCAN"

    if "PASS" in statement or "WARN" in statement or "FAIL" in statement:
        return "UNQUOTED_STATUS_TOKEN_REVIEW_REQUIRED"

    return "NO_STATUS_TOKEN_PRESENT"


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))

    exact_owned = []
    unresolved = []
    counts = Counter()

    for item in data.get("entries", []):
        action = item.get("ownership_action")

        if action in {
            "LOCAL_STATUS_STATE_MACHINE_OWNER_REQUIRED",
            "RESULTS_PAYLOAD_EXACT_STATUS_OWNER_REQUIRED",
        }:
            exact_owned.append(item)
            counts[action] += 1
            continue

        if action == "NO_LITERAL_RESCAN_REQUIRED":
            rescan = rescan_statement(item.get("statement", ""))
            enriched = {
                **item,
                "rescan_result": rescan,
            }
            unresolved.append(enriched)
            counts[rescan] += 1
            continue

        counts[action or "UNKNOWN"] += 1

    passed = (
        len(exact_owned) == 52
        and all(item.get("ownership_action") for item in exact_owned)
    )

    result = {
        "phase": "16U.171F",
        "exact_owned_count": len(exact_owned),
        "unresolved_count": len(unresolved),
        "counts": dict(counts),
        "exact_owned_entries": exact_owned,
        "unresolved_entries": unresolved,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U171F_NO_LITERAL_RESCAN_AND_EXACT_OWNER_GATE"
            if passed
            else "FAIL_PHASE_16U171F_NO_LITERAL_RESCAN_AND_EXACT_OWNER_GATE"
        ),
        "next_phase": "16U.172_WAVE2_REGRESSION_AND_RECLASSIFICATION",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.171F",
        "NO-LITERAL RESCAN AND EXACT OWNER GATE",
        "=" * 46,
        f"status={result['status']}",
        f"exact_owned_count={result['exact_owned_count']}",
        f"unresolved_count={result['unresolved_count']}",
        "",
        "COUNTS",
        "-" * 6,
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "UNRESOLVED ENTRIES", "-" * 18])

    if unresolved:
        for item in unresolved:
            lines.append("")
            lines.append(
                f"{item['path']}:{item['line_number']} "
                f"[{item['rescan_result']}]"
            )
            lines.append(f"statement={item['compact_statement']}")
    else:
        lines.append("No unresolved entries.")

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"exact_owned_count={result['exact_owned_count']}")
    print(f"unresolved_count={result['unresolved_count']}")
    print(f"counts={result['counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
