from pathlib import Path
import json
import py_compile
import subprocess
import sys
import re

ROOT = Path(__file__).resolve().parents[1]

TARGET = ROOT / "leaf_qt" / "regen_acceptance_audit.py"
PATCH = ROOT / "project_maintenance" / "regen_acceptance_audit_presentation_layer_patch_phase_16u116.py"
REGRESSION = ROOT / "project_maintenance" / "test_regen_acceptance_audit_phase_16u117.py"

PATCH_JSON = ROOT / "project_maintenance" / "regen_acceptance_audit_presentation_layer_patch_phase_16u116.json"
REGRESSION_JSON = ROOT / "project_maintenance" / "regen_acceptance_audit_regression_phase_16u117.json"

OUT_JSON = ROOT / "project_maintenance" / "regen_acceptance_audit_closure_gate_phase_16u118.json"
OUT_TXT = ROOT / "project_maintenance" / "REGEN_ACCEPTANCE_AUDIT_CLOSURE_GATE_PHASE_16U118.txt"

PASS = "PASS_PHASE_16U118_REGEN_ACCEPTANCE_AUDIT_CLOSURE_GATE"
FAIL = "FAIL_PHASE_16U118_REGEN_ACCEPTANCE_AUDIT_CLOSURE_GATE"

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

patch_proc = run_script(PATCH)
regression_proc = run_script(REGRESSION)

text = TARGET.read_text(encoding="utf-8", errors="replace") if TARGET.exists() else ""

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    failures.append(f"target compile failed: {exc}")

check("LegacyCompatibilityProducer" in text, "LegacyCompatibilityProducer missing")
check("status_severity" in text, "status_severity missing")
check("marker_from_bool" in text or "marker_from_status" in text, "shared marker helper usage missing")

legacy_patterns = [
    r'"PASS"\s+if\s+.+?\s+else\s+"FAIL"',
    r"'PASS'\s+if\s+.+?\s+else\s+'FAIL'",
    r'"FAIL"\s+if\s+.+?\s+else\s+"PASS"',
    r"'FAIL'\s+if\s+.+?\s+else\s+'PASS'",
    r'"WARN"\s+if\s+.+?\s+else\s+"PASS"',
    r"'WARN'\s+if\s+.+?\s+else\s+'PASS'",
]

for pattern in legacy_patterns:
    for match in re.finditer(pattern, text):
        line_no = text.count("\n", 0, match.start()) + 1
        line = text.splitlines()[line_no - 1].strip()
        if line.startswith("#"):
            continue
        failures.append(f"legacy inline marker remains at line {line_no}: {line}")

check(PATCH_JSON.exists(), "Phase 16U.116 patch JSON missing")
check(REGRESSION_JSON.exists(), "Phase 16U.117 regression JSON missing")

if PATCH_JSON.exists():
    try:
        patch_data = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
        check(
            patch_data.get("phase_16u116_regen_acceptance_audit_presentation_layer_patch_complete") is True,
            "Phase 16U.116 patch completion flag not true",
        )
    except Exception as exc:
        failures.append(f"could not parse patch JSON: {exc}")

if REGRESSION_JSON.exists():
    try:
        regression_data = json.loads(REGRESSION_JSON.read_text(encoding="utf-8"))
        check(
            regression_data.get("phase_16u117_regen_acceptance_audit_regression_complete") is True,
            "Phase 16U.117 regression completion flag not true",
        )
    except Exception as exc:
        failures.append(f"could not parse regression JSON: {exc}")

passed = not failures

result = {
    "phase": "16U.118",
    "target": "leaf_qt/regen_acceptance_audit.py",
    "passed": passed,
    "failures": failures,
    "phase_16u118_regen_acceptance_audit_closure_gate_complete": passed,
    "closed_target": "leaf_qt/regen_acceptance_audit.py" if passed else None,
    "next_phase": "16U.119 — Updated Global Remaining Candidate Audit",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    "LEAF PHASE 16U.118",
    "REGEN ACCEPTANCE AUDIT CLOSURE GATE",
    "====================================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "Target: leaf_qt/regen_acceptance_audit.py",
    "",
    "CLOSURE CHECKS",
    "--------------",
    "Phase 16U.116 patch rerun",
    "Phase 16U.117 regression rerun",
    "target compile",
    "LegacyCompatibilityProducer",
    "status_severity",
    "shared marker helper usage",
    "legacy inline PASS/WARN/FAIL logic removed",
    "patch JSON completion flag",
    "regression JSON completion flag",
]

if failures:
    lines += ["", "FAILURES", "--------"]
    lines.extend(f"- {f}" for f in failures)
else:
    lines += [
        "",
        "COMPLETION",
        "----------",
        "Phase 16U.118 closure gate complete.",
        "regen_acceptance_audit.py is now formally closed for Phase 16U migration.",
    ]

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(PASS if passed else FAIL)
print("target=leaf_qt/regen_acceptance_audit.py")
print("closed_target=leaf_qt/regen_acceptance_audit.py" if passed else "closed_target=None")

for f in failures:
    print(f"- {f}")

if not passed:
    raise SystemExit(1)
