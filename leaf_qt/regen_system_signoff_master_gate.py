OWNER_NAME = "REGEN_SYSTEM_SIGNOFF_MASTER_GATE"
PHASE = "16E"

PASS_STATUS = "PASS_REGEN_SYSTEM_SIGNOFF_MASTER_GATE_PHASE_16E"
FAIL_STATUS = "FAIL_REGEN_SYSTEM_SIGNOFF_MASTER_GATE_PHASE_16E"


def attach_regen_system_signoff_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_system_signoff_completion_audit_ready") is not True:
        blockers.append("16E regen system signoff completion audit is not ready.")

    if results.get("regen_system_signoff_completion_audit_status") != "PASS_REGEN_SYSTEM_SIGNOFF_AUDIT_PHASE_16E":
        blockers.append("16E regen system signoff completion audit has not passed.")

    if results.get("phase_16f_regen_completion_gate_allowed") is not True:
        blockers.append("Phase 16F regen completion gate was not unlocked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_system_signoff_master_gate_complete": True,
        "phase_16e_regen_system_signoff_master_gate_complete": True,
        "regen_system_signoff_master_gate_passed": ready,
        "regen_system_signoff_master_gate_status": status,
        "regen_system_signoff_master_gate_blockers": blockers,

        "phase_16e_complete": ready,
        "phase_16e_status": (
            "PASS_REGEN_SYSTEM_SIGNOFF_AUDIT_PHASE_16E"
            if ready else
            "FAIL_REGEN_SYSTEM_SIGNOFF_AUDIT_PHASE_16E"
        ),

        "phase_16f_regen_completion_gate_allowed": ready,
    })

    return results
