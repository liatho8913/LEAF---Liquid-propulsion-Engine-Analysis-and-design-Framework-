OWNER_NAME = "REGEN_RUNTIME_CONVERGENCE_DETECTION_ENGINE"
PHASE = "14E"

PASS_STATUS = "PASS_REGEN_RUNTIME_CONVERGENCE_DETECTION_ENGINE_PHASE_14E"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CONVERGENCE_DETECTION_ENGINE_PHASE_14E"


def attach_regen_runtime_convergence_detection_engine(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_runtime_stagnation_detection_engine_ready") is not True:
        blockers.append("Runtime stagnation detection engine is not ready.")

    improvement_within_tolerance = results.get("runtime_improvement_within_tolerance") is True
    stagnation_limit_reached = results.get("runtime_stagnation_limit_reached") is True
    max_generation_reached = _max_generation_reached(results)

    converged = bool(improvement_within_tolerance and stagnation_limit_reached)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_convergence_detection_engine_complete": True,
        "phase_14e_runtime_convergence_detection_engine_complete": True,
        "regen_runtime_convergence_detection_engine_ready": ready,
        "regen_runtime_convergence_detection_engine_status": status,
        "regen_runtime_convergence_detection_engine_blockers": blockers,

        "runtime_convergence_detected": converged if ready else False,
        "runtime_max_generation_reached": max_generation_reached if ready else False,
        "runtime_convergence_reason": _reason(converged, max_generation_reached, results) if ready else "BLOCKED",

        "regen_runtime_convergence_record": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "convergence_detected": converged,
            "max_generation_reached": max_generation_reached,
            "reason": _reason(converged, max_generation_reached, results),
        } if ready else None,
    })

    return results


def _max_generation_reached(results):
    current = results.get("runtime_generation_advance_to", results.get("runtime_generation_number", 0))
    maximum = results.get("runtime_max_generations", 50)

    try:
        return int(current) >= int(maximum)
    except Exception:
        return False


def _reason(converged, max_generation_reached, results):
    if converged:
        return "CONVERGED_BY_STAGNATION_AND_IMPROVEMENT_TOLERANCE"
    if max_generation_reached:
        return "STOP_RECOMMENDED_BY_MAX_GENERATION_LIMIT"
    return "NOT_CONVERGED_CONTINUE_RUNTIME_OPTIMISATION"
