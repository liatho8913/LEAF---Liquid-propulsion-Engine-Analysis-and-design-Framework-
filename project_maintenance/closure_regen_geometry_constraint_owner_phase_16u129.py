from pathlib import Path
import json, py_compile, subprocess, sys, re

ROOT = Path(__file__).resolve().parents[1]
PM = ROOT / "project_maintenance"

TARGET = ROOT / "leaf_qt" / "regen_geometry_constraint_owner.py"
PATCH = PM / "regen_geometry_constraint_owner_presentation_layer_patch_phase_16u127.py"
REGRESSION = PM / "test_regen_geometry_constraint_owner_phase_16u128.py"

PATCH_JSON = PM / "regen_geometry_constraint_owner_presentation_layer_patch_phase_16u127.json"
REGRESSION_JSON = PM / "regen_geometry_constraint_owner_regression_phase_16u128.json"

BASELINE_JSON = PM / "phase_16u126b_locked_migration_scope_baseline.json"

OUT_JSON = PM / "regen_geometry_constraint_owner_closure_gate_phase_16u129.json"
OUT_TXT = PM / "REGEN_GEOMETRY_CONSTRAINT_OWNER_CLOSURE_GATE_PHASE_16U129.txt"

PASS = "PASS_PHASE_16U129_REGEN_GEOMETRY_CONSTRAINT_OWNER_CLOSURE_GATE"
FAIL = "FAIL_PHASE_16U129_REGEN_GEOMETRY_CONSTRAINT_OWNER_CLOSURE_GATE"

failures = []

def check(condition, message):
    if not condition:
        failures.append(message)

def run_script(path):
    check(path.exists(), f"missing script: {path.relative_to(ROOT)}")
    if not path.exists():
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
run_script(PATCH)
run_script(REGRESSION)

text = TARGET.read_text(encoding="utf-8", errors="replace") if TARGET.exists() else ""

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    failures.append(f"target compile failed: {exc}")

check("LegacyCompatibilityProducer" in text, "LegacyCompatibilityProducer missing")
check("status_severity" in text, "status_severity missing")
check("marker_from_bool" in text or "marker_from_status" in text, "shared marker helper usage missing")

for pattern in [
    r'"PASS"\s+if\s+.+?\s+else\s+"FAIL"',
    r"'PASS'\s+if\s+.+?\s+else\s+'FAIL'",
    r'"FAIL"\s+if\s+.+?\s+else\s+"PASS"',
    r"'FAIL'\s+if\s+.+?\s+else\s+'PASS'",
    r'"WARN"\s+if\s+.+?\s+else\s+"PASS"',
    r"'WARN'\s+if\s+.+?\s+else\s+'PASS'",
]:
    for match in re.finditer(pattern, text):
        line_no = text.count("\n", 0, match.start()) + 1
        line = text.splitlines()[line_no - 1].strip()
        if not line.startswith("#"):
            failures.append(f"legacy inline marker remains at line {line_no}: {line}")

check(PATCH_JSON.exists(), "Phase 16U.127 patch JSON missing")
check(REGRESSION_JSON.exists(), "Phase 16U.128 regression JSON missing")
check(BASELINE_JSON.exists(), "locked Phase 16U.126B baseline missing")

if PATCH_JSON.exists():
    data = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
    check(
        data.get("phase_16u127_regen_geometry_constraint_owner_presentation_layer_patch_complete") is True,
        "Phase 16U.127 patch completion flag not true",
    )

if REGRESSION_JSON.exists():
    data = json.loads(REGRESSION_JSON.read_text(encoding="utf-8"))
    check(
        data.get("phase_16u128_regen_geometry_constraint_owner_regression_complete") is True,
        "Phase 16U.128 regression completion flag not true",
    )

baseline_count = None
closed_before = 14
remaining_before = 54
expected_closed_after_audit = 15
expected_remaining_after_audit = 53

if BASELINE_JSON.exists():
    baseline = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
    baseline_count = baseline.get("baseline_scope_count")
    check(baseline_count == 68, f"locked baseline expected 68, got {baseline_count}")

passed = not failures

result = {
    "phase": "16U.129",
    "target": "leaf_qt/regen_geometry_constraint_owner.py",
    "passed": passed,
    "closed_target": "leaf_qt/regen_geometry_constraint_owner.py" if passed else None,
    "locked_baseline": baseline_count,
    "closed_before_this_target": closed_before,
    "remaining_before_this_target": remaining_before,
    "expected_closed_after_next_audit": expected_closed_after_audit,
    "expected_remaining_after_next_audit": expected_remaining_after_audit,
    "phase_16u129_regen_geometry_constraint_owner_closure_gate_complete": passed,
    "next_phase": "16U.130 — Updated Global Remaining Candidate Audit",
    "failures": failures,
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text("\n".join([
    "LEAF PHASE 16U.129",
    "REGEN GEOMETRY CONSTRAINT OWNER CLOSURE GATE",
    "============================================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "Target: leaf_qt/regen_geometry_constraint_owner.py",
    "",
    "ROADMAP",
    "-------",
    f"Locked baseline: {baseline_count}",
    "Closed before this target: 14",
    "Remaining before this target: 54",
    "Expected after next audit: closed=15, remaining=53",
    "",
    "CLOSURE CHECKS",
    "--------------",
    "Phase 16U.127 patch rerun",
    "Phase 16U.128 regression rerun",
    "target compile",
    "LegacyCompatibilityProducer",
    "status_severity",
    "shared marker helper usage",
    "legacy inline PASS/WARN/FAIL logic removed",
    "patch JSON completion flag",
    "regression JSON completion flag",
    "locked baseline present",
    "",
    "FAILURES",
    "--------",
    *[f"- {f}" for f in failures],
]), encoding="utf-8")

print(PASS if passed else FAIL)
print("target=leaf_qt/regen_geometry_constraint_owner.py")
print("closed_target=leaf_qt/regen_geometry_constraint_owner.py" if passed else "closed_target=None")
print(f"locked_baseline={baseline_count}")
print("closed_before_this_target=14")
print("remaining_before_this_target=54")
print("expected_after_next_audit=closed_15_remaining_53")

for f in failures:
    print(f"- {f}")

if not passed:
    raise SystemExit(1)
