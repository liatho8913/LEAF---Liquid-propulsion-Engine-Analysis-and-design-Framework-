from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PM = ROOT / "project_maintenance"
LEDGER_JSON = PM / "phase_16u125b_corrected_migration_roadmap_ledger.json"

OUT_JSON = PM / "single_file_decision_phase_16u126.json"
OUT_TXT = PM / "SINGLE_FILE_DECISION_PHASE_16U126.txt"

PASS = "PASS_PHASE_16U126_SINGLE_FILE_DECISION"
FAIL = "FAIL_PHASE_16U126_SINGLE_FILE_DECISION"

failures = []

def check(condition, message):
    if not condition:
        failures.append(message)

check(LEDGER_JSON.exists(), "Phase 16U.125B corrected ledger JSON missing")

ledger = {}
if LEDGER_JSON.exists():
    try:
        ledger = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"could not parse corrected ledger JSON: {exc}")

check(
    ledger.get("phase_16u125b_corrected_migration_roadmap_ledger_complete") is True,
    "Phase 16U.125B corrected ledger completion flag not true",
)

remaining = ledger.get("remaining_candidates", [])
check(isinstance(remaining, list), "remaining_candidates is not a list")
check(bool(remaining), "no remaining candidates found")

avoid_tokens = [
    "main_window",
    "viewer",
    "canvas",
    "widget",
    "dialog",
    "qt",
    "ui",
]

priority_tokens = [
    "owner",
    "report",
    "validation",
    "gate",
    "audit",
]

def score(name):
    value = 0

    if name.startswith("regen_"):
        value -= 1000

    for token in priority_tokens:
        if token in name:
            value -= 100

    for token in avoid_tokens:
        if token in name:
            value += 500

    value += len(name)
    return value

selection = sorted(remaining, key=score)[0] if remaining else None
target = f"leaf_qt/{selection}" if selection else None

check(selection is not None, "no single-file selection could be made")

passed = not failures

result = {
    "phase": "16U.126",
    "passed": passed,
    "selected_file": target,
    "closed_target_count": ledger.get("closed_target_count"),
    "remaining_candidate_count_before_selection": len(remaining),
    "total_measured_scope": ledger.get("total_measured_scope"),
    "selection_reason": "Conservative lowest-risk structural candidate selected from corrected Phase 16U.125B ledger.",
    "phase_16u126_single_file_decision_complete": passed,
    "next_phase": "16U.127 — Presentation Layer Patch",
    "failures": failures,
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    "LEAF PHASE 16U.126",
    "SINGLE FILE DECISION",
    "====================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "",
    "ROADMAP STATE",
    "-------------",
    f"Closed targets: {ledger.get('closed_target_count')}",
    f"Remaining before selection: {len(remaining)}",
    f"Total measured scope: {ledger.get('total_measured_scope')}",
    "",
    "SELECTED TARGET",
    "---------------",
    str(target),
    "",
    "DECISION",
    "--------",
    "Proceed to Phase 16U.127 presentation-layer patch for the selected single file.",
]

if failures:
    lines += ["", "FAILURES", "--------"]
    lines.extend(f"- {f}" for f in failures)

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(PASS if passed else FAIL)
print(f"selected_file={target}")
print(f"closed_targets={ledger.get('closed_target_count')}")
print(f"remaining_before_selection={len(remaining)}")
print(f"total_measured_scope={ledger.get('total_measured_scope')}")
print("next_phase=16U.127_PRESENTATION_LAYER_PATCH")

if not passed:
    raise SystemExit(1)
