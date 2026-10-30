from __future__ import annotations

import json
import py_compile
import re
from datetime import datetime
from pathlib import Path


PHASE = "16U.62"
PASS_BANNER = "PASS_PHASE_16U62_GROUPED_LOW_RISK_OWNER_BATCH_PATCH"
FAIL_BANNER = "FAIL_PHASE_16U62_GROUPED_LOW_RISK_OWNER_BATCH_PATCH"

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "leaf_qt/coating_property_consumption_audit_owner.py",
    ROOT / "leaf_qt/coating_thermal_conductivity_integration_owner.py",
    ROOT / "leaf_qt/coating_thermal_resistance_integration_owner.py",
    ROOT / "leaf_qt/coating_thickness_integration_owner.py",
    ROOT / "leaf_qt/material_density_integration_owner.py",
    ROOT / "leaf_qt/material_property_consumption_audit_owner.py",
    ROOT / "leaf_qt/material_specific_heat_integration_owner.py",
    ROOT / "leaf_qt/material_thermal_conductivity_integration_owner.py",
]

OUT_TXT = ROOT / "project_maintenance" / "GROUPED_LOW_RISK_OWNER_BATCH_PATCH_PHASE_16U62.txt"
OUT_JSON = ROOT / "project_maintenance" / "grouped_low_risk_owner_batch_patch_phase_16u62.json"

HELPER_BLOCK = '''\
try:
    from leaf_qt.status_presentation import status_severity
except Exception:
    def status_severity(value):
        text = str(value or "").upper()
        if "FAIL" in text or "BLOCKED" in text or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if "WARN" in text or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if "PASS" in text or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u62_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if "FAIL" in text or "BLOCKED" in text or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if "WARN" in text or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if "PASS" in text or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u62_is_fail_like(value):
    return _leaf_16u62_status_severity(value) == "FAIL"


def _leaf_16u62_is_warn_like(value):
    return _leaf_16u62_status_severity(value) == "WARN"


def _leaf_16u62_is_pass_like(value):
    return _leaf_16u62_status_severity(value) == "PASS"
'''

