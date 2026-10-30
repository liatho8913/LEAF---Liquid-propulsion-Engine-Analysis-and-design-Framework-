from pathlib import Path
import json
import re

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"
PM = ROOT / "project_maintenance"

FOUNDATION = PM / "phase_16u131_migration_pipeline_foundation.json"
OUT_JSON = PM / "phase_16u132_wave1_manifest_selection.json"
OUT_TXT = PM / "PHASE_16U132_WAVE1_MANIFEST_SELECTION.txt"

PASS = "PASS_PHASE_16U132_WAVE1_MANIFEST_SELECTION"
FAIL = "FAIL_PHASE_16U132_WAVE1_MANIFEST_SELECTION"

failures = []

def check(condition, message):
    if not condition:
        failures.append(message)

check(FOUNDATION.exists(), "Phase 16U.131 foundation JSON missing")

foundation = {}
if FOUNDATION.exists():
    foundation = json.loads(FOUNDATION.read_text(encoding="utf-8"))

check(
    foundation.get("phase_16u131_migration_pipeline_foundation_complete") is True,
    "Phase 16U.131 foundation completion flag not true",
)

manifest = foundation.get("manifest", [])
check(isinstance(manifest, list), "foundation manifest is not a list")

# Wave 1: low-risk material/coating integration owners.
# These were shown by the live audit as missing the shared producer, not as complex multi-hit legacy files.
wave_prefixes = (
    "bond_coat_",
    "coating_",
    "material_",
)

candidates = []
for item in manifest:
    name = item.get("file")
    if not name:
        continue

    if not name.startswith(wave_prefixes):
        continue

    if not item.get("eligible_for_wave_patch"):
        continue

    path = LEAF / name
    text = path.read_text(encoding="utf-8", errors="replace")

    legacy_hits = []
    for pat in [
        r'"PASS"\s+if\s+.+?\s+else\s+"FAIL"',
        r"'PASS'\s+if\s+.+?\s+else\s+'FAIL'",
        r'"FAIL"\s+if\s+.+?\s+else\s+"PASS"',
        r"'FAIL'\s+if\s+.+?\s+else\s+'PASS'",
        r'"WARN"\s+if\s+.+?\s+else\s+"PASS"',
        r"'WARN'\s+if\s+.+?\s+else\s+'PASS'",
    ]:
        for m in re.finditer(pat, text):
            line_no = text.count("\n", 0, m.start()) + 1
            line = text.splitlines()[line_no - 1].strip()
            if not line.startswith("#"):
                legacy_hits.append({"line": line_no, "content": line})

    candidates.append({
        **item,
        "wave": "16U-WAVE1",
        "reason": "material/coating integration owner; low-risk shared presentation import migration",
        "legacy_hit_count": len(legacy_hits),
        "legacy_hits": legacy_hits,
        "expected_edits": [
            "ensure LegacyCompatibilityProducer import/fallback",
            "ensure status_severity availability",
            "replace any inline PASS/WARN/FAIL ternary marker logic if present",
            "no solver behaviour changes",
            "no public API changes",
        ],
    })

check(bool(candidates), "no Wave 1 candidates selected")

# Keep Wave 1 bounded for safety.
# If more than 12 are found, take 12 in deterministic order.
candidates = sorted(candidates, key=lambda x: x["file"])[:12]

passed = not failures

result = {
    "phase": "16U.132",
    "passed": passed,
    "wave_id": "16U-WAVE1",
    "wave_name": "Material and coating integration owner presentation migration",
    "selected_count": len(candidates),
    "selected_files": [x["file"] for x in candidates],
    "locked_baseline": foundation.get("locked_baseline"),
    "closed_targets_before_wave": foundation.get("closed_targets"),
    "remaining_candidates_before_wave": foundation.get("remaining_candidates"),
    "acceptance_contract": {
        "backup_required_for_each_file": True,
        "pre_hash_required_for_each_file": True,
        "post_hash_required_for_each_file": True,
        "compile_required_for_each_file": True,
        "shared_layer_required_for_each_file": True,
        "legacy_inline_status_logic_removed_for_each_file": True,
        "rollback_available_for_each_file": True,
        "wave_rejected_if_any_file_fails": True,
        "locked_baseline_audit_required_after_wave": True,
        "migration_certificate_required": True,
    },
    "manifest": candidates,
    "phase_16u132_wave1_manifest_selection_complete": passed,
    "next_phase": "16U.133 — Wave 1 Transactional Patch",
    "failures": failures,
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    "LEAF PHASE 16U.132",
    "WAVE 1 MANIFEST SELECTION",
    "=========================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "",
    "WAVE",
    "----",
    "16U-WAVE1 — Material and coating integration owner presentation migration",
    "",
    "ROADMAP STATE",
    "-------------",
    f"Locked baseline: {foundation.get('locked_baseline')}",
    f"Closed before wave: {foundation.get('closed_targets')}",
    f"Remaining before wave: {foundation.get('remaining_candidates')}",
    "",
    f"Selected files: {len(candidates)}",
    "",
    "SELECTED FILES",
    "--------------",
    *[f"- {x['file']}" for x in candidates],
    "",
    "ACCEPTANCE CONTRACT",
    "-------------------",
    "✓ backup per file",
    "✓ pre-hash per file",
    "✓ post-hash per file",
    "✓ compile per file",
    "✓ shared presentation layer per file",
    "✓ no legacy inline status logic per file",
    "✓ rollback per file",
    "✓ reject whole wave if any file fails",
    "✓ locked-baseline audit after wave",
    "✓ migration certificate required",
]

if failures:
    lines += ["", "FAILURES", "--------"]
    lines.extend(f"- {f}" for f in failures)

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(PASS if passed else FAIL)
print("wave_id=16U-WAVE1")
print(f"selected_count={len(candidates)}")
print(f"locked_baseline={foundation.get('locked_baseline')}")
print(f"closed_before_wave={foundation.get('closed_targets')}")
print(f"remaining_before_wave={foundation.get('remaining_candidates')}")
print("selected_files=" + ",".join(x["file"] for x in candidates))
print("next_phase=16U.133_WAVE1_TRANSACTIONAL_PATCH")

if not passed:
    raise SystemExit(1)
