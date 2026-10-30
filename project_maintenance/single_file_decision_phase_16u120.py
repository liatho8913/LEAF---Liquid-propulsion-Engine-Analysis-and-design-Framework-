from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PM = ROOT / "project_maintenance"
AUDIT_JSON = PM / "updated_global_remaining_candidate_audit_phase_16u119.json"

OUT_JSON = PM / "single_file_decision_phase_16u120.json"
OUT_TXT = PM / "SINGLE_FILE_DECISION_PHASE_16U120.txt"

PASS = "PASS_PHASE_16U120_SINGLE_FILE_DECISION"
FAIL = "FAIL_PHASE_16U120_SINGLE_FILE_DECISION"

failures = []

def check(condition, message):
    if not condition:
        failures.append(message)

check(AUDIT_JSON.exists(), "Phase 16U.119 audit JSON missing")

audit = {}
if AUDIT_JSON.exists():
    try:
        audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"could not parse audit JSON: {exc}")

check(
    audit.get("phase_16u119_updated_global_remaining_candidate_audit_complete") is True,
    "Phase 16U.119 audit completion flag not true",
)

remaining = audit.get("remaining_candidates", [])
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
    score_value = 0

    if name.startswith("regen_"):
        score_value -= 1000

    for token in priority_tokens:
        if token in name:
            score_value -= 100

    for token in avoid_tokens:
        if token in name:
            score_value += 500

    score_value += len(name)
    return score_value

selection = sorted(remaining, key=score)[0] if remaining else None
target = f"leaf_qt/{selection}" if selection else None

check(selection is not None, "no single-file selection could be made")

passed = not failures

result = {
    "phase": "16U.120",
    "passed": passed,
    "selected_file": target,
    "remaining_candidate_count": len(remaining),
    "selection_reason": "Conservative lowest-risk structural candidate selected from Phase 16U.119 remaining candidates.",
    "phase_16u120_single_file_decision_complete": passed,
    "next_phase": "16U.121 — Presentation Layer Patch",
    "failures": failures,
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    "LEAF PHASE 16U.120",
    "SINGLE FILE DECISION",
    "====================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "",
    f"Remaining candidates: {len(remaining)}",
    f"Selected file: {target}",
    "",
    "DECISION",
    "--------",
    "Proceed to Phase 16U.121 presentation-layer patch for the selected single file.",
    "",
    "SELECTION REASON",
    "----------------",
    result["selection_reason"],
]

if failures:
    lines += ["", "FAILURES", "--------"]
    lines.extend(f"- {f}" for f in failures)

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print(PASS if passed else FAIL)
print(f"selected_file={target}")
print(f"remaining_candidate_count={len(remaining)}")

if not passed:
    raise SystemExit(1)
