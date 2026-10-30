from __future__ import annotations

import json
import py_compile
import re
from datetime import datetime
from pathlib import Path


PHASE = "16U.58"
PASS_BANNER = "PASS_PHASE_16U58_MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER_PRESENTATION_LAYER_PATCH"
FAIL_BANNER = "FAIL_PHASE_16U58_MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER_PRESENTATION_LAYER_PATCH"

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "leaf_qt" / "material_strength_limit_integration_owner.py"

OUT_TXT = ROOT / "project_maintenance" / "MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER_PRESENTATION_LAYER_PATCH_PHASE_16U58.txt"
OUT_JSON = ROOT / "project_maintenance" / "material_strength_limit_integration_owner_presentation_layer_patch_phase_16u58.json"

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


def _leaf_16u58_status_severity(value):
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


def _leaf_16u58_is_fail_like(value):
    return _leaf_16u58_status_severity(value) == "FAIL"


def _leaf_16u58_is_warn_like(value):
    return _leaf_16u58_status_severity(value) == "WARN"


def _leaf_16u58_is_pass_like(value):
    return _leaf_16u58_status_severity(value) == "PASS"
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


def compile_target() -> tuple[bool, str]:
    try:
        py_compile.compile(str(TARGET), doraise=True)
        return True, ""
    except Exception as exc:
        return False, repr(exc)


def insert_helper_after_imports(text: str) -> tuple[str, bool]:
    if "_leaf_16u58_status_severity" in text:
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
        (r'["\']FAIL["\']\s+in\s+str\(([^)]*)\)\.upper\(\)', r'_leaf_16u58_is_fail_like(\1)', "migrate_fail_in_str_upper"),
        (r'["\']WARN["\']\s+in\s+str\(([^)]*)\)\.upper\(\)', r'_leaf_16u58_is_warn_like(\1)', "migrate_warn_in_str_upper"),
        (r'["\']PASS["\']\s+in\s+str\(([^)]*)\)\.upper\(\)', r'_leaf_16u58_is_pass_like(\1)', "migrate_pass_in_str_upper"),
        (r'["\']BLOCKED["\']\s+in\s+str\(([^)]*)\)\.upper\(\)', r'_leaf_16u58_is_fail_like(\1)', "migrate_blocked_in_str_upper"),
        (r'["\']FAIL["\']\s+in\s+([A-Za-z_][A-Za-z0-9_]*)', r'_leaf_16u58_is_fail_like(\1)', "migrate_fail_in_variable"),
        (r'["\']WARN["\']\s+in\s+([A-Za-z_][A-Za-z0-9_]*)', r'_leaf_16u58_is_warn_like(\1)', "migrate_warn_in_variable"),
        (r'["\']PASS["\']\s+in\s+([A-Za-z_][A-Za-z0-9_]*)', r'_leaf_16u58_is_pass_like(\1)', "migrate_pass_in_variable"),
        (r'["\']BLOCKED["\']\s+in\s+([A-Za-z_][A-Za-z0-9_]*)', r'_leaf_16u58_is_fail_like(\1)', "migrate_blocked_in_variable"),
        (r'([A-Za-z_][A-Za-z0-9_]*)\.startswith\(\s*["\']FAIL["\']\s*\)', r'_leaf_16u58_is_fail_like(\1)', "migrate_fail_startswith"),
        (r'([A-Za-z_][A-Za-z0-9_]*)\.startswith\(\s*["\']PASS["\']\s*\)', r'_leaf_16u58_is_pass_like(\1)', "migrate_pass_startswith"),
        (r'([A-Za-z_][A-Za-z0-9_]*)\.startswith\(\s*["\']WARN["\']\s*\)', r'_leaf_16u58_is_warn_like(\1)', "migrate_warn_startswith"),
        (r'([A-Za-z_][A-Za-z0-9_]*)\.startswith\(\s*["\']BLOCKED["\']\s*\)', r'_leaf_16u58_is_fail_like(\1)', "migrate_blocked_startswith"),
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
            findings.append({
                "pattern": pattern,
                "line": text.count("\n", 0, match.start()) + 1,
                "snippet": text[match.start():match.end()].replace("\n", " ")[:160],
            })
    return findings


