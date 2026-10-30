OWNER_NAME = "REGEN_OPTIMISATION_SELECTION_HISTORY_OWNER"
PHASE = "13K"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_SELECTION_HISTORY_OWNER_PHASE_13K"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_SELECTION_HISTORY_OWNER_PHASE_13K"


def attach_regen_optimisation_selection_history_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_selection_history_owner(results)
    results.update(payload)
    return results


def build_regen_optimisation_selection_history_owner(results):
    blockers = []

    state = results.get("regen_optimisation_selection_state")
    ranked = results.get("regen_optimisation_selection_ranked_candidates", [])
    parent_pool = results.get("regen_optimisation_parent_pool", [])

    if not isinstance(state, dict) or state.get("ready") is not True:
        blockers.append("Selection state is missing or not ready.")

    if not isinstance(ranked, list) or not ranked:
        blockers.append("Ranked candidates are missing.")

    if not isinstance(parent_pool, list) or not parent_pool:
        blockers.append("Parent pool is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None

    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "SELECTION_HISTORY_CREATED_NO_GENERATION_ADVANCE",
            "selection_count": 1,
            "generation_advance_count": 0,
            "solver_execution_count": 0,
            "candidate_acceptance_count": 0,
            "live_commit_count": 0,
            "entries": [
                {
                    "entry_id": "SELECTION_HISTORY_ENTRY_0001",
                    "event": "CANDIDATES_RANKED",
                    "ranked_candidate_count": len(ranked),
                    "best_candidate_id": state.get("best_candidate_id"),
                    "execution_locked": True,
                },
                {
                    "entry_id": "SELECTION_HISTORY_ENTRY_0002",
                    "event": "PARENT_POOL_CREATED",
                    "parent_pool_candidate_ids": [
                        item.get("candidate_id") for item in parent_pool
                    ],
                    "generation_advance_allowed": False,
                },
            ],
        }

    return {
        "regen_optimisation_selection_history_owner_complete": True,
        "phase_13k_selection_history_owner_complete": True,
        "regen_optimisation_selection_history_owner_ready": ready,
        "regen_optimisation_selection_history_owner_status": status,
        "regen_optimisation_selection_history_owner_blockers": blockers,
        "regen_optimisation_selection_history": history,
    }
