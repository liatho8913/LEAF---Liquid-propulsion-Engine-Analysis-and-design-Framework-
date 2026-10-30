OWNER_NAME = "REGEN_OPTIMISATION_SELECTION_PARENT_POOL_BUILDER"
PHASE = "13K"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_SELECTION_PARENT_POOL_BUILDER_PHASE_13K"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_SELECTION_PARENT_POOL_BUILDER_PHASE_13K"


def attach_regen_optimisation_selection_parent_pool_builder(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_selection_parent_pool_builder(results)
    results.update(payload)
    return results


def build_regen_optimisation_selection_parent_pool_builder(results):
    blockers = []

    validation_ready = results.get("regen_optimisation_selection_validation_owner_ready") is True
    if not validation_ready:
        blockers.append("Selection validation owner is not ready.")

    ranked = results.get("regen_optimisation_selection_ranked_candidates", [])
    if not isinstance(ranked, list) or not ranked:
        blockers.append("Ranked candidates are missing.")

    requested_pool_size = results.get("regen_optimisation_parent_pool_size", 4)
    try:
        requested_pool_size = int(requested_pool_size)
    except Exception:
        requested_pool_size = 4

    requested_pool_size = max(1, requested_pool_size)

    parent_pool = []
    if isinstance(ranked, list):
        survivors = [
            dict(item)
            for item in ranked
            if isinstance(item, dict) and item.get("survives_generation") is True
        ]

        parent_pool = survivors[:requested_pool_size]

        for item in parent_pool:
            item["selected_for_parent_pool"] = True

    if not parent_pool:
        blockers.append("No surviving candidates are available for the parent pool.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_optimisation_selection_parent_pool_builder_complete": True,
        "phase_13k_parent_pool_builder_complete": True,
        "regen_optimisation_selection_parent_pool_builder_ready": ready,
        "regen_optimisation_selection_parent_pool_builder_status": status,
        "regen_optimisation_selection_parent_pool_builder_blockers": blockers,
        "regen_optimisation_parent_pool": parent_pool if ready else [],
        "regen_optimisation_parent_pool_candidate_ids": [
            item.get("candidate_id") for item in parent_pool
        ] if ready else [],
        "regen_optimisation_parent_pool_size_actual": len(parent_pool) if ready else 0,
        "regen_optimisation_parent_pool_size_requested": requested_pool_size,

        "regen_optimisation_parent_pool_solver_executed": False,
        "regen_optimisation_parent_pool_generation_advanced": False,
        "regen_optimisation_parent_pool_live_geometry_committed": False,
    }
