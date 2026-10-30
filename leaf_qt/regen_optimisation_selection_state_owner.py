OWNER_NAME = "REGEN_OPTIMISATION_SELECTION_STATE_OWNER"
PHASE = "13K"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_SELECTION_STATE_OWNER_PHASE_13K"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_SELECTION_STATE_OWNER_PHASE_13K"


def attach_regen_optimisation_selection_state_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_selection_state_owner(results)
    results.update(payload)
    return results


def build_regen_optimisation_selection_state_owner(results):
    blockers = []

    registry = results.get("regen_optimisation_selection_registry")
    parent_pool = results.get("regen_optimisation_parent_pool", [])

    if not isinstance(registry, dict) or registry.get("ready") is not True:
        blockers.append("Selection registry is not ready.")

    if not isinstance(parent_pool, list) or not parent_pool:
        blockers.append("Parent pool has not been built.")

    best = results.get("regen_optimisation_selection_best_candidate")

    if not isinstance(best, dict):
        blockers.append("Best candidate is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    state = None

    if ready:
        state = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": True,
            "selection_state": "SELECTION_COMPLETED_EXECUTION_LOCKED",
            "best_candidate_id": best.get("candidate_id"),
            "parent_pool_candidate_ids": [
                item.get("candidate_id") for item in parent_pool
            ],
            "survivor_count": len([
                item for item in results.get("regen_optimisation_selection_ranked_candidates", [])
                if isinstance(item, dict) and item.get("survives_generation") is True
            ]),
            "generation_advance_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        }

    return {
        "regen_optimisation_selection_state_owner_complete": True,
        "phase_13k_selection_state_owner_complete": True,
        "regen_optimisation_selection_state_owner_ready": ready,
        "regen_optimisation_selection_state_owner_status": status,
        "regen_optimisation_selection_state_owner_blockers": blockers,
        "regen_optimisation_selection_state": state,

        "selection_rank": best.get("selection_rank") if isinstance(best, dict) else None,
        "selection_score": best.get("selection_score") if isinstance(best, dict) else None,
        "selected_for_parent_pool": (
            best.get("candidate_id") in [
                item.get("candidate_id") for item in parent_pool
            ]
            if isinstance(best, dict) and isinstance(parent_pool, list)
            else False
        ),
        "survives_generation": best.get("survives_generation") if isinstance(best, dict) else False,

        "regen_optimisation_selection_execution_locked": True,
        "regen_optimisation_selection_solver_execution_allowed": False,
        "regen_optimisation_selection_candidate_acceptance_allowed": False,
        "regen_optimisation_selection_live_geometry_commit_allowed": False,
        "regen_optimisation_selection_generation_advance_allowed": False,
    }
