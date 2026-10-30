OWNER_NAME = "REGEN_OPTIMISATION_FOUNDATION_REGISTRY"
PHASE = "13L"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_FOUNDATION_REGISTRY_PHASE_13L"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_FOUNDATION_REGISTRY_PHASE_13L"


def attach_regen_optimisation_foundation_registry(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_foundation_registry(results)
    results.update(payload)
    return results


def build_regen_optimisation_foundation_registry(results):
    blockers = []

    phase_13k_allowed = (
        results.get("phase_13l_optimisation_foundation_allowed") is True
        or results.get("regen_optimisation_foundation_phase_13l_allowed") is True
    )

    phase_13k_complete = (
        results.get("phase_13k_complete") is True
        or results.get("regen_optimisation_selection_master_gate_passed") is True
        or results.get("phase_13k_status") == "PASS_REGEN_OPTIMISATION_SELECTION_FRAMEWORK_PHASE_13K"
    )

    if not phase_13k_allowed:
        blockers.append("Phase 13K has not unlocked Phase 13L optimisation foundation.")

    if not phase_13k_complete:
        blockers.append("Phase 13K selection framework is not complete.")

    parent_pool = results.get("regen_optimisation_parent_pool", [])
    ranked = results.get("regen_optimisation_selection_ranked_candidates", [])

    if not isinstance(ranked, list) or not ranked:
        blockers.append("No ranked candidate set exists from Phase 13K.")

    if not isinstance(parent_pool, list) or not parent_pool:
        blockers.append("No parent pool exists from Phase 13K.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    registry = None

    if ready:
        registry = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": True,
            "optimisation_foundation_id": "REGEN_OPTIMISATION_FOUNDATION_PHASE_13L",
            "completed_foundation_layers": [
                "candidate_blueprint_generation",
                "candidate_population_generation",
                "candidate_mutation_framework",
                "multi_variable_mutation_packaging",
                "candidate_improvement_validation",
                "evolution_engine_foundation",
                "optimisation_selection_framework",
            ],
            "runtime_layers_locked_until_phase_14": [
                "runtime_mutation_execution",
                "runtime_candidate_evaluation",
                "runtime_selection",
                "runtime_generation_advance",
                "runtime_convergence",
            ],
            "phase_14_unlocks": {
                "phase_14a_runtime_mutation_execution_allowed": True,
                "phase_14b_runtime_candidate_evaluation_allowed": False,
                "phase_14c_runtime_selection_allowed": False,
                "phase_14d_runtime_evolution_allowed": False,
                "phase_14e_runtime_convergence_allowed": False,
            },
            "execution_locks": {
                "solver_execution_allowed": False,
                "runtime_optimisation_allowed": False,
                "candidate_acceptance_allowed": False,
                "live_geometry_commit_allowed": False,
                "generation_advance_allowed": False,
            },
        }

    return {
        "regen_optimisation_foundation_registry_complete": True,
        "phase_13l_optimisation_foundation_registry_complete": True,
        "regen_optimisation_foundation_registry_ready": ready,
        "regen_optimisation_foundation_registry_status": status,
        "regen_optimisation_foundation_registry_blockers": blockers,
        "regen_optimisation_foundation_registry": registry,

        "regen_optimisation_foundation_solver_executed": False,
        "regen_optimisation_foundation_runtime_executed": False,
        "regen_optimisation_foundation_generation_advanced": False,
        "regen_optimisation_foundation_candidate_accepted": False,
        "regen_optimisation_foundation_live_geometry_committed": False,
    }
