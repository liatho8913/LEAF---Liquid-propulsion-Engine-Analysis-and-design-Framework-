OWNER_NAME = "REGEN_RUNTIME_IMPROVEMENT_TRACKING_ENGINE"
PHASE = "14E"

PASS_STATUS = "PASS_REGEN_RUNTIME_IMPROVEMENT_TRACKING_ENGINE_PHASE_14E"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_IMPROVEMENT_TRACKING_ENGINE_PHASE_14E"


def attach_regen_runtime_improvement_tracking_engine(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_runtime_convergence_registry_ready") is not True:
        blockers.append("Runtime convergence registry is not ready.")

    parent_pool = results.get("regen_runtime_parent_pool", [])
    previous_best = _previous_best_score(results)

    scores = []

    if isinstance(parent_pool, list):
        for item in parent_pool:
            if isinstance(item, dict):
                score = item.get("runtime_selection_score")
                if isinstance(score, (int, float)) and not isinstance(score, bool):
                    scores.append(float(score))

    if not scores:
        blockers.append("No runtime selection scores are available for improvement tracking.")

    current_best = max(scores) if scores else None
    improvement = None

    if current_best is not None:
        improvement = current_best - previous_best

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_improvement_tracking_engine_complete": True,
        "phase_14e_runtime_improvement_tracking_engine_complete": True,
        "regen_runtime_improvement_tracking_engine_ready": ready,
        "regen_runtime_improvement_tracking_engine_status": status,
        "regen_runtime_improvement_tracking_engine_blockers": blockers,

        "runtime_current_best_score": current_best,
        "runtime_previous_best_score": previous_best,
        "runtime_generation_improvement": improvement,
        "runtime_improvement_detected": bool(improvement is not None and improvement > 0.0),
        "runtime_improvement_within_tolerance": bool(improvement is not None and abs(improvement) <= _tolerance(results)),

        "regen_runtime_improvement_record": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "previous_best_score": previous_best,
            "current_best_score": current_best,
            "generation_improvement": improvement,
            "improvement_tolerance": _tolerance(results),
        } if ready else None,
    })

    return results


def _previous_best_score(results):
    value = results.get("runtime_previous_best_score")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)

    value = results.get("runtime_baseline_best_score")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)

    return 0.0


def _tolerance(results):
    value = results.get("runtime_convergence_improvement_tolerance", 1.0e-6)
    try:
        return max(0.0, float(value))
    except Exception:
        return 1.0e-6
