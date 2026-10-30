OWNER_NAME = "REGEN_CANDIDATE_COMPARISON_CURRENT_OWNER"
PHASE = "15B"

PASS_STATUS = "PASS_REGEN_CANDIDATE_COMPARISON_CURRENT_OWNER_PHASE_15B"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_COMPARISON_CURRENT_OWNER_PHASE_15B"


def attach_regen_candidate_comparison_current_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_candidate_comparison_baseline_owner_ready") is not True:
        blockers.append("Candidate comparison baseline owner is not ready.")

    candidates = results.get("optimisation_viewer_candidates", [])
    current = _select_current(candidates)

    if current is None:
        blockers.append("No current candidate could be selected.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_candidate_comparison_current_owner_complete": True,
        "phase_15b_candidate_comparison_current_owner_complete": True,
        "regen_candidate_comparison_current_owner_ready": ready,
        "regen_candidate_comparison_current_owner_status": status,
        "regen_candidate_comparison_current_owner_blockers": blockers,
        "candidate_comparison_current": current if ready else {},
    })

    return results


def _select_current(candidates):
    if not isinstance(candidates, list) or not candidates:
        return None

    for item in reversed(candidates):
        if isinstance(item, dict):
            return dict(item)

    return None
