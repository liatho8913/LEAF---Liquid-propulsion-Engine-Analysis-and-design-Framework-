OWNER_NAME = "REGEN_RUNTIME_EVOLUTION_COMPLETION_AUDIT"
PHASE = "14D"

PASS_STATUS = "PASS_REGEN_RUNTIME_EVOLUTION_PHASE_14D"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_EVOLUTION_PHASE_14D"


def attach_regen_runtime_evolution_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_runtime_evolution_registry_ready": "Runtime evolution registry is not ready.",
        "regen_runtime_generation_advance_engine_ready": "Runtime generation advance engine is not ready.",
        "regen_runtime_generation_creation_engine_ready": "Runtime generation creation engine is not ready.",
        "regen_runtime_population_carryover_engine_ready": "Runtime population carryover engine is not ready.",
        "regen_runtime_evolution_validation_owner_ready": "Runtime evolution validation owner is not ready.",
        "regen_runtime_evolution_history_owner_ready": "Runtime evolution history owner is not ready.",
        "regen_runtime_evolution_report_owner_ready": "Runtime evolution report owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("runtime_generation_advanced") is not True:
        blockers.append("Runtime generation was not advanced.")

    if results.get("regen_runtime_generation_population_count", 0) <= 0:
        blockers.append("Runtime generation population was not created.")

    if results.get("regen_runtime_parent_lineage_count", 0) <= 0:
        blockers.append("Runtime parent lineage was not created.")

    required_false = {
        "regen_runtime_evolution_convergence_checked": "Convergence was checked in 14D.",
        "regen_runtime_evolution_termination_checked": "Termination was checked in 14D.",
        "regen_runtime_evolution_live_geometry_committed": "Live geometry was committed in 14D.",
    }

    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_evolution_completion_audit_complete": True,
        "phase_14d_runtime_evolution_completion_audit_complete": True,
        "regen_runtime_evolution_completion_audit_ready": ready,
        "regen_runtime_evolution_completion_audit_status": status,
        "regen_runtime_evolution_completion_audit_blockers": blockers,

        "phase_14d_complete": ready,
        "phase_14d_status": status,

        "phase_14e_runtime_convergence_allowed": ready,
        "phase_14f_runtime_optimisation_audit_allowed": False,
        "phase_14_runtime_optimisation_allowed": False,
    })

    return results
