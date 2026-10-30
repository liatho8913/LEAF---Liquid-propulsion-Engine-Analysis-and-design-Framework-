OWNER_NAME = "REGEN_CANDIDATE_COMPARISON_BEST_OWNER"
PHASE = "15B"

PASS_STATUS = "PASS_REGEN_CANDIDATE_COMPARISON_BEST_OWNER_PHASE_15B"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_COMPARISON_BEST_OWNER_PHASE_15B"


def attach_regen_candidate_comparison_best_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_candidate_comparison_current_owner_ready") is not True:
        blockers.append("Candidate comparison current owner is not ready.")

    candidates = results.get("optimisation_viewer_candidates", [])
    best = _select_best(candidates)

    if best is None:
        blockers.append("No best candidate could be selected.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_candidate_comparison_best_owner_complete": True,
        "phase_15b_candidate_comparison_best_owner_complete": True,
        "regen_candidate_comparison_best_owner_ready": ready,
        "regen_candidate_comparison_best_owner_status": status,
        "regen_candidate_comparison_best_owner_blockers": blockers,
        "candidate_comparison_best": best if ready else {},
    })

    return results


def _select_best(candidates):
    if not isinstance(candidates, list) or not candidates:
        return None

    valid = [dict(c) for c in candidates if isinstance(c, dict)]
    if not valid:
        return None

    return max(valid, key=lambda c: _score(c))


def _score(candidate):
    value = candidate.get("score")
    try:
        return float(value)
    except Exception:
        return float("-inf")
