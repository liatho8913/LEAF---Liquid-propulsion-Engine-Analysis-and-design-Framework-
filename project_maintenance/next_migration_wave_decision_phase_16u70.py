from __future__ import annotations

import ast
import json
import re
from datetime import datetime
from pathlib import Path


PHASE = "16U.70"
PASS_BANNER = "PASS_PHASE_16U70_NEXT_MIGRATION_WAVE_DECISION"
FAIL_BANNER = "FAIL_PHASE_16U70_NEXT_MIGRATION_WAVE_DECISION"

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "leaf_qt/failure_root_cause_owner.py",
    ROOT / "leaf_qt/regen_completion_gate_validation_owner.py",
    ROOT / "leaf_qt/regen_system_signoff_validation_owner.py",
    ROOT / "leaf_qt/regen_optimisation_scoring_owner.py",
]

OUT_TXT = ROOT / "project_maintenance" / "NEXT_MIGRATION_WAVE_DECISION_PHASE_16U70.txt"
OUT_JSON = ROOT / "project_maintenance" / "next_migration_wave_decision_phase_16u70.json"

LEGACY_PATTERNS = [
    ("fail_in_status_text", re.compile(r'["\']FAIL["\']\s+in\s+')),
    ("warn_in_status_text", re.compile(r'["\']WARN["\']\s+in\s+')),
    ("pass_in_status_text", re.compile(r'["\']PASS["\']\s+in\s+')),
    ("blocked_in_status_text", re.compile(r'["\']BLOCKED["\']\s+in\s+')),
    ("status_startswith", re.compile(r'\.startswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)')),
    ("status_endswith", re.compile(r'\.endswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)')),
    ("inline_pass_fail_ternary", re.compile(r'["\']PASS["\']\s+if\s+.+?\s+else\s+["\']FAIL["\']')),
    ("inline_fail_pass_ternary", re.compile(r'["\']FAIL["\']\s+if\s+.+?\s+else\s+["\']PASS["\']')),
]

SIMPLE_PATTERNS = {
    "fail_in_status_text",
    "warn_in_status_text",
    "pass_in_status_text",
    "blocked_in_status_text",
    "status_startswith",
    "status_endswith",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def scan_one(path: Path) -> dict:
    if not path.exists():
        return {
            "file": rel(path),
            "exists": False,
            "decision": "BLOCK",
            "reason": "missing target",
            "approved_for_wave_patch": False,
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

    try:
        ast.parse(text)
        parses = True
        parse_error = ""
    except Exception as exc:
        parses = False
        parse_error = repr(exc)

    simple_only = all(item["pattern"] in SIMPLE_PATTERNS for item in findings)
    finding_count = len(findings)
    imports_shared = "from leaf_qt.status_presentation import" in text

    approved = (
        parses
        and finding_count > 0
        and finding_count <= 3
        and simple_only
    )

    if approved:
        decision = "APPROVE_FOR_16U71_BATCH_PATCH"
        reason = "simple owner-style status presentation findings only"
    elif finding_count == 0 and imports_shared:
        decision = "ALREADY_MIGRATED"
        reason = "no remaining findings and shared presentation import already present"
    else:
        decision = "DEFER_OR_SPLIT"
        reason = "complex findings, parse issue, or no actionable status presentation pattern"

    return {
        "file": rel(path),
        "exists": True,
        "parses": parses,
        "parse_error": parse_error,
        "finding_count": finding_count,
        "findings": findings[:20],
        "simple_only": simple_only,
        "imports_shared_status_presentation": imports_shared,
        "approved_for_wave_patch": approved,
        "decision": decision,
        "reason": reason,
    }


def main() -> dict:
    per_file = [scan_one(path) for path in TARGETS]
    approved = [item for item in per_file if item.get("approved_for_wave_patch")]
    deferred = [item for item in per_file if not item.get("approved_for_wave_patch")]

    passed = len(approved) >= 1 and all(item["exists"] for item in per_file)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "target_count": len(TARGETS),
        "approved_count": len(approved),
        "deferred_count": len(deferred),
        "approved_targets": [item["file"] for item in approved],
        "deferred_targets": [item["file"] for item in deferred],
        "per_file": per_file,
        "phase_16u70_next_migration_wave_decision_complete": passed,
        "next_phase": "16U.71 — Approved Migration Wave Patch",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.70",
        "NEXT MIGRATION WAVE DECISION",
        "============================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Decide whether the next grouped-safe candidates can be patched together safely.",
        "",
        "COUNTDOWN",
        "---------",
        "Current completed before this phase: 16U.69",
        "Estimated remaining after this phase if PASS: ~11–77 phases",
        "Likely final range: 16U.100–16U.120",
        "",
        "SUMMARY",
        "-------",
        f"Target count: {result['target_count']}",
        f"Approved count: {result['approved_count']}",
        f"Deferred count: {result['deferred_count']}",
        "",
        "PER-FILE DECISION",
        "-----------------",
    ]

    for item in per_file:
        lines.append(
            f"{item['file']}: {item['decision']} | findings={item.get('finding_count')} | "
            f"simple={item.get('simple_only')} | reason={item['reason']}"
        )
        for finding in item.get("findings", [])[:5]:
            lines.append(f"  - line {finding['line']} [{finding['pattern']}]: {finding['snippet']}")

    lines.extend(
        [
            "",
            "APPROVED TARGETS FOR 16U.71",
            "---------------------------",
            *result["approved_targets"],
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.70 COMPLETE." if passed else "PHASE 16U.70 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.71 — APPROVED MIGRATION WAVE PATCH",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"target_count={result['target_count']}")
    print(f"approved_count={result['approved_count']}")
    print(f"deferred_count={result['deferred_count']}")
    print("approved_targets:")
    for item in result["approved_targets"]:
        print(f"- {item}")
    print("deferred_targets:")
    for item in result["deferred_targets"]:
        print(f"- {item}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u70_next_migration_wave_decision_complete"]:
        raise SystemExit(1)
