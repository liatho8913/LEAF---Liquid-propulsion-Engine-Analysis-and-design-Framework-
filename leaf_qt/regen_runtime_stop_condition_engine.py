OWNER_NAME = "REGEN_RUNTIME_STOP_CONDITION_ENGINE"
PHASE = "14E"

PASS_STATUS = "PASS_REGEN_RUNTIME_STOP_CONDITION_ENGINE_PHASE_14E"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_STOP_CONDITION_ENGINE_PHASE_14E"


def attach_regen_runtime_stop_condition_engine(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_runtime_convergence_detection_engine_ready") is not True:
        blockers.append("Runtime convergence detection engine is not ready.")

    convergence_detected = results.get("runtime_convergence_detected") is True
    max_generation_reached = results.get("runtime_max_generation_reached") is True

    stop_recommended = bool(convergence_detected or max_generation_reached)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_stop_condition_engine_complete": True,
        "phase_14e_runtime_stop_condition_engine_complete": True,
        "regen_runtime_stop_condition_engine_ready": ready,
        "regen_runtime_stop_condition_engine_status": status,
        "regen_runtime_stop_condition_engine_blockers": blockers,

        "runtime_stop_condition_checked": ready,
        "runtime_stop_recommended": stop_recommended if ready else False,
        "runtime_stop_reason": _stop_reason(convergence_detected, max_generation_reached) if ready else "BLOCKED",

        "regen_runtime_stop_condition_record": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "stop_condition_checked": ready,
            "stop_recommended": stop_recommended,
            "stop_reason": _stop_reason(convergence_detected, max_generation_reached),
        } if ready else None,

        "phase_14f_runtime_optimisation_audit_allowed": ready,
        "phase_14_runtime_optimisation_allowed": False,
        "regen_runtime_optimisation_complete": False,
    })

    return results


def _stop_reason(convergence_detected, max_generation_reached):
    if convergence_detected:
        return "STOP_RECOMMENDED_CONVERGENCE_DETECTED"
    if max_generation_reached:
        return "STOP_RECOMMENDED_MAX_GENERATION_REACHED"
    return "CONTINUE_RUNTIME_OPTIMISATION"
