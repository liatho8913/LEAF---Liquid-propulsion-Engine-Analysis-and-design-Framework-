from __future__ import annotations

from pathlib import Path
from collections import Counter, defaultdict
import json


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u171d_exact_status_code_guardrail_audit.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u171e_exact_status_code_ownership_manifest.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u171e_exact_status_code_ownership_manifest.txt"


def classify_exact_code_owner(item: dict) -> str:
    statement = item.get("compact_statement", "")

    if "results.get(" in statement:
        return "RESULTS_PAYLOAD_EXACT_STATUS_OWNER_REQUIRED"

    if " status " in f" {statement} " or statement.startswith(("if status", "elif status")):
        return "LOCAL_STATUS_STATE_MACHINE_OWNER_REQUIRED"

    if "get(" in statement:
        return "MAPPING_LOOKUP_EXACT_STATUS_OWNER_REQUIRED"

    return "EXACT_STATUS_CODE_OWNER_REVIEW_REQUIRED"


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))

    entries = data.get("entries", [])

    owned = []
    owner_counts = Counter()
    by_file = defaultdict(list)

    for item in entries:
        classification = item["guardrail_classification"]

        if classification == "EXACT_STATUS_CODE_LOGIC_REQUIRED":
            owner = classify_exact_code_owner(item)
        elif classification == "NO_STATUS_CODE_LITERAL":
            owner = "NO_LITERAL_RESCAN_REQUIRED"
        else:
            owner = "MIXED_REVIEW_REQUIRED"

        owner_counts[owner] += 1

        enriched = {
            **item,
            "ownership_action": owner,
        }

        owned.append(enriched)
        by_file[item["path"]].append(enriched)

    result = {
        "phase": "16U.171E",
        "entry_count": len(owned),
        "ownership_action_counts": dict(owner_counts),
        "files": {
            path: items
            for path, items in sorted(by_file.items())
        },
        "entries": owned,
        "passed": True,
        "status": "PASS_PHASE_16U171E_EXACT_STATUS_CODE_OWNERSHIP_MANIFEST",
        "next_phase": "16U.171F_NO_LITERAL_RESCAN_AND_EXACT_OWNER_GATE",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.171E",
        "EXACT STATUS CODE OWNERSHIP MANIFEST",
        "=" * 45,
        f"status={result['status']}",
        f"entry_count={result['entry_count']}",
        "",
        "OWNERSHIP ACTION COUNTS",
        "-" * 24,
    ]

    for key, value in sorted(owner_counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "FILES", "-" * 5])

    for path, items in sorted(by_file.items()):
        lines.append("")
        lines.append(path)
        for item in items:
            lines.append(
                f"  line {item['line_number']} "
                f"[{item['ownership_action']}]: {item['compact_statement']}"
            )

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"entry_count={result['entry_count']}")
    print(f"ownership_action_counts={result['ownership_action_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
