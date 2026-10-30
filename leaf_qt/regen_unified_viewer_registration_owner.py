OWNER_NAME = "REGEN_UNIFIED_VIEWER_REGISTRATION_OWNER"
PHASE = "16A"

PASS_STATUS = "PASS_REGEN_UNIFIED_VIEWER_REGISTRATION_OWNER_PHASE_16A"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VIEWER_REGISTRATION_OWNER_PHASE_16A"


def attach_regen_unified_viewer_registration_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_ecosystem_registry_ready") is not True:
        blockers.append("Unified ecosystem registry is not ready.")

    viewers = [
        {
            "viewer_id": "CROSS_SECTION_VIEWER",
            "backend_key": "regen_cross_section_viewer",
            "registered": True,
            "ui_created": False,
        },
        {
            "viewer_id": "STATION_VIEWER",
            "backend_key": "station_table",
            "registered": True,
            "ui_created": False,
        },
        {
            "viewer_id": "OPTIMISATION_VIEWER",
            "backend_key": "optimisation_viewer_backend_payload",
            "registered": bool(results.get("optimisation_viewer_backend_payload") is not None),
            "ui_created": False,
        },
        {
            "viewer_id": "CANDIDATE_COMPARISON_VIEWER",
            "backend_key": "candidate_comparison_summary",
            "registered": bool(results.get("candidate_comparison_summary") is not None),
            "ui_created": False,
        },
        {
            "viewer_id": "EVOLUTION_TREE_VIEWER",
            "backend_key": "evolution_tree_summary",
            "registered": bool(results.get("evolution_tree_summary") is not None),
            "ui_created": False,
        },
        {
            "viewer_id": "OPTIMISATION_REPORT_VIEWER",
            "backend_key": "optimisation_report_backend_summary",
            "registered": bool(results.get("optimisation_report_backend_summary") is not None),
            "ui_created": False,
        },
    ]

    missing = [v["viewer_id"] for v in viewers if v.get("registered") is not True]
    if missing:
        blockers.append("Viewer backend registrations missing: " + ", ".join(missing))

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_viewer_registration_owner_complete": True,
        "phase_16a_unified_viewer_registration_owner_complete": True,
        "regen_unified_viewer_registration_owner_ready": ready,
        "regen_unified_viewer_registration_owner_status": status,
        "regen_unified_viewer_registration_owner_blockers": blockers,

        "unified_regen_registered_viewers": viewers if ready else [],
        "unified_regen_registered_viewer_count": len(viewers) if ready else 0,
        "unified_regen_qt_windows_created": False,
        "unified_regen_rendering_performed": False,
    })

    return results
