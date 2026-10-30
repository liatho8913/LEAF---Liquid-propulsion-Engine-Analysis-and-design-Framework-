OWNER_NAME = "REGEN_UNIFIED_VALIDATION_STATE_OWNER"
PHASE = "16D"

PASS_STATUS = "PASS_REGEN_UNIFIED_VALIDATION_STATE_OWNER_PHASE_16D"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VALIDATION_STATE_OWNER_PHASE_16D"


def attach_regen_unified_validation_state_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_validation_session_owner_ready") is not True:
        blockers.append("Unified validation session owner is not ready.")

    session = results.get("unified_regen_validation_session", {})
    routes = results.get("unified_regen_validation_routes", [])

    if not isinstance(session, dict) or not session:
        blockers.append("Unified validation session is missing.")

    if not isinstance(routes, list) or not routes:
        blockers.append("Unified validation routes are missing.")

    state = None

    if not blockers:
        state = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": PASS_STATUS,
            "validation_integration_ready": True,
            "active_validation_id": session.get("active_validation_id"),
            "available_validation_ids": [
                route.get("validation_id")
                for route in routes
                if isinstance(route, dict)
            ],
            "route_count": len(routes),
            "sync_link_count": results.get("unified_regen_validation_sync_link_count", 0),
            "validation_view_created": False,
            "validation_rendering_performed": False,
            "validation_export_performed": False,
        }

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    if state:
        state["status"] = status

    results.update({
        "regen_unified_validation_state_owner_complete": True,
        "phase_16d_unified_validation_state_owner_complete": True,
        "regen_unified_validation_state_owner_ready": ready,
        "regen_unified_validation_state_owner_status": status,
        "regen_unified_validation_state_owner_blockers": blockers,

        "unified_regen_validation_state": state if ready else {},
        "unified_regen_validation_integration_ready": ready,
        "unified_regen_validation_rendering_performed": False,
        "unified_regen_validation_export_performed": False,
    })

    return results
