OWNER_NAME = "REGEN_UNIFIED_REPORT_ROUTING_OWNER"
PHASE = "16C"

PASS_STATUS = "PASS_REGEN_UNIFIED_REPORT_ROUTING_OWNER_PHASE_16C"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_REPORT_ROUTING_OWNER_PHASE_16C"


def attach_regen_unified_report_routing_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_report_integration_registry_ready") is not True:
        blockers.append("Unified report integration registry is not ready.")

    reports = results.get("unified_regen_registered_reports", [])
    if not isinstance(reports, list) or not reports:
        blockers.append("Unified registered reports are missing.")

    routes = []

    if isinstance(reports, list):
        for index, report in enumerate(reports):
            if not isinstance(report, dict):
                blockers.append(f"Report registration at index {index} is not a dictionary.")
                continue

            report_id = report.get("report_id")
            source_key = report.get("source_key")

            if not report_id:
                blockers.append(f"Report registration at index {index} is missing report_id.")
                continue

            routes.append({
                "report_route_id": f"UNIFIED_REPORT_ROUTE_16C_{index:04d}",
                "report_id": report_id,
                "source_key": source_key,
                "route_active": True,
                "rendered": False,
                "exported": False,
            })

    if not routes:
        blockers.append("No unified report routes were created.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_report_routing_owner_complete": True,
        "phase_16c_unified_report_routing_owner_complete": True,
        "regen_unified_report_routing_owner_ready": ready,
        "regen_unified_report_routing_owner_status": status,
        "regen_unified_report_routing_owner_blockers": blockers,

        "unified_regen_report_routes": routes if ready else [],
        "unified_regen_report_route_count": len(routes) if ready else 0,
    })

    return results
