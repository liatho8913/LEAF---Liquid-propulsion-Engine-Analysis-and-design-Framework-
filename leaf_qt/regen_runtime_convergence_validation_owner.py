OWNER_NAME = "REGEN_RUNTIME_CONVERGENCE_VALIDATION_OWNER"
PHASE = "14E"

PASS_STATUS = "PASS_REGEN_RUNTIME_CONVERGENCE_VALIDATION_OWNER_PHASE_14E"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CONVERGENCE_VALIDATION_OWNER_PHASE_14E"


def attach_regen_runtime_convergence_validation_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    required = {
        "regen_runtime_convergence_registry_ready": "Runtime convergence registry is not ready.",
        "regen_runtime_improvement_tracking_engine_ready": "Runtime improvement tracking engine is not ready.",
        "regen_runtime_stagnation_detection_engine_ready": "Runtime stagnation detection engine is not ready.",
        "regen_runtime_convergence_detection_engine_ready": "Runtime convergence detection engine is not ready.",
        "regen_runtime_stop_condition_engine_ready": "Runtime stop condition engine is not ready.",
    }

    for key, message in required.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("runtime_stop_condition_checked") is not True:
        blockers.append("Runtime stop condition was not checked.")

    if results.get("regen_runtime_optimisation_complete") is not False:
        blockers.append("Runtime optimisation was illegally marked complete in 14E.")

    if results.get("phase_14_runtime_optimisation_allowed") is not False:
        blockers.append("Full runtime optimisation is not locked after 14E.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_convergence_validation_owner_complete": True,
        "phase_14e_runtime_convergence_validation_owner_complete": True,
        "regen_runtime_convergence_validation_owner_ready": ready,
        "regen_runtime_convergence_validation_owner_status": status,
        "regen_runtime_convergence_validation_owner_blockers": blockers,
        "regen_runtime_convergence_validation": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "convergence_detected": results.get("runtime_convergence_detected"),
            "stop_recommended": results.get("runtime_stop_recommended"),
            "optimisation_completion_locked_until_14f": True,
        },

        "phase_14f_runtime_optimisation_audit_allowed": ready,
    })

    return results
