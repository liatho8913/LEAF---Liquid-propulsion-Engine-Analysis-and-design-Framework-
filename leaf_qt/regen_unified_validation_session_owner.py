OWNER_NAME = "REGEN_UNIFIED_VALIDATION_SESSION_OWNER"
PHASE = "16D"

PASS_STATUS = "PASS_REGEN_UNIFIED_VALIDATION_SESSION_OWNER_PHASE_16D"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VALIDATION_SESSION_OWNER_PHASE_16D"


def attach_regen_unified_validation_session_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_validation_synchronisation_owner_ready") is not True:
        blockers.append("Unified validation synchronisation owner is not ready.")

    routes = results.get("unified_regen_validation_routes", [])
    sync_links = results.get("unified_regen_validation_sync_links", [])

    if not isinstance(routes, list) or not routes:
        blockers.append("Unified validation routes are missing.")

    if not isinstance(sync_links, list) or not sync_links:
        blockers.append("Unified validation sync links are missing.")

    session = None

    if not blockers:
        session = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": PASS_STATUS,
            "session_id": "UNIFIED_REGEN_VALIDATION_SESSION_16D",
            "validation_route_count": len(routes),
            "validation_sync_link_count": len(sync_links),
            "active_validation_id": routes[0].get("validation_id") if routes else None,
            "session_state": "BACKEND_VALIDATION_SESSION_READY_NO_UI",
            "validation_view_created": False,
            "validation_rendering_performed": False,
            "validation_export_performed": False,
        }

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    if session:
        session["status"] = status

    results.update({
        "regen_unified_validation_session_owner_complete": True,
        "phase_16d_unified_validation_session_owner_complete": True,
        "regen_unified_validation_session_owner_ready": ready,
        "regen_unified_validation_session_owner_status": status,
        "regen_unified_validation_session_owner_blockers": blockers,

        "unified_regen_validation_session": session if ready else {},
        "unified_regen_validation_session_active": ready,
    })

    return results
