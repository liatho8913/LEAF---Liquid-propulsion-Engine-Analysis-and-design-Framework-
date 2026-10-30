OWNER_NAME = "REGEN_CANDIDATE_COMPARISON_REGISTRY"
PHASE = "15B"

PASS_STATUS = "PASS_REGEN_CANDIDATE_COMPARISON_REGISTRY_PHASE_15B"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_COMPARISON_REGISTRY_PHASE_15B"


def attach_regen_candidate_comparison_registry(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    allowed = results.get("phase_15b_candidate_comparison_viewer_backend_allowed") is True
    phase_15a_complete = (
        results.get("phase_15a_complete") is True
        or results.get("phase_15a_status") == "PASS_REGEN_OPTIMISATION_VIEWER_BACKEND_PHASE_15A"
    )

    if not allowed:
        blockers.append("Phase 15B has not been unlocked by Phase 15A.")

    if not phase_15a_complete:
        blockers.append("Phase 15A optimisation viewer backend is not complete.")

    candidates = results.get("optimisation_viewer_candidates", [])
    if not isinstance(candidates, list) or not candidates:
        blockers.append("Optimisation viewer candidates are missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_candidate_comparison_registry_complete": True,
        "phase_15b_candidate_comparison_registry_complete": True,
        "regen_candidate_comparison_registry_ready": ready,
        "regen_candidate_comparison_registry_status": status,
        "regen_candidate_comparison_registry_blockers": blockers,
        "regen_candidate_comparison_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "comparison_backend_allowed": ready,
            "qt_window_allowed": False,
            "plot_rendering_allowed": False,
            "ui_widget_allowed": False,
            "evolution_tree_backend_allowed_next": ready,
        } if ready else None,
    })

    return results
