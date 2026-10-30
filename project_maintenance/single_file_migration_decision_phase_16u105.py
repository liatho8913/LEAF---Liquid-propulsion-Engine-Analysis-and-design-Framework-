from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


PHASE = "16U.105"
PASS_BANNER = "PASS_PHASE_16U105_SINGLE_FILE_MIGRATION_DECISION"
FAIL_BANNER = "FAIL_PHASE_16U105_SINGLE_FILE_MIGRATION_DECISION"

ROOT = Path(__file__).resolve().parents[1]

PREVIOUS_AUDIT_JSON = ROOT / "project_maintenance" / "updated_global_remaining_candidate_audit_phase_16u104.json"

OUT_TXT = ROOT / "project_maintenance" / "SINGLE_FILE_MIGRATION_DECISION_PHASE_16U105.txt"
OUT_JSON = ROOT / "project_maintenance" / "single_file_migration_decision_phase_16u105.json"

LEGACY_PATTERNS = [
    ("inline_pass_fail_ternary", re.compile(r'["\']PASS["\']\s+if\s+.+?\s+else\s+["\']FAIL["\']')),
    ("inline_fail_pass_ternary", re.compile(r'["\']FAIL["\']\s+if\s+.+?\s+else\s+["\']PASS["\']')),
    ("status_startswith", re.compile(r'\.startswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)')),
    ("status_endswith", re.compile(r'\.endswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)')),
    ("fail_in_status_text", re.compile(r'["\']FAIL["\']\s+in\s+')),
    ("warn_in_status_text", re.compile(r'["\']WARN["\']\s+in\s+')),
    ("pass_in_status_text", re.compile(r'["\']PASS["\']\s+in\s+')),
    ("blocked_in_status_text", re.compile(r'["\']BLOCKED["\']\s+in\s+')),
]


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def scan_file(rel_file: str) -> dict:
    path = ROOT / rel_file
    if not path.exists():
        return {
            "file": rel_file,
            "exists": False,
            "finding_count": 0,
            "findings": [],
            "risk_score": 9999,
            "decision": "MISSING",
        }

    text = path.read_text(encoding="utf-8", errors="replace")

    findings = []
    for name, pattern in LEGACY_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                {
                    "pattern": name,
                    "line": line_number(text, match.start()),
                    "snippet": text[match.start():match.end()].replace("\n", " ")[:160],
                }
            )

    risk = 0
    risk += len(findings) * 10

    name = Path(rel_file).name.lower()

    if "failure" in name:
        risk += 30
    if "validation" in name:
        risk += 25
    if "gate" in name:
        risk += 20
    if "report" in name:
        risk += 20
    if "optimisation" in name:
        risk += 15
    if "regen" in name:
        risk += 10

    if "from leaf_qt.status_presentation import" in text:
        risk -= 20

    decision = "SELECTABLE" if findings else "NO_FINDINGS"

    return {
        "file": rel_file,
        "exists": True,
        "finding_count": len(findings),
        "findings": findings[:30],
        "risk_score": risk,
        "imports_status_presentation": "from leaf_qt.status_presentation import" in text,
        "decision": decision,
    }


def main() -> dict:
    if not PREVIOUS_AUDIT_JSON.exists():
        result = {
            "phase": PHASE,
            "status": FAIL_BANNER,
            "error": f"missing previous audit: {PREVIOUS_AUDIT_JSON.relative_to(ROOT)}",
            "phase_16u105_single_file_migration_decision_complete": False,
        }
        OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    audit = json.loads(PREVIOUS_AUDIT_JSON.read_text(encoding="utf-8"))

    source_candidates = audit.get("single_file_required", [])
    if not source_candidates:
        source_candidates = audit.get("top_production_candidates", [])

    rescanned = []
    for item in source_candidates:
        rel_file = item.get("file")
        if rel_file:
            rescanned.append(scan_file(rel_file))

    selectable = [item for item in rescanned if item["decision"] == "SELECTABLE"]
    selectable.sort(key=lambda item: (-item["risk_score"], -item["finding_count"], item["file"]))

    selected = selectable[0] if selectable else None

    passed = selected is not None

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "previous_audit": str(PREVIOUS_AUDIT_JSON.relative_to(ROOT)),
        "source_candidate_count": len(source_candidates),
        "rescanned_count": len(rescanned),
        "selectable_count": len(selectable),
        "selected_target": selected,
        "top_selectable": selectable[:20],
        "phase_16u105_single_file_migration_decision_complete": passed,
        "next_phase": "16U.106 — Selected Single-File Presentation Layer Patch",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.105",
        "SINGLE-FILE MIGRATION DECISION",
        "==============================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Select the next highest-priority single-file-required production candidate.",
        "",
        "SUMMARY",
        "-------",
        f"Previous audit: {result['previous_audit']}",
        f"Source candidate count: {result['source_candidate_count']}",
        f"Rescanned count: {result['rescanned_count']}",
        f"Selectable count: {result['selectable_count']}",
        "",
        "SELECTED TARGET",
        "---------------",
    ]

    if selected:
        lines.extend(
            [
                f"File: {selected['file']}",
                f"Finding count: {selected['finding_count']}",
                f"Risk score: {selected['risk_score']}",
                f"Imports status presentation: {selected['imports_status_presentation']}",
            ]
        )
        for finding in selected["findings"][:10]:
            lines.append(f"  - line {finding['line']} [{finding['pattern']}]: {finding['snippet']}")
    else:
        lines.append("No selectable target found.")

    lines.extend(["", "TOP SELECTABLE", "--------------"])

    for idx, item in enumerate(selectable[:20], 1):
        lines.append(f"{idx}. {item['file']} | findings={item['finding_count']} | risk={item['risk_score']}")

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.105 COMPLETE." if passed else "PHASE 16U.105 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.106 — SELECTED SINGLE-FILE PRESENTATION LAYER PATCH",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"source_candidate_count={result.get('source_candidate_count')}")
    print(f"rescanned_count={result.get('rescanned_count')}")
    print(f"selectable_count={result.get('selectable_count')}")
    if result.get("selected_target"):
        print(f"selected_target={result['selected_target']['file']}")
        print(f"finding_count={result['selected_target']['finding_count']}")
        print(f"risk_score={result['selected_target']['risk_score']}")
    else:
        print("selected_target=None")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result.get("phase_16u105_single_file_migration_decision_complete"):
        raise SystemExit(1)
