OWNER_NAME = "REGEN_RUNTIME_SELECTION_VALIDATION_OWNER"
PHASE = "14C"

PASS_STATUS = "PASS_REGEN_RUNTIME_SELECTION_VALIDATION_OWNER_PHASE_14C"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_SELECTION_VALIDATION_OWNER_PHASE_14C"


def attach_regen_runtime_selection_validation_owner(results):
    if not isinstance(results, dict):
        return results

    ranked = results.get("regen_runtime_selection_ranked_candidates", [])
    parent_pool = results.get("regen_runtime_parent_pool", [])
    blockers = []

    if results.get("regen_runtime_selection_parent_pool_builder_ready") is not True:
        blockers.append("Runtime parent pool builder is not ready.")

    if not isinstance(ranked, list) or not ranked:
        blockers.append("Ranked runtime candidates are missing.")

    if not isinstance(parent_pool, list) or not parent_pool:
        blockers.append("Runtime parent pool is missing.")

    seen_ranks = set()
    seen_ids = set()

    if isinstance(ranked, list):
        for item in ranked:
            if not isinstance(item, dict):
                blockers.append("Ranked runtime selection item is not a dictionary.")
                continue

            cid = item.get("runtime_candidate_id")
            rank = item.get("runtime_selection_rank")
            score = item.get("runtime_selection_score")

            if not cid:
                blockers.append("Ranked runtime selection item is missing runtime_candidate_id.")
            elif cid in seen_ids:
                blockers.append(f"Duplicate runtime candidate id: {cid}")
            else:
                seen_ids.add(cid)

            if not isinstance(rank, int) or rank <= 0:
                blockers.append(f"Runtime candidate {cid} has invalid rank.")
            elif rank in seen_ranks:
                blockers.append(f"Duplicate runtime selection rank: {rank}")
            else:
                seen_ranks.add(rank)

            if not isinstance(score, (int, float)) or isinstance(score, bool):
                blockers.append(f"Runtime candidate {cid} has invalid selection score.")

            if item.get("runtime_candidate_survives") not in (True, False):
                blockers.append(f"Runtime candidate {cid} has invalid survives flag.")

            if item.get("runtime_candidate_eliminated") not in (True, False):
                blockers.append(f"Runtime candidate {cid} has invalid eliminated flag.")

    if results.get("regen_generation_advance_execution_allowed") is not False:
        blockers.append("Generation advancement is not globally locked.")

    if results.get("regen_optimisation_live_geometry_commit_allowed") is not False:
        blockers.append("Live geometry commit is not globally locked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_selection_validation_owner_complete": True,
        "phase_14c_runtime_selection_validation_owner_complete": True,
        "regen_runtime_selection_validation_owner_ready": ready,
        "regen_runtime_selection_validation_owner_status": status,
        "regen_runtime_selection_validation_owner_blockers": blockers,
        "regen_runtime_selection_validation": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "ranked_candidate_count": len(ranked) if isinstance(ranked, list) else 0,
            "parent_pool_count": len(parent_pool) if isinstance(parent_pool, list) else 0,
            "generation_advance_locked": True,
            "live_geometry_commit_locked": True,
        },

        "phase_14d_runtime_evolution_allowed": ready,
        "regen_runtime_selection_generation_advance_allowed": False,
        "regen_runtime_selection_live_geometry_commit_allowed": False,
    })

    return results
