OWNER_NAME = "REGEN_UNIFIED_REPORT_STATE_OWNER"
PHASE = "16C"

PASS_STATUS = "PASS_REGEN_UNIFIED_REPORT_STATE_OWNER_PHASE_16C"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_REPORT_STATE_OWNER_PHASE_16C"


def attach_regen_unified_report_state_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_report_session_owner_ready") is not True:
        blockers.append("Unified report session owner is not ready.")

    session = results.get("unified_regen_report_session", {})
    routes = results.get("unified_regen_report_routes", [])

    if not isinstance(session, dict) or not session:
        blockers.append("Unified report session is missing.")

    if not isinstance(routes, list) or not routes:
        blockers.append("Unified report routes are missing.")

    state = None

    if not blockers:
        state = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": PASS_STATUS,
            "report_integration_ready": True,
            "active_report_id": session.get("active_report_id"),
            "available_report_ids": [
                route.get("report_id")
                for route in routes
                if isinstance(route, dict)
            ],
            "route_count": len(routes),
            "sync_link_count": results.get("unified_regen_report_sync_link_count", 0),
            "report_window_created": False,
            "report_rendering_performed": False,
            "report_export_performed": False,
        }

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    if state:
        state["status"] = status

    results.update({
        "regen_unified_report_state_owner_complete": True,
        "phase_16c_unified_report_state_owner_complete": True,
        "regen_unified_report_state_owner_ready": ready,
        "regen_unified_report_state_owner_status": status,
        "regen_unified_report_state_owner_blockers": blockers,

        "unified_regen_report_state": state if ready else {},
        "unified_regen_report_integration_ready": ready,
        "unified_regen_report_window_created": False,
        "unified_regen_report_rendering_performed": False,
        "unified_regen_report_export_performed": False,
    })

    return results
