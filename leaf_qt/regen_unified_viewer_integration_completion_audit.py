OWNER_NAME = "REGEN_UNIFIED_VIEWER_INTEGRATION_COMPLETION_AUDIT"
PHASE = "16B"

PASS_STATUS = "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_PHASE_16B"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VIEWER_INTEGRATION_PHASE_16B"


def attach_regen_unified_viewer_integration_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_unified_viewer_integration_registry_ready": "Viewer integration registry is not ready.",
        "regen_unified_viewer_routing_owner_ready": "Viewer routing owner is not ready.",
        "regen_unified_viewer_synchronisation_owner_ready": "Viewer synchronisation owner is not ready.",
        "regen_unified_viewer_session_owner_ready": "Viewer session owner is not ready.",
        "regen_unified_viewer_state_owner_ready": "Viewer state owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    forbidden = {
        "unified_regen_viewer_qt_window_created": "Qt viewer window was illegally created in 16B.",
        "unified_regen_viewer_rendering_performed": "Viewer rendering was illegally performed in 16B.",
        "unified_regen_viewer_ui_widget_created": "Viewer UI widget was illegally created in 16B.",
    }

    for key, message in forbidden.items():
        if results.get(key) is not False:
            blockers.append(message)

    if results.get("unified_regen_viewer_route_count", 0) <= 0:
        blockers.append("No unified viewer routes exist.")

    if results.get("unified_regen_viewer_sync_link_count", 0) <= 0:
        blockers.append("No unified viewer sync links exist.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_viewer_integration_completion_audit_complete": True,
        "phase_16b_unified_viewer_integration_completion_audit_complete": True,
        "regen_unified_viewer_integration_completion_audit_ready": ready,
        "regen_unified_viewer_integration_completion_audit_status": status,
        "regen_unified_viewer_integration_completion_audit_blockers": blockers,

        "phase_16b_complete": ready,
        "phase_16b_status": status,
        "phase_16c_report_integration_allowed": ready,
    })

    return results
