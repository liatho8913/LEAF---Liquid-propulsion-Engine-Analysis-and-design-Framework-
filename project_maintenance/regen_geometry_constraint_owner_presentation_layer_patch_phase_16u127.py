from pathlib import Path
import json, py_compile, re, shutil

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "leaf_qt" / "regen_geometry_constraint_owner.py"
PM = ROOT / "project_maintenance"

OUT_JSON = PM / "regen_geometry_constraint_owner_presentation_layer_patch_phase_16u127.json"
OUT_TXT = PM / "REGEN_GEOMETRY_CONSTRAINT_OWNER_PRESENTATION_LAYER_PATCH_PHASE_16U127.txt"
BACKUP = PM / "regen_geometry_constraint_owner_phase_16u127_backup.py"

PASS = "PASS_PHASE_16U127_REGEN_GEOMETRY_CONSTRAINT_OWNER_PRESENTATION_LAYER_PATCH"
FAIL = "FAIL_PHASE_16U127_REGEN_GEOMETRY_CONSTRAINT_OWNER_PRESENTATION_LAYER_PATCH"

failures = []
applied = []

fallback = '''try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    def status_severity(value):
        text = str(value or "").upper()
        if "FAIL" in text or "BLOCKED" in text or "ERROR" in text:
            return "FAIL"
        if "WARN" in text or "PARTIAL" in text or "DEGRADED" in text:
            return "WARN"
        if "PASS" in text or "OK" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"

    class LegacyCompatibilityProducer:
        @staticmethod
        def marker_from_bool(value, pass_marker="PASS", fail_marker="FAIL"):
            return pass_marker if bool(value) else fail_marker

        @staticmethod
        def marker_from_status(value):
            severity = status_severity(value)
            if severity in {"PASS", "WARN", "FAIL"}:
                return severity
            return "UNKNOWN"

        @staticmethod
        def status_severity(value):
            return status_severity(value)

'''

if not TARGET.exists():
    failures.append("target missing")
    text = ""
else:
    shutil.copy2(TARGET, BACKUP)
    text = TARGET.read_text(encoding="utf-8", errors="replace")

original = text

if "LegacyCompatibilityProducer" not in text:
    if "from leaf_qt.status_presentation import status_severity" in text:
        text = text.replace(
            "from leaf_qt.status_presentation import status_severity",
            "from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity",
            1,
        )
        applied.append("extended_existing_status_presentation_import")
    elif "from leaf_qt.status_presentation import" in text:
        text = re.sub(
            r"from leaf_qt\.status_presentation import ([^\n]+)",
            lambda m: m.group(0) if "LegacyCompatibilityProducer" in m.group(1)
            else "from leaf_qt.status_presentation import LegacyCompatibilityProducer, " + m.group(1),
            text,
            count=1,
        )
        applied.append("extended_existing_status_presentation_import_generic")
    else:
        lines = text.splitlines(True)
        idx = 0
        while idx < len(lines):
            stripped = lines[idx].strip()
            if stripped.startswith("#") or stripped == "":
                idx += 1
                continue
            if stripped.startswith('"""') or stripped.startswith("'''"):
                quote = stripped[:3]
                idx += 1
                while idx < len(lines) and quote not in lines[idx]:
                    idx += 1
                idx += 1
                continue
            break
        text = "".join(lines[:idx]) + fallback + "".join(lines[idx:])
        applied.append("inserted_status_presentation_import_fallback")

replacements = [
    (r'"PASS"\s+if\s+([^,\n]+?)\s+else\s+"FAIL"', r'LegacyCompatibilityProducer.marker_from_bool(\1)'),
    (r"'PASS'\s+if\s+([^,\n]+?)\s+else\s+'FAIL'", r'LegacyCompatibilityProducer.marker_from_bool(\1)'),
    (r'"FAIL"\s+if\s+([^,\n]+?)\s+else\s+"PASS"', r'LegacyCompatibilityProducer.marker_from_bool(not (\1))'),
    (r"'FAIL'\s+if\s+([^,\n]+?)\s+else\s+'PASS'", r'LegacyCompatibilityProducer.marker_from_bool(not (\1))'),
    (r'"WARN"\s+if\s+([^,\n]+?)\s+else\s+"PASS"', r'("WARN" if bool(\1) else "PASS")'),
    (r"'WARN'\s+if\s+([^,\n]+?)\s+else\s+'PASS'", r'("WARN" if bool(\1) else "PASS")'),
]

for pattern, repl in replacements:
    text, count = re.subn(pattern, repl, text)
    if count:
        applied.append(f"regex_replacement:{pattern}:{count}")

if TARGET.exists():
    TARGET.write_text(text, encoding="utf-8")

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    failures.append(f"compile failed after patch: {exc}")
    TARGET.write_text(original, encoding="utf-8")
    py_compile.compile(str(TARGET), doraise=True)

patched = TARGET.read_text(encoding="utf-8", errors="replace") if TARGET.exists() else ""
if "LegacyCompatibilityProducer" not in patched:
    failures.append("LegacyCompatibilityProducer missing after patch")
if "status_severity" not in patched:
    failures.append("status_severity missing after patch")

passed = not failures

result = {
    "phase": "16U.127",
    "target": "leaf_qt/regen_geometry_constraint_owner.py",
    "passed": passed,
    "applied": applied,
    "backup": str(BACKUP.relative_to(ROOT)),
    "phase_16u127_regen_geometry_constraint_owner_presentation_layer_patch_complete": passed,
    "failures": failures,
    "next_phase": "16U.128 — Regression",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text("\n".join([
    "LEAF PHASE 16U.127",
    "REGEN GEOMETRY CONSTRAINT OWNER PRESENTATION LAYER PATCH",
    "=========================================================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "Target: leaf_qt/regen_geometry_constraint_owner.py",
    f"Backup: {BACKUP.relative_to(ROOT)}",
    "",
    "APPLIED",
    "-------",
    *[f"- {a}" for a in applied],
    "",
    "FAILURES",
    "--------",
    *[f"- {f}" for f in failures],
]), encoding="utf-8")

print(PASS if passed else FAIL)
print("target=leaf_qt/regen_geometry_constraint_owner.py")
print(f"applied={applied}")
print(f"backup={BACKUP.relative_to(ROOT)}")

if not passed:
    raise SystemExit(1)
