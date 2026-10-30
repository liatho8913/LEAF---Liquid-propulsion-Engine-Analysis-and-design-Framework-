OWNER_NAME = "REGEN_RUNTIME_MUTATION_EXECUTION_VALIDATION_OWNER"
PHASE = "14A"

PASS_STATUS = "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_VALIDATION_OWNER_PHASE_14A"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_MUTATION_EXECUTION_VALIDATION_OWNER_PHASE_14A"


def attach_regen_runtime_mutation_execution_validation_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_runtime_mutation_execution_validation_owner(results)
    results.update(payload)
    return results


def build_regen_runtime_mutation_execution_validation_owner(results):
    blockers = []

    records = results.get("regen_runtime_mutation_execution_records", [])

    if not isinstance(records, list) or not records:
        blockers.append("Runtime mutation execution records are missing.")

    seen_ids = set()

    for record in records if isinstance(records, list) else []:
        if not isinstance(record, dict):
            blockers.append("Runtime mutation execution record is not a dictionary.")
            continue

        runtime_id = record.get("runtime_candidate_id")
        execution_id = record.get("runtime_mutation_execution_id")

        if not runtime_id:
            blockers.append("Runtime mutation record is missing runtime_candidate_id.")
        elif runtime_id in seen_ids:
            blockers.append(f"Duplicate runtime_candidate_id detected: {runtime_id}")
        else:
            seen_ids.add(runtime_id)

        if not execution_id:
            blockers.append(f"Runtime candidate {runtime_id} is missing runtime_mutation_execution_id.")

        if record.get("runtime_candidate_created") is not True:
            blockers.append(f"Runtime candidate {runtime_id} was not marked as created.")

        if not isinstance(record.get("mutation_vector"), dict):
            blockers.append(f"Runtime candidate {runtime_id} is missing mutation_vector.")

        _validate_record_locks(record, runtime_id, blockers)

    _validate_global_locks(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_runtime_mutation_execution_validation_owner_complete": True,
        "phase_14a_runtime_mutation_execution_validation_owner_complete": True,
        "regen_runtime_mutation_execution_validation_owner_ready": ready,
        "regen_runtime_mutation_execution_validation_owner_status": status,
        "regen_runtime_mutation_execution_validation_owner_blockers": blockers,
        "regen_runtime_mutation_execution_validation": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "validated_runtime_candidate_count": len(records) if isinstance(records, list) else 0,
            "solver_execution_locked": True,
            "candidate_evaluation_locked": True,
            "candidate_acceptance_locked": True,
            "generation_advance_locked": True,
            "live_geometry_commit_locked": True,
        },

        "phase_14b_runtime_candidate_evaluation_allowed": ready,

        "regen_runtime_mutation_solver_execution_allowed": False,
        "regen_runtime_mutation_candidate_acceptance_allowed": False,
        "regen_runtime_mutation_generation_advance_allowed": False,
        "regen_runtime_mutation_live_geometry_commit_allowed": False,
    }


def _validate_record_locks(record, runtime_id, blockers):
    required_false = {
        "solver_executed": "solver executed",
        "candidate_evaluated": "candidate evaluated",
        "candidate_accepted": "candidate accepted",
        "generation_advanced": "generation advanced",
        "live_geometry_committed": "live geometry committed",
    }

    for key, label in required_false.items():
        if record.get(key) is not False:
            blockers.append(f"Runtime candidate {runtime_id} has illegal state: {label}.")


def _validate_global_locks(results, blockers):
    required_false = {
        "regen_runtime_mutation_solver_executed": "Runtime mutation solver execution occurred.",
        "regen_runtime_mutation_candidate_evaluated": "Runtime candidate evaluation occurred too early.",
        "regen_runtime_mutation_candidate_accepted": "Runtime candidate acceptance occurred too early.",
        "regen_runtime_mutation_generation_advanced": "Runtime generation advancement occurred too early.",
        "regen_runtime_mutation_live_geometry_committed": "Runtime live geometry commit occurred too early.",
        "regen_optimisation_candidate_acceptance_allowed": "Candidate acceptance is not locked.",
        "regen_optimisation_live_geometry_commit_allowed": "Live geometry commit is not locked.",
        "regen_generation_advance_execution_allowed": "Generation advancement is not locked.",
    }

    for key, message in required_false.items():
        if key in results and results.get(key) is not False:
            blockers.append(message)
