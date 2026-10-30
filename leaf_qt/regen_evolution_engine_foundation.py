OWNER_NAME = "REGEN_EVOLUTION_ENGINE_FOUNDATION"
PHASE = "13J"
PASS_STATUS = "PASS_REGEN_EVOLUTION_ENGINE_FOUNDATION_PHASE_13J"
FAIL_STATUS = "FAIL_REGEN_EVOLUTION_ENGINE_FOUNDATION_PHASE_13J"

def attach_regen_evolution_engine_foundation(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_evolution_engine_foundation(results))
    return results

def build_regen_evolution_engine_foundation(results):
    blockers = []

    allowed = (
        results.get("phase_13j_evolution_engine_foundation_allowed") is True
        and results.get("regen_evolution_engine_foundation_allowed") is True
    )
    if not allowed:
        blockers.append("13I candidate improvement validation has not allowed evolution engine foundation.")

    improvement_framework = results.get("regen_candidate_improvement_validation_framework", {})
    improvement_records = results.get("regen_candidate_improvement_validation_records", [])
    population = results.get("regen_candidate_blueprint_population", {})

    if not isinstance(improvement_framework, dict) or improvement_framework.get("ready") is not True:
        blockers.append("Candidate improvement validation framework is missing or not ready.")
    if not isinstance(population, dict) or population.get("ready") is not True:
        blockers.append("Candidate blueprint population is missing or not ready.")
    if not isinstance(improvement_records, list) or not improvement_records:
        blockers.append("Candidate improvement records are missing.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    foundation = _build_foundation(population, improvement_records) if ready else None

    return {
        "regen_evolution_engine_foundation_complete": True,
        "phase_13j_regen_evolution_engine_foundation_complete": True,
        "regen_evolution_engine_foundation_ready": ready,
        "regen_evolution_engine_foundation_status": status,
        "regen_evolution_engine_foundation_blockers": blockers,

        "regen_evolution_engine_foundation": foundation,
        "regen_evolution_registry": foundation.get("evolution_registry") if foundation else None,
        "regen_generation_registry": foundation.get("generation_registry") if foundation else None,
        "regen_generation_history": foundation.get("generation_history") if foundation else None,
        "regen_evolution_report": _report(status, ready, foundation, blockers),

        "phase_13k_optimisation_selection_framework_allowed": ready,
        "regen_optimisation_selection_framework_allowed": ready,

        "regen_evolution_engine_execution_allowed": False,
        "regen_generation_advance_execution_allowed": False,
        "regen_candidate_improvement_validation_execution_allowed": False,
        "regen_multi_variable_mutation_execution_allowed": False,
        "regen_real_geometry_mutation_allowed": False,
        "regen_solver_execution_from_mutation_allowed": False,
        "regen_candidate_acceptance_from_mutation_allowed": False,
        "regen_live_geometry_commit_from_mutation_allowed": False,
        "regen_candidate_blueprint_mutation_execution_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }

def _build_foundation(population, improvement_records):
    improved = [r for r in improvement_records if r.get("improvement_validation", {}).get("improved_from_parent") is True]
    valid = [r for r in improvement_records if r.get("improvement_validation", {}).get("valid") is True]

    generation_zero = {
        "generation_id": "GENERATION_0000",
        "parent_generation_id": None,
        "generation_index": 0,
        "source_population_id": population.get("population_id"),
        "candidate_record_count": len(improvement_records),
        "valid_candidate_record_count": len(valid),
        "improved_candidate_record_count": len(improved),
        "generation_state": "BASELINE_GENERATION_EVALUATED_EXECUTION_LOCKED",
        "ready_for_selection": True,
        "solver_executed": False,
        "candidate_accepted": False,
        "live_geometry_committed": False,
    }

    next_generation_plan = {
        "planned_generation_id": "GENERATION_0001",
        "parent_generation_id": "GENERATION_0000",
        "planned_candidate_source": "IMPROVED_RECORDS_FROM_GENERATION_0000",
        "planned_seed_count": len(improved),
        "generation_advance_allowed": False,
        "reason": "Evolution foundation is created, but generation advance execution remains locked.",
    }

    evolution_registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "evolution_registry_id": f"EVOLUTION_REGISTRY_FOR_{population.get('population_id')}",
        "source_population_id": population.get("population_id"),
        "current_generation_id": "GENERATION_0000",
        "planned_next_generation_id": "GENERATION_0001",
        "registered_generation_states": [
            "BASELINE_GENERATION_EVALUATED_EXECUTION_LOCKED",
            "NEXT_GENERATION_PLANNED_EXECUTION_LOCKED",
            "GENERATION_ADVANCE_BLOCKED",
            "READY_FOR_SELECTION_FRAMEWORK",
        ],
        "permissions": {
            "optimisation_selection_framework_allowed": True,
            "evolution_engine_execution_allowed": False,
            "generation_advance_execution_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
    }

    generation_registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "generation_count": 1,
        "current_generation": generation_zero,
        "next_generation_plan": next_generation_plan,
    }

    generation_history = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "history_state": "EVOLUTION_HISTORY_CREATED_NO_GENERATION_ADVANCE",
        "generation_count": 1,
        "generation_advance_count": 0,
        "selection_count": 0,
        "solver_execution_count": 0,
        "candidate_acceptance_count": 0,
        "live_commit_count": 0,
        "entries": [
            {
                "entry_id": "EVOLUTION_HISTORY_ENTRY_0001",
                "event": "GENERATION_0000_REGISTERED",
                "candidate_record_count": len(improvement_records),
                "improved_candidate_record_count": len(improved),
                "execution_locked": True,
            }
        ],
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "evolution_state": "EVOLUTION_ENGINE_FOUNDATION_CREATED_EXECUTION_LOCKED",
        "evolution_registry": evolution_registry,
        "generation_registry": generation_registry,
        "generation_history": generation_history,
        "evolution_readiness": {
            "ready_for_optimisation_selection_framework": True,
            "ready_for_generation_advance_execution": False,
            "ready_for_solver_execution": False,
            "ready_for_candidate_acceptance": False,
            "ready_for_live_commit": False,
            "next_phase": "13K_OPTIMISATION_SELECTION_FRAMEWORK",
        },
    }

