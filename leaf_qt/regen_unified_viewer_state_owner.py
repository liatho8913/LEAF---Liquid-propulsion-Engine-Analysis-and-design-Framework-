OWNER_NAME = "REGEN_UNIFIED_VIEWER_STATE_OWNER"
PHASE = "16B"

PASS_STATUS = "PASS_REGEN_UNIFIED_VIEWER_STATE_OWNER_PHASE_16B"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VIEWER_STATE_OWNER_PHASE_16B"


def attach_regen_unified_viewer_state_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_viewer_session_owner_ready") is not True:
        blockers.append("Unified viewer session owner is not ready.")

    session = results.get("unified_regen_viewer_session", {})
    routes = results.get("unified_regen_viewer_routes", [])

    if not isinstance(session, dict) or not session:
        blockers.append("Unified viewer session is missing.")

    if not isinstance(routes, list) or not routes:
        blockers.append("Unified viewer routes are missing.")

    state = None

    if not blockers:
        state = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": PASS_STATUS,
            "viewer_integration_ready": True,
            "active_viewer_id": session.get("active_viewer_id"),
            "available_viewer_ids": [
                route.get("viewer_id")
                for route in routes
                if isinstance(route, dict)
            ],
            "route_count": len(routes),
            "sync_link_count": results.get("unified_regen_viewer_sync_link_count", 0),
            "qt_window_created": False,
            "rendering_performed": False,
            "ui_widget_created": False,
        }

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    if state:
        state["status"] = status

    results.update({
        "regen_unified_viewer_state_owner_complete": True,
        "phase_16b_unified_viewer_state_owner_complete": True,
        "regen_unified_viewer_state_owner_ready": ready,
        "regen_unified_viewer_state_owner_status": status,
        "regen_unified_viewer_state_owner_blockers": blockers,

        "unified_regen_viewer_state": state if ready else {},
        "unified_regen_viewer_integration_ready": ready,
        "unified_regen_viewer_qt_window_created": False,
        "unified_regen_viewer_rendering_performed": False,
        "unified_regen_viewer_ui_widget_created": False,
    })

    return results
