OWNER_NAME = "REGEN_UNIFIED_VIEWER_ROUTING_OWNER"
PHASE = "16B"

PASS_STATUS = "PASS_REGEN_UNIFIED_VIEWER_ROUTING_OWNER_PHASE_16B"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VIEWER_ROUTING_OWNER_PHASE_16B"


def attach_regen_unified_viewer_routing_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_viewer_integration_registry_ready") is not True:
        blockers.append("Unified viewer integration registry is not ready.")

    viewers = results.get("unified_regen_registered_viewers", [])
    if not isinstance(viewers, list) or not viewers:
        blockers.append("Unified registered viewers are missing.")

    routes = []

    if isinstance(viewers, list):
        for index, viewer in enumerate(viewers):
            if not isinstance(viewer, dict):
                blockers.append(f"Viewer registration at index {index} is not a dictionary.")
                continue

            viewer_id = viewer.get("viewer_id")
            backend_key = viewer.get("backend_key")

            if not viewer_id:
                blockers.append(f"Viewer registration at index {index} is missing viewer_id.")
                continue

            routes.append({
                "viewer_route_id": f"UNIFIED_VIEWER_ROUTE_16B_{index:04d}",
                "viewer_id": viewer_id,
                "backend_key": backend_key,
                "route_active": True,
                "ui_created": False,
                "rendered": False,
            })

    if not routes:
        blockers.append("No unified viewer routes were created.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_viewer_routing_owner_complete": True,
        "phase_16b_unified_viewer_routing_owner_complete": True,
        "regen_unified_viewer_routing_owner_ready": ready,
        "regen_unified_viewer_routing_owner_status": status,
        "regen_unified_viewer_routing_owner_blockers": blockers,

        "unified_regen_viewer_routes": routes if ready else [],
        "unified_regen_viewer_route_count": len(routes) if ready else 0,
    })

    return results
