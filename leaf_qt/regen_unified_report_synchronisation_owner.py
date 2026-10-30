OWNER_NAME = "REGEN_UNIFIED_REPORT_SYNCHRONISATION_OWNER"
PHASE = "16C"

PASS_STATUS = "PASS_REGEN_UNIFIED_REPORT_SYNCHRONISATION_OWNER_PHASE_16C"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_REPORT_SYNCHRONISATION_OWNER_PHASE_16C"


def attach_regen_unified_report_synchronisation_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_report_routing_owner_ready") is not True:
        blockers.append("Unified report routing owner is not ready.")

    routes = results.get("unified_regen_report_routes", [])
    if not isinstance(routes, list) or not routes:
        blockers.append("Unified report routes are missing.")

    sync_links = []

    if isinstance(routes, list):
        report_ids = [
            route.get("report_id")
            for route in routes
            if isinstance(route, dict) and route.get("report_id")
        ]

        for index, report_id in enumerate(report_ids):
            sync_links.append({
                "report_sync_id": f"UNIFIED_REPORT_SYNC_16C_{index:04d}",
                "source_report_id": report_id,
                "linked_report_ids": [rid for rid in report_ids if rid != report_id],
                "sync_state": "BACKEND_REPORT_SYNC_READY",
                "render_triggered": False,
                "export_triggered": False,
            })

    if not sync_links:
        blockers.append("No unified report synchronisation links were created.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_report_synchronisation_owner_complete": True,
        "phase_16c_unified_report_synchronisation_owner_complete": True,
        "regen_unified_report_synchronisation_owner_ready": ready,
        "regen_unified_report_synchronisation_owner_status": status,
        "regen_unified_report_synchronisation_owner_blockers": blockers,

        "unified_regen_report_sync_links": sync_links if ready else [],
        "unified_regen_report_sync_link_count": len(sync_links) if ready else 0,
    })

    return results
