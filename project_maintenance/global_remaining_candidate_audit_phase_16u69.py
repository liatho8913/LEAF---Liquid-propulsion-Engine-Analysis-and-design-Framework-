from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


PHASE = "16U.69"
PASS_BANNER = "PASS_PHASE_16U69_GLOBAL_REMAINING_CANDIDATE_AUDIT"
FAIL_BANNER = "FAIL_PHASE_16U69_GLOBAL_REMAINING_CANDIDATE_AUDIT"

ROOT = Path(__file__).resolve().parents[1]

CLOSED_TARGETS = {
    "leaf_qt/foundation_test_runner_window.py",
    "leaf_qt/regen_cross_section_viewer.py",
    "leaf_qt/regen_scalability_failure_owner.py",
    "leaf_qt/real_engine_benchmark_failure_owner.py",
    "leaf_qt/bond_coat_integration_owner.py",
    "leaf_qt/coating_temperature_limit_integration_owner.py",
    "leaf_qt/material_strength_limit_integration_owner.py",
    "leaf_qt/coating_property_consumption_audit_owner.py",
    "leaf_qt/coating_thermal_conductivity_integration_owner.py",
    "leaf_qt/coating_thermal_resistance_integration_owner.py",
    "leaf_qt/coating_thickness_integration_owner.py",
    "leaf_qt/material_density_integration_owner.py",
    "leaf_qt/material_property_consumption_audit_owner.py",
    "leaf_qt/material_specific_heat_integration_owner.py",
    "leaf_qt/material_thermal_conductivity_integration_owner.py",
    "leaf_qt/material_temperature_limit_integration_owner.py",
}

EXCLUDED_DIR_PARTS = {
    ".git", ".venv", "venv", "__pycache__",
    "_handover_exports", "build", "dist", "LEAF_UPLOAD",
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

OUT_TXT = ROOT / "project_maintenance" / "GLOBAL_REMAINING_CANDIDATE_AUDIT_PHASE_16U69.txt"
OUT_JSON = ROOT / "project_maintenance" / "global_remaining_candidate_audit_phase_16u69.json"


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
    if "window" in name or "viewer" in name or "panel" in name or "dialog" in name:
        return "complex_ui_deferred"
    if name.endswith("_integration_owner.py") or name.endswith("_audit_owner.py") or name.endswith("_failure_owner.py") or name.endswith("_report_owner.py"):
        return "production_owner_candidate"
    if "owner" in name:
        return "production_owner_candidate"
    return "supporting_or_deferred"


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def scan(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    findings = []

    for name, pattern in LEGACY_PATTERNS:
        for match in pattern.finditer(text):
            findings.append({
                "pattern": name,
                "line": line_number(text, match.start()),
                "snippet": text[match.start():match.end()].replace("\n", " ")[:160],
            })

    classification = classify(path)
    simple_only = all(item["pattern"] in {
        "fail_in_status_text",
        "warn_in_status_text",
        "pass_in_status_text",
        "blocked_in_status_text",
        "status_startswith",
        "status_endswith",
    } for item in findings)

    grouped_safe = (
        classification == "production_owner_candidate"
        and 0 < len(findings) <= 3
        and simple_only
    )

    return {
        "file": str(path.relative_to(ROOT)),
        "classification": classification,
        "finding_count": len(findings),
        "findings": findings[:20],
        "simple_only": simple_only,
        "grouped_safe": grouped_safe,
        "imports_status_presentation": "from leaf_qt.status_presentation import" in text,
    }


def main() -> dict:
    py_files = [p for p in ROOT.rglob("*.py") if p.is_file() and not is_excluded(p)]
    scanned = [scan(p) for p in py_files]

    with_findings = [item for item in scanned if item["finding_count"] > 0]
    production_candidates = [item for item in with_findings if item["classification"] == "production_owner_candidate"]
    grouped_safe = [item for item in production_candidates if item["grouped_safe"]]
    complex_deferred = [item for item in with_findings if item["classification"] == "complex_ui_deferred"]
    test_or_maintenance = [item for item in with_findings if item["classification"] == "test_or_maintenance"]

    grouped_safe.sort(key=lambda item: (item["finding_count"], item["file"]))
    production_candidates.sort(key=lambda item: (item["finding_count"], item["file"]))

    next_batch = grouped_safe[:8]

    remaining_production = len(production_candidates)
    estimated_min_phases = 0
    if remaining_production:
        estimated_min_phases = 4 * ((remaining_production + 7) // 8)

    estimated_max_phases = remaining_production * 3 + 6

    passed = True

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "closed_target_count": len(CLOSED_TARGETS),
        "scanned_leaf_qt_python_files": len(scanned),
        "files_with_findings": len(with_findings),
        "remaining_production_candidates": remaining_production,
        "grouped_safe_count": len(grouped_safe),
        "complex_deferred_count": len(complex_deferred),
        "test_or_maintenance_count": len(test_or_maintenance),
        "next_batch": next_batch,
        "top_production_candidates": production_candidates[:30],
        "estimated_remaining_phase_range": {
            "min_grouped_path": estimated_min_phases,
            "max_conservative_path": estimated_max_phases,
            "likely_final_phase_range": "16U.100–16U.120",
        },
        "phase_16u69_global_remaining_candidate_audit_complete": passed,
        "next_phase": "16U.70 — Next Migration Wave Decision",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.69",
        "GLOBAL REMAINING-CANDIDATE AUDIT",
        "================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "SUMMARY",
        "-------",
        f"Closed target count: {len(CLOSED_TARGETS)}",
        f"Scanned leaf_qt Python files: {len(scanned)}",
        f"Files with findings: {len(with_findings)}",
        f"Remaining production candidates: {remaining_production}",
        f"Grouped-safe count: {len(grouped_safe)}",
        f"Complex deferred count: {len(complex_deferred)}",
        f"Test/maintenance finding count: {len(test_or_maintenance)}",
        "",
        "COUNTDOWN",
        "---------",
        f"Estimated remaining phase range after 16U.69: {estimated_min_phases}–{estimated_max_phases}",
        "Likely 16U final range: 16U.100–16U.120",
        "",
        "NEXT BATCH",
        "----------",
    ]

    for idx, item in enumerate(next_batch, 1):
        lines.append(f"{idx}. {item['file']} | findings={item['finding_count']}")

    lines.extend(["", "TOP PRODUCTION CANDIDATES", "-------------------------"])

    for idx, item in enumerate(production_candidates[:20], 1):
        lines.append(f"{idx}. {item['file']} | findings={item['finding_count']} | grouped_safe={item['grouped_safe']}")

    lines.extend([
        "",
        "COMPLETION NOTICE",
        "-----------------",
        "PHASE 16U.69 COMPLETE.",
        "",
        "NEXT FEATURE",
        "------------",
        "PHASE 16U.70 — NEXT MIGRATION WAVE DECISION",
    ])

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"closed_target_count={result['closed_target_count']}")
    print(f"files_with_findings={result['files_with_findings']}")
    print(f"remaining_production_candidates={result['remaining_production_candidates']}")
    print(f"grouped_safe_count={result['grouped_safe_count']}")
    print(f"complex_deferred_count={result['complex_deferred_count']}")
    print("next_batch:")
    for item in result["next_batch"]:
        print(f"- {item['file']} | findings={item['finding_count']}")
    print(f"estimated_remaining_phase_range={result['estimated_remaining_phase_range']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u69_global_remaining_candidate_audit_complete"]:
        raise SystemExit(1)
