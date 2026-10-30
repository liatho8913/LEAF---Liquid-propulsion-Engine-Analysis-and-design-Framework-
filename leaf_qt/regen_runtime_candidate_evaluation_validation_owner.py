OWNER_NAME = "REGEN_RUNTIME_CANDIDATE_EVALUATION_VALIDATION_OWNER"
PHASE = "14B"

PASS_STATUS = "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_VALIDATION_OWNER_PHASE_14B"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CANDIDATE_EVALUATION_VALIDATION_OWNER_PHASE_14B"


def attach_regen_runtime_candidate_evaluation_validation_owner(results):
    if not isinstance(results, dict):
        return results

    evaluations = results.get("regen_runtime_candidate_evaluation_records", [])
    blockers = []

    if results.get("regen_runtime_candidate_evaluation_registry_ready") is not True:
        blockers.append("Runtime candidate evaluation registry is not ready.")

    if results.get("regen_runtime_candidate_evaluation_engine_ready") is not True:
        blockers.append("Runtime candidate evaluation engine is not ready.")

    if not isinstance(evaluations, list) or not evaluations:
        blockers.append("No runtime candidate evaluation records are available.")

    seen = set()

    if isinstance(evaluations, list):
        for record in evaluations:
            candidate_id = record.get("runtime_candidate_id") if isinstance(record, dict) else None

            if not isinstance(record, dict):
                blockers.append("Evaluation record is not a dictionary.")
                continue

            if not candidate_id:
                blockers.append("Evaluation record is missing runtime_candidate_id.")
            elif candidate_id in seen:
                blockers.append(f"Duplicate evaluated runtime candidate id: {candidate_id}")
            else:
                seen.add(candidate_id)

            if record.get("evaluation_complete") is not True:
                blockers.append(f"Candidate {candidate_id} evaluation is not complete.")

            if record.get("solver_executed") is not True:
                blockers.append(f"Candidate {candidate_id} solver/evaluation bridge did not execute.")

            if not isinstance(record.get("candidate_score"), (int, float)):
                blockers.append(f"Candidate {candidate_id} has invalid candidate_score.")

            if record.get("candidate_accepted") is not False:
                blockers.append(f"Candidate {candidate_id} was illegally accepted in 14B.")

            if record.get("generation_advanced") is not False:
                blockers.append(f"Candidate {candidate_id} illegally advanced generation in 14B.")

            if record.get("live_geometry_committed") is not False:
                blockers.append(f"Candidate {candidate_id} illegally committed live geometry in 14B.")

    if results.get("regen_optimisation_candidate_acceptance_allowed") is not False:
        blockers.append("Candidate acceptance is not globally locked.")

    if results.get("regen_generation_advance_execution_allowed") is not False:
        blockers.append("Generation advancement is not globally locked.")

    if results.get("regen_optimisation_live_geometry_commit_allowed") is not False:
        blockers.append("Live geometry commit is not globally locked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_candidate_evaluation_validation_owner_complete": True,
        "phase_14b_runtime_candidate_evaluation_validation_owner_complete": True,
        "regen_runtime_candidate_evaluation_validation_owner_ready": ready,
        "regen_runtime_candidate_evaluation_validation_owner_status": status,
        "regen_runtime_candidate_evaluation_validation_owner_blockers": blockers,
        "regen_runtime_candidate_evaluation_validation": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "evaluated_candidate_count": len(evaluations) if isinstance(evaluations, list) else 0,
            "candidate_acceptance_locked": True,
            "generation_advance_locked": True,
            "live_geometry_commit_locked": True,
        },

        "phase_14c_runtime_selection_allowed": ready,

        "regen_runtime_candidate_acceptance_allowed": False,
        "regen_runtime_candidate_generation_advance_allowed": False,
        "regen_runtime_candidate_live_geometry_commit_allowed": False,
    })

    return results
