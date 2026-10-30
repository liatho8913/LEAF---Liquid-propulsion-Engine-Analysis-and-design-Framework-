OWNER_NAME = "REGEN_COMPLETION_MASTER_GATE"
PHASE = "16F"

PASS_STATUS = "PASS_REGEN_SYSTEM_COMPLETE"
FAIL_STATUS = "FAIL_REGEN_SYSTEM_COMPLETE"


def attach_regen_completion_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_completion_gate_completion_audit_ready") is not True:
        blockers.append("16F regen completion gate audit is not ready.")

    if results.get("regen_completion_gate_completion_audit_status") != "PASS_REGEN_COMPLETION_GATE_AUDIT_PHASE_16F":
        blockers.append("16F regen completion gate audit has not passed.")

    if results.get("regen_system_completion_gate_ready") is not True:
        blockers.append("Regen system completion gate is not ready.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_completion_master_gate_complete": True,
        "phase_16f_regen_completion_master_gate_complete": True,
        "regen_completion_master_gate_passed": ready,
        "regen_completion_master_gate_status": status,
        "regen_completion_master_gate_blockers": blockers,

        "phase_16f_complete": ready,
        "phase_16f_status": (
            "PASS_REGEN_COMPLETION_GATE_AUDIT_PHASE_16F"
            if ready else
            "FAIL_REGEN_COMPLETION_GATE_AUDIT_PHASE_16F"
        ),

        "regen_system_complete": ready,
        "regen_system_status": status,
        "regen_system_completion_status": status,
        "leaf_regen_ecosystem_complete": ready,
    })

    return results
