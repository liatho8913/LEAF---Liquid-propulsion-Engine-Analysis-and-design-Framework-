OWNER_NAME = "REGEN_RUNTIME_CONVERGENCE_COMPLETION_AUDIT"
PHASE = "14E"

PASS_STATUS = "PASS_REGEN_RUNTIME_CONVERGENCE_PHASE_14E"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CONVERGENCE_PHASE_14E"


def attach_regen_runtime_convergence_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_runtime_convergence_registry_ready": "Runtime convergence registry is not ready.",
        "regen_runtime_improvement_tracking_engine_ready": "Runtime improvement tracking engine is not ready.",
        "regen_runtime_stagnation_detection_engine_ready": "Runtime stagnation detection engine is not ready.",
        "regen_runtime_convergence_detection_engine_ready": "Runtime convergence detection engine is not ready.",
        "regen_runtime_stop_condition_engine_ready": "Runtime stop condition engine is not ready.",
        "regen_runtime_convergence_validation_owner_ready": "Runtime convergence validation owner is not ready.",
        "regen_runtime_convergence_history_owner_ready": "Runtime convergence history owner is not ready.",
        "regen_runtime_convergence_report_owner_ready": "Runtime convergence report owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("runtime_stop_condition_checked") is not True:
        blockers.append("Runtime stop condition was not checked.")

    if results.get("regen_runtime_optimisation_complete") is not False:
        blockers.append("Runtime optimisation was illegally completed in 14E.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_convergence_completion_audit_complete": True,
        "phase_14e_runtime_convergence_completion_audit_complete": True,
        "regen_runtime_convergence_completion_audit_ready": ready,
        "regen_runtime_convergence_completion_audit_status": status,
        "regen_runtime_convergence_completion_audit_blockers": blockers,

        "phase_14e_complete": ready,
        "phase_14e_status": status,

        "phase_14f_runtime_optimisation_audit_allowed": ready,
        "phase_14_runtime_optimisation_allowed": False,
        "regen_runtime_optimisation_complete": False,
    })

    return results
