OWNER_NAME = "REGEN_RUNTIME_SELECTION_PARENT_POOL_BUILDER"
PHASE = "14C"

PASS_STATUS = "PASS_REGEN_RUNTIME_SELECTION_PARENT_POOL_BUILDER_PHASE_14C"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_SELECTION_PARENT_POOL_BUILDER_PHASE_14C"


def attach_regen_runtime_selection_parent_pool_builder(results):
    if not isinstance(results, dict):
        return results

    ranked = results.get("regen_runtime_selection_ranked_candidates", [])
    blockers = []

    if results.get("regen_runtime_selection_ranking_engine_ready") is not True:
        blockers.append("Runtime selection ranking engine is not ready.")

    if not isinstance(ranked, list) or not ranked:
        blockers.append("No ranked runtime candidates exist for parent pool construction.")

    requested_size = results.get("regen_runtime_parent_pool_size", 4)
    try:
        requested_size = max(1, int(requested_size))
    except Exception:
        requested_size = 4

    parent_pool = []

    if isinstance(ranked, list):
        survivors = [
            dict(item)
            for item in ranked
            if isinstance(item, dict) and item.get("runtime_candidate_survives") is True
        ]

        parent_pool = survivors[:requested_size]

        for item in parent_pool:
            item["runtime_selected_for_parent_pool"] = True

    if not parent_pool:
        blockers.append("No surviving runtime candidates are available for the parent pool.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_selection_parent_pool_builder_complete": True,
        "phase_14c_runtime_selection_parent_pool_builder_complete": True,
        "regen_runtime_selection_parent_pool_builder_ready": ready,
        "regen_runtime_selection_parent_pool_builder_status": status,
        "regen_runtime_selection_parent_pool_builder_blockers": blockers,

        "regen_runtime_parent_pool": parent_pool if ready else [],
        "regen_runtime_parent_pool_candidate_ids": [
            item.get("runtime_candidate_id") for item in parent_pool
        ] if ready else [],
        "regen_runtime_parent_pool_size_actual": len(parent_pool) if ready else 0,
        "regen_runtime_parent_pool_size_requested": requested_size,

        "runtime_candidate_survives": True if ready else False,
        "runtime_candidate_eliminated": False if ready else True,

        "regen_runtime_selection_generation_advanced": False,
        "regen_runtime_selection_live_geometry_committed": False,
    })

    return results
