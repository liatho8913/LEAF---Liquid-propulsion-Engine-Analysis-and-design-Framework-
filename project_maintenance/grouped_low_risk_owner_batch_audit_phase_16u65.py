from __future__ import annotations

import ast
import json
import re
from datetime import datetime
from pathlib import Path


PHASE = "16U.65"
PASS_BANNER = "PASS_PHASE_16U65_GROUPED_LOW_RISK_OWNER_MIGRATION_FRAMEWORK"
FAIL_BANNER = "FAIL_PHASE_16U65_GROUPED_LOW_RISK_OWNER_MIGRATION_FRAMEWORK"

ROOT = Path(__file__).resolve().parents[1]

OUT_TXT = ROOT / "project_maintenance" / "GROUPED_LOW_RISK_OWNER_MIGRATION_FRAMEWORK_PHASE_16U65.txt"
OUT_JSON = ROOT / "project_maintenance" / "grouped_low_risk_owner_migration_framework_phase_16u65.json"

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
}

EXCLUDED_DIR_PARTS = {
    ".git", ".venv", "venv", "__pycache__",
    "_handover_exports", "build", "dist", "LEAF_UPLOAD",
}

LOW_RISK_NAME_PATTERNS = [
    "_integration_owner.py",
    "_audit_owner.py",
    "_limit_integration_owner.py",
]

DISALLOWED_BATCH_NAME_PATTERNS = [
    "window.py",
    "viewer.py",
    "panel.py",
    "dialog.py",
    "main_window.py",
    "solver.py",
    "engine_solver.py",
    "regen_cross_section_viewer.py",
]

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
    if path.name.startswith("test_"):
        return True
    return False


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def is_low_risk_name(path: Path) -> bool:
    name = path.name
    return any(name.endswith(pattern) for pattern in LOW_RISK_NAME_PATTERNS)


def is_disallowed_batch_name(path: Path) -> bool:
    name = path.name
    return any(name.endswith(pattern) or name == pattern for pattern in DISALLOWED_BATCH_NAME_PATTERNS)


def scan_file(path: Path) -> dict:
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

    imports_shared = "from leaf_qt.status_presentation import" in text

    low_risk_name = is_low_risk_name(path)
    disallowed_name = is_disallowed_batch_name(path)

    simple_patterns_only = all(
        item["pattern"] in {
            "fail_in_status_text",
            "warn_in_status_text",
            "pass_in_status_text",
            "blocked_in_status_text",
            "status_startswith",
            "status_endswith",
        }
        for item in findings
    )

    finding_count = len(findings)

    batch_safe = (
        parses
        and low_risk_name
        and not disallowed_name
        and 0 < finding_count <= 3
        and simple_patterns_only
    )

    return {
        "file": str(path.relative_to(ROOT)),
        "finding_count": finding_count,
        "findings": findings[:20],
        "parses": parses,
        "parse_error": parse_error,
        "imports_shared_status_presentation": imports_shared,
        "low_risk_name": low_risk_name,
        "disallowed_name": disallowed_name,
        "simple_patterns_only": simple_patterns_only,
        "batch_safe": batch_safe,
    }


def main() -> dict:
    candidates = [
        path for path in ROOT.rglob("*.py")
        if path.is_file() and not is_excluded(path)
    ]

    scanned = [scan_file(path) for path in candidates]
    with_findings = [item for item in scanned if item["finding_count"] > 0]

    batch_safe = [item for item in with_findings if item["batch_safe"]]
    batch_safe.sort(key=lambda item: (item["finding_count"], item["file"]))

    first_batch = batch_safe[:8]

    blocked = [
        item for item in with_findings
        if not item["batch_safe"]
    ]

    passed = bool(first_batch)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "closed_targets_excluded": sorted(CLOSED_TARGETS),
        "scanned_leaf_qt_python_files": len(scanned),
        "files_with_findings": len(with_findings),
        "batch_safe_count": len(batch_safe),
        "first_batch": first_batch,
        "blocked_or_deferred_count": len(blocked),
        "blocked_or_deferred_sample": blocked[:20],
        "phase_16u65_grouped_low_risk_owner_migration_framework_complete": passed,
        "next_phase": "16U.66 — Second Grouped Low-Risk Owner Batch Patch",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.65",
        "NEXT GROUPED LOW-RISK OWNER BATCH AUDIT",
        "===========================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Audit the next safe grouped low-risk owner presentation-layer batch.",
        "",
        "SAFETY RULES",
        "------------",
        "1. Only low-risk owner/audit/integration-owner files are eligible.",
        "2. GUI windows, viewers, panels, solvers, and complex files are excluded.",
        "3. Each file must parse successfully before selection.",
        "4. Each selected file must have only simple legacy status patterns.",
        "5. Each selected file must have 1–3 findings.",
        "6. Batch patching is allowed only after per-file audit selection.",
        "7. Regression and closure must remain per-file inside the batch.",
        "",
        "SUMMARY",
        "-------",
        f"Scanned leaf_qt Python files: {len(scanned)}",
        f"Files with findings: {len(with_findings)}",
        f"Batch-safe files: {len(batch_safe)}",
        f"First batch size: {len(first_batch)}",
        f"Blocked/deferred files: {len(blocked)}",
        "",
        "FIRST BATCH",
        "-----------",
    ]

    for idx, item in enumerate(first_batch, start=1):
        lines.append(f"{idx}. {item['file']} | findings={item['finding_count']}")
        for finding in item["findings"][:5]:
            lines.append(f"   - line {finding['line']} [{finding['pattern']}]: {finding['snippet']}")

    lines.extend(
        [
            "",
            "DEFERRED SAMPLE",
            "---------------",
        ]
    )

    for idx, item in enumerate(blocked[:10], start=1):
        lines.append(
            f"{idx}. {item['file']} | findings={item['finding_count']} | "
            f"low_risk={item['low_risk_name']} | simple={item['simple_patterns_only']} | parses={item['parses']}"
        )

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.65 COMPLETE." if passed else "PHASE 16U.65 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.66 — SECOND GROUPED LOW-RISK OWNER BATCH PATCH",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"scanned_leaf_qt_python_files={result['scanned_leaf_qt_python_files']}")
    print(f"files_with_findings={result['files_with_findings']}")
    print(f"batch_safe_count={result['batch_safe_count']}")
    print("first_batch:")
    for item in result["first_batch"]:
        print(f"- {item['file']} | findings={item['finding_count']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u65_grouped_low_risk_owner_migration_framework_complete"]:
        raise SystemExit(1)
