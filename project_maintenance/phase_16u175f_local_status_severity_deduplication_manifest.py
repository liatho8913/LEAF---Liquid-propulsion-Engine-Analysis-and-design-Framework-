from __future__ import annotations

from pathlib import Path
from collections import Counter
import json


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u175e_local_status_severity_semantic_variant_classifier.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u175f_local_status_severity_deduplication_manifest.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u175f_local_status_severity_deduplication_manifest.txt"


def dedupe_action(entry: dict) -> str:
    variant = entry.get("variant")

    if variant == "EXTENDED_SEVERITY_VARIANT":
        return "UPGRADE_SHARED_OWNER_THEN_DEDUPLICATE"

    if variant in {
        "CANONICAL_PREFIX_TRIPLE_VARIANT",
        "SPLIT_PREFIX_TRIPLE_VARIANT",
        "MAPPING_BASED_TRIPLE_VARIANT",
    }:
        return "SAFE_DEDUPLICATE_TO_SHARED_OWNER"

    if variant == "NO_LOCAL_DEFINITION_SOURCE":
        return "RESCAN_OR_FALSE_POSITIVE"

    return "MANUAL_REVIEW_REQUIRED"


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))

    entries = []
    counts = Counter()

    for entry in data.get("entries", []):
        action = dedupe_action(entry)
        counts[action] += 1

        entries.append(
            {
                "path": entry["path"],
                "variant": entry["variant"],
                "deduplication_action": action,
                "local_start_line": entry.get("local_start_line"),
                "local_end_line": entry.get("local_end_line"),
                "returns": entry.get("returns", []),
            }
        )

    result = {
        "phase": "16U.175F",
        "deduplication_candidate_count": len(entries),
        "deduplication_action_counts": dict(counts),
        "entries": entries,
        "passed": True,
        "status": "PASS_PHASE_16U175F_LOCAL_STATUS_SEVERITY_DEDUPLICATION_MANIFEST",
        "next_phase": "16U.175G_SHARED_STATUS_SEVERITY_EXTENDED_OWNER_UPGRADE",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.175F",
        "LOCAL STATUS SEVERITY DEDUPLICATION MANIFEST",
        "=" * 54,
        f"status={result['status']}",
        f"deduplication_candidate_count={result['deduplication_candidate_count']}",
        "",
        "DEDUPLICATION ACTION COUNTS",
        "-" * 27,
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "ENTRIES", "-" * 7])

    for entry in entries:
        lines.append(
            f"{entry['path']} :: {entry['deduplication_action']} "
            f"variant={entry['variant']} "
            f"lines={entry['local_start_line']}-{entry['local_end_line']}"
        )

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"deduplication_candidate_count={result['deduplication_candidate_count']}")
    print(f"deduplication_action_counts={result['deduplication_action_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
