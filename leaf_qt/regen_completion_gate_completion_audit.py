OWNER_NAME = "REGEN_COMPLETION_GATE_COMPLETION_AUDIT"
PHASE = "16F"

PASS_STATUS = "PASS_REGEN_COMPLETION_GATE_AUDIT_PHASE_16F"
FAIL_STATUS = "FAIL_REGEN_COMPLETION_GATE_AUDIT_PHASE_16F"


def attach_regen_completion_gate_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_completion_gate_registry_ready": "Completion gate registry is not ready.",
        "regen_completion_gate_validation_owner_ready": "Completion gate validation owner is not ready.",
        "regen_completion_gate_report_owner_ready": "Completion gate report owner is not ready.",
        "regen_completion_gate_history_owner_ready": "Completion gate history owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("regen_completion_gate_validation_passed") is not True:
        blockers.append("Completion gate validation did not pass.")

    if results.get("regen_completion_gate_summary", {}).get("blocking_issue_count") != 0:
        blockers.append("Completion gate summary contains blocking issues.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_completion_gate_completion_audit_complete": True,
        "phase_16f_regen_completion_gate_completion_audit_complete": True,
        "regen_completion_gate_completion_audit_ready": ready,
        "regen_completion_gate_completion_audit_status": status,
        "regen_completion_gate_completion_audit_blockers": blockers,

        "phase_16f_complete": ready,
        "phase_16f_status": status,
        "regen_system_completion_gate_ready": ready,
    })

    return results
