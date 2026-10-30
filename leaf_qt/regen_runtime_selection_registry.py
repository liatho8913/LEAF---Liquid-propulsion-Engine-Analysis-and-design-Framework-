OWNER_NAME = "REGEN_RUNTIME_SELECTION_REGISTRY"
PHASE = "14C"

PASS_STATUS = "PASS_REGEN_RUNTIME_SELECTION_REGISTRY_PHASE_14C"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_SELECTION_REGISTRY_PHASE_14C"


def attach_regen_runtime_selection_registry(results):
    if not isinstance(results, dict):
        return results

    evaluations = results.get("regen_runtime_candidate_evaluation_records", [])
    blockers = []

    allowed = results.get("phase_14c_runtime_selection_allowed") is True
    phase_14b_complete = (
        results.get("phase_14b_complete") is True
        or results.get("phase_14b_status") == "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_PHASE_14B"
    )

    if not allowed:
        blockers.append("Phase 14C has not been unlocked by Phase 14B.")

    if not phase_14b_complete:
        blockers.append("Phase 14B runtime candidate evaluation is not complete.")

    if not isinstance(evaluations, list) or not evaluations:
        blockers.append("No runtime candidate evaluation records exist for selection.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_selection_registry_complete": True,
        "phase_14c_runtime_selection_registry_complete": True,
        "regen_runtime_selection_registry_ready": ready,
        "regen_runtime_selection_registry_status": status,
        "regen_runtime_selection_registry_blockers": blockers,
        "regen_runtime_selection_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "evaluated_candidate_count": len(evaluations) if isinstance(evaluations, list) else 0,
            "runtime_selection_allowed": ready,
            "parent_pool_allowed": ready,
            "generation_advance_allowed": False,
            "live_geometry_commit_allowed": False,
            "full_runtime_optimisation_allowed": False,
        } if ready else None,
    })

    return results
