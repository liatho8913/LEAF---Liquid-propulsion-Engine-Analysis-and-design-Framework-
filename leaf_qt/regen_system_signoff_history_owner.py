OWNER_NAME = "REGEN_SYSTEM_SIGNOFF_HISTORY_OWNER"
PHASE = "16E"

PASS_STATUS = "PASS_REGEN_SYSTEM_SIGNOFF_HISTORY_OWNER_PHASE_16E"
FAIL_STATUS = "FAIL_REGEN_SYSTEM_SIGNOFF_HISTORY_OWNER_PHASE_16E"


def attach_regen_system_signoff_history_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_system_signoff_report_owner_ready") is not True:
        blockers.append("Regen system signoff report owner is not ready.")

    summary = results.get("regen_system_signoff_summary", {})
    if not isinstance(summary, dict) or not summary:
        blockers.append("Regen system signoff summary is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None
    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "REGEN_SYSTEM_SIGNOFF_AUDITED",
            "entries": [
                {
                    "entry_id": "REGEN_SYSTEM_SIGNOFF_HISTORY_16E_AUDIT",
                    "event": "REGEN_SYSTEM_SIGNOFF_AUDIT_COMPLETED",
                    "validation_check_count": summary.get("validation_check_count"),
                    "blocking_issue_count": summary.get("blocking_issue_count"),
                },
                {
                    "entry_id": "REGEN_SYSTEM_SIGNOFF_HISTORY_16E_NEXT_GATE",
                    "event": "REGEN_COMPLETION_GATE_UNLOCKED",
                    "phase_16f_regen_completion_gate_allowed": True,
                },
            ],
            "new_physics_added": False,
            "ui_created": False,
            "live_geometry_committed": False,
        }

    results.update({
        "regen_system_signoff_history_owner_complete": True,
        "phase_16e_regen_system_signoff_history_owner_complete": True,
        "regen_system_signoff_history_owner_ready": ready,
        "regen_system_signoff_history_owner_status": status,
        "regen_system_signoff_history_owner_blockers": blockers,

        "regen_system_signoff_history": history if ready else {},
    })

    return results
