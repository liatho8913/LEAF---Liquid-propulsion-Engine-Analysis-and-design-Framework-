OWNER_NAME = "REGEN_UNIFIED_VALIDATION_SYNCHRONISATION_OWNER"
PHASE = "16D"

PASS_STATUS = "PASS_REGEN_UNIFIED_VALIDATION_SYNCHRONISATION_OWNER_PHASE_16D"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VALIDATION_SYNCHRONISATION_OWNER_PHASE_16D"


def attach_regen_unified_validation_synchronisation_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_validation_routing_owner_ready") is not True:
        blockers.append("Unified validation routing owner is not ready.")

    routes = results.get("unified_regen_validation_routes", [])
    if not isinstance(routes, list) or not routes:
        blockers.append("Unified validation routes are missing.")

    sync_links = []

    if isinstance(routes, list):
        validation_ids = [
            route.get("validation_id")
            for route in routes
            if isinstance(route, dict) and route.get("validation_id")
        ]

        for index, validation_id in enumerate(validation_ids):
            sync_links.append({
                "validation_sync_id": f"UNIFIED_VALIDATION_SYNC_16D_{index:04d}",
                "source_validation_id": validation_id,
                "linked_validation_ids": [vid for vid in validation_ids if vid != validation_id],
                "sync_state": "BACKEND_VALIDATION_SYNC_READY",
                "display_triggered": False,
                "ui_event_bound": False,
            })

    if not sync_links:
        blockers.append("No unified validation synchronisation links were created.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_validation_synchronisation_owner_complete": True,
        "phase_16d_unified_validation_synchronisation_owner_complete": True,
        "regen_unified_validation_synchronisation_owner_ready": ready,
        "regen_unified_validation_synchronisation_owner_status": status,
        "regen_unified_validation_synchronisation_owner_blockers": blockers,

        "unified_regen_validation_sync_links": sync_links if ready else [],
        "unified_regen_validation_sync_link_count": len(sync_links) if ready else 0,
    })

    return results
