from pathlib import Path
import re

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

closed = [
    "failure_root_cause_owner.py",
    "regen_completion_gate_validation_owner.py",
    "regen_system_signoff_validation_owner.py",
    "regen_optimisation_scoring_owner.py",
    "regen_optimisation_report_owner.py",
    "regen_runtime_optimisation_report_owner.py",
    "regen_geometry_report_owner.py",
    "regen_candidate_blueprint_population_validation_owner.py",
    "regen_candidate_creation_report_owner.py",
    "regen_candidate_generation_report_owner.py",
    "regen_candidate_mutation_report_owner.py",
    "regen_runtime_execution_report_owner.py",
]

patterns = [
    r'"PASS"\s+if\s+.+?\s+else\s+"FAIL"',
    r"'PASS'\s+if\s+.+?\s+else\s+'FAIL'",
    r'"FAIL"\s+if\s+.+?\s+else\s+"PASS"',
    r"'FAIL'\s+if\s+.+?\s+else\s+'PASS'",
    r'"WARN"\s+if\s+.+?\s+else\s+"PASS"',
    r"'WARN'\s+if\s+.+?\s+else\s+'PASS'",
    r'\.startswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)',
    r'\.endswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)',
]

print("PHASE_16U114_FAILURE_DIAGNOSTIC")
for name in closed:
    p = LEAF / name
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8", errors="replace")
    hits = []
    for pat in patterns:
        for m in re.finditer(pat, text):
            line_no = text.count("\n", 0, m.start()) + 1
            line = text.splitlines()[line_no - 1].strip()
            hits.append((line_no, pat, line))

    has_shared = "LegacyCompatibilityProducer" in text
    if hits or not has_shared:
        print()
        print(f"FILE: {name}")
        print(f"LegacyCompatibilityProducer={has_shared}")
        for line_no, pat, line in hits[:20]:
            print(f"  line {line_no}: {line}")
