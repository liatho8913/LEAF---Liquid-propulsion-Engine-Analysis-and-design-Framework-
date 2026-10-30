OWNER_NAME = "REGEN_RUNTIME_MUTATION_EXECUTION_HISTORY_OWNER"
PHASE = "14A"

PASS_STATUS = "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_HISTORY_OWNER_PHASE_14A"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_MUTATION_EXECUTION_HISTORY_OWNER_PHASE_14A"


def attach_regen_runtime_mutation_execution_history_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_runtime_mutation_execution_history_owner(results)
    results.update(payload)
    return results


def build_regen_runtime_mutation_execution_history_owner(results):
    blockers = []

    validation = results.get("regen_runtime_mutation_execution_validation")
    records = results.get("regen_runtime_mutation_execution_records", [])

    if not isinstance(validation, dict) or validation.get("ready") is not True:
        blockers.append("Runtime mutation execution validation is not ready.")

    if not isinstance(records, list) or not records:
        blockers.append("Runtime mutation execution records are missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None

    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "RUNTIME_MUTATION_EXECUTED_RECORDS_CREATED_ONLY",
            "runtime_mutation_execution_count": len(records),
            "solver_execution_count": 0,
            "candidate_evaluation_count": 0,
            "candidate_acceptance_count": 0,
            "generation_advance_count": 0,
            "live_geometry_commit_count": 0,
            "entries": [
                {
                    "entry_id": f"RUNTIME_MUTATION_HISTORY_14A_{index:04d}",
                    "event": "MUTATION_PACKAGE_TRANSLATED_TO_RUNTIME_CANDIDATE",
                    "runtime_candidate_id": record.get("runtime_candidate_id"),
                    "source_mutation_package_id": record.get("source_mutation_package_id"),
                    "parent_candidate_id": record.get("parent_candidate_id"),
                    "execution_locked_after_creation": True,
                }
                for index, record in enumerate(records)
            ],
        }

    return {
        "regen_runtime_mutation_execution_history_owner_complete": True,
        "phase_14a_runtime_mutation_execution_history_owner_complete": True,
        "regen_runtime_mutation_execution_history_owner_ready": ready,
        "regen_runtime_mutation_execution_history_owner_status": status,
        "regen_runtime_mutation_execution_history_owner_blockers": blockers,
        "regen_runtime_mutation_execution_history": history,
    }
