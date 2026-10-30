OWNER_NAME = "REGEN_RUNTIME_EVOLUTION_VALIDATION_OWNER"
PHASE = "14D"

PASS_STATUS = "PASS_REGEN_RUNTIME_EVOLUTION_VALIDATION_OWNER_PHASE_14D"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_EVOLUTION_VALIDATION_OWNER_PHASE_14D"


def attach_regen_runtime_evolution_validation_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    required = {
        "regen_runtime_evolution_registry_ready": "Runtime evolution registry is not ready.",
        "regen_runtime_generation_advance_engine_ready": "Runtime generation advance engine is not ready.",
        "regen_runtime_generation_creation_engine_ready": "Runtime generation creation engine is not ready.",
        "regen_runtime_population_carryover_engine_ready": "Runtime population carryover engine is not ready.",
    }

    for key, message in required.items():
        if results.get(key) is not True:
            blockers.append(message)

    population = results.get("regen_runtime_generation_population", [])
    lineage = results.get("regen_runtime_parent_lineage", [])

    if not isinstance(population, list) or not population:
        blockers.append("Runtime generation population is missing.")

    if not isinstance(lineage, list) or not lineage:
        blockers.append("Runtime parent lineage is missing.")

    if results.get("runtime_generation_advanced") is not True:
        blockers.append("Runtime generation was not advanced.")

    if results.get("regen_runtime_evolution_convergence_checked") is not False:
        blockers.append("Convergence was illegally checked in 14D.")

    if results.get("regen_runtime_evolution_termination_checked") is not False:
        blockers.append("Termination was illegally checked in 14D.")

    if results.get("regen_runtime_evolution_live_geometry_committed") is not False:
        blockers.append("Live geometry was illegally committed in 14D.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_evolution_validation_owner_complete": True,
        "phase_14d_runtime_evolution_validation_owner_complete": True,
        "regen_runtime_evolution_validation_owner_ready": ready,
        "regen_runtime_evolution_validation_owner_status": status,
        "regen_runtime_evolution_validation_owner_blockers": blockers,
        "regen_runtime_evolution_validation": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "generation_advanced": results.get("runtime_generation_advanced") is True,
            "population_count": len(population) if isinstance(population, list) else 0,
            "lineage_count": len(lineage) if isinstance(lineage, list) else 0,
            "convergence_locked": True,
            "termination_locked": True,
            "live_geometry_commit_locked": True,
        },

        "phase_14e_runtime_convergence_allowed": ready,
        "regen_runtime_evolution_convergence_allowed": False,
        "regen_runtime_evolution_termination_allowed": False,
        "regen_runtime_evolution_live_geometry_commit_allowed": False,
    })

    return results
