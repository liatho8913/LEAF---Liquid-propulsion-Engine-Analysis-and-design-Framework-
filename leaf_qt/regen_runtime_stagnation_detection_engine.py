OWNER_NAME = "REGEN_RUNTIME_STAGNATION_DETECTION_ENGINE"
PHASE = "14E"

PASS_STATUS = "PASS_REGEN_RUNTIME_STAGNATION_DETECTION_ENGINE_PHASE_14E"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_STAGNATION_DETECTION_ENGINE_PHASE_14E"


def attach_regen_runtime_stagnation_detection_engine(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_runtime_improvement_tracking_engine_ready") is not True:
        blockers.append("Runtime improvement tracking engine is not ready.")

    improvement = results.get("runtime_generation_improvement")

    if not isinstance(improvement, (int, float)) or isinstance(improvement, bool):
        blockers.append("Runtime generation improvement is invalid.")

    tolerance = _tolerance(results)
    stagnation_limit = _stagnation_limit(results)
    previous_stagnation_count = _previous_stagnation_count(results)

    stagnated_this_generation = (
        isinstance(improvement, (int, float))
        and not isinstance(improvement, bool)
        and abs(float(improvement)) <= tolerance
    )

    stagnation_count = previous_stagnation_count + 1 if stagnated_this_generation else 0
    stagnation_limit_reached = stagnation_count >= stagnation_limit

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_stagnation_detection_engine_complete": True,
        "phase_14e_runtime_stagnation_detection_engine_complete": True,
        "regen_runtime_stagnation_detection_engine_ready": ready,
        "regen_runtime_stagnation_detection_engine_status": status,
        "regen_runtime_stagnation_detection_engine_blockers": blockers,

        "runtime_stagnated_this_generation": stagnated_this_generation if ready else False,
        "runtime_stagnation_count": stagnation_count if ready else 0,
        "runtime_stagnation_limit": stagnation_limit,
        "runtime_stagnation_limit_reached": stagnation_limit_reached if ready else False,

        "regen_runtime_stagnation_record": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "stagnated_this_generation": stagnated_this_generation,
            "stagnation_count": stagnation_count,
            "stagnation_limit": stagnation_limit,
            "stagnation_limit_reached": stagnation_limit_reached,
        } if ready else None,
    })

    return results


def _tolerance(results):
    value = results.get("runtime_convergence_improvement_tolerance", 1.0e-6)
    try:
        return max(0.0, float(value))
    except Exception:
        return 1.0e-6


def _stagnation_limit(results):
    value = results.get("runtime_stagnation_limit", 3)
    try:
        return max(1, int(value))
    except Exception:
        return 3


def _previous_stagnation_count(results):
    value = results.get("runtime_previous_stagnation_count", 0)
    try:
        return max(0, int(value))
    except Exception:
        return 0
