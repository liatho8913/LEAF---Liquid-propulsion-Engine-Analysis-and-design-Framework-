from pathlib import Path
import ast, json, py_compile, re

ROOT = Path(__file__).resolve().parents[1]
PM = ROOT / "project_maintenance"
TARGET = ROOT / "leaf_qt" / "regen_geometry_constraint_owner.py"
PATCH_JSON = PM / "regen_geometry_constraint_owner_presentation_layer_patch_phase_16u127.json"

OUT_JSON = PM / "regen_geometry_constraint_owner_regression_phase_16u128.json"
OUT_TXT = PM / "REGEN_GEOMETRY_CONSTRAINT_OWNER_REGRESSION_PHASE_16U128.txt"

PASS = "PASS_PHASE_16U128_REGEN_GEOMETRY_CONSTRAINT_OWNER_REGRESSION"
FAIL = "FAIL_PHASE_16U128_REGEN_GEOMETRY_CONSTRAINT_OWNER_REGRESSION"

failures = []

def check(c, m):
    if not c:
        failures.append(m)

check(TARGET.exists(), "target missing")
text = TARGET.read_text(encoding="utf-8", errors="replace") if TARGET.exists() else ""

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    failures.append(f"compile failed: {exc}")

try:
    tree = ast.parse(text)
except Exception as exc:
    tree = None
    failures.append(f"AST parse failed: {exc}")

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

check(PATCH_JSON.exists(), "Phase 16U.127 patch JSON missing")
if PATCH_JSON.exists():
    data = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
    check(data.get("phase_16u127_regen_geometry_constraint_owner_presentation_layer_patch_complete") is True, "patch completion flag not true")

function_names = []
if tree:
    function_names = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]

owner_like = [
    n for n in function_names
    if any(t in n.lower() for t in ["owner", "constraint", "geometry", "build", "validate", "check"])
]

check(bool(function_names), "no top-level functions found")
check(bool(owner_like), "no owner-like functions found")

passed = not failures

result = {
    "phase": "16U.128",
    "target": "leaf_qt/regen_geometry_constraint_owner.py",
    "passed": passed,
    "function_count": len(function_names),
    "owner_like_functions": owner_like,
    "phase_16u128_regen_geometry_constraint_owner_regression_complete": passed,
    "failures": failures,
    "next_phase": "16U.129 — Closure Gate",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text("\n".join([
    "LEAF PHASE 16U.128",
    "REGEN GEOMETRY CONSTRAINT OWNER REGRESSION",
    "==========================================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "Target: leaf_qt/regen_geometry_constraint_owner.py",
    "",
    "ROADMAP",
    "-------",
    "Locked baseline: 68",
    "Closed before this target: 14",
    "Remaining before this target: 54",
    "Expected after closure + audit: closed=15, remaining=53",
    "",
    "FAILURES",
    "--------",
    *[f"- {f}" for f in failures],
]), encoding="utf-8")

print(PASS if passed else FAIL)
print("target=leaf_qt/regen_geometry_constraint_owner.py")
print(f"function_count={len(function_names)}")
print(f"owner_like_functions={owner_like}")
print("locked_baseline=68")
print("closed_before_this_target=14")
print("remaining_before_this_target=54")
print("expected_after_closure_audit=closed_15_remaining_53")

for f in failures:
    print(f"- {f}")

if not passed:
    raise SystemExit(1)
