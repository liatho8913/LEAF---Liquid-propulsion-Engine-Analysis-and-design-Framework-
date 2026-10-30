OWNER_NAME = "REGEN_IMPROVEMENT_VIEWER_DATA_OWNER"
PHASE = "15A"

PASS_STATUS = "PASS_REGEN_IMPROVEMENT_VIEWER_DATA_OWNER_PHASE_15A"
FAIL_STATUS = "FAIL_REGEN_IMPROVEMENT_VIEWER_DATA_OWNER_PHASE_15A"


def attach_regen_improvement_viewer_data_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_candidate_viewer_data_owner_ready") is not True:
        blockers.append("Candidate viewer data owner is not ready.")

    improvements = [
        {
            "metric": "best_score",
            "previous": results.get("runtime_previous_best_score"),
            "current": results.get("runtime_current_best_score"),
            "delta": results.get("runtime_generation_improvement"),
            "improvement_detected": results.get("runtime_improvement_detected"),
        },
        {
            "metric": "stagnation",
            "previous": results.get("runtime_previous_stagnation_count"),
            "current": results.get("runtime_stagnation_count"),
            "limit": results.get("runtime_stagnation_limit"),
            "limit_reached": results.get("runtime_stagnation_limit_reached"),
        },
        {
            "metric": "completion",
            "complete": results.get("regen_runtime_optimisation_complete"),
            "continue_required": results.get("runtime_optimisation_continue_required"),
            "reason": results.get("runtime_optimisation_completion_reason"),
        },
    ]

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_improvement_viewer_data_owner_complete": True,
        "phase_15a_improvement_viewer_data_owner_complete": True,
        "regen_improvement_viewer_data_owner_ready": ready,
        "regen_improvement_viewer_data_owner_status": status,
        "regen_improvement_viewer_data_owner_blockers": blockers,

        "optimisation_viewer_improvements": improvements if ready else [],
        "optimisation_viewer_improvement_count": len(improvements) if ready else 0,
    })

    return results
