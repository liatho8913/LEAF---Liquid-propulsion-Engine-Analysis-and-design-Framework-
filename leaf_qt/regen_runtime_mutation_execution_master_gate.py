OWNER_NAME = "REGEN_RUNTIME_MUTATION_EXECUTION_MASTER_GATE"
PHASE = "14A"

PASS_STATUS = "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_MASTER_GATE_PHASE_14A"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_MUTATION_EXECUTION_MASTER_GATE_PHASE_14A"


def attach_regen_runtime_mutation_execution_master_gate(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_runtime_mutation_execution_master_gate(results)
    results.update(payload)
    return results


def build_regen_runtime_mutation_execution_master_gate(results):
    blockers = []

    completion_ready = results.get("regen_runtime_mutation_execution_completion_audit_ready") is True
    completion_status = results.get("regen_runtime_mutation_execution_completion_audit_status")

    if not completion_ready:
        blockers.append("14A runtime mutation execution completion audit is not ready.")

    if completion_status != "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_PHASE_14A":
        blockers.append("14A runtime mutation execution completion audit has not passed.")

    if results.get("phase_14b_runtime_candidate_evaluation_allowed") is not True:
        blockers.append("Phase 14B runtime candidate evaluation has not been unlocked.")

    if results.get("phase_14_runtime_optimisation_allowed") is not False:
        blockers.append("Full Phase 14 runtime optimisation must remain locked after 14A.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_runtime_mutation_execution_master_gate_complete": True,
        "phase_14a_runtime_mutation_execution_master_gate_complete": True,
        "regen_runtime_mutation_execution_master_gate_passed": ready,
        "regen_runtime_mutation_execution_master_gate_status": status,
        "regen_runtime_mutation_execution_master_gate_blockers": blockers,

        "phase_14a_complete": ready,
        "phase_14a_status": (
            "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_PHASE_14A"
            if ready
            else "FAIL_REGEN_RUNTIME_MUTATION_EXECUTION_PHASE_14A"
        ),

        "phase_14b_runtime_candidate_evaluation_allowed": ready,
        "phase_14_runtime_optimisation_allowed": False,

        "regen_runtime_candidate_evaluation_allowed": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_generation_advance_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }
