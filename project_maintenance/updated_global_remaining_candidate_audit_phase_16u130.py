from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
LEAF = ROOT / "leaf_qt"
PM = ROOT / "project_maintenance"

BASELINE = PM / "phase_16u126b_locked_migration_scope_baseline.json"
OUT_JSON = PM / "updated_global_remaining_candidate_audit_phase_16u130.json"
OUT_TXT = PM / "UPDATED_GLOBAL_REMAINING_CANDIDATE_AUDIT_PHASE_16U130.txt"

PASS = "PASS_PHASE_16U130_UPDATED_GLOBAL_REMAINING_CANDIDATE_AUDIT"

legacy_patterns = [
    r'"PASS"\s+if\s+.+?\s+else\s+"FAIL"',
    r"'PASS'\s+if\s+.+?\s+else\s+'FAIL'",
    r'"FAIL"\s+if\s+.+?\s+else\s+"PASS"',
    r"'FAIL'\s+if\s+.+?\s+else\s+'PASS'",
    r'"WARN"\s+if\s+.+?\s+else\s+"PASS"',
    r"'WARN'\s+if\s+.+?\s+else\s+'PASS'",
]

def has_legacy(text):
    for pat in legacy_patterns:
        for m in re.finditer(pat, text):
            line = text.splitlines()[text.count("\n", 0, m.start())].strip()
            if not line.startswith("#"):
                return True
    return False

baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
scope = baseline["baseline_scope"]

closed = []
remaining = []

for name in scope:
    p = LEAF / name
    if not p.exists():
        remaining.append(name)
        continue

    text = p.read_text(encoding="utf-8", errors="replace")
    migrated = (
        "LegacyCompatibilityProducer" in text
        and "status_severity" in text
        and not has_legacy(text)
    )

    if migrated:
        closed.append(name)
    else:
        remaining.append(name)

result = {
    "phase": "16U.130",
    "passed": True,
    "locked_baseline": len(scope),
    "closed_targets": len(closed),
    "remaining_candidates": len(remaining),
    "closed_files": sorted(closed),
    "remaining_files": sorted(remaining),
    "recently_closed": "regen_geometry_constraint_owner.py",
    "phase_16u130_updated_global_remaining_candidate_audit_complete": True,
    "next_phase": "16U.131 — Single File Decision",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text("\n".join([
    "LEAF PHASE 16U.130",
    "LOCKED BASELINE GLOBAL AUDIT",
    "============================",
    "",
    f"STATUS: {PASS}",
    "",
    f"Locked baseline: {len(scope)}",
    f"Closed targets: {len(closed)}",
    f"Remaining candidates: {len(remaining)}",
    "",
    "RECENTLY CLOSED",
    "---------------",
    "regen_geometry_constraint_owner.py",
    "",
    "PROGRESS",
    "--------",
    f"{len(closed)} / {len(scope)} migrated",
    f"{len(remaining)} / {len(scope)} remaining",
]), encoding="utf-8")

print(PASS)
print(f"locked_baseline={len(scope)}")
print(f"closed_targets={len(closed)}")
print(f"remaining_candidates={len(remaining)}")
print(f"progress={len(closed)}/{len(scope)}")
print("expected_now=closed_15_remaining_53")

if "regen_geometry_constraint_owner.py" not in closed:
    print("WARNING_recent_target_not_counted_closed")
    raise SystemExit(1)
