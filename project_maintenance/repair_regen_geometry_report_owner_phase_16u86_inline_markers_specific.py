from pathlib import Path
import py_compile

target = Path("leaf_qt/regen_geometry_report_owner.py")
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

replacements = {
    '"PASS" if value else "FAIL"': 'LegacyCompatibilityProducer.marker_from_bool(value)',
    "'PASS' if solver_pass else 'FAIL'": 'LegacyCompatibilityProducer.marker_from_bool(solver_pass)',
}

counts = {}
for old, new in replacements.items():
    counts[old] = s.count(old)
    s = s.replace(old, new)

target.write_text(s, encoding="utf-8")
py_compile.compile(str(target), doraise=True)

print("PATCHED_REGEN_GEOMETRY_REPORT_OWNER_INLINE_MARKERS_PHASE_16U86")
for old, count in counts.items():
    print(f"replacements[{old}]={count}")
print("COMPILE_PASS")
