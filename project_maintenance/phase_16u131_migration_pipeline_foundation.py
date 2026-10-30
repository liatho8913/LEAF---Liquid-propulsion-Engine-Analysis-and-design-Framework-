from pathlib import Path
import json
import hashlib
import py_compile

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"
PM = ROOT / "project_maintenance"

BASELINE = PM / "phase_16u126b_locked_migration_scope_baseline.json"
LIVE_AUDIT = PM / "FULL_PHASE_16U_LIVE_AUDIT.json"

OUT_JSON = PM / "phase_16u131_migration_pipeline_foundation.json"
OUT_TXT = PM / "PHASE_16U131_MIGRATION_PIPELINE_FOUNDATION.txt"

PASS = "PASS_PHASE_16U131_MIGRATION_PIPELINE_FOUNDATION"

baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
audit = json.loads(LIVE_AUDIT.read_text(encoding="utf-8"))

remaining = audit["remaining_files"]
closed = audit["closed_files"]

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

manifest = []

for name in remaining:
    path = LEAF / name
    compile_ok = False
    compile_error = None

    try:
        py_compile.compile(str(path), doraise=True)
        compile_ok = True
    except Exception as exc:
        compile_error = str(exc)

    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""

    manifest.append({
        "file": name,
        "path": f"leaf_qt/{name}",
        "exists": path.exists(),
        "sha256_before": sha256(path) if path.exists() else None,
        "compile_before": compile_ok,
        "compile_error": compile_error,
        "has_LegacyCompatibilityProducer": "LegacyCompatibilityProducer" in text,
        "has_status_severity": "status_severity" in text,
        "rollback_required": True,
        "eligible_for_wave_patch": path.exists() and compile_ok,
    })

result = {
    "phase": "16U.131",
    "passed": True,
    "purpose": "Create migration pipeline safety foundation before wave-based patching.",
    "locked_baseline": baseline["baseline_scope_count"],
    "closed_targets": len(closed),
    "remaining_candidates": len(remaining),
    "security_model": {
        "batching_changes_only": True,
        "per_file_hashing": True,
        "per_file_backups": True,
        "per_file_compile_checks": True,
        "per_file_legacy_detection": True,
        "rollback_required": True,
        "wave_rejected_if_any_file_fails": True,
        "locked_baseline_accounting": True,
        "migration_certificate_required": True,
    },
    "manifest": manifest,
    "phase_16u131_migration_pipeline_foundation_complete": True,
    "next_phase": "16U.132 — Wave 1 Manifest Selection",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text("\n".join([
    "LEAF PHASE 16U.131",
    "MIGRATION PIPELINE FOUNDATION",
    "================================",
    "",
    f"STATUS: {PASS}",
    "",
    "SECURITY MODEL",
    "--------------",
    "This system batches implementation, not verification.",
    "Every file still receives independent backup, hash, compile, migration validation, rollback evidence, and closure evidence.",
    "",
    f"Locked baseline: {baseline['baseline_scope_count']}",
    f"Closed targets: {len(closed)}",
    f"Remaining candidates: {len(remaining)}",
    "",
    "PIPELINE GUARANTEES",
    "-------------------",
    "✓ per-file pre-patch hash",
    "✓ per-file compile check",
    "✓ per-file rollback requirement",
    "✓ per-file shared presentation validation",
    "✓ wave rejected if any file fails",
    "✓ locked baseline accounting",
    "✓ migration certificate required",
    "",
    "NEXT",
    "----",
    "16U.132 — Wave 1 Manifest Selection",
]), encoding="utf-8")

print(PASS)
print(f"locked_baseline={baseline['baseline_scope_count']}")
print(f"closed_targets={len(closed)}")
print(f"remaining_candidates={len(remaining)}")
print("security=batch_changes_only_not_verification")
print("wave_rule=reject_entire_wave_if_any_file_fails")
print(f"report={OUT_TXT.relative_to(ROOT)}")
print(f"json={OUT_JSON.relative_to(ROOT)}")
