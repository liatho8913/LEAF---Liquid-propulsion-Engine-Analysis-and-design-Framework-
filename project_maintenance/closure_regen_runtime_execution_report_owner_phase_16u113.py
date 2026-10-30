from pathlib import Path
import json
import py_compile
import subprocess
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "leaf_qt" / "regen_runtime_execution_report_owner.py"

PATCH = ROOT / "project_maintenance" / "regen_runtime_execution_report_owner_presentation_layer_patch_phase_16u111.py"
REGRESSION = ROOT / "project_maintenance" / "test_regen_runtime_execution_report_owner_phase_16u112.py"

PATCH_JSON = ROOT / "project_maintenance" / "regen_runtime_execution_report_owner_presentation_layer_patch_phase_16u111.json"
REGRESSION_JSON = ROOT / "project_maintenance" / "regen_runtime_execution_report_owner_regression_phase_16u112.json"

OUT_JSON = ROOT / "project_maintenance" / "regen_runtime_execution_report_owner_closure_gate_phase_16u113.json"
OUT_TXT = ROOT / "project_maintenance" / "REGEN_RUNTIME_EXECUTION_REPORT_OWNER_CLOSURE_GATE_PHASE_16U113.txt"

PASS = "PASS_PHASE_16U113_REGEN_RUNTIME_EXECUTION_REPORT_OWNER_CLOSURE_GATE"
FAIL = "FAIL_PHASE_16U113_REGEN_RUNTIME_EXECUTION_REPORT_OWNER_CLOSURE_GATE"

failures = []

def check(condition, message):
    if not condition:
        failures.append(message)

def run_script(path):
    if not path.exists():
        failures.append(f"missing script: {path.relative_to(ROOT)}")
        return None

    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    if proc.returncode != 0:
        failures.append(
            f"script failed: {path.relative_to(ROOT)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )

    return proc

check(TARGET.exists(), "target missing")
check(PATCH.exists(), "Phase 16U.111 patch script missing")
check(REGRESSION.exists(), "Phase 16U.112 regression script missing")

patch_proc = run_script(PATCH)
regression_proc = run_script(REGRESSION)

text = TARGET.read_text(encoding="utf-8", errors="replace") if TARGET.exists() else ""

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    failures.append(f"target compile failed: {exc}")

check("LegacyCompatibilityProducer" in text, "LegacyCompatibilityProducer missing")
check("status_severity" in text, "status_severity missing")
check("_leaf_16u111_status_severity" in text, "Phase 16U.111 severity helper missing")
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
check(REGRESSION_JSON.exists(), "Phase 16U.112 regression JSON missing")

if PATCH_JSON.exists():
    try:
        patch_data = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
        check(
            patch_data.get("phase_16u111_regen_runtime_execution_report_owner_presentation_layer_patch_complete") is True,
            "Phase 16U.111 patch completion flag not true",
        )
    except Exception as exc:
        failures.append(f"could not parse patch JSON: {exc}")

if REGRESSION_JSON.exists():
    try:
        regression_data = json.loads(REGRESSION_JSON.read_text(encoding="utf-8"))
        check(
            regression_data.get("phase_16u112_regen_runtime_execution_report_owner_regression_complete") is True,
            "Phase 16U.112 regression completion flag not true",
        )
    except Exception as exc:
        failures.append(f"could not parse regression JSON: {exc}")

passed = not failures

result = {
    "phase": "16U.113",
    "target": str(TARGET.relative_to(ROOT)),
    "passed": passed,
    "failures": failures,
    "phase_16u113_regen_runtime_execution_report_owner_closure_gate_complete": passed,
    "closed_target": "leaf_qt/regen_runtime_execution_report_owner.py" if passed else None,
    "next_phase": "16U.114 — Updated Global Remaining Candidate Audit",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    "LEAF PHASE 16U.113",
    "REGEN RUNTIME EXECUTION REPORT OWNER CLOSURE GATE",
    "==================================================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    f"Target: {result['target']}",
    "",
    "CLOSURE CHECKS",
    "--------------",
    "Phase 16U.111 patch rerun",
    "Phase 16U.112 regression rerun",
    "target compile",
    "shared presentation helper presence",
    "shared status severity semantics",
    "legacy inline PASS/WARN/FAIL logic removed",
    "patch JSON completion flag",
    "regression JSON completion flag",
    "",
]

if failures:
    lines.append("FAILURES")
    lines.append("--------")
    lines.extend(f"- {f}" for f in failures)
else:
    lines.append("COMPLETION")
    lines.append("----------")
    lines.append("Phase 16U.113 closure gate complete.")
    lines.append("regen_runtime_execution_report_owner.py is now formally closed for Phase 16U migration.")

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(PASS if passed else FAIL)
for f in failures:
    print(f"- {f}")

if not passed:
    raise SystemExit(1)
