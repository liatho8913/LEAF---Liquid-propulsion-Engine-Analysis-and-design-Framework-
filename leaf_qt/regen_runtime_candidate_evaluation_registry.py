OWNER_NAME = "REGEN_RUNTIME_CANDIDATE_EVALUATION_REGISTRY"
PHASE = "14B"

PASS_STATUS = "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_REGISTRY_PHASE_14B"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CANDIDATE_EVALUATION_REGISTRY_PHASE_14B"


def attach_regen_runtime_candidate_evaluation_registry(results):
    if not isinstance(results, dict):
        return results

    records = results.get("regen_runtime_candidate_records", [])
    blockers = []

    allowed = results.get("phase_14b_runtime_candidate_evaluation_allowed") is True
    phase_14a_complete = (
        results.get("phase_14a_complete") is True
        or results.get("phase_14a_status") == "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_PHASE_14A"
    )

    if not allowed:
        blockers.append("Phase 14B has not been unlocked by Phase 14A.")

    if not phase_14a_complete:
        blockers.append("Phase 14A runtime mutation execution is not complete.")

    if not isinstance(records, list) or not records:
        blockers.append("No runtime candidate records exist for evaluation.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_candidate_evaluation_registry_complete": True,
        "phase_14b_runtime_candidate_evaluation_registry_complete": True,
        "regen_runtime_candidate_evaluation_registry_ready": ready,
        "regen_runtime_candidate_evaluation_registry_status": status,
        "regen_runtime_candidate_evaluation_registry_blockers": blockers,
        "regen_runtime_candidate_evaluation_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "candidate_count": len(records) if isinstance(records, list) else 0,
            "solver_execution_allowed": True if ready else False,
            "candidate_acceptance_allowed": False,
            "generation_advance_allowed": False,
            "live_geometry_commit_allowed": False,
        } if ready else None,
    })

    return results
