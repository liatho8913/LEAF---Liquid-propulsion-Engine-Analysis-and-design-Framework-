from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


PHASE = "16U.49"
PASS_BANNER = "PASS_PHASE_16U49_NEXT_REPORT_OWNER_ROLLOUT_CANDIDATE_AUDIT"
FAIL_BANNER = "FAIL_PHASE_16U49_NEXT_REPORT_OWNER_ROLLOUT_CANDIDATE_AUDIT"

ROOT = Path(__file__).resolve().parents[1]

CLOSED_TARGETS = {
    "leaf_qt/foundation_test_runner_window.py",
    "leaf_qt/regen_cross_section_viewer.py",
    "leaf_qt/regen_scalability_failure_owner.py",
    "leaf_qt/real_engine_benchmark_failure_owner.py",
}

EXCLUDED_DIR_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "_handover_exports",
    "build",
    "dist",
    "LEAF_UPLOAD",
}

EXCLUDED_FILES = {
    "status_presentation.py",
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
    ("status_startswith", re.compile(r'\.startswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)')),
    ("status_endswith", re.compile(r'\.endswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)')),
    ("fail_in_status_text", re.compile(r'["\']FAIL["\']\s+in\s+')),
    ("warn_in_status_text", re.compile(r'["\']WARN["\']\s+in\s+')),
    ("pass_in_status_text", re.compile(r'["\']PASS["\']\s+in\s+')),
    ("blocked_in_status_text", re.compile(r'["\']BLOCKED["\']\s+in\s+')),
]

OUT_TXT = ROOT / "project_maintenance" / "NEXT_REPORT_OWNER_ROLLOUT_CANDIDATE_AUDIT_PHASE_16U49.txt"
OUT_JSON = ROOT / "project_maintenance" / "next_report_owner_rollout_candidate_audit_phase_16u49.json"


def is_excluded(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if str(rel) in CLOSED_TARGETS:
        return True
    if any(part in EXCLUDED_DIR_PARTS for part in rel.parts):
        return True
    if path.name in EXCLUDED_FILES:
        return True
    return False


def classify(path: Path) -> str:
    rel = str(path.relative_to(ROOT)).lower()
    name = path.name.lower()

    if "project_maintenance" in rel:
        return "maintenance_or_test"
    if not rel.startswith("leaf_qt/"):
        return "non_leaf_qt"
    if name.startswith("test_") or "/test_" in rel:
        return "maintenance_or_test"
    if any(hint in name for hint in TARGET_NAME_HINTS):
        return "probable_report_or_ui_consumer"
    return "leaf_qt_supporting_consumer"


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def scan(path: Path) -> dict:
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

    classification = classify(path)

    risk = 0
    if classification == "probable_report_or_ui_consumer":
        risk += 50
    elif classification == "leaf_qt_supporting_consumer":
        risk += 25
    elif classification == "maintenance_or_test":
        risk += 5
    else:
        risk += 1

    risk += min(len(findings), 25) * 3

    if "from leaf_qt.status_presentation import" in text:
        risk -= 10

    if "class " in text and ("QWidget" in text or "QDialog" in text or "QMainWindow" in text):
        risk += 10

    suggested_action = "NO_ACTION"
    if findings and classification == "probable_report_or_ui_consumer":
        suggested_action = "CANDIDATE_FOR_PHASE_16U50_PATCH"
    elif findings and classification == "leaf_qt_supporting_consumer":
        suggested_action = "REVIEW_AFTER_UI_REPORT_CONSUMERS"
    elif findings:
        suggested_action = "LOW_PRIORITY_OR_FALSE_POSITIVE"

    return {
        "file": str(path.relative_to(ROOT)),
        "classification": classification,
        "finding_count": len(findings),
        "findings": findings[:25],
        "risk_score": risk,
        "suggested_action": suggested_action,
        "imports_status_presentation": "from leaf_qt.status_presentation import" in text,
    }


def main() -> dict:
    py_files = [
        path
        for path in ROOT.rglob("*.py")
        if path.is_file() and not is_excluded(path)
    ]

    scanned = [scan(path) for path in py_files]
    with_findings = [item for item in scanned if item["finding_count"] > 0]

    candidates = [
        item for item in with_findings
        if item["suggested_action"] == "CANDIDATE_FOR_PHASE_16U50_PATCH"
    ]
    candidates.sort(key=lambda item: (-item["risk_score"], item["file"]))

    next_candidate = candidates[0] if candidates else None

    passed = bool(py_files) and next_candidate is not None

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "closed_targets_excluded": sorted(CLOSED_TARGETS),
        "scanned_python_files": len(py_files),
        "files_with_findings": len(with_findings),
        "candidate_count": len(candidates),
        "next_candidate": next_candidate,
        "top_candidates": candidates[:20],
        "phase_16u49_next_report_owner_rollout_candidate_audit_complete": passed,
        "next_phase": "16U.50 — Next Report Owner Presentation Layer Patch",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.49",
        "NEXT REPORT OWNER ROLLOUT CANDIDATE AUDIT",
        "==========================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Audit remaining production report-owner/UI files after closing real engine benchmark failure owner.",
        "",
        "CLOSED TARGETS EXCLUDED",
        "-----------------------",
        *sorted(CLOSED_TARGETS),
        "",
        "SUMMARY",
        "-------",
        f"Python files scanned: {len(py_files)}",
        f"Files with findings: {len(with_findings)}",
        f"Candidate count: {len(candidates)}",
        "",
        "NEXT CANDIDATE",
        "--------------",
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
        lines.append("No candidate found.")

    lines.extend(["", "TOP CANDIDATES", "--------------"])

    for idx, item in enumerate(candidates[:20], start=1):
        lines.append(f"{idx}. {item['file']} | findings={item['finding_count']} | risk={item['risk_score']}")
        for finding in item["findings"][:5]:
            lines.append(f"   - line {finding['line']} [{finding['pattern']}]: {finding['snippet']}")

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.49 COMPLETE." if passed else "PHASE 16U.49 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.50 — NEXT REPORT OWNER PRESENTATION LAYER PATCH",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"scanned_python_files={result['scanned_python_files']}")
    print(f"files_with_findings={result['files_with_findings']}")
    print(f"candidate_count={result['candidate_count']}")
    if result["next_candidate"]:
        print(f"next_candidate={result['next_candidate']['file']}")
    else:
        print("next_candidate=None")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u49_next_report_owner_rollout_candidate_audit_complete"]:
        raise SystemExit(1)
