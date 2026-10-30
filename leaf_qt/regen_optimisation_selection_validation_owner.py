OWNER_NAME = "REGEN_OPTIMISATION_SELECTION_VALIDATION_OWNER"
PHASE = "13K"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_SELECTION_VALIDATION_OWNER_PHASE_13K"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_SELECTION_VALIDATION_OWNER_PHASE_13K"


def attach_regen_optimisation_selection_validation_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_selection_validation_owner(results)
    results.update(payload)
    return results


def build_regen_optimisation_selection_validation_owner(results):
    blockers = []

    ranked = results.get("regen_optimisation_selection_ranked_candidates", [])
    registry = results.get("regen_optimisation_selection_registry")

    if not isinstance(registry, dict) or registry.get("ready") is not True:
        blockers.append("Selection registry is missing or not ready.")

    if not isinstance(ranked, list) or not ranked:
        blockers.append("Ranked candidate list is missing.")

    seen_ranks = set()
    seen_ids = set()

    for item in ranked:
        if not isinstance(item, dict):
            blockers.append("A ranked selection candidate is not a dictionary.")
            continue

        candidate_id = item.get("candidate_id")
        rank = item.get("selection_rank")
        score = item.get("selection_score")

        if not candidate_id:
            blockers.append("A ranked candidate is missing candidate_id.")
        elif candidate_id in seen_ids:
            blockers.append(f"Duplicate candidate_id detected: {candidate_id}")
        else:
            seen_ids.add(candidate_id)

        if not isinstance(rank, int) or rank <= 0:
            blockers.append(f"Candidate {candidate_id} has invalid selection_rank.")
        elif rank in seen_ranks:
            blockers.append(f"Duplicate selection_rank detected: {rank}")
        else:
            seen_ranks.add(rank)

        if not isinstance(score, (int, float)) or isinstance(score, bool):
            blockers.append(f"Candidate {candidate_id} has invalid selection_score.")

        if item.get("survives_generation") not in (True, False):
            blockers.append(f"Candidate {candidate_id} has invalid survives_generation flag.")

        if item.get("selected_for_parent_pool") not in (True, False):
            blockers.append(f"Candidate {candidate_id} has invalid selected_for_parent_pool flag.")

    _require_execution_locks(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_optimisation_selection_validation_owner_complete": True,
        "phase_13k_selection_validation_owner_complete": True,
        "regen_optimisation_selection_validation_owner_ready": ready,
        "regen_optimisation_selection_validation_owner_status": status,
        "regen_optimisation_selection_validation_owner_blockers": blockers,
        "regen_optimisation_selection_validation": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "validated_candidate_count": len(ranked) if isinstance(ranked, list) else 0,
            "execution_locked": True,
        },

        "regen_optimisation_selection_execution_allowed": False,
        "regen_optimisation_selection_generation_advance_allowed": False,
        "regen_optimisation_selection_solver_execution_allowed": False,
        "regen_optimisation_selection_candidate_acceptance_allowed": False,
        "regen_optimisation_selection_live_geometry_commit_allowed": False,
    }


def _require_execution_locks(results, blockers):
    required_false = {
        "regen_optimisation_runtime_execution_allowed": "Runtime optimisation execution is not locked.",
        "regen_optimisation_candidate_acceptance_allowed": "Candidate acceptance is not locked.",
        "regen_optimisation_live_geometry_commit_allowed": "Live geometry commit is not locked.",
        "regen_generation_advance_execution_allowed": "Generation advance execution is not locked.",
        "regen_evolution_engine_execution_allowed": "Evolution engine execution is not locked.",
        "regen_solver_execution_from_mutation_allowed": "Mutation solver execution is not locked.",
    }

    for key, message in required_false.items():
        if key in results and results.get(key) is not False:
            blockers.append(message)
