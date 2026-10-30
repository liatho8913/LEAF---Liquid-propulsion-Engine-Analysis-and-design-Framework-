OWNER_NAME = "REGEN_UNIFIED_REPORT_INTEGRATION_REGISTRY"
PHASE = "16C"

PASS_STATUS = "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_REGISTRY_PHASE_16C"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_REPORT_INTEGRATION_REGISTRY_PHASE_16C"


def attach_regen_unified_report_integration_registry(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    allowed = results.get("phase_16c_report_integration_allowed") is True
    phase_16b_complete = (
        results.get("phase_16b_complete") is True
        or results.get("phase_16b_status") == "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_PHASE_16B"
    )

    if not allowed:
        blockers.append("Phase 16C has not been unlocked by Phase 16B.")

    if not phase_16b_complete:
        blockers.append("Phase 16B unified viewer integration is not complete.")

    reports = results.get("unified_regen_registered_reports", [])
    if not isinstance(reports, list) or not reports:
        blockers.append("Unified registered reports are missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_report_integration_registry_complete": True,
        "phase_16c_unified_report_integration_registry_complete": True,
        "regen_unified_report_integration_registry_ready": ready,
        "regen_unified_report_integration_registry_status": status,
        "regen_unified_report_integration_registry_blockers": blockers,
        "regen_unified_report_integration_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "report_routing_allowed": ready,
            "report_synchronisation_allowed": ready,
            "report_session_allowed": ready,
            "report_state_allowed": ready,
            "report_rendering_allowed": False,
            "report_export_allowed": False,
            "phase_16d_validation_integration_allowed_next": ready,
        } if ready else None,
    })

    return results
