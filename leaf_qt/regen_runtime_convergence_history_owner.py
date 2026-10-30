OWNER_NAME = "REGEN_RUNTIME_CONVERGENCE_HISTORY_OWNER"
PHASE = "14E"

PASS_STATUS = "PASS_REGEN_RUNTIME_CONVERGENCE_HISTORY_OWNER_PHASE_14E"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CONVERGENCE_HISTORY_OWNER_PHASE_14E"


def attach_regen_runtime_convergence_history_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_runtime_convergence_validation_owner_ready") is not True:
        blockers.append("Runtime convergence validation owner is not ready.")

    required_records = {
        "regen_runtime_improvement_record": "Improvement record is missing.",
        "regen_runtime_stagnation_record": "Stagnation record is missing.",
        "regen_runtime_convergence_record": "Convergence record is missing.",
        "regen_runtime_stop_condition_record": "Stop condition record is missing.",
    }

    for key, message in required_records.items():
        if not isinstance(results.get(key), dict):
            blockers.append(message)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None

    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "RUNTIME_CONVERGENCE_CHECKED_NO_COMPLETION",
            "entries": [
                {
                    "entry_id": "RUNTIME_CONVERGENCE_HISTORY_14E_IMPROVEMENT",
                    "event": "IMPROVEMENT_TRACKED",
                    "previous_best_score": results.get("runtime_previous_best_score"),
                    "current_best_score": results.get("runtime_current_best_score"),
                    "improvement": results.get("runtime_generation_improvement"),
                },
                {
                    "entry_id": "RUNTIME_CONVERGENCE_HISTORY_14E_STAGNATION",
                    "event": "STAGNATION_CHECKED",
                    "stagnation_count": results.get("runtime_stagnation_count"),
                    "stagnation_limit_reached": results.get("runtime_stagnation_limit_reached"),
                },
                {
                    "entry_id": "RUNTIME_CONVERGENCE_HISTORY_14E_CONVERGENCE",
                    "event": "CONVERGENCE_CHECKED",
                    "convergence_detected": results.get("runtime_convergence_detected"),
                    "reason": results.get("runtime_convergence_reason"),
                },
                {
                    "entry_id": "RUNTIME_CONVERGENCE_HISTORY_14E_STOP_CONDITION",
                    "event": "STOP_CONDITION_CHECKED",
                    "stop_recommended": results.get("runtime_stop_recommended"),
                    "stop_reason": results.get("runtime_stop_reason"),
                },
            ],
            "optimisation_completion_count": 0,
            "live_geometry_commit_count": 0,
        }

    results.update({
        "regen_runtime_convergence_history_owner_complete": True,
        "phase_14e_runtime_convergence_history_owner_complete": True,
        "regen_runtime_convergence_history_owner_ready": ready,
        "regen_runtime_convergence_history_owner_status": status,
        "regen_runtime_convergence_history_owner_blockers": blockers,
        "regen_runtime_convergence_history": history,
        "runtime_convergence_history": history.get("entries") if isinstance(history, dict) else [],
    })

    return results
