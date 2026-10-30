OWNER_NAME = "REGEN_OPTIMISATION_REPORT_BACKEND_REGISTRY"
PHASE = "15D"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_REGISTRY_PHASE_15D"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_REPORT_BACKEND_REGISTRY_PHASE_15D"


def attach_regen_optimisation_report_backend_registry(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    allowed = results.get("phase_15d_optimisation_report_backend_allowed") is True
    phase_15c_complete = (
        results.get("phase_15c_complete") is True
        or results.get("phase_15c_status") == "PASS_REGEN_EVOLUTION_TREE_BACKEND_PHASE_15C"
    )

    if not allowed:
        blockers.append("Phase 15D has not been unlocked by Phase 15C.")

    if not phase_15c_complete:
        blockers.append("Phase 15C evolution tree backend is not complete.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_optimisation_report_backend_registry_complete": True,
        "phase_15d_optimisation_report_backend_registry_complete": True,
        "regen_optimisation_report_backend_registry_ready": ready,
        "regen_optimisation_report_backend_registry_status": status,
        "regen_optimisation_report_backend_registry_blockers": blockers,
        "regen_optimisation_report_backend_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "report_backend_allowed": ready,
            "qt_report_window_allowed": False,
            "pdf_export_allowed": False,
            "html_export_allowed": False,
            "phase_16_unified_regen_ecosystem_allowed_next": ready,
        } if ready else None,
    })

    return results