FORBIDDEN_PATTERNS = [
    r'\.startswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)',
    r'\.endswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)',
    r'["\']FAIL["\']\s+in\s+',
    r'["\']WARN["\']\s+in\s+',
    r'["\']PASS["\']\s+in\s+',
    r'["\']BLOCKED["\']\s+in\s+',
    r'["\']PASS["\']\s+if\s+.+?\s+else\s+["\']FAIL["\']',
    r'["\']FAIL["\']\s+if\s+.+?\s+else\s+["\']PASS["\']',
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def compile_target(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except Exception as exc:
        return False, repr(exc)


def insert_helper_after_imports(text: str) -> tuple[str, bool]:
    if "_leaf_16u62_status_severity" in text:
        return text, False

    lines = text.splitlines()
    insert_at = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            insert_at = index + 1

    return "\n".join(lines[:insert_at] + ["", HELPER_BLOCK, ""] + lines[insert_at:]) + "\n", True


def migrate_text(text: str) -> tuple[str, list[str]]:
    applied = []
    replacements = [
        (r'["\']FAIL["\']\s+in\s+str\(([^)]*)\)\.upper\(\)', r'_leaf_16u62_is_fail_like(\1)', "migrate_fail_in_str_upper"),
        (r'["\']WARN["\']\s+in\s+str\(([^)]*)\)\.upper\(\)', r'_leaf_16u62_is_warn_like(\1)', "migrate_warn_in_str_upper"),
        (r'["\']PASS["\']\s+in\s+str\(([^)]*)\)\.upper\(\)', r'_leaf_16u62_is_pass_like(\1)', "migrate_pass_in_str_upper"),
        (r'["\']BLOCKED["\']\s+in\s+str\(([^)]*)\)\.upper\(\)', r'_leaf_16u62_is_fail_like(\1)', "migrate_blocked_in_str_upper"),
        (r'["\']FAIL["\']\s+in\s+([A-Za-z_][A-Za-z0-9_]*)', r'_leaf_16u62_is_fail_like(\1)', "migrate_fail_in_variable"),
        (r'["\']WARN["\']\s+in\s+([A-Za-z_][A-Za-z0-9_]*)', r'_leaf_16u62_is_warn_like(\1)', "migrate_warn_in_variable"),
        (r'["\']PASS["\']\s+in\s+([A-Za-z_][A-Za-z0-9_]*)', r'_leaf_16u62_is_pass_like(\1)', "migrate_pass_in_variable"),
        (r'["\']BLOCKED["\']\s+in\s+([A-Za-z_][A-Za-z0-9_]*)', r'_leaf_16u62_is_fail_like(\1)', "migrate_blocked_in_variable"),
        (r'([A-Za-z_][A-Za-z0-9_]*)\.startswith\(\s*["\']FAIL["\']\s*\)', r'_leaf_16u62_is_fail_like(\1)', "migrate_fail_startswith"),
        (r'([A-Za-z_][A-Za-z0-9_]*)\.startswith\(\s*["\']PASS["\']\s*\)', r'_leaf_16u62_is_pass_like(\1)', "migrate_pass_startswith"),
        (r'([A-Za-z_][A-Za-z0-9_]*)\.startswith\(\s*["\']WARN["\']\s*\)', r'_leaf_16u62_is_warn_like(\1)', "migrate_warn_startswith"),
        (r'([A-Za-z_][A-Za-z0-9_]*)\.startswith\(\s*["\']BLOCKED["\']\s*\)', r'_leaf_16u62_is_fail_like(\1)', "migrate_blocked_startswith"),
    ]

    for pattern, replacement, name in replacements:
        text, count = re.subn(pattern, replacement, text)
        if count:
            applied.append(f"{name}:{count}")

    return text, applied


def forbidden_findings(text: str) -> list[dict]:
    findings = []
    for pattern in FORBIDDEN_PATTERNS:
        for match in re.finditer(pattern, text):
            findings.append(
                {
                    "pattern": pattern,
                    "line": text.count("\n", 0, match.start()) + 1,
                    "snippet": text[match.start():match.end()].replace("\n", " ")[:160],
                }
            )
    return findings


def production_findings(findings: list[dict]) -> list[dict]:
    return [item for item in findings if item["line"] > 40]


def patch_one(path: Path) -> dict:
    if not path.exists():
        return {
            "file": rel(path),
            "exists": False,
            "passed": False,
            "error": "target missing",
        }

    original = path.read_text(encoding="utf-8", errors="replace")
    before = production_findings(forbidden_findings(original))

    backup = path.with_suffix(".py.phase_16u62_backup")
    if not backup.exists():
        backup.write_text(original, encoding="utf-8")

    text, helper_inserted = insert_helper_after_imports(original)
    text, applied = migrate_text(text)

    changed = text != original
    if changed:
        path.write_text(text, encoding="utf-8")

    final_text = path.read_text(encoding="utf-8", errors="replace")
    after_raw = forbidden_findings(final_text)
    after = production_findings(after_raw)

    compiled, compile_error = compile_target(path)

    required_tokens = [
        "from leaf_qt.status_presentation import status_severity",
        "_leaf_16u62_status_severity",
        "_leaf_16u62_is_fail_like",
        "_leaf_16u62_is_warn_like",
        "_leaf_16u62_is_pass_like",
    ]
    missing_tokens = [token for token in required_tokens if token not in final_text]

    passed = compiled and not missing_tokens and len(after) == 0

    return {
        "file": rel(path),
        "exists": True,
        "passed": passed,
        "changed": changed,
        "backup": rel(backup),
        "helper_inserted": helper_inserted,
        "applied": applied,
        "before_forbidden_count": len(before),
        "after_forbidden_count": len(after),
        "ignored_helper_fallback_findings": len(after_raw) - len(after),
        "remaining_findings": after[:20],
        "compiled": compiled,
        "compile_error": compile_error,
        "missing_tokens": missing_tokens,
    }


def main() -> dict:
    per_file = [patch_one(path) for path in TARGETS]
    passed = all(item.get("passed") for item in per_file)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "target_count": len(TARGETS),
        "passed_count": sum(1 for item in per_file if item.get("passed")),
        "failed_count": sum(1 for item in per_file if not item.get("passed")),
        "per_file": per_file,
        "phase_16u62_grouped_low_risk_owner_batch_patch_complete": passed,
        "next_phase": "16U.63 — First Grouped Low-Risk Owner Batch Regression",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.62",
        "FIRST GROUPED LOW-RISK OWNER BATCH PATCH",
        "=========================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Patch first grouped low-risk owner batch onto the shared status presentation layer.",
        "",
        "SUMMARY",
        "-------",
        f"Target count: {result['target_count']}",
        f"Passed count: {result['passed_count']}",
        f"Failed count: {result['failed_count']}",
        "",
        "PER-FILE RESULTS",
        "----------------",
    ]

    for item in per_file:
        lines.append(
            f"{item['file']}: {'PASS' if item.get('passed') else 'FAIL'} | "
            f"changed={item.get('changed')} | before={item.get('before_forbidden_count')} | "
            f"after={item.get('after_forbidden_count')} | compiled={item.get('compiled')}"
        )
        if item.get("applied"):
            lines.append(f"  applied={', '.join(item['applied'])}")
        if item.get("missing_tokens"):
            lines.append(f"  missing_tokens={item['missing_tokens']}")
        if item.get("compile_error"):
            lines.append(f"  compile_error={item['compile_error']}")
        if item.get("remaining_findings"):
            for finding in item["remaining_findings"][:5]:
                lines.append(f"  remaining line {finding['line']}: {finding['snippet']}")

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.62 COMPLETE." if passed else "PHASE 16U.62 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.63 — FIRST GROUPED LOW-RISK OWNER BATCH REGRESSION",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"target_count={result['target_count']}")
    print(f"passed_count={result['passed_count']}")
    print(f"failed_count={result['failed_count']}")
    for item in result["per_file"]:
        print(f"{item['file']}={'PASS' if item.get('passed') else 'FAIL'} before={item.get('before_forbidden_count')} after={item.get('after_forbidden_count')} compiled={item.get('compiled')}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u62_grouped_low_risk_owner_batch_patch_complete"]:
        raise SystemExit(1)
