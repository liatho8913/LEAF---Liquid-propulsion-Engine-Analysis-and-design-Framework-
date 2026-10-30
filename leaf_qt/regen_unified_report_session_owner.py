OWNER_NAME = "REGEN_UNIFIED_REPORT_SESSION_OWNER"
PHASE = "16C"

PASS_STATUS = "PASS_REGEN_UNIFIED_REPORT_SESSION_OWNER_PHASE_16C"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_REPORT_SESSION_OWNER_PHASE_16C"


def attach_regen_unified_report_session_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_report_synchronisation_owner_ready") is not True:
        blockers.append("Unified report synchronisation owner is not ready.")

    routes = results.get("unified_regen_report_routes", [])
    sync_links = results.get("unified_regen_report_sync_links", [])

    if not isinstance(routes, list) or not routes:
        blockers.append("Unified report routes are missing.")

    if not isinstance(sync_links, list) or not sync_links:
        blockers.append("Unified report sync links are missing.")

    session = None

    if not blockers:
        session = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": PASS_STATUS,
            "session_id": "UNIFIED_REGEN_REPORT_SESSION_16C",
            "report_route_count": len(routes),
            "report_sync_link_count": len(sync_links),
            "active_report_id": routes[0].get("report_id") if routes else None,
            "session_state": "BACKEND_REPORT_SESSION_READY_NO_RENDERING",
            "report_window_created": False,
            "report_rendering_performed": False,
            "report_export_performed": False,
        }

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    if session:
        session["status"] = status

    results.update({
        "regen_unified_report_session_owner_complete": True,
        "phase_16c_unified_report_session_owner_complete": True,
        "regen_unified_report_session_owner_ready": ready,
        "regen_unified_report_session_owner_status": status,
        "regen_unified_report_session_owner_blockers": blockers,

        "unified_regen_report_session": session if ready else {},
        "unified_regen_report_session_active": ready,
    })

    return results
