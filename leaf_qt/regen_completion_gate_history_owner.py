OWNER_NAME = "REGEN_COMPLETION_GATE_HISTORY_OWNER"
PHASE = "16F"

PASS_STATUS = "PASS_REGEN_COMPLETION_GATE_HISTORY_OWNER_PHASE_16F"
FAIL_STATUS = "FAIL_REGEN_COMPLETION_GATE_HISTORY_OWNER_PHASE_16F"


def attach_regen_completion_gate_history_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_completion_gate_report_owner_ready") is not True:
        blockers.append("Regen completion gate report owner is not ready.")

    summary = results.get("regen_completion_gate_summary", {})
    if not isinstance(summary, dict) or not summary:
        blockers.append("Regen completion gate summary is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None
    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "REGEN_COMPLETION_GATE_READY",
            "entries": [
                {
                    "entry_id": "REGEN_COMPLETION_HISTORY_16F_FINAL_GATE_READY",
                    "event": "FINAL_REGEN_COMPLETION_GATE_READY",
                    "validation_check_count": summary.get("validation_check_count"),
                    "blocking_issue_count": summary.get("blocking_issue_count"),
                },
                {
                    "entry_id": "REGEN_COMPLETION_HISTORY_16F_SYSTEM_COMPLETE_PENDING",
                    "event": "PASS_REGEN_SYSTEM_COMPLETE_PENDING_MASTER_GATE",
                },
            ],
            "new_physics_added": False,
            "ui_created": False,
            "live_geometry_committed": False,
        }

    results.update({
        "regen_completion_gate_history_owner_complete": True,
        "phase_16f_regen_completion_gate_history_owner_complete": True,
        "regen_completion_gate_history_owner_ready": ready,
        "regen_completion_gate_history_owner_status": status,
        "regen_completion_gate_history_owner_blockers": blockers,

        "regen_completion_gate_history": history if ready else {},
    })

    return results
