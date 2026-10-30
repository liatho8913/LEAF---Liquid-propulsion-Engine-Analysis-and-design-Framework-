OWNER_NAME = "REGEN_UNIFIED_VALIDATION_INTEGRATION_COMPLETION_AUDIT"
PHASE = "16D"

PASS_STATUS = "PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_PHASE_16D"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VALIDATION_INTEGRATION_PHASE_16D"


def attach_regen_unified_validation_integration_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_unified_validation_integration_registry_ready": "Validation integration registry is not ready.",
        "regen_unified_validation_routing_owner_ready": "Validation routing owner is not ready.",
        "regen_unified_validation_synchronisation_owner_ready": "Validation synchronisation owner is not ready.",
        "regen_unified_validation_session_owner_ready": "Validation session owner is not ready.",
        "regen_unified_validation_state_owner_ready": "Validation state owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    forbidden = {
        "unified_regen_validation_view_created": "Validation view was illegally created in 16D.",
        "unified_regen_validation_rendering_performed": "Validation rendering was illegally performed in 16D.",
        "unified_regen_validation_export_performed": "Validation export was illegally performed in 16D.",
    }

    for key, message in forbidden.items():
        if results.get(key) is not False:
            blockers.append(message)

    if results.get("unified_regen_validation_route_count", 0) <= 0:
        blockers.append("No unified validation routes exist.")

    if results.get("unified_regen_validation_sync_link_count", 0) <= 0:
        blockers.append("No unified validation sync links exist.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_validation_integration_completion_audit_complete": True,
        "phase_16d_unified_validation_integration_completion_audit_complete": True,
        "regen_unified_validation_integration_completion_audit_ready": ready,
        "regen_unified_validation_integration_completion_audit_status": status,
        "regen_unified_validation_integration_completion_audit_blockers": blockers,

        "phase_16d_complete": ready,
        "phase_16d_status": status,
        "phase_16e_regen_signoff_allowed": ready,
    })

    return results
