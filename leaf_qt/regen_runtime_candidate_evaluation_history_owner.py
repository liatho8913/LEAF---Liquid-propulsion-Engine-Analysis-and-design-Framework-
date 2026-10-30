OWNER_NAME = "REGEN_RUNTIME_CANDIDATE_EVALUATION_HISTORY_OWNER"
PHASE = "14B"

PASS_STATUS = "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_HISTORY_OWNER_PHASE_14B"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CANDIDATE_EVALUATION_HISTORY_OWNER_PHASE_14B"


def attach_regen_runtime_candidate_evaluation_history_owner(results):
    if not isinstance(results, dict):
        return results

    evaluations = results.get("regen_runtime_candidate_evaluation_records", [])
    blockers = []

    if results.get("regen_runtime_candidate_evaluation_validation_owner_ready") is not True:
        blockers.append("Runtime candidate evaluation validation owner is not ready.")

    if not isinstance(evaluations, list) or not evaluations:
        blockers.append("Runtime candidate evaluations are missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None
    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "RUNTIME_CANDIDATES_EVALUATED_NO_ACCEPTANCE",
            "evaluation_count": len(evaluations),
            "candidate_acceptance_count": 0,
            "generation_advance_count": 0,
            "live_geometry_commit_count": 0,
            "entries": [
                {
                    "entry_id": f"RUNTIME_CANDIDATE_EVALUATION_HISTORY_14B_{i:04d}",
                    "event": "RUNTIME_CANDIDATE_EVALUATED",
                    "runtime_candidate_id": e.get("runtime_candidate_id"),
                    "candidate_score": e.get("candidate_score"),
                    "accepted": False,
                    "generation_advanced": False,
                    "live_geometry_committed": False,
                }
                for i, e in enumerate(evaluations)
            ],
        }

    results.update({
        "regen_runtime_candidate_evaluation_history_owner_complete": True,
        "phase_14b_runtime_candidate_evaluation_history_owner_complete": True,
        "regen_runtime_candidate_evaluation_history_owner_ready": ready,
        "regen_runtime_candidate_evaluation_history_owner_status": status,
        "regen_runtime_candidate_evaluation_history_owner_blockers": blockers,
        "regen_runtime_candidate_evaluation_history": history,
    })

    return results
