from __future__ import annotations

import ast
import json
import re
from datetime import datetime
from pathlib import Path


PHASE = "16U.37"
PASS_BANNER = "PASS_PHASE_16U37_REPORT_OWNER_PRESENTATION_LAYER_ROLLOUT_AUDIT"
FAIL_BANNER = "FAIL_PHASE_16U37_REPORT_OWNER_PRESENTATION_LAYER_ROLLOUT_AUDIT"

ROOT = Path(__file__).resolve().parents[1]

OUT_TXT = ROOT / "project_maintenance" / "REPORT_OWNER_PRESENTATION_LAYER_ROLLOUT_AUDIT_PHASE_16U37.txt"
OUT_JSON = ROOT / "project_maintenance" / "report_owner_presentation_layer_rollout_audit_phase_16u37.json"

EXCLUDED_DIR_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "_handover_exports",
    "build",
    "dist",
}

EXCLUDED_FILES = {
    "status_presentation.py",
    "report_owner_presentation_layer_pilot_regression_phase_16u35.py",
    "report_owner_presentation_layer_pilot_closure_gate_phase_16u36.py",
    "report_owner_presentation_layer_rollout_audit_phase_16u37.py",
}

TARGET_NAME_HINTS = [
    "window",
    "viewer",
    "panel",
    "report",
    "owner",
    "inspector",
    "runner",
    "dialog",
]

LEGACY_PATTERNS = [
    ("inline_pass_fail_ternary", re.compile(r'["\']PASS["\']\s+if\s+.+?\s+else\s+["\']FAIL["\']')),
    ("inline_fail_pass_ternary", re.compile(r'["\']FAIL["\']\s+if\s+.+?\s+else\s+["\']PASS["\']')),
    ("inline_warn_fail_pass", re.compile(r'["\']WARN["\']|["\']WARNING["\']|["\']FAIL["\']|["\']PASS["\']')),
    ("status_startswith", re.compile(r'\.startswith\(\s*["\'](?:PASS|FAIL|WARN)')),
    ("status_endswith", re.compile(r'\.endswith\(\s*["\'](?:PASS|FAIL|WARN)')),
    ("fail_in_text", re.compile(r'["\']FAIL["\']\s+in\s+')),
    ("warn_in_text", re.compile(r'["\']WARN["\']\s+in\s+')),
    ("pass_in_text", re.compile(r'["\']PASS["\']\s+in\s+')),
]

LOW_RISK_IMPORT_TARGETS = [
    "LegacyCompatibilityProducer",
    "display_status",
    "present_status",
    "status_badge",
]


def is_excluded(path: Path) -> bool:
    rel_parts = set(path.relative_to(ROOT).parts)
    if rel_parts & EXCLUDED_DIR_PARTS:
        return True
    return path.name in EXCLUDED_FILES


def classify_file(path: Path, text: str) -> str:
    lower = path.name.lower()
    rel = str(path.relative_to(ROOT)).lower()

    if "project_maintenance" in rel:
        return "maintenance_or_test"
    if any(hint in lower for hint in TARGET_NAME_HINTS):
        return "probable_report_or_ui_consumer"
    if "leaf_qt" in rel:
        return "leaf_qt_supporting_consumer"
    return "other_python_consumer"


def line_for_offset(text: str, start: int) -> int:
    return text.count("\n", 0, start) + 1


