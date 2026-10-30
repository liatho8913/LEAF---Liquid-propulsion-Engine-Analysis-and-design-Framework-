from __future__ import annotations

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u167_manual_review_presentation_debt_architecture_manifest.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u168_presentation_debt_context_extractor.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u168_presentation_debt_context_extractor.txt"


CONTROL_FLOW_MARKERS = (
    "if ",
    "elif ",
    "while ",
    "return ",
    "raise ",
    "assert ",
)

HARmless_TEXT_MARKERS = (
    "print(",
    "lines.append",
    "report_lines.append",
    "text.append",
    "json.dumps",
    "status =",
    '"status"',
    "'status'",
)


def classify_line(line: str) -> str:
    stripped = line.strip()

    if any(stripped.startswith(marker) for marker in CONTROL_FLOW_MARKERS):
        return "ACTIVE_CONTROL_FLOW_REVIEW_REQUIRED"

    if any(marker in stripped for marker in HARmless_TEXT_MARKERS):
        return "LIKELY_REPORT_OR_CERTIFICATE_TEXT"

    if "status_severity(" in stripped:
        return "LIKELY_SHARED_SEVERITY_USAGE"

    return "UNKNOWN_CONTEXT_REVIEW_REQUIRED"


def get_context(path: Path, line_number: int, radius: int = 4) -> list[dict]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(1, line_number - radius)
    end = min(len(lines), line_number + radius)

    return [
        {
            "line_number": idx,
            "is_target": idx == line_number,
            "line": lines[idx - 1],
        }
        for idx in range(start, end + 1)
    ]


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    manifest = data.get("manual_review_manifest", [])

    extracted = []
    counts = {}

    for item in manifest:
        path = ROOT / item["path"]

        file_entry = {
            "path": item["path"],
            "finding_count": item["finding_count"],
            "contexts": [],
        }

        for sample in item.get("sample_lines", []):
            line_number = sample["line_number"]

            if not path.exists():
                classification = "MISSING_FILE"
                context = []
            else:
                context = get_context(path, line_number)
                target_line = sample["line"]
                classification = classify_line(target_line)

            counts[classification] = counts.get(classification, 0) + 1

            file_entry["contexts"].append(
                {
                    "line_number": line_number,
                    "pattern": sample["pattern"],
                    "line": sample["line"],
                    "context_classification": classification,
                    "context": context,
                }
            )

        extracted.append(file_entry)

    result = {
        "phase": "16U.168",
        "manual_review_file_count": len(extracted),
        "sample_context_count": sum(len(item["contexts"]) for item in extracted),
        "context_classification_counts": counts,
        "context_manifest": extracted,
        "passed": True,
        "status": "PASS_PHASE_16U168_PRESENTATION_DEBT_CONTEXT_EXTRACTOR",
        "next_phase": "16U.169_ACTIVE_CONTROL_FLOW_PRESENTATION_DEBT_MANIFEST",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.168",
        "PRESENTATION DEBT CONTEXT EXTRACTOR",
        "=" * 44,
        f"status={result['status']}",
        f"manual_review_file_count={result['manual_review_file_count']}",
        f"sample_context_count={result['sample_context_count']}",
        "",
        "CONTEXT CLASSIFICATION COUNTS",
        "-" * 31,
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "CONTEXT MANIFEST", "-" * 16])

    for item in extracted:
        lines.append("")
        lines.append(item["path"])
        for ctx in item["contexts"][:4]:
            lines.append(
                f"  line {ctx['line_number']} "
                f"[{ctx['context_classification']}]: {ctx['line']}"
            )
            for row in ctx["context"]:
                marker = ">>" if row["is_target"] else "  "
                lines.append(f"    {marker} {row['line_number']:5d}: {row['line']}")

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"manual_review_file_count={result['manual_review_file_count']}")
    print(f"sample_context_count={result['sample_context_count']}")
    print(f"context_classification_counts={result['context_classification_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
