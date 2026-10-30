from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u162_global_repository_presentation_layer_sanity_audit.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u163_presentation_debt_classification.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u163_presentation_debt_classification.txt"


LOW_RISK_PATH_FRAGMENTS = (
    "project_maintenance/",
    "test_",
    "_test",
    "tests/",
    "archive/",
    "backup",
    "legacy",
)

HIGH_RISK_PATH_FRAGMENTS = (
    "leaf_qt/",
)

DOCUMENTATION_LINE_MARKERS = (
    "print(",
    "PASS_PHASE_",
    "FAIL_PHASE_",
    "WARN_PHASE_",
    "certificate",
    "report",
    "status=",
)

PRODUCTION_DEBT_MARKERS = (
    ".startswith(",
    ".endswith(",
    "if status",
    "if result",
    "severity",
    "presentation",
)


def classify_finding(finding: dict) -> str:
    path = finding["path"]
    line = finding["line"]

    if any(fragment in path for fragment in LOW_RISK_PATH_FRAGMENTS):
        return "LOW_RISK_MAINTENANCE_OR_TEST_EVIDENCE"

    if any(marker in line for marker in DOCUMENTATION_LINE_MARKERS):
        return "LOW_RISK_CERTIFICATE_OR_REPORT_LITERAL"

    if path.startswith(HIGH_RISK_PATH_FRAGMENTS):
        if any(marker in line for marker in PRODUCTION_DEBT_MARKERS):
            return "HIGH_RISK_PRODUCTION_PRESENTATION_LOGIC"
        return "MEDIUM_RISK_PRODUCTION_LITERAL"

    return "MEDIUM_RISK_UNCLASSIFIED_REPOSITORY_LITERAL"


def main() -> dict:
    if not IN_JSON.exists():
        raise FileNotFoundError(f"Missing 16U.162 audit file: {IN_JSON}")

    audit = json.loads(IN_JSON.read_text(encoding="utf-8"))
    findings = audit.get("findings", [])

    classified = []
    category_counts = Counter()
    file_counts = Counter()
    pattern_counts = Counter()
    high_risk_by_file = defaultdict(list)

    for finding in findings:
        category = classify_finding(finding)
        enriched = dict(finding)
        enriched["category"] = category

        classified.append(enriched)
        category_counts[category] += 1
        file_counts[finding["path"]] += 1
        pattern_counts[finding["pattern"]] += 1

        if category == "HIGH_RISK_PRODUCTION_PRESENTATION_LOGIC":
            high_risk_by_file[finding["path"]].append(enriched)

    result = {
        "phase": "16U.163",
        "source_audit": str(IN_JSON),
        "total_findings": len(findings),
        "category_counts": dict(category_counts),
        "pattern_counts": dict(pattern_counts),
        "top_files": file_counts.most_common(50),
        "high_risk_file_count": len(high_risk_by_file),
        "high_risk_finding_count": category_counts.get("HIGH_RISK_PRODUCTION_PRESENTATION_LOGIC", 0),
        "high_risk_files": {
            path: items[:25]
            for path, items in sorted(high_risk_by_file.items())
        },
        "classified_findings": classified,
        "passed": True,
        "status": "PASS_PHASE_16U163_PRESENTATION_DEBT_CLASSIFICATION",
        "next_phase": "16U.164_TARGETED_HIGH_RISK_PRESENTATION_DEBT_MANIFEST",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.163",
        "PRESENTATION DEBT CLASSIFICATION",
        "=" * 42,
        f"status={result['status']}",
        f"total_findings={result['total_findings']}",
        f"high_risk_file_count={result['high_risk_file_count']}",
        f"high_risk_finding_count={result['high_risk_finding_count']}",
        "",
        "CATEGORY COUNTS",
        "-" * 15,
    ]

    for key, value in sorted(category_counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "PATTERN COUNTS", "-" * 14])
    for key, value in sorted(pattern_counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "TOP FILES BY FINDING COUNT", "-" * 27])
    for path, count in file_counts.most_common(30):
        lines.append(f"{count:5d}  {path}")

    lines.extend(["", "HIGH RISK PRODUCTION FILES", "-" * 27])
    if high_risk_by_file:
        for path, items in sorted(high_risk_by_file.items()):
            lines.append(f"{len(items):5d}  {path}")
    else:
        lines.append("No high-risk production presentation logic detected.")

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"total_findings={result['total_findings']}")
    print(f"high_risk_file_count={result['high_risk_file_count']}")
    print(f"high_risk_finding_count={result['high_risk_finding_count']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
