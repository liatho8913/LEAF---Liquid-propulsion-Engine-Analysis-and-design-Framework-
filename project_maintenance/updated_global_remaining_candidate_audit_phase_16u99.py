from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


PHASE = "16U.99"
PASS_BANNER = "PASS_PHASE_16U99_UPDATED_GLOBAL_REMAINING_CANDIDATE_AUDIT"
FAIL_BANNER = "FAIL_PHASE_16U99_UPDATED_GLOBAL_REMAINING_CANDIDATE_AUDIT"

ROOT = Path(__file__).resolve().parents[1]

CLOSED_TARGETS = {
    "leaf_qt/foundation_test_runner_window.py",
    "leaf_qt/regen_cross_section_viewer.py",
    "leaf_qt/regen_scalability_failure_owner.py",
    "leaf_qt/real_engine_benchmark_failure_owner.py",
    "leaf_qt/bond_coat_integration_owner.py",
    "leaf_qt/coating_temperature_limit_integration_owner.py",
    "leaf_qt/material_strength_limit_integration_owner.py",
    "leaf_qt/material_temperature_limit_integration_owner.py",
    "leaf_qt/coating_property_consumption_audit_owner.py",
    "leaf_qt/coating_thermal_conductivity_integration_owner.py",
    "leaf_qt/coating_thermal_resistance_integration_owner.py",
    "leaf_qt/coating_thickness_integration_owner.py",
    "leaf_qt/material_density_integration_owner.py",
    "leaf_qt/material_property_consumption_audit_owner.py",
    "leaf_qt/material_specific_heat_integration_owner.py",
    "leaf_qt/material_thermal_conductivity_integration_owner.py",
    "leaf_qt/failure_root_cause_owner.py",
    "leaf_qt/regen_completion_gate_validation_owner.py",
    "leaf_qt/regen_system_signoff_validation_owner.py",
    "leaf_qt/regen_optimisation_scoring_owner.py",
    "leaf_qt/regen_optimisation_report_owner.py",
    "leaf_qt/regen_runtime_optimisation_report_owner.py",
    "leaf_qt/regen_geometry_report_owner.py",
    "leaf_qt/regen_candidate_blueprint_population_validation_owner.py",
    "leaf_qt/regen_candidate_creation_report_owner.py",
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

SIMPLE_PATTERNS = {
    "fail_in_status_text",
    "warn_in_status_text",
    "pass_in_status_text",
    "blocked_in_status_text",
    "status_startswith",
    "status_endswith",
}

OUT_TXT = ROOT / "project_maintenance" / "UPDATED_GLOBAL_REMAINING_CANDIDATE_AUDIT_PHASE_16U99.txt"
OUT_JSON = ROOT / "project_maintenance" / "updated_global_remaining_candidate_audit_phase_16u99.json"


def is_excluded(path: Path) -> bool:
    rel = path.relative_to(ROOT)

    if str(rel) in CLOSED_TARGETS:
        return True
    if any(part in EXCLUDED_DIR_PARTS for part in rel.parts):
        return True
    if path.name == "status_presentation.py":
        return True
    if not str(rel).startswith("leaf_qt/"):
        return True

    return False


def classify(path: Path) -> str:
    rel = str(path.relative_to(ROOT)).lower()
    name = path.name.lower()

    if name.startswith("test_") or "/test_" in rel:
        return "test_or_maintenance"

    if (
        "window" in name
        or "viewer" in name
        or "panel" in name
        or "dialog" in name
        or name == "main_window.py"
    ):
        return "complex_ui_deferred"

    if (
        name.endswith("_integration_owner.py")
        or name.endswith("_audit_owner.py")
        or name.endswith("_failure_owner.py")
        or name.endswith("_report_owner.py")
        or "owner" in name
    ):
        return "production_owner_candidate"

    return "supporting_or_deferred"


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

    simple_only = all(item["pattern"] in SIMPLE_PATTERNS for item in findings)

    grouped_safe = (
        classification == "production_owner_candidate"
        and 0 < len(findings) <= 3
        and simple_only
    )

    single_file_required = (
        classification == "production_owner_candidate"
        and len(findings) > 0
        and not grouped_safe
    )

    return {
        "file": str(path.relative_to(ROOT)),
        "classification": classification,
        "finding_count": len(findings),
        "findings": findings[:20],
        "simple_only": simple_only,
        "grouped_safe": grouped_safe,
        "single_file_required": single_file_required,
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
    production_candidates = [
        item for item in with_findings
        if item["classification"] == "production_owner_candidate"
    ]
    grouped_safe = [item for item in production_candidates if item["grouped_safe"]]
    single_file_required = [item for item in production_candidates if item["single_file_required"]]
    complex_deferred = [
        item for item in with_findings
        if item["classification"] == "complex_ui_deferred"
    ]
    test_or_maintenance = [
        item for item in with_findings
        if item["classification"] == "test_or_maintenance"
    ]
    supporting_or_deferred = [
        item for item in with_findings
        if item["classification"] == "supporting_or_deferred"
    ]

    grouped_safe.sort(key=lambda item: (item["finding_count"], item["file"]))
    single_file_required.sort(key=lambda item: (-item["finding_count"], item["file"]))
    production_candidates.sort(key=lambda item: (item["grouped_safe"] is False, item["finding_count"], item["file"]))

    next_batch = grouped_safe[:8]

    if next_batch:
        recommended_next_action = "PHASE_16U75_NEXT_MIGRATION_WAVE_DECISION"
        recommended_next_mode = "GROUPED_SAFE_BATCH"
    elif single_file_required:
        recommended_next_action = "PHASE_16U75_SINGLE_FILE_MIGRATION_DECISION"
        recommended_next_mode = "SINGLE_FILE_REQUIRED"
    elif complex_deferred:
        recommended_next_action = "PHASE_16U75_COMPLEX_UI_DEFERRED_REVIEW"
        recommended_next_mode = "COMPLEX_UI_REVIEW"
    else:
        recommended_next_action = "PHASE_16U75_FINAL_STATUS_ARCHITECTURE_CLOSURE_AUDIT"
        recommended_next_mode = "FINAL_CLOSURE_CANDIDATE"

    passed = True

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "closed_target_count": len(CLOSED_TARGETS),
        "scanned_leaf_qt_python_files": len(scanned),
        "files_with_findings": len(with_findings),
        "remaining_production_candidates": len(production_candidates),
        "grouped_safe_count": len(grouped_safe),
        "single_file_required_count": len(single_file_required),
        "complex_deferred_count": len(complex_deferred),
        "test_or_maintenance_count": len(test_or_maintenance),
        "supporting_or_deferred_count": len(supporting_or_deferred),
        "next_batch": next_batch,
        "top_production_candidates": production_candidates[:40],
        "single_file_required": single_file_required[:30],
        "complex_deferred": complex_deferred[:30],
        "recommended_next_action": recommended_next_action,
        "recommended_next_mode": recommended_next_mode,
        "phase_16u99_updated_global_remaining_candidate_audit_complete": passed,
        "next_phase": "16U.100 — Single-File Migration Decision",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.99",
        "UPDATED GLOBAL REMAINING-CANDIDATE AUDIT",
        "========================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Re-audit all remaining shared-status presentation candidates after the Phase 16U.73 closure gate.",
        "",
        "SUMMARY",
        "-------",
        f"Closed target count: {result['closed_target_count']}",
        f"Scanned leaf_qt Python files: {result['scanned_leaf_qt_python_files']}",
        f"Files with findings: {result['files_with_findings']}",
        f"Remaining production candidates: {result['remaining_production_candidates']}",
        f"Grouped-safe count: {result['grouped_safe_count']}",
        f"Single-file-required count: {result['single_file_required_count']}",
        f"Complex deferred count: {result['complex_deferred_count']}",
        f"Test/maintenance count: {result['test_or_maintenance_count']}",
        f"Supporting/deferred count: {result['supporting_or_deferred_count']}",
        "",
        "RECOMMENDED NEXT ACTION",
        "-----------------------",
        f"Mode: {recommended_next_mode}",
        f"Action: {recommended_next_action}",
        "",
        "NEXT BATCH",
        "----------",
    ]

    if next_batch:
        for idx, item in enumerate(next_batch, 1):
            lines.append(f"{idx}. {item['file']} | findings={item['finding_count']}")
            for finding in item["findings"][:5]:
                lines.append(f"   - line {finding['line']} [{finding['pattern']}]: {finding['snippet']}")
    else:
        lines.append("No grouped-safe batch available.")

    lines.extend(["", "TOP PRODUCTION CANDIDATES", "-------------------------"])

    for idx, item in enumerate(production_candidates[:25], 1):
        lines.append(
            f"{idx}. {item['file']} | findings={item['finding_count']} | "
            f"grouped_safe={item['grouped_safe']} | single_file_required={item['single_file_required']}"
        )

    lines.extend(["", "COMPLETION NOTICE", "-----------------"])
    lines.append("PHASE 16U.99 COMPLETE.")
    lines.extend(
        [
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.100 — SINGLE-FILE MIGRATION DECISION",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"closed_target_count={result['closed_target_count']}")
    print(f"files_with_findings={result['files_with_findings']}")
    print(f"remaining_production_candidates={result['remaining_production_candidates']}")
    print(f"grouped_safe_count={result['grouped_safe_count']}")
    print(f"single_file_required_count={result['single_file_required_count']}")
    print(f"complex_deferred_count={result['complex_deferred_count']}")
    print(f"recommended_next_mode={result['recommended_next_mode']}")
    print("next_batch:")
    for item in result["next_batch"]:
        print(f"- {item['file']} | findings={item['finding_count']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u99_updated_global_remaining_candidate_audit_complete"]:
        raise SystemExit(1)
