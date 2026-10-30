from pathlib import Path
import json, py_compile, subprocess, sys, re

ROOT = Path(__file__).resolve().parents[1]
PM = ROOT / "project_maintenance"
TARGET = ROOT / "leaf_qt" / "regen_acceptance_criteria_owner.py"

PATCH = PM / "regen_acceptance_criteria_owner_presentation_layer_patch_phase_16u121.py"
REGRESSION = PM / "test_regen_acceptance_criteria_owner_phase_16u122.py"
PATCH_JSON = PM / "regen_acceptance_criteria_owner_presentation_layer_patch_phase_16u121.json"
REGRESSION_JSON = PM / "regen_acceptance_criteria_owner_regression_phase_16u122.json"

OUT_JSON = PM / "regen_acceptance_criteria_owner_closure_gate_phase_16u123.json"
OUT_TXT = PM / "REGEN_ACCEPTANCE_CRITERIA_OWNER_CLOSURE_GATE_PHASE_16U123.txt"

PASS = "PASS_PHASE_16U123_REGEN_ACCEPTANCE_CRITERIA_OWNER_CLOSURE_GATE"
FAIL = "FAIL_PHASE_16U123_REGEN_ACCEPTANCE_CRITERIA_OWNER_CLOSURE_GATE"

failures = []

def check(c, m):
    if not c:
        failures.append(m)

def run_script(path):
    check(path.exists(), f"missing script: {path.relative_to(ROOT)}")
    if not path.exists():
        return
    p = subprocess.run([sys.executable, str(path)], cwd=ROOT, text=True, capture_output=True)
    if p.returncode:
        failures.append(f"script failed: {path.relative_to(ROOT)}\n{p.stdout}\n{p.stderr}")

check(TARGET.exists(), "target missing")
run_script(PATCH)
run_script(REGRESSION)

text = TARGET.read_text(encoding="utf-8", errors="replace") if TARGET.exists() else ""

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    failures.append(f"compile failed: {exc}")

check("LegacyCompatibilityProducer" in text, "LegacyCompatibilityProducer missing")
check("status_severity" in text, "status_severity missing")
check("marker_from_bool" in text or "marker_from_status" in text, "shared marker usage missing")

for pattern in [
    r'"PASS"\s+if\s+.+?\s+else\s+"FAIL"',
    r"'PASS'\s+if\s+.+?\s+else\s+'FAIL'",
    r'"FAIL"\s+if\s+.+?\s+else\s+"PASS"',
    r"'FAIL'\s+if\s+.+?\s+else\s+'PASS'",
    r'"WARN"\s+if\s+.+?\s+else\s+"PASS"',
    r"'WARN'\s+if\s+.+?\s+else\s+'PASS'",
]:
    for m in re.finditer(pattern, text):
        line_no = text.count("\n", 0, m.start()) + 1
        line = text.splitlines()[line_no - 1].strip()
        if not line.startswith("#"):
            failures.append(f"legacy inline marker remains at line {line_no}: {line}")

check(PATCH_JSON.exists(), "Phase 16U.121 patch JSON missing")
check(REGRESSION_JSON.exists(), "Phase 16U.122 regression JSON missing")

if PATCH_JSON.exists():
    data = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
    check(data.get("phase_16u121_regen_acceptance_criteria_owner_presentation_layer_patch_complete") is True, "patch completion flag not true")

if REGRESSION_JSON.exists():
    data = json.loads(REGRESSION_JSON.read_text(encoding="utf-8"))
    check(data.get("phase_16u122_regen_acceptance_criteria_owner_regression_complete") is True, "regression completion flag not true")

passed = not failures

result = {
    "phase": "16U.123",
    "target": "leaf_qt/regen_acceptance_criteria_owner.py",
    "passed": passed,
    "closed_target": "leaf_qt/regen_acceptance_criteria_owner.py" if passed else None,
    "closed_targets_before_this": 13,
    "remaining_candidates_before_this_closure": 55,
    "expected_remaining_after_next_audit": 54,
    "phase_16u123_regen_acceptance_criteria_owner_closure_gate_complete": passed,
    "next_phase": "16U.124 — Updated Global Remaining Candidate Audit",
    "failures": failures,
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text("\n".join([
    "LEAF PHASE 16U.123",
    "REGEN ACCEPTANCE CRITERIA OWNER CLOSURE GATE",
    "=============================================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "Target: leaf_qt/regen_acceptance_criteria_owner.py",
    "",
    "WHOLE FEATURE ROADMAP",
    "---------------------",
    "Closed before this closure: 13",
    "Closing now: regen_acceptance_criteria_owner.py",
    "Remaining before closure: 55",
    "Expected remaining after next audit: 54",
    "",
    "NEXT",
    "----",
    "16U.124 — Updated Global Remaining Candidate Audit",
    "",
    "FAILURES",
    "--------",
    *[f"- {f}" for f in failures],
]), encoding="utf-8")

print(PASS if passed else FAIL)
print("target=leaf_qt/regen_acceptance_criteria_owner.py")
print("closed_target=leaf_qt/regen_acceptance_criteria_owner.py" if passed else "closed_target=None")
print("closed_targets_before_this=13")
print("remaining_candidates_before_this_closure=55")
print("expected_remaining_after_next_audit=54")

for f in failures:
    print(f"- {f}")

if not passed:
    raise SystemExit(1)
