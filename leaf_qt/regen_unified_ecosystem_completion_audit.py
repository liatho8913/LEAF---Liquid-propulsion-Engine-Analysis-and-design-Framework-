OWNER_NAME = "REGEN_UNIFIED_ECOSYSTEM_COMPLETION_AUDIT"
PHASE = "16A"

PASS_STATUS = "PASS_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A"


def attach_regen_unified_ecosystem_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_unified_ecosystem_registry_ready": "Unified ecosystem registry is not ready.",
        "regen_unified_viewer_registration_owner_ready": "Viewer registration owner is not ready.",
        "regen_unified_report_registration_owner_ready": "Report registration owner is not ready.",
        "regen_unified_validation_registration_owner_ready": "Validation registration owner is not ready.",
        "regen_unified_ecosystem_state_owner_ready": "Ecosystem state owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    forbidden = {
        "unified_regen_qt_windows_created": "Qt windows were illegally created in 16A.",
        "unified_regen_rendering_performed": "Rendering was illegally performed in 16A.",
        "unified_regen_report_rendering_performed": "Report rendering was illegally performed in 16A.",
        "unified_regen_report_export_performed": "Report export was illegally performed in 16A.",
        "unified_regen_validation_view_created": "Validation view was illegally created in 16A.",
    }

    for key, message in forbidden.items():
        if results.get(key) is not False:
            blockers.append(message)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_ecosystem_completion_audit_complete": True,
        "phase_16a_unified_ecosystem_completion_audit_complete": True,
        "regen_unified_ecosystem_completion_audit_ready": ready,
        "regen_unified_ecosystem_completion_audit_status": status,
        "regen_unified_ecosystem_completion_audit_blockers": blockers,

        "phase_16a_complete": ready,
        "phase_16a_status": status,
        "phase_16b_viewer_integration_allowed": ready,
    })

    return results
