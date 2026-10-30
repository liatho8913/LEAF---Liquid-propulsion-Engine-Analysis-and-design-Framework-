from pathlib import Path
import ast
import json
import py_compile
import re

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "leaf_qt" / "regen_acceptance_audit.py"
PATCH_JSON = ROOT / "project_maintenance" / "regen_acceptance_audit_presentation_layer_patch_phase_16u116.json"

OUT_JSON = ROOT / "project_maintenance" / "regen_acceptance_audit_regression_phase_16u117.json"
OUT_TXT = ROOT / "project_maintenance" / "REGEN_ACCEPTANCE_AUDIT_REGRESSION_PHASE_16U117.txt"

PASS = "PASS_PHASE_16U117_REGEN_ACCEPTANCE_AUDIT_REGRESSION"
FAIL = "FAIL_PHASE_16U117_REGEN_ACCEPTANCE_AUDIT_REGRESSION"

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

try:
    tree = ast.parse(text)
except Exception as exc:
    tree = None
    failures.append(f"AST parse failed: {exc}")

check("LegacyCompatibilityProducer" in text, "LegacyCompatibilityProducer missing")
check("status_severity" in text, "status_severity missing")
check("marker_from_bool" in text or "marker_from_status" in text, "shared marker producer usage missing")

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

if PATCH_JSON.exists():
    try:
        patch_data = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
        check(
            patch_data.get("phase_16u116_regen_acceptance_audit_presentation_layer_patch_complete") is True,
            "Phase 16U.116 patch completion flag not true",
        )
    except Exception as exc:
        failures.append(f"could not parse patch JSON: {exc}")

function_names = []
if tree is not None:
    function_names = [
        node.name for node in tree.body
        if isinstance(node, ast.FunctionDef)
    ]

audit_like_functions = [
    name for name in function_names
    if "audit" in name.lower()
    or "validate" in name.lower()
    or "check" in name.lower()
    or "run" in name.lower()
    or "build" in name.lower()
]

check(bool(function_names), "no top-level functions found")
check(bool(audit_like_functions), "no audit-like top-level functions found")

passed = not failures

result = {
    "phase": "16U.117",
    "target": "leaf_qt/regen_acceptance_audit.py",
    "passed": passed,
    "function_count": len(function_names),
    "audit_like_functions": audit_like_functions,
    "failures": failures,
    "phase_16u117_regen_acceptance_audit_regression_complete": passed,
    "next_phase": "16U.118 — Closure Gate",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    "LEAF PHASE 16U.117",
    "REGEN ACCEPTANCE AUDIT REGRESSION",
    "==================================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "Target: leaf_qt/regen_acceptance_audit.py",
    "",
    "CHECKS",
    "------",
    "compile",
    "AST parse",
    "LegacyCompatibilityProducer",
    "status_severity",
    "shared marker usage",
    "legacy inline PASS/WARN/FAIL logic removed",
    "Phase 16U.116 patch JSON",
    "Phase 16U.116 patch completion flag",
    "audit-like top-level function presence",
    "",
    f"Top-level function count: {len(function_names)}",
    f"Audit-like functions: {audit_like_functions}",
]

if failures:
    lines += ["", "FAILURES", "--------"]
    lines.extend(f"- {f}" for f in failures)
else:
    lines += ["", "COMPLETION", "----------", "Phase 16U.117 regression complete."]

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(PASS if passed else FAIL)
print(f"target=leaf_qt/regen_acceptance_audit.py")
print(f"function_count={len(function_names)}")
print(f"audit_like_functions={audit_like_functions}")

for f in failures:
    print(f"- {f}")

if not passed:
    raise SystemExit(1)
