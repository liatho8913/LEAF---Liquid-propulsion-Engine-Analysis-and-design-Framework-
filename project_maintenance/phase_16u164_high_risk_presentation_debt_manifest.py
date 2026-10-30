from __future__ import annotations

from pathlib import Path
from collections import Counter
import json


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u163_presentation_debt_classification.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u164_high_risk_presentation_debt_manifest.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u164_high_risk_presentation_debt_manifest.txt"


SAFE_WAVE_PATTERNS = (
    ".startswith(",
    ".endswith(",
)

MANUAL_REVIEW_MARKERS = (
    "severity",
    "presentation",
    "LegacyCompatibilityProducer",
    "status_severity",
)


def classify_patch_mode(findings: list[dict]) -> str:
    lines = "\n".join(f["line"] for f in findings)

    if any(marker in lines for marker in MANUAL_REVIEW_MARKERS):
        return "MANUAL_ARCHITECTURE_REVIEW"

    if any(pattern in lines for pattern in SAFE_WAVE_PATTERNS):
        return "SAFE_TRANSACTIONAL_WAVE_CANDIDATE"

    return "MANUAL_REVIEW_REQUIRED"


def main() -> dict:
    if not IN_JSON.exists():
        raise FileNotFoundError(f"Missing classifier file: {IN_JSON}")

    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    high_risk_files = data.get("high_risk_files", {})

    manifest = []
    mode_counts = Counter()

    for path, findings in sorted(high_risk_files.items()):
        patch_mode = classify_patch_mode(findings)
        mode_counts[patch_mode] += 1

        manifest.append(
            {
                "path": path,
                "finding_count": len(findings),
                "patch_mode": patch_mode,
                "patterns": sorted(set(f["pattern"] for f in findings)),
                "sample_lines": [
                    {
                        "line_number": f["line_number"],
                        "pattern": f["pattern"],
                        "line": f["line"],
                    }
                    for f in findings[:8]
                ],
            }
        )

    manifest.sort(
        key=lambda item: (
            item["patch_mode"] != "SAFE_TRANSACTIONAL_WAVE_CANDIDATE",
            -item["finding_count"],
            item["path"],
        )
    )

    safe_wave_candidates = [
        item for item in manifest
        if item["patch_mode"] == "SAFE_TRANSACTIONAL_WAVE_CANDIDATE"
    ]

    result = {
        "phase": "16U.164",
        "source_classification": str(IN_JSON),
        "high_risk_file_count": len(manifest),
        "high_risk_finding_count": sum(item["finding_count"] for item in manifest),
        "patch_mode_counts": dict(mode_counts),
        "safe_wave_candidate_count": len(safe_wave_candidates),
        "safe_wave_candidates": safe_wave_candidates,
        "manifest": manifest,
        "passed": True,
        "status": "PASS_PHASE_16U164_HIGH_RISK_PRESENTATION_DEBT_MANIFEST",
        "next_phase": "16U.165_SAFE_TRANSACTIONAL_PRESENTATION_DEBT_CLEANUP_WAVE_1",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.164",
        "HIGH-RISK PRESENTATION DEBT MANIFEST",
        "=" * 46,
        f"status={result['status']}",
        f"high_risk_file_count={result['high_risk_file_count']}",
        f"high_risk_finding_count={result['high_risk_finding_count']}",
        f"safe_wave_candidate_count={result['safe_wave_candidate_count']}",
        "",
        "PATCH MODE COUNTS",
        "-" * 17,
    ]

    for key, value in sorted(mode_counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "SAFE TRANSACTIONAL WAVE CANDIDATES", "-" * 36])

    if safe_wave_candidates:
        for item in safe_wave_candidates[:30]:
            lines.append(f"{item['finding_count']:4d}  {item['path']}")
    else:
        lines.append("No safe transactional candidates identified.")

    lines.extend(["", "FULL HIGH-RISK MANIFEST", "-" * 23])

    for item in manifest:
        lines.append("")
        lines.append(f"{item['path']}")
        lines.append(f"  finding_count={item['finding_count']}")
        lines.append(f"  patch_mode={item['patch_mode']}")
        lines.append(f"  patterns={', '.join(item['patterns'])}")
        for sample in item["sample_lines"][:3]:
            lines.append(
                f"  line {sample['line_number']} [{sample['pattern']}]: {sample['line']}"
            )

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"high_risk_file_count={result['high_risk_file_count']}")
    print(f"high_risk_finding_count={result['high_risk_finding_count']}")
    print(f"safe_wave_candidate_count={result['safe_wave_candidate_count']}")
    print(f"patch_mode_counts={result['patch_mode_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