def scan_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    findings = []

    for name, pattern in LEGACY_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                {
                    "pattern": name,
                    "line": line_for_offset(text, match.start()),
                    "snippet": text[match.start():match.end()].replace("\n", " ")[:160],
                }
            )

    imports_status_presentation = "status_presentation" in text
    uses_low_risk_api = any(token in text for token in LOW_RISK_IMPORT_TARGETS)

    try:
        ast.parse(text)
        parses = True
        parse_error = ""
    except Exception as exc:
        parses = False
        parse_error = repr(exc)

    classification = classify_file(path, text)

    risk_score = 0
    if classification == "probable_report_or_ui_consumer":
        risk_score += 40
    elif classification == "leaf_qt_supporting_consumer":
        risk_score += 25
    elif classification == "maintenance_or_test":
        risk_score += 5
    else:
        risk_score += 10

    risk_score += min(len(findings), 20) * 3

    if imports_status_presentation:
        risk_score -= 10
    if uses_low_risk_api:
        risk_score -= 5
    if not parses:
        risk_score += 20

    suggested_action = "NO_ACTION"
    if findings:
        if classification == "probable_report_or_ui_consumer":
            suggested_action = "CANDIDATE_FOR_PHASE_16U38_PATCH"
        elif classification == "leaf_qt_supporting_consumer":
            suggested_action = "REVIEW_AFTER_REPORT_UI_CONSUMERS"
        elif classification == "maintenance_or_test":
            suggested_action = "LIKELY_TEST_OR_AUDIT_FALSE_POSITIVE"
        else:
            suggested_action = "LOW_PRIORITY_REVIEW"

    return {
        "file": str(path.relative_to(ROOT)),
        "classification": classification,
        "finding_count": len(findings),
        "findings": findings[:25],
        "imports_status_presentation": imports_status_presentation,
        "uses_low_risk_api": uses_low_risk_api,
        "parses": parses,
        "parse_error": parse_error,
        "risk_score": risk_score,
        "suggested_action": suggested_action,
    }


def main() -> dict:
    py_files = [
        path
        for path in ROOT.rglob("*.py")
        if path.is_file() and not is_excluded(path)
    ]

    scanned = [scan_file(path) for path in py_files]
    files_with_findings = [item for item in scanned if item["finding_count"] > 0]

    rollout_candidates = [
        item for item in files_with_findings
        if item["suggested_action"] == "CANDIDATE_FOR_PHASE_16U38_PATCH"
    ]

    rollout_candidates.sort(key=lambda item: (-item["risk_score"], item["file"]))

    next_candidate = rollout_candidates[0] if rollout_candidates else None

    passed = bool(py_files) and all(item["parses"] for item in scanned if item["classification"] != "maintenance_or_test")

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "scanned_python_files": len(py_files),
        "files_with_legacy_status_findings": len(files_with_findings),
        "rollout_candidate_count": len(rollout_candidates),
        "next_candidate": next_candidate,
        "top_rollout_candidates": rollout_candidates[:20],
        "all_files_with_findings": files_with_findings,
        "phase_16u37_report_owner_presentation_layer_rollout_audit_complete": passed,
        "next_phase": "16U.38 — First Report Owner Presentation Layer Rollout Patch",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.37",
        "REPORT OWNER PRESENTATION LAYER ROLLOUT AUDIT",
        "==============================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Audit remaining report-owner/UI consumers for legacy inline status presentation logic.",
        "",
        "SUMMARY",
        "-------",
        f"Python files scanned: {result['scanned_python_files']}",
        f"Files with legacy status findings: {result['files_with_legacy_status_findings']}",
        f"Report/UI rollout candidates: {result['rollout_candidate_count']}",
        "",
        "NEXT PATCH CANDIDATE",
        "--------------------",
    ]

    if next_candidate:
        lines.extend(
            [
                f"File: {next_candidate['file']}",
                f"Classification: {next_candidate['classification']}",
                f"Finding count: {next_candidate['finding_count']}",
                f"Risk score: {next_candidate['risk_score']}",
                f"Suggested action: {next_candidate['suggested_action']}",
            ]
        )
    else:
        lines.append("No report/UI rollout candidate found.")

    lines.extend(["", "TOP ROLLOUT CANDIDATES", "----------------------"])

    for index, item in enumerate(rollout_candidates[:20], start=1):
        lines.append(
            f"{index}. {item['file']} | findings={item['finding_count']} | risk={item['risk_score']} | action={item['suggested_action']}"
        )
        for finding in item["findings"][:5]:
            lines.append(f"   - line {finding['line']} [{finding['pattern']}]: {finding['snippet']}")

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.37 COMPLETE." if passed else "PHASE 16U.37 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.38 — FIRST REPORT OWNER PRESENTATION LAYER ROLLOUT PATCH",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"scanned_python_files={result['scanned_python_files']}")
    print(f"files_with_legacy_status_findings={result['files_with_legacy_status_findings']}")
    print(f"rollout_candidate_count={result['rollout_candidate_count']}")
    if result["next_candidate"]:
        print(f"next_candidate={result['next_candidate']['file']}")
    else:
        print("next_candidate=None")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u37_report_owner_presentation_layer_rollout_audit_complete"]:
        raise SystemExit(1)
