OWNER_NAME = "REGEN_EVOLUTION_TREE_REGISTRY"
PHASE = "15C"

PASS_STATUS = "PASS_REGEN_EVOLUTION_TREE_REGISTRY_PHASE_15C"
FAIL_STATUS = "FAIL_REGEN_EVOLUTION_TREE_REGISTRY_PHASE_15C"


def attach_regen_evolution_tree_registry(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    allowed = results.get("phase_15c_evolution_tree_backend_allowed") is True
    phase_15b_complete = (
        results.get("phase_15b_complete") is True
        or results.get("phase_15b_status")
        == "PASS_REGEN_CANDIDATE_COMPARISON_VIEWER_BACKEND_PHASE_15B"
    )

    if not allowed:
        blockers.append("Phase 15C has not been unlocked by Phase 15B.")

    if not phase_15b_complete:
        blockers.append("Phase 15B candidate comparison backend is not complete.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_evolution_tree_registry_complete": True,
        "phase_15c_evolution_tree_registry_complete": True,
        "regen_evolution_tree_registry_ready": ready,
        "regen_evolution_tree_registry_status": status,
        "regen_evolution_tree_registry_blockers": blockers,
        "regen_evolution_tree_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "tree_backend_allowed": ready,
            "qt_window_allowed": False,
            "node_graph_allowed": False,
            "rendering_allowed": False,
            "optimisation_report_backend_allowed_next": ready,
        } if ready else None,
    })

    return results
