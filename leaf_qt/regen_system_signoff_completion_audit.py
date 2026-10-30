OWNER_NAME = "REGEN_SYSTEM_SIGNOFF_COMPLETION_AUDIT"
PHASE = "16E"

PASS_STATUS = "PASS_REGEN_SYSTEM_SIGNOFF_AUDIT_PHASE_16E"
FAIL_STATUS = "FAIL_REGEN_SYSTEM_SIGNOFF_AUDIT_PHASE_16E"


def attach_regen_system_signoff_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_system_signoff_registry_ready": "Regen system signoff registry is not ready.",
        "regen_system_signoff_validation_owner_ready": "Regen system signoff validation owner is not ready.",
        "regen_system_signoff_report_owner_ready": "Regen system signoff report owner is not ready.",
        "regen_system_signoff_history_owner_ready": "Regen system signoff history owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("regen_system_signoff_validation_passed") is not True:
        blockers.append("Regen system signoff validation did not pass.")

    if results.get("regen_system_signoff_summary", {}).get("blocking_issue_count") != 0:
        blockers.append("Regen system signoff summary contains blocking issues.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_system_signoff_completion_audit_complete": True,
        "phase_16e_regen_system_signoff_completion_audit_complete": True,
        "regen_system_signoff_completion_audit_ready": ready,
        "regen_system_signoff_completion_audit_status": status,
        "regen_system_signoff_completion_audit_blockers": blockers,

        "phase_16e_complete": ready,
        "phase_16e_status": status,
        "phase_16f_regen_completion_gate_allowed": ready,
    })

    return results
