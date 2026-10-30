OWNER_NAME = "REGEN_UNIFIED_VIEWER_SESSION_OWNER"
PHASE = "16B"

PASS_STATUS = "PASS_REGEN_UNIFIED_VIEWER_SESSION_OWNER_PHASE_16B"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VIEWER_SESSION_OWNER_PHASE_16B"


def attach_regen_unified_viewer_session_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_viewer_synchronisation_owner_ready") is not True:
        blockers.append("Unified viewer synchronisation owner is not ready.")

    routes = results.get("unified_regen_viewer_routes", [])
    sync_links = results.get("unified_regen_viewer_sync_links", [])

    if not isinstance(routes, list) or not routes:
        blockers.append("Unified viewer routes are missing.")

    if not isinstance(sync_links, list) or not sync_links:
        blockers.append("Unified viewer sync links are missing.")

    session = None

    if not blockers:
        session = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": PASS_STATUS,
            "session_id": "UNIFIED_REGEN_VIEWER_SESSION_16B",
            "viewer_route_count": len(routes),
            "viewer_sync_link_count": len(sync_links),
            "active_viewer_id": routes[0].get("viewer_id") if routes else None,
            "session_state": "BACKEND_SESSION_READY_NO_UI",
            "qt_window_created": False,
            "rendering_performed": False,
        }

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    if session:
        session["status"] = status

    results.update({
        "regen_unified_viewer_session_owner_complete": True,
        "phase_16b_unified_viewer_session_owner_complete": True,
        "regen_unified_viewer_session_owner_ready": ready,
        "regen_unified_viewer_session_owner_status": status,
        "regen_unified_viewer_session_owner_blockers": blockers,

        "unified_regen_viewer_session": session if ready else {},
        "unified_regen_viewer_session_active": ready,
    })

    return results
