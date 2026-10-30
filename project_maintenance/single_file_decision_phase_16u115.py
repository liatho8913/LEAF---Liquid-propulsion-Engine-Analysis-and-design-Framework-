from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PM = ROOT / "project_maintenance"
AUDIT_JSON = PM / "updated_global_remaining_candidate_audit_phase_16u114.json"

OUT_JSON = PM / "single_file_decision_phase_16u115.json"
OUT_TXT = PM / "SINGLE_FILE_DECISION_PHASE_16U115.txt"

PASS = "PASS_PHASE_16U115_SINGLE_FILE_DECISION"
FAIL = "FAIL_PHASE_16U115_SINGLE_FILE_DECISION"

failures = []

def check(condition, message):
    if not condition:
        failures.append(message)

check(AUDIT_JSON.exists(), "Phase 16U.114 audit JSON missing")

audit = {}
if AUDIT_JSON.exists():
    try:
        audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"could not parse audit JSON: {exc}")

check(audit.get("phase_16u114_updated_global_remaining_candidate_audit_complete") is True, "Phase 16U.114 audit completion flag not true")

remaining = audit.get("remaining_candidates", [])
check(isinstance(remaining, list), "remaining_candidates is not a list")
check(bool(remaining), "no remaining candidates found")

# Conservative single-file priority:
# 1. regen files first
# 2. owner/report/validation/gate files before broad UI files
# 3. avoid main_window until late because it is high-risk
# 4. choose shortest/simple-looking structural filename first
avoid_tokens = [
    "main_window",
    "viewer",
    "canvas",
    "widget",
    "dialog",
    "qt",
]

priority_tokens = [
    "owner",
    "report",
    "validation",
    "gate",
    "audit",
]

def score(name):
    s = 0
    if name.startswith("regen_"):
        s -= 1000
    for token in priority_tokens:
        if token in name:
            s -= 100
    for token in avoid_tokens:
        if token in name:
            s += 500
    s += len(name)
    return s

selection = None
if remaining:
    selection = sorted(remaining, key=score)[0]

check(selection is not None, "no single-file selection could be made")

target = f"leaf_qt/{selection}" if selection else None

passed = not failures

result = {
    "phase": "16U.115",
    "passed": passed,
    "selected_file": target,
    "selection_reason": "Conservative lowest-risk structural candidate selected from Phase 16U.114 remaining candidates.",
    "remaining_candidate_count": len(remaining),
    "phase_16u115_single_file_decision_complete": passed,
    "next_phase": "16U.116 — Presentation Layer Patch",
    "failures": failures,
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    "LEAF PHASE 16U.115",
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
    "Proceed to Phase 16U.116 presentation-layer patch for the selected single file.",
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
