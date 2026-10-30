from pathlib import Path
import py_compile

target = Path("leaf_qt/regen_runtime_optimisation_report_owner.py")
s = target.read_text(encoding="utf-8", errors="replace")

if "LegacyCompatibilityProducer" not in s:
    anchor = "from leaf_qt.status_presentation import status_severity"
    if anchor in s:
        s = s.replace(
            anchor,
            "from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity",
            1,
        )
    else:
        print("STATUS_PRESENTATION_IMPORT_ANCHOR_NOT_FOUND")

old = '"PASS" if check["passed"] else "FAIL"'
new = 'LegacyCompatibilityProducer.marker_from_bool(check["passed"])'

count = s.count(old)
s = s.replace(old, new)

target.write_text(s, encoding="utf-8")
py_compile.compile(str(target), doraise=True)

print("PATCHED_REGEN_RUNTIME_OPTIMISATION_REPORT_OWNER_INLINE_MARKER_PHASE_16U81")
print(f"replacements={count}")
print("COMPILE_PASS")
