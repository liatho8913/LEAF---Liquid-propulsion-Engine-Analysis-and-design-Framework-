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
    '"PASS" if check["passed"] else "FAIL"': 'LegacyCompatibilityProducer.marker_from_bool(check["passed"])',
    "'PASS' if check['passed'] else 'FAIL'": "LegacyCompatibilityProducer.marker_from_bool(check['passed'])",
    '"PASS" if value else "FAIL"': 'LegacyCompatibilityProducer.marker_from_bool(value)',
    "'PASS' if value else 'FAIL'": "LegacyCompatibilityProducer.marker_from_bool(value)",
    '"PASS" if solver_pass else "FAIL"': 'LegacyCompatibilityProducer.marker_from_bool(solver_pass)',
    "'PASS' if solver_pass else 'FAIL'": "LegacyCompatibilityProducer.marker_from_bool(solver_pass)",
    '"FAIL" if check["failed"] else "PASS"': 'LegacyCompatibilityProducer.marker_from_bool(not check["failed"])',
    "'FAIL' if check['failed'] else 'PASS'": "LegacyCompatibilityProducer.marker_from_bool(not check['failed'])",
}

for old, new in replacements.items():
    if old in s:
        print(f"replacing={old}")
        s = s.replace(old, new)

target.write_text(s, encoding="utf-8")
py_compile.compile(str(target), doraise=True)
print("COMPILE_PASS")
