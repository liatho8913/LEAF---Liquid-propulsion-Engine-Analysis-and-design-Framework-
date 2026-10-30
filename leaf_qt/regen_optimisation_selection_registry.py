OWNER_NAME = "REGEN_OPTIMISATION_SELECTION_REGISTRY"
PHASE = "13K"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_SELECTION_REGISTRY_PHASE_13K"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_SELECTION_REGISTRY_PHASE_13K"


def attach_regen_optimisation_selection_registry(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_selection_registry(results)
    results.update(payload)
    return results


def build_regen_optimisation_selection_registry(results):
    ranked = results.get("regen_optimisation_selection_ranked_candidates", [])

    blockers = []

    if not isinstance(ranked, list) or not ranked:
        blockers.append("Selection ranking engine has not produced ranked candidates.")

    generation_registry = results.get("regen_generation_registry")
    evolution_registry = results.get("regen_evolution_registry")

    if generation_registry is None and evolution_registry is None:
        blockers.append("No generation or evolution registry is available from Phase 13J.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    registry = None
    if ready:
        generation_id = _generation_id(results)
        registry = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": True,
            "selection_registry_id": f"SELECTION_REGISTRY_FOR_{generation_id}",
            "source_generation_id": generation_id,
            "ranked_candidate_count": len(ranked),
            "best_candidate_id": ranked[0].get("candidate_id") if ranked else None,
            "registered_selection_fields": [
                "selection_rank",
                "selection_score",
                "selected_for_parent_pool",
                "survives_generation",
            ],
            "permissions": {
                "parent_pool_building_allowed": True,
                "generation_advance_execution_allowed": False,
                "solver_execution_allowed": False,
                "candidate_acceptance_allowed": False,
                "live_geometry_commit_allowed": False,
            },
        }

    return {
        "regen_optimisation_selection_registry_complete": True,
        "phase_13k_selection_registry_complete": True,
        "regen_optimisation_selection_registry_ready": ready,
        "regen_optimisation_selection_registry_status": status,
        "regen_optimisation_selection_registry_blockers": blockers,
        "regen_optimisation_selection_registry": registry,

        "regen_optimisation_selection_registry_solver_executed": False,
        "regen_optimisation_selection_registry_live_geometry_modified": False,
    }


def _generation_id(results):
    generation_registry = results.get("regen_generation_registry")
    if isinstance(generation_registry, dict):
        current = generation_registry.get("current_generation")
        if isinstance(current, dict) and current.get("generation_id"):
            return str(current.get("generation_id"))

    evolution = results.get("regen_evolution_engine_foundation")
    if isinstance(evolution, dict):
        registry = evolution.get("generation_registry")
        if isinstance(registry, dict):
            current = registry.get("current_generation")
            if isinstance(current, dict) and current.get("generation_id"):
                return str(current.get("generation_id"))

    return "GENERATION_0000"
