OWNER_NAME = "REGEN_RUNTIME_SELECTION_COMPLETION_AUDIT"
PHASE = "14C"

PASS_STATUS = "PASS_REGEN_RUNTIME_SELECTION_PHASE_14C"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_SELECTION_PHASE_14C"


def attach_regen_runtime_selection_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_runtime_selection_registry_ready": "Runtime selection registry is not ready.",
        "regen_runtime_selection_ranking_engine_ready": "Runtime selection ranking engine is not ready.",
        "regen_runtime_selection_parent_pool_builder_ready": "Runtime parent pool builder is not ready.",
        "regen_runtime_selection_validation_owner_ready": "Runtime selection validation owner is not ready.",
        "regen_runtime_selection_history_owner_ready": "Runtime selection history owner is not ready.",
        "regen_runtime_selection_report_owner_ready": "Runtime selection report owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("regen_runtime_parent_pool_size_actual", 0) <= 0:
        blockers.append("No runtime parent pool was created.")

    required_false = {
        "regen_runtime_selection_generation_advanced": "Generation advancement occurred in 14C.",
        "regen_runtime_selection_live_geometry_committed": "Live geometry commit occurred in 14C.",
        "regen_generation_advance_execution_allowed": "Global generation advance is not locked.",
        "regen_optimisation_live_geometry_commit_allowed": "Global live geometry commit is not locked.",
    }

    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_selection_completion_audit_complete": True,
        "phase_14c_runtime_selection_completion_audit_complete": True,
        "regen_runtime_selection_completion_audit_ready": ready,
        "regen_runtime_selection_completion_audit_status": status,
        "regen_runtime_selection_completion_audit_blockers": blockers,

        "phase_14c_complete": ready,
        "phase_14c_status": status,

        "phase_14d_runtime_evolution_allowed": ready,
        "phase_14e_runtime_convergence_allowed": False,
        "phase_14f_runtime_optimisation_audit_allowed": False,
        "phase_14_runtime_optimisation_allowed": False,
    })

    return results
