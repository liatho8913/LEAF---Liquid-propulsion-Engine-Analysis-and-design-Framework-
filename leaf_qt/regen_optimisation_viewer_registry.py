OWNER_NAME = "REGEN_OPTIMISATION_VIEWER_REGISTRY"
PHASE = "15A"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_VIEWER_REGISTRY_PHASE_15A"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_VIEWER_REGISTRY_PHASE_15A"


def attach_regen_optimisation_viewer_registry(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    allowed = results.get("phase_15a_optimisation_viewer_backend_allowed") is True
    phase_14_complete = (
        results.get("phase_14_runtime_backend_complete") is True
        or results.get("phase_14f_status") == "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_PHASE_14F"
    )

    if not allowed:
        blockers.append("Phase 15A has not been unlocked by Phase 14F.")

    if not phase_14_complete:
        blockers.append("Phase 14 runtime backend is not complete.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_optimisation_viewer_registry_complete": True,
        "phase_15a_optimisation_viewer_registry_complete": True,
        "regen_optimisation_viewer_registry_ready": ready,
        "regen_optimisation_viewer_registry_status": status,
        "regen_optimisation_viewer_registry_blockers": blockers,
        "regen_optimisation_viewer_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "viewer_backend_allowed": ready,
            "qt_window_allowed": False,
            "plot_rendering_allowed": False,
            "ui_widget_allowed": False,
            "candidate_comparison_backend_allowed_next": ready,
        } if ready else None,
    })

    return results
