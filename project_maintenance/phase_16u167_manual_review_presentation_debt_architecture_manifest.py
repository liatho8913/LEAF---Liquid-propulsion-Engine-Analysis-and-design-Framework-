from __future__ import annotations

from pathlib import Path
from collections import Counter
import json


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u164_high_risk_presentation_debt_manifest.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u167_manual_review_presentation_debt_architecture_manifest.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u167_manual_review_presentation_debt_architecture_manifest.txt"


def classify_architecture_action(item: dict) -> str:
    joined = "\n".join(s["line"] for s in item.get("sample_lines", []))

    if "severity" in joined or "status_severity" in joined:
        return "VERIFY_SHARED_SEVERITY_USAGE"

    if "presentation" in joined:
        return "VERIFY_PRESENTATION_OWNER_BOUNDARY"

    if "LegacyCompatibilityProducer" in joined:
        return "VERIFY_LEGACY_COMPATIBILITY_BOUNDARY"

    return "MANUAL_LINE_CONTEXT_REQUIRED"


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))

    manifest = [
        item for item in data.get("manifest", [])
        if item.get("patch_mode") != "SAFE_TRANSACTIONAL_WAVE_CANDIDATE"
    ]

    action_counts = Counter()
    enriched = []

    for item in manifest:
        action = classify_architecture_action(item)
        action_counts[action] += 1

        enriched.append(
            {
                **item,
                "architecture_action": action,
            }
        )

    enriched.sort(
        key=lambda item: (
            item["architecture_action"],
            -item["finding_count"],
            item["path"],
        )
    )

    result = {
        "phase": "16U.167",
        "manual_review_file_count": len(enriched),
        "manual_review_finding_count": sum(item["finding_count"] for item in enriched),
        "architecture_action_counts": dict(action_counts),
        "manual_review_manifest": enriched,
        "passed": True,
        "status": "PASS_PHASE_16U167_MANUAL_REVIEW_PRESENTATION_DEBT_ARCHITECTURE_MANIFEST",
        "next_phase": "16U.168_PRESENTATION_DEBT_CONTEXT_EXTRACTOR",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.167",
        "MANUAL REVIEW PRESENTATION DEBT ARCHITECTURE MANIFEST",
        "=" * 60,
        f"status={result['status']}",
        f"manual_review_file_count={result['manual_review_file_count']}",
        f"manual_review_finding_count={result['manual_review_finding_count']}",
        "",
        "ARCHITECTURE ACTION COUNTS",
        "-" * 28,
    ]

    for key, value in sorted(action_counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "MANUAL REVIEW FILES", "-" * 19])

    for item in enriched:
        lines.append("")
        lines.append(f"{item['path']}")
        lines.append(f"  finding_count={item['finding_count']}")
        lines.append(f"  architecture_action={item['architecture_action']}")
        lines.append(f"  patterns={', '.join(item['patterns'])}")
        for sample in item.get("sample_lines", [])[:3]:
            lines.append(
                f"  line {sample['line_number']} [{sample['pattern']}]: {sample['line']}"
            )

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"manual_review_file_count={result['manual_review_file_count']}")
    print(f"manual_review_finding_count={result['manual_review_finding_count']}")
    print(f"architecture_action_counts={result['architecture_action_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
