OWNER_NAME = "REGEN_RUNTIME_OPTIMISATION_COMPLETION_HISTORY_OWNER"
PHASE = "14F"

PASS_STATUS = "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_HISTORY_OWNER_PHASE_14F"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_OPTIMISATION_COMPLETION_HISTORY_OWNER_PHASE_14F"


def attach_regen_runtime_optimisation_completion_history_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_runtime_optimisation_completion_validation_owner_ready") is not True:
        blockers.append("Runtime optimisation completion validation owner is not ready.")

    record = results.get("regen_runtime_optimisation_completion_record")
    if not isinstance(record, dict):
        blockers.append("Runtime optimisation completion record is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None
    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "RUNTIME_OPTIMISATION_COMPLETION_AUDITED",
            "entries": [
                {
                    "entry_id": "RUNTIME_OPTIMISATION_COMPLETION_HISTORY_14F_AUDIT",
                    "event": "RUNTIME_OPTIMISATION_COMPLETION_AUDITED",
                    "runtime_optimisation_complete": results.get("regen_runtime_optimisation_complete"),
                    "continue_required": results.get("runtime_optimisation_continue_required"),
                    "reason": results.get("runtime_optimisation_completion_reason"),
                    "final_best_score": results.get("runtime_optimisation_final_best_score"),
                    "final_generation": results.get("runtime_optimisation_final_generation"),
                }
            ],
            "live_geometry_commit_count": 0,
        }

    results.update({
        "regen_runtime_optimisation_completion_history_owner_complete": True,
        "phase_14f_runtime_optimisation_completion_history_owner_complete": True,
        "regen_runtime_optimisation_completion_history_owner_ready": ready,
        "regen_runtime_optimisation_completion_history_owner_status": status,
        "regen_runtime_optimisation_completion_history_owner_blockers": blockers,
        "regen_runtime_optimisation_completion_history": history,
        "runtime_optimisation_completion_history": history.get("entries") if isinstance(history, dict) else [],
    })

    return results
