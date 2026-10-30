OWNER_NAME = "REGEN_RUNTIME_SELECTION_HISTORY_OWNER"
PHASE = "14C"

PASS_STATUS = "PASS_REGEN_RUNTIME_SELECTION_HISTORY_OWNER_PHASE_14C"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_SELECTION_HISTORY_OWNER_PHASE_14C"


def attach_regen_runtime_selection_history_owner(results):
    if not isinstance(results, dict):
        return results

    ranked = results.get("regen_runtime_selection_ranked_candidates", [])
    parent_pool = results.get("regen_runtime_parent_pool", [])
    blockers = []

    if results.get("regen_runtime_selection_validation_owner_ready") is not True:
        blockers.append("Runtime selection validation owner is not ready.")

    if not isinstance(ranked, list) or not ranked:
        blockers.append("Ranked runtime candidates are missing.")

    if not isinstance(parent_pool, list) or not parent_pool:
        blockers.append("Runtime parent pool is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None
    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "RUNTIME_SELECTION_COMPLETED_NO_GENERATION_ADVANCE",
            "ranked_candidate_count": len(ranked),
            "parent_pool_count": len(parent_pool),
            "generation_advance_count": 0,
            "live_geometry_commit_count": 0,
            "entries": [
                {
                    "entry_id": f"RUNTIME_SELECTION_HISTORY_14C_{i:04d}",
                    "event": "RUNTIME_CANDIDATE_SELECTED",
                    "runtime_candidate_id": item.get("runtime_candidate_id"),
                    "runtime_selection_rank": item.get("runtime_selection_rank"),
                    "runtime_selection_score": item.get("runtime_selection_score"),
                    "selected_for_parent_pool": item.get("runtime_selected_for_parent_pool", False),
                }
                for i, item in enumerate(ranked)
            ],
        }

    results.update({
        "regen_runtime_selection_history_owner_complete": True,
        "phase_14c_runtime_selection_history_owner_complete": True,
        "regen_runtime_selection_history_owner_ready": ready,
        "regen_runtime_selection_history_owner_status": status,
        "regen_runtime_selection_history_owner_blockers": blockers,
        "regen_runtime_selection_history": history,
    })

    return results