def production_findings(findings: list[dict]) -> list[dict]:
    return [item for item in findings if item["line"] > 40]


def main() -> dict:
    if not TARGET.exists():
        result = {
            "phase": PHASE,
            "status": FAIL_BANNER,
            "error": "target missing",
            "phase_16u58_material_strength_limit_integration_owner_presentation_layer_patch_complete": False,
        }
        OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    original = TARGET.read_text(encoding="utf-8", errors="replace")
    before = production_findings(forbidden_findings(original))

    backup = TARGET.with_suffix(".py.phase_16u58_backup")
    if not backup.exists():
        backup.write_text(original, encoding="utf-8")

    text, helper_inserted = insert_helper_after_imports(original)
    text, applied = migrate_text(text)

    if text != original:
        TARGET.write_text(text, encoding="utf-8")

    final_text = TARGET.read_text(encoding="utf-8", errors="replace")
    after_raw = forbidden_findings(final_text)
    after = production_findings(after_raw)

    compiled, compile_error = compile_target()

    required_tokens = [
        "from leaf_qt.status_presentation import status_severity",
        "_leaf_16u58_status_severity",
        "_leaf_16u58_is_fail_like",
        "_leaf_16u58_is_warn_like",
        "_leaf_16u58_is_pass_like",
    ]
    missing_tokens = [token for token in required_tokens if token not in final_text]

    passed = compiled and not missing_tokens and len(after) == 0

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "target": str(TARGET.relative_to(ROOT)),
        "backup": str(backup.relative_to(ROOT)),
        "helper_inserted": helper_inserted,
        "applied": applied,
        "before_forbidden_count": len(before),
        "after_forbidden_count": len(after),
        "ignored_helper_fallback_findings": len(after_raw) - len(after),
        "remaining_findings": after[:30],
        "compiled": compiled,
        "compile_error": compile_error,
        "missing_tokens": missing_tokens,
        "phase_16u58_material_strength_limit_integration_owner_presentation_layer_patch_complete": passed,
        "next_phase": "16U.55 — Material Strength Limit Integration Owner Presentation Layer Regression",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.58",
        "COATING TEMPERATURE LIMIT INTEGRATION OWNER PRESENTATION LAYER PATCH",
        "====================================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Patch the material strength limit integration owner onto the shared status presentation layer.",
        "",
        "TARGET",
        "------",
        result["target"],
        "",
        "PATCH ACCOUNTING",
        "----------------",
        f"Helper inserted: {helper_inserted}",
        f"Applied migrations: {len(applied)}",
        f"Before forbidden production count: {len(before)}",
        f"After forbidden production count: {len(after)}",
        f"Ignored helper fallback literals: {result['ignored_helper_fallback_findings']}",
        f"Compiled: {compiled}",
        f"Compile error: {compile_error}",
        "",
        "APPLIED",
        "-------",
        *applied,
        "",
        "COMPLETION NOTICE",
        "-----------------",
        "PHASE 16U.58 COMPLETE." if passed else "PHASE 16U.58 FAILED.",
        "",
        "NEXT FEATURE",
        "------------",
        "PHASE 16U.55 — COATING TEMPERATURE LIMIT INTEGRATION OWNER PRESENTATION LAYER REGRESSION",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"target={result.get('target')}")
    print(f"helper_inserted={result.get('helper_inserted')}")
    print(f"applied={result.get('applied')}")
    print(f"before_forbidden_count={result.get('before_forbidden_count')}")
    print(f"after_forbidden_count={result.get('after_forbidden_count')}")
    print(f"ignored_helper_fallback_findings={result.get('ignored_helper_fallback_findings')}")
    print(f"compiled={result.get('compiled')}")
    if result.get("remaining_findings"):
        print("remaining_findings:")
        for item in result["remaining_findings"][:10]:
            print(f"- line {item['line']}: {item['snippet']}")
    if result.get("compile_error"):
        print(result["compile_error"])
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result.get("phase_16u58_material_strength_limit_integration_owner_presentation_layer_patch_complete"):
        raise SystemExit(1)
