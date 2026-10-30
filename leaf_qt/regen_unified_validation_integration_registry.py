OWNER_NAME = "REGEN_UNIFIED_VALIDATION_INTEGRATION_REGISTRY"
PHASE = "16D"

PASS_STATUS = "PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_REGISTRY_PHASE_16D"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VALIDATION_INTEGRATION_REGISTRY_PHASE_16D"


def attach_regen_unified_validation_integration_registry(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    allowed = results.get("phase_16d_validation_integration_allowed") is True
    phase_16c_complete = (
        results.get("phase_16c_complete") is True
        or results.get("phase_16c_status") == "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_PHASE_16C"
    )

    if not allowed:
        blockers.append("Phase 16D has not been unlocked by Phase 16C.")

    if not phase_16c_complete:
        blockers.append("Phase 16C unified report integration is not complete.")

    validations = results.get("unified_regen_registered_validations", [])
    if not isinstance(validations, list) or not validations:
        blockers.append("Unified registered validations are missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_validation_integration_registry_complete": True,
        "phase_16d_unified_validation_integration_registry_complete": True,
        "regen_unified_validation_integration_registry_ready": ready,
        "regen_unified_validation_integration_registry_status": status,
        "regen_unified_validation_integration_registry_blockers": blockers,
        "regen_unified_validation_integration_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "validation_routing_allowed": ready,
            "validation_synchronisation_allowed": ready,
            "validation_session_allowed": ready,
            "validation_state_allowed": ready,
            "validation_ui_allowed": False,
            "validation_rendering_allowed": False,
            "phase_16e_regen_signoff_allowed_next": ready,
        } if ready else None,
    })

    return results