def _require_locked(results, blockers):
    required_false = {
        "regen_candidate_improvement_validation_execution_allowed": "Candidate improvement validation execution is not safely locked.",
        "regen_multi_variable_mutation_execution_allowed": "Multi-variable mutation execution is not safely locked.",
        "regen_real_geometry_mutation_allowed": "Real geometry mutation is not safely locked.",
        "regen_solver_execution_from_mutation_allowed": "Solver execution from mutation is not safely locked.",
        "regen_candidate_acceptance_from_mutation_allowed": "Candidate acceptance from mutation is not safely locked.",
        "regen_live_geometry_commit_from_mutation_allowed": "Live geometry commit from mutation is not safely locked.",
        "regen_candidate_blueprint_mutation_execution_allowed": "Candidate blueprint mutation execution is not safely locked.",
        "regen_optimisation_mutation_execution_allowed": "Optimisation mutation execution is not safely locked.",
        "regen_optimisation_live_geometry_commit_allowed": "Optimisation live geometry commit is not safely locked.",
    }
    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)

def _report(status, ready, foundation, blockers):
    if not ready:
        return "PHASE 13J BLOCKED\n" + "\n".join(f"- {b}" for b in blockers)
    registry = foundation["generation_registry"]
    current = registry["current_generation"]
    return (
        "PHASE 13J REGEN EVOLUTION ENGINE FOUNDATION\n"
        f"Status: {status}\n"
        f"Current Generation: {current.get('generation_id')}\n"
        f"Improved Candidates: {current.get('improved_candidate_record_count')}\n"
        "Generation advance execution remains locked.\n"
        "13K optimisation selection framework may begin."
    )
