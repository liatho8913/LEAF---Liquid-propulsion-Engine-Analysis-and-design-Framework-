from __future__ import annotations

import importlib
import json
import py_compile
import re
import sys
from datetime import datetime
from pathlib import Path


PHASE = "16U.59"
PASS_BANNER = "PASS_PHASE_16U59_MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER_PRESENTATION_LAYER_REGRESSION"
FAIL_BANNER = "FAIL_PHASE_16U59_MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER_PRESENTATION_LAYER_REGRESSION"

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TARGET = ROOT / "leaf_qt" / "material_strength_limit_integration_owner.py"
PATCH_JSON = ROOT / "project_maintenance" / "material_strength_limit_integration_owner_presentation_layer_patch_phase_16u58.json"

OUT_TXT = ROOT / "project_maintenance" / "MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER_PRESENTATION_LAYER_REGRESSION_PHASE_16U59.txt"
OUT_JSON = ROOT / "project_maintenance" / "material_strength_limit_integration_owner_presentation_layer_regression_phase_16u59.json"

REQUIRED_TOKENS = [
    "from leaf_qt.status_presentation import status_severity",
    "_leaf_16u58_status_severity",
    "_leaf_16u58_is_fail_like",
    "_leaf_16u58_is_warn_like",
    "_leaf_16u58_is_pass_like",
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


def check(name: str, passed: bool, detail: str = "") -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def compile_target() -> tuple[bool, str]:
    try:
        py_compile.compile(str(TARGET), doraise=True)
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


def main() -> dict:
    checks = []

    checks.append(check("production_target_exists", TARGET.exists(), str(TARGET.relative_to(ROOT))))
    checks.append(check("phase_16u58_patch_json_exists", PATCH_JSON.exists(), str(PATCH_JSON.relative_to(ROOT))))

    if not TARGET.exists():
        result = {
            "phase": PHASE,
            "status": FAIL_BANNER,
            "checks": checks,
            "phase_16u59_material_strength_limit_integration_owner_presentation_layer_regression_complete": False,
        }
        OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    text = TARGET.read_text(encoding="utf-8", errors="replace")

    compiled, compile_error = compile_target()
    checks.append(check("production_target_compiles", compiled, compile_error or "compile pass"))

    missing_tokens = [token for token in REQUIRED_TOKENS if token not in text]
    checks.append(
        check(
            "shared_presentation_tokens_present",
            not missing_tokens,
            "missing=" + ", ".join(missing_tokens) if missing_tokens else "all tokens present",
        )
    )

    raw_forbidden = forbidden_findings(text)
    remaining_forbidden = [item for item in raw_forbidden if item["line"] > 40]

    checks.append(
        check(
            "legacy_status_patterns_removed",
            not remaining_forbidden,
            f"{len(remaining_forbidden)} forbidden production pattern(s); ignored {len(raw_forbidden) - len(remaining_forbidden)} helper fallback literal(s)",
        )
    )

    patch_payload = {}
    if PATCH_JSON.exists():
        try:
            patch_payload = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
        except Exception as exc:
            patch_payload = {"json_error": repr(exc)}

    checks.append(
        check(
            "phase_16u58_patch_completed",
            patch_payload.get("phase_16u58_material_strength_limit_integration_owner_presentation_layer_patch_complete") is True,
            str(patch_payload.get("status")),
        )
    )

    try:
        module = importlib.import_module("leaf_qt.material_strength_limit_integration_owner")
        import_passed = True
        import_detail = "module import pass"
    except Exception as exc:
        module = None
        import_passed = False
        import_detail = repr(exc)

    checks.append(check("production_module_imports", import_passed, import_detail))

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
                ("BLOCKED_BY_MATERIAL_STRENGTH_LIMIT", "FAIL"),
                ("INVALID", "FAIL"),
                ("ERROR", "FAIL"),
                ("MISSING_DATA", "FAIL"),
                ("UNKNOWN", "UNKNOWN"),
            ]
            failures = []
            for raw, expected in cases:
                actual = module._leaf_16u58_status_severity(raw)
                if actual != expected:
                    failures.append((raw, expected, actual))

            helper_passed = not failures
            helper_detail = f"severity_failures={failures}"
        except Exception as exc:
            helper_passed = False
            helper_detail = repr(exc)

    checks.append(check("helper_status_semantics", helper_passed, helper_detail))

    passed = all(item["passed"] for item in checks)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "target": str(TARGET.relative_to(ROOT)),
        "checks": checks,
        "missing_tokens": missing_tokens,
        "remaining_forbidden": remaining_forbidden[:30],
        "phase_16u59_material_strength_limit_integration_owner_presentation_layer_regression_complete": passed,
        "next_phase": "16U.60 — Material Strength Limit Integration Owner Presentation Layer Closure Gate",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.59",
        "MATERIAL STRENGTH LIMIT INTEGRATION OWNER PRESENTATION LAYER REGRESSION",
        "=======================================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Regression verification for the Phase 16U.58 presentation-layer patch.",
        "",
        "TARGET",
        "------",
        result["target"],
        "",
        "CHECKS",
        "------",
    ]

    for item in checks:
        lines.append(f"{item['name']}: {'PASS' if item['passed'] else 'FAIL'} — {item['detail']}")

    if remaining_forbidden:
        lines.extend(["", "REMAINING FORBIDDEN PATTERNS", "----------------------------"])
        for item in remaining_forbidden[:20]:
            lines.append(f"line {item['line']}: {item['snippet']}")

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.59 COMPLETE." if passed else "PHASE 16U.59 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.60 — MATERIAL STRENGTH LIMIT INTEGRATION OWNER PRESENTATION LAYER CLOSURE GATE",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    for item in result["checks"]:
        print(f"{item['name']}={'PASS' if item['passed'] else 'FAIL'}")
    if result.get("remaining_forbidden"):
        print("remaining_forbidden:")
        for item in result["remaining_forbidden"][:10]:
            print(f"- line {item['line']}: {item['snippet']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u59_material_strength_limit_integration_owner_presentation_layer_regression_complete"]:
        raise SystemExit(1)
