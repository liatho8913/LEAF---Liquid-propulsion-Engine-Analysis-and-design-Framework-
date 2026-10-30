OWNER_NAME = "REGEN_UNIFIED_VIEWER_INTEGRATION_REGISTRY"
PHASE = "16B"

PASS_STATUS = "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_REGISTRY_PHASE_16B"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VIEWER_INTEGRATION_REGISTRY_PHASE_16B"


def attach_regen_unified_viewer_integration_registry(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    allowed = results.get("phase_16b_viewer_integration_allowed") is True
    phase_16a_complete = (
        results.get("phase_16a_complete") is True
        or results.get("phase_16a_status") == "PASS_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A"
    )

    if not allowed:
        blockers.append("Phase 16B has not been unlocked by Phase 16A.")

    if not phase_16a_complete:
        blockers.append("Phase 16A unified ecosystem registry is not complete.")

    viewers = results.get("unified_regen_registered_viewers", [])
    if not isinstance(viewers, list) or not viewers:
        blockers.append("Unified registered viewers are missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_viewer_integration_registry_complete": True,
        "phase_16b_unified_viewer_integration_registry_complete": True,
        "regen_unified_viewer_integration_registry_ready": ready,
        "regen_unified_viewer_integration_registry_status": status,
        "regen_unified_viewer_integration_registry_blockers": blockers,
        "regen_unified_viewer_integration_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "routing_allowed": ready,
            "synchronisation_allowed": ready,
            "session_allowed": ready,
            "viewer_state_allowed": ready,
            "qt_window_allowed": False,
            "rendering_allowed": False,
            "phase_16c_report_integration_allowed_next": ready,
        } if ready else None,
    })

    return results
