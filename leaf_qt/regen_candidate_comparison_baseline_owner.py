OWNER_NAME = "REGEN_CANDIDATE_COMPARISON_BASELINE_OWNER"
PHASE = "15B"

PASS_STATUS = "PASS_REGEN_CANDIDATE_COMPARISON_BASELINE_OWNER_PHASE_15B"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_COMPARISON_BASELINE_OWNER_PHASE_15B"


def attach_regen_candidate_comparison_baseline_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_candidate_comparison_registry_ready") is not True:
        blockers.append("Candidate comparison registry is not ready.")

    candidates = results.get("optimisation_viewer_candidates", [])
    baseline = _select_baseline(candidates)

    if baseline is None:
        blockers.append("No baseline candidate could be selected.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_candidate_comparison_baseline_owner_complete": True,
        "phase_15b_candidate_comparison_baseline_owner_complete": True,
        "regen_candidate_comparison_baseline_owner_ready": ready,
        "regen_candidate_comparison_baseline_owner_status": status,
        "regen_candidate_comparison_baseline_owner_blockers": blockers,
        "candidate_comparison_baseline": baseline if ready else {},
    })

    return results


def _select_baseline(candidates):
    if not isinstance(candidates, list) or not candidates:
        return None

    for item in candidates:
        if isinstance(item, dict) and str(item.get("source_key", "")).endswith("candidate_records"):
            return dict(item)

    for item in candidates:
        if isinstance(item, dict):
            return dict(item)

    return None
