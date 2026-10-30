from pathlib import Path
import json
import py_compile
import re

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "leaf_qt" / "regen_runtime_execution_report_owner.py"
PATCH_JSON = ROOT / "project_maintenance" / "regen_runtime_execution_report_owner_presentation_layer_patch_phase_16u111.json"

PASS = "PASS_PHASE_16U112_REGEN_RUNTIME_EXECUTION_REPORT_OWNER_REGRESSION"
FAIL = "FAIL_PHASE_16U112_REGEN_RUNTIME_EXECUTION_REPORT_OWNER_REGRESSION"

failures = []

def check(condition, message):
    if not condition:
        failures.append(message)

check(TARGET.exists(), "target file missing")

text = TARGET.read_text(encoding="utf-8", errors="replace") if TARGET.exists() else ""

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    failures.append(f"compile failed: {exc}")

check("LegacyCompatibilityProducer" in text, "LegacyCompatibilityProducer missing")
check("status_severity" in text, "status_severity missing")
check("_leaf_16u111_status_severity" in text, "Phase 16U.111 shared severity helper missing")
check("_leaf_16u111_is_fail_like" in text, "fail-like helper missing")
check("_leaf_16u111_is_warn_like" in text, "warn-like helper missing")
check("_leaf_16u111_is_pass_like" in text, "pass-like helper missing")

legacy_patterns = [
    r'"PASS"\s+if\s+.+?\s+else\s+"FAIL"',
    r"'PASS'\s+if\s+.+?\s+else\s+'FAIL'",
    r'"FAIL"\s+if\s+.+?\s+else\s+"PASS"',
    r"'FAIL'\s+if\s+.+?\s+else\s+'PASS'",
    r'"WARN"\s+if\s+.+?\s+else\s+"PASS"',
    r"'WARN'\s+if\s+.+?\s+else\s+'PASS'",
    r'\.startswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)',
    r'\.endswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)',
]

for pattern in legacy_patterns:
    matches = list(re.finditer(pattern, text))
    production_matches = [
        m for m in matches
        if text.count("\n", 0, m.start()) + 1 > 40
    ]
    if production_matches:
        line = text.count("\n", 0, production_matches[0].start()) + 1
        failures.append(f"legacy production status logic remains: {pattern} at line {line}")

check(PATCH_JSON.exists(), "Phase 16U.111 patch JSON missing")

if PATCH_JSON.exists():
    try:
        data = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
        check(
            data.get("phase_16u111_regen_runtime_execution_report_owner_presentation_layer_patch_complete") is True,
            "Phase 16U.111 completion flag is not true",
        )
    except Exception as exc:
        failures.append(f"could not read Phase 16U.111 patch JSON: {exc}")

OUT_JSON = ROOT / "project_maintenance" / "regen_runtime_execution_report_owner_regression_phase_16u112.json"
OUT_TXT = ROOT / "project_maintenance" / "REGEN_RUNTIME_EXECUTION_REPORT_OWNER_REGRESSION_PHASE_16U112.txt"

result = {
    "phase": "16U.112",
    "target": str(TARGET.relative_to(ROOT)),
    "passed": not failures,
    "failures": failures,
    "phase_16u112_regen_runtime_execution_report_owner_regression_complete": not failures,
    "next_phase": "16U.113 — Regen Runtime Execution Report Owner Closure Gate",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    "LEAF PHASE 16U.112",
    "REGEN RUNTIME EXECUTION REPORT OWNER REGRESSION",
    "================================================",
    "",
    f"STATUS: {PASS if not failures else FAIL}",
    f"Target: {result['target']}",
    "",
    "CHECKS",
    "------",
    "compile",
    "LegacyCompatibilityProducer",
    "status_severity",
    "shared helper semantics",
    "legacy production PASS/WARN/FAIL logic removed",
    "Phase 16U.111 patch JSON",
    "Phase 16U.111 completion flag",
    "",
]

if failures:
    lines.append("FAILURES")
    lines.append("--------")
    lines.extend(f"- {f}" for f in failures)
else:
    lines.append("COMPLETION")
    lines.append("----------")
    lines.append("Phase 16U.112 regression complete.")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(PASS if not failures else FAIL)
for f in failures:
    print(f"- {f}")

if failures:
    raise SystemExit(1)
