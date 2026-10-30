from pathlib import Path
import py_compile

target = Path("leaf_qt/regen_candidate_mutation_report_owner.py")
s = target.read_text(encoding="utf-8", errors="replace")

if "LegacyCompatibilityProducer" not in s:
    anchor = "from leaf_qt.status_presentation import status_severity"
    if anchor in s:
        s = s.replace(
            anchor,
            "from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity",
            1,
        )

replacements = {
    '"PASS" if check.get("passed") else "FAIL"': 'LegacyCompatibilityProducer.marker_from_bool(check.get("passed"))',
    "'PASS' if check.get('passed') else 'FAIL'": "LegacyCompatibilityProducer.marker_from_bool(check.get('passed'))",
}

for old, new in replacements.items():
    count = s.count(old)
    if count:
        print(f"replacements[{old}]={count}")
        s = s.replace(old, new)

target.write_text(s, encoding="utf-8")
py_compile.compile(str(target), doraise=True)
print("COMPILE_PASS")
