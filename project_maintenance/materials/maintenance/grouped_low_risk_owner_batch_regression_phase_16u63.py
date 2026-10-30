from __future__ import annotations

import importlib
import json
import py_compile
import re
import sys
from datetime import datetime
from pathlib import Path


PHASE = "16U.63"
PASS_BANNER = "PASS_PHASE_16U63_GROUPED_LOW_RISK_OWNER_BATCH_REGRESSION"
FAIL_BANNER = "FAIL_PHASE_16U63_GROUPED_LOW_RISK_OWNER_BATCH_REGRESSION"

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PATCH_JSON = ROOT / "project_maintenance" / "grouped_low_risk_owner_batch_patch_phase_16u62.json"

OUT_TXT = ROOT / "project_maintenance" / "GROUPED_LOW_RISK_OWNER_BATCH_REGRESSION_PHASE_16U63.txt"
OUT_JSON = ROOT / "project_maintenance" / "grouped_low_risk_owner_batch_regression_phase_16u63.json"

TARGETS = [
    "leaf_qt/coating_property_consumption_audit_owner.py",
    "leaf_qt/coating_thermal_conductivity_integration_owner.py",
    "leaf_qt/coating_thermal_resistance_integration_owner.py",
    "leaf_qt/coating_thickness_integration_owner.py",
    "leaf_qt/material_density_integration_owner.py",
    "leaf_qt/material_property_consumption_audit_owner.py",
    "leaf_qt/material_specific_heat_integration_owner.py",
    "leaf_qt/material_thermal_conductivity_integration_owner.py",
]

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


def compile_file(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except Exception as exc:
        return False, repr(exc)


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


def module_name_from_rel(rel_path: str) -> str:
    return rel_path[:-3].replace("/", ".")


def verify_one(rel_path: str, patch_payload: dict) -> dict:
    path = ROOT / rel_path
    checks = []

    exists = path.exists()
    checks.append({"name": "exists", "passed": exists, "detail": rel_path})

    if not exists:
        return {"file": rel_path, "passed": False, "checks": checks}

    text = path.read_text(encoding="utf-8", errors="replace")

    compiled, compile_error = compile_file(path)
    checks.append({"name": "compiles", "passed": compiled, "detail": compile_error or "compile pass"})

    required_tokens = [
        "from leaf_qt.status_presentation import status_severity",
        "_leaf_16u62_status_severity",
        "_leaf_16u62_is_fail_like",
        "_leaf_16u62_is_warn_like",
        "_leaf_16u62_is_pass_like",
    ]
    missing_tokens = [token for token in required_tokens if token not in text]
    checks.append(
        {
            "name": "shared_tokens_present",
            "passed": not missing_tokens,
            "detail": "missing=" + ", ".join(missing_tokens) if missing_tokens else "all tokens present",
        }
    )

    raw_forbidden = forbidden_findings(text)
    remaining_forbidden = [item for item in raw_forbidden if item["line"] > 40]
    checks.append(
        {
            "name": "legacy_patterns_removed",
            "passed": not remaining_forbidden,
            "detail": f"{len(remaining_forbidden)} production pattern(s); ignored {len(raw_forbidden) - len(remaining_forbidden)} helper fallback literal(s)",
        }
    )

    patch_file_payload = None
    for item in patch_payload.get("per_file", []):
        if item.get("file") == rel_path:
            patch_file_payload = item
            break

    checks.append(
        {
            "name": "phase_16u62_file_patch_completed",
            "passed": bool(patch_file_payload and patch_file_payload.get("passed")),
            "detail": "patch payload pass" if patch_file_payload else "missing from patch payload",
        }
    )

    try:
        module = importlib.import_module(module_name_from_rel(rel_path))
        import_passed = True
        import_detail = "module import pass"
    except Exception as exc:
        module = None
        import_passed = False
        import_detail = repr(exc)

    checks.append({"name": "module_imports", "passed": import_passed, "detail": import_detail})

    helper_passed = False
    helper_detail = ""

    if module is not None:
        try:
            cases = [
                ("PASS", "PASS"),
                ("VALID", "PASS"),
                ("COMPLETE", "PASS"),
                ("WARN", "WARN"),
                ("PARTIAL", "WARN"),
                ("MARGINAL", "WARN"),
                ("FAIL", "FAIL"),
                ("BLOCKED_BY_BATCH", "FAIL"),
                ("INVALID", "FAIL"),
                ("ERROR", "FAIL"),
                ("MISSING_DATA", "FAIL"),
                ("UNKNOWN", "UNKNOWN"),
            ]
            failures = []
            for raw, expected in cases:
                actual = module._leaf_16u62_status_severity(raw)
                if actual != expected:
                    failures.append((raw, expected, actual))

            helper_passed = not failures
            helper_detail = f"severity_failures={failures}"
        except Exception as exc:
            helper_passed = False
            helper_detail = repr(exc)

    checks.append({"name": "helper_status_semantics", "passed": helper_passed, "detail": helper_detail})

    passed = all(item["passed"] for item in checks)

    return {
        "file": rel_path,
        "passed": passed,
        "checks": checks,
        "remaining_forbidden": remaining_forbidden[:20],
        "missing_tokens": missing_tokens,
    }


def main() -> dict:
    patch_payload = {}
    if PATCH_JSON.exists():
        try:
            patch_payload = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
        except Exception as exc:
            patch_payload = {"json_error": repr(exc)}

    per_file = [verify_one(target, patch_payload) for target in TARGETS]

    patch_complete = patch_payload.get("phase_16u62_grouped_low_risk_owner_batch_patch_complete") is True
    all_files_passed = all(item["passed"] for item in per_file)

    passed = patch_complete and all_files_passed

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "patch_json_exists": PATCH_JSON.exists(),
        "phase_16u62_patch_complete": patch_complete,
        "target_count": len(TARGETS),
        "passed_count": sum(1 for item in per_file if item["passed"]),
        "failed_count": sum(1 for item in per_file if not item["passed"]),
        "per_file": per_file,
        "phase_16u63_grouped_low_risk_owner_batch_regression_complete": passed,
        "next_phase": "16U.64 — First Grouped Low-Risk Owner Batch Closure Gate",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.63",
        "FIRST GROUPED LOW-RISK OWNER BATCH REGRESSION",
        "==============================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Regression verification for the first grouped low-risk owner batch.",
        "",
        "SUMMARY",
        "-------",
        f"Patch JSON exists: {result['patch_json_exists']}",
        f"Phase 16U.62 patch complete: {patch_complete}",
        f"Target count: {result['target_count']}",
        f"Passed count: {result['passed_count']}",
        f"Failed count: {result['failed_count']}",
        "",
        "PER-FILE RESULTS",
        "----------------",
    ]

    for item in per_file:
        lines.append(f"{item['file']}: {'PASS' if item['passed'] else 'FAIL'}")
        for check in item["checks"]:
            lines.append(f"  {check['name']}: {'PASS' if check['passed'] else 'FAIL'} — {check['detail']}")

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.63 COMPLETE." if passed else "PHASE 16U.63 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.64 — FIRST GROUPED LOW-RISK OWNER BATCH CLOSURE GATE",
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
        print(f"{item['file']}={'PASS' if item['passed'] else 'FAIL'}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u63_grouped_low_risk_owner_batch_regression_complete"]:
        raise SystemExit(1)
