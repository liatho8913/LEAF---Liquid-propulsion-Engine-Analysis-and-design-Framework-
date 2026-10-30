from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PM = ROOT / "project_maintenance"

LEDGER = PM / "phase_16u125b_corrected_migration_roadmap_ledger.json"
OUT = PM / "phase_16u126b_locked_migration_scope_baseline.json"

PASS = "PASS_PHASE_16U126B_LOCKED_MIGRATION_SCOPE_BASELINE"

data = json.loads(LEDGER.read_text(encoding="utf-8"))

closed = sorted(set(data["closed_verified"]))
remaining = sorted(set(data["remaining_candidates"]))
baseline_scope = sorted(set(closed + remaining))

result = {
    "phase": "16U.126B",
    "passed": True,
    "baseline_scope_count": len(baseline_scope),
    "closed_at_lock": len(closed),
    "remaining_at_lock": len(remaining),
    "baseline_scope": baseline_scope,
    "closed_at_lock_files": closed,
    "remaining_at_lock_files": remaining,
    "rule": "Future Phase 16U audits must use this fixed baseline_scope. Do not recalculate total scope dynamically.",
    "phase_16u126b_locked_migration_scope_baseline_complete": True,
    "next_phase": "16U.127 — Presentation Layer Patch",
}

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(PASS)
print(f"baseline_scope_count={len(baseline_scope)}")
print(f"closed_at_lock={len(closed)}")
print(f"remaining_at_lock={len(remaining)}")
print("future_remaining_formula=baseline_scope_count_minus_closed_verified_within_baseline")
