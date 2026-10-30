OWNER_NAME = "REGEN_SYSTEM_SIGNOFF_REGISTRY"
PHASE = "16E"

PASS_STATUS = "PASS_REGEN_SYSTEM_SIGNOFF_REGISTRY_PHASE_16E"
FAIL_STATUS = "FAIL_REGEN_SYSTEM_SIGNOFF_REGISTRY_PHASE_16E"


def attach_regen_system_signoff_registry(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    allowed = results.get("phase_16e_regen_signoff_allowed") is True
    phase_16d_complete = (
        results.get("phase_16d_complete") is True
        or results.get("phase_16d_status") == "PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_PHASE_16D"
    )

    if not allowed:
        blockers.append("Phase 16E has not been unlocked by Phase 16D.")

    if not phase_16d_complete:
        blockers.append("Phase 16D unified validation integration is not complete.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_system_signoff_registry_complete": True,
        "phase_16e_regen_system_signoff_registry_complete": True,
        "regen_system_signoff_registry_ready": ready,
        "regen_system_signoff_registry_status": status,
        "regen_system_signoff_registry_blockers": blockers,
        "regen_system_signoff_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "signoff_validation_allowed": ready,
            "signoff_report_allowed": ready,
            "signoff_history_allowed": ready,
            "completion_gate_allowed_next": ready,
            "new_physics_allowed": False,
            "ui_creation_allowed": False,
            "runtime_mutation_allowed": False,
            "live_geometry_commit_allowed": False,
        } if ready else None,
    })

    return results
