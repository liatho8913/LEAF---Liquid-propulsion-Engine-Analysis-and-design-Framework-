from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
LEAF = ROOT / "leaf_qt"
PM = ROOT / "project_maintenance"

OUT_JSON = PM / "updated_global_remaining_candidate_audit_phase_16u119.json"
OUT_TXT = PM / "UPDATED_GLOBAL_REMAINING_CANDIDATE_AUDIT_PHASE_16U119.txt"

PASS = "PASS_PHASE_16U119_UPDATED_GLOBAL_REMAINING_CANDIDATE_AUDIT"
FAIL = "FAIL_PHASE_16U119_UPDATED_GLOBAL_REMAINING_CANDIDATE_AUDIT"

CLOSED_TARGETS = {
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
    "regen_acceptance_audit.py",
}

legacy_patterns = [
    r'"PASS"\s+if\s+.+?\s+else\s+"FAIL"',
    r"'PASS'\s+if\s+.+?\s+else\s+'FAIL'",
    r'"FAIL"\s+if\s+.+?\s+else\s+"PASS"',
    r"'FAIL'\s+if\s+.+?\s+else\s+'PASS'",
    r'"WARN"\s+if\s+.+?\s+else\s+"PASS"',
    r"'WARN'\s+if\s+.+?\s+else\s+'PASS'",
]

def has_production_legacy_logic(text):
    for pattern in legacy_patterns:
        for match in re.finditer(pattern, text):
            line_no = text.count("\n", 0, match.start()) + 1
            line = text.splitlines()[line_no - 1].strip()
            if line.startswith("#"):
                continue
            if "legacy_patterns" in line:
                continue
            if "PASS_STATUS" in line:
                continue
            if "_STATUS" in line and "=" in line:
                continue
            return True, line_no, line
    return False, None, None

closed_verified = []
closed_failed = []
remaining_candidates = []

for path in sorted(LEAF.glob("*.py")):
    text = path.read_text(encoding="utf-8", errors="replace")
    name = path.name

    has_shared = "LegacyCompatibilityProducer" in text
    has_severity = "status_severity" in text
    has_legacy, line_no, line = has_production_legacy_logic(text)

    if name in CLOSED_TARGETS:
        if has_shared and has_severity and not has_legacy:
            closed_verified.append(name)
        else:
            closed_failed.append({
                "file": name,
                "has_shared": has_shared,
                "has_severity": has_severity,
                "has_legacy": has_legacy,
                "line": line_no,
                "content": line,
            })
        continue

    is_structural = any(token in name for token in [
        "owner",
        "validation",
        "report",
        "gate",
        "audit",
    ])

    if is_structural and (has_legacy or (has_severity and not has_shared)):
        remaining_candidates.append(name)

passed = not closed_failed

result = {
    "phase": "16U.119",
    "passed": passed,
    "closed_production_targets": len(closed_verified),
    "closed_verified": closed_verified,
    "closed_failed": closed_failed,
    "remaining_production_candidates": len(remaining_candidates),
    "remaining_candidates": remaining_candidates,
    "phase_16u119_updated_global_remaining_candidate_audit_complete": passed,
    "next_phase": "16U.120 — Single File Decision",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    "LEAF PHASE 16U.119",
    "UPDATED GLOBAL REMAINING CANDIDATE AUDIT",
    "========================================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "",
    f"Closed production targets: {len(closed_verified)}",
    f"Remaining production candidates: {len(remaining_candidates)}",
    f"Closed target verification failures: {len(closed_failed)}",
    "",
    "RECENTLY CLOSED",
    "---------------",
    "regen_acceptance_audit.py",
    "",
    "REMAINING CANDIDATES",
    "--------------------",
]
lines.extend(f"- {c}" for c in remaining_candidates)

if closed_failed:
    lines += ["", "CLOSED TARGET FAILURES", "----------------------"]
    lines.extend(f"- {item}" for item in closed_failed)

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(PASS if passed else FAIL)
print(f"closed_production_targets={len(closed_verified)}")
print(f"remaining_production_candidates={len(remaining_candidates)}")
print(f"closed_target_failures={len(closed_failed)}")

if closed_failed:
    raise SystemExit(1)
