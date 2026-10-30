OWNER_NAME = "REGEN_UNIFIED_VIEWER_SYNCHRONISATION_OWNER"
PHASE = "16B"

PASS_STATUS = "PASS_REGEN_UNIFIED_VIEWER_SYNCHRONISATION_OWNER_PHASE_16B"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VIEWER_SYNCHRONISATION_OWNER_PHASE_16B"


def attach_regen_unified_viewer_synchronisation_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_viewer_routing_owner_ready") is not True:
        blockers.append("Unified viewer routing owner is not ready.")

    routes = results.get("unified_regen_viewer_routes", [])
    if not isinstance(routes, list) or not routes:
        blockers.append("Unified viewer routes are missing.")

    sync_links = []

    if isinstance(routes, list):
        route_ids = [
            r.get("viewer_id") for r in routes
            if isinstance(r, dict) and r.get("viewer_id")
        ]

        for index, viewer_id in enumerate(route_ids):
            sync_links.append({
                "viewer_sync_id": f"UNIFIED_VIEWER_SYNC_16B_{index:04d}",
                "source_viewer_id": viewer_id,
                "linked_viewer_ids": [v for v in route_ids if v != viewer_id],
                "sync_state": "BACKEND_SYNC_READY",
                "render_triggered": False,
                "ui_event_bound": False,
            })

    if not sync_links:
        blockers.append("No unified viewer synchronisation links were created.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_viewer_synchronisation_owner_complete": True,
        "phase_16b_unified_viewer_synchronisation_owner_complete": True,
        "regen_unified_viewer_synchronisation_owner_ready": ready,
        "regen_unified_viewer_synchronisation_owner_status": status,
        "regen_unified_viewer_synchronisation_owner_blockers": blockers,

        "unified_regen_viewer_sync_links": sync_links if ready else [],
        "unified_regen_viewer_sync_link_count": len(sync_links) if ready else 0,
    })

    return results
