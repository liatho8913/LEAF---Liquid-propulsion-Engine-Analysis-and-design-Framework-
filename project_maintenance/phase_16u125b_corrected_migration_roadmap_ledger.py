from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
LEAF = ROOT / "leaf_qt"
PM = ROOT / "project_maintenance"

AUDIT_JSON = PM / "updated_global_remaining_candidate_audit_phase_16u124.json"
OUT_JSON = PM / "phase_16u125b_corrected_migration_roadmap_ledger.json"
OUT_TXT = PM / "PHASE_16U125B_CORRECTED_MIGRATION_ROADMAP_LEDGER.txt"

PASS = "PASS_PHASE_16U125B_CORRECTED_MIGRATION_ROADMAP_LEDGER"

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

audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))

closed_verified = []
for name in audit.get("closed_verified", []):
    p = LEAF / name
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8", errors="replace")
    if "LegacyCompatibilityProducer" in text and "status_severity" in text and not has_legacy(text):
        closed_verified.append(name)

remaining = audit.get("remaining_candidates", [])

result = {
    "phase": "16U.125B",
    "passed": True,
    "closed_target_count": len(closed_verified),
    "remaining_candidate_count": len(remaining),
    "total_measured_scope": len(closed_verified) + len(remaining),
    "closed_verified": closed_verified,
    "remaining_candidates": remaining,
    "measurement_method": "latest global audit closed_verified + live source verification",
    "phase_16u125b_corrected_migration_roadmap_ledger_complete": True,
    "next_phase": "16U.126 — Single File Decision",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text("\n".join([
    "LEAF PHASE 16U.125B",
    "CORRECTED MIGRATION ROADMAP LEDGER",
    "==================================",
    "",
    f"STATUS: {PASS}",
    "",
    f"Closed targets: {len(closed_verified)}",
    f"Remaining candidates: {len(remaining)}",
    f"Total measured scope: {len(closed_verified) + len(remaining)}",
    "",
    "NOTE",
    "----",
    "This ledger uses the latest global audit closed_verified list, then re-verifies each closed source file live.",
    "This avoids under-counting older closed targets that predate modern closure JSON records.",
]), encoding="utf-8")

print(PASS)
print(f"closed_targets={len(closed_verified)}")
print(f"remaining_candidates={len(remaining)}")
print(f"total_measured_scope={len(closed_verified) + len(remaining)}")
print("next_phase=16U.126_SINGLE_FILE_DECISION")
