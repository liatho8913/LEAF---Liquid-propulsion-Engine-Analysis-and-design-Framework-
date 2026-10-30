from pathlib import Path
import ast
import json
import py_compile
import re

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "leaf_qt" / "regen_acceptance_criteria_owner.py"
PATCH_JSON = ROOT / "project_maintenance" / "regen_acceptance_criteria_owner_presentation_layer_patch_phase_16u121.json"

OUT_JSON = ROOT / "project_maintenance" / "regen_acceptance_criteria_owner_regression_phase_16u122.json"
OUT_TXT = ROOT / "project_maintenance" / "REGEN_ACCEPTANCE_CRITERIA_OWNER_REGRESSION_PHASE_16U122.txt"

PASS = "PASS_PHASE_16U122_REGEN_ACCEPTANCE_CRITERIA_OWNER_REGRESSION"
FAIL = "FAIL_PHASE_16U122_REGEN_ACCEPTANCE_CRITERIA_OWNER_REGRESSION"

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

check(PATCH_JSON.exists(), "Phase 16U.121 patch JSON missing")

if PATCH_JSON.exists():
    try:
        patch_data = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
        check(
            patch_data.get("phase_16u121_regen_acceptance_criteria_owner_presentation_layer_patch_complete") is True,
            "Phase 16U.121 patch completion flag not true",
        )
    except Exception as exc:
        failures.append(f"could not parse patch JSON: {exc}")

function_names = []
class_names = []

if tree is not None:
    function_names = [
        node.name for node in tree.body
        if isinstance(node, ast.FunctionDef)
    ]
    class_names = [
        node.name for node in tree.body
        if isinstance(node, ast.ClassDef)
    ]

owner_like_symbols = [
    name for name in function_names + class_names
    if "owner" in name.lower()
    or "criteria" in name.lower()
    or "acceptance" in name.lower()
    or "build" in name.lower()
    or "validate" in name.lower()
    or "check" in name.lower()
]

check(bool(function_names or class_names), "no top-level functions/classes found")
check(bool(owner_like_symbols), "no owner-like top-level symbols found")

passed = not failures

result = {
    "phase": "16U.122",
    "target": "leaf_qt/regen_acceptance_criteria_owner.py",
    "passed": passed,
    "function_count": len(function_names),
    "class_count": len(class_names),
    "owner_like_symbols": owner_like_symbols,
    "failures": failures,
    "phase_16u122_regen_acceptance_criteria_owner_regression_complete": passed,
    "next_phase": "16U.123 — Closure Gate",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    "LEAF PHASE 16U.122",
    "REGEN ACCEPTANCE CRITERIA OWNER REGRESSION",
    "===========================================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "Target: leaf_qt/regen_acceptance_criteria_owner.py",
    "",
    "CHECKS",
    "------",
    "compile",
    "AST parse",
    "LegacyCompatibilityProducer",
    "status_severity",
    "shared marker usage",
    "legacy inline PASS/WARN/FAIL logic removed",
    "Phase 16U.121 patch JSON",
    "Phase 16U.121 patch completion flag",
    "owner-like top-level symbol presence",
    "",
    f"Top-level function count: {len(function_names)}",
    f"Top-level class count: {len(class_names)}",
    f"Owner-like symbols: {owner_like_symbols}",
]

if failures:
    lines += ["", "FAILURES", "--------"]
    lines.extend(f"- {f}" for f in failures)
else:
    lines += ["", "COMPLETION", "----------", "Phase 16U.122 regression complete."]

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(PASS if passed else FAIL)
print("target=leaf_qt/regen_acceptance_criteria_owner.py")
print(f"function_count={len(function_names)}")
print(f"class_count={len(class_names)}")
print(f"owner_like_symbols={owner_like_symbols}")

for f in failures:
    print(f"- {f}")

if not passed:
    raise SystemExit(1)
