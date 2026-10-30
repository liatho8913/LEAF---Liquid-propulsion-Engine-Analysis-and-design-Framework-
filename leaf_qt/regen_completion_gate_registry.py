OWNER_NAME = "REGEN_COMPLETION_GATE_REGISTRY"
PHASE = "16F"

PASS_STATUS = "PASS_REGEN_COMPLETION_GATE_REGISTRY_PHASE_16F"
FAIL_STATUS = "FAIL_REGEN_COMPLETION_GATE_REGISTRY_PHASE_16F"


def attach_regen_completion_gate_registry(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    allowed = results.get("phase_16f_regen_completion_gate_allowed") is True
    phase_16e_complete = (
        results.get("phase_16e_complete") is True
        or results.get("phase_16e_status") == "PASS_REGEN_SYSTEM_SIGNOFF_AUDIT_PHASE_16E"
    )

    if not allowed:
        blockers.append("Phase 16F has not been unlocked by Phase 16E.")

    if not phase_16e_complete:
        blockers.append("Phase 16E regen signoff audit is not complete.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_completion_gate_registry_complete": True,
        "phase_16f_regen_completion_gate_registry_complete": True,
        "regen_completion_gate_registry_ready": ready,
        "regen_completion_gate_registry_status": status,
        "regen_completion_gate_registry_blockers": blockers,
        "regen_completion_gate_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "completion_validation_allowed": ready,
            "completion_report_allowed": ready,
            "completion_history_allowed": ready,
            "regen_system_complete_allowed": ready,
        } if ready else None,
    })

    return results
