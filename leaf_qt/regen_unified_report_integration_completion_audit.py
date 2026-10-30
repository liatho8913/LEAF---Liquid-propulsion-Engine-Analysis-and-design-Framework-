OWNER_NAME = "REGEN_UNIFIED_REPORT_INTEGRATION_COMPLETION_AUDIT"
PHASE = "16C"

PASS_STATUS = "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_PHASE_16C"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_REPORT_INTEGRATION_PHASE_16C"


def attach_regen_unified_report_integration_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_unified_report_integration_registry_ready": "Report integration registry is not ready.",
        "regen_unified_report_routing_owner_ready": "Report routing owner is not ready.",
        "regen_unified_report_synchronisation_owner_ready": "Report synchronisation owner is not ready.",
        "regen_unified_report_session_owner_ready": "Report session owner is not ready.",
        "regen_unified_report_state_owner_ready": "Report state owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    forbidden = {
        "unified_regen_report_window_created": "Report window was illegally created in 16C.",
        "unified_regen_report_rendering_performed": "Report rendering was illegally performed in 16C.",
        "unified_regen_report_export_performed": "Report export was illegally performed in 16C.",
    }

    for key, message in forbidden.items():
        if results.get(key) is not False:
            blockers.append(message)

    if results.get("unified_regen_report_route_count", 0) <= 0:
        blockers.append("No unified report routes exist.")

    if results.get("unified_regen_report_sync_link_count", 0) <= 0:
        blockers.append("No unified report sync links exist.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_report_integration_completion_audit_complete": True,
        "phase_16c_unified_report_integration_completion_audit_complete": True,
        "regen_unified_report_integration_completion_audit_ready": ready,
        "regen_unified_report_integration_completion_audit_status": status,
        "regen_unified_report_integration_completion_audit_blockers": blockers,

        "phase_16c_complete": ready,
        "phase_16c_status": status,
        "phase_16d_validation_integration_allowed": ready,
    })

    return results
