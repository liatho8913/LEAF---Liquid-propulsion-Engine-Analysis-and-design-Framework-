OWNER_NAME = "REGEN_RUNTIME_CANDIDATE_EVALUATION_MASTER_GATE"
PHASE = "14B"

PASS_STATUS = "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_MASTER_GATE_PHASE_14B"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CANDIDATE_EVALUATION_MASTER_GATE_PHASE_14B"


def attach_regen_runtime_candidate_evaluation_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_runtime_candidate_evaluation_completion_audit_ready") is not True:
        blockers.append("14B runtime candidate evaluation completion audit is not ready.")

    if results.get("regen_runtime_candidate_evaluation_completion_audit_status") != "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_PHASE_14B":
        blockers.append("14B runtime candidate evaluation completion audit has not passed.")

    if results.get("phase_14c_runtime_selection_allowed") is not True:
        blockers.append("Phase 14C runtime selection has not been unlocked.")

    if results.get("phase_14_runtime_optimisation_allowed") is not False:
        blockers.append("Full runtime optimisation must remain locked after 14B.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_candidate_evaluation_master_gate_complete": True,
        "phase_14b_runtime_candidate_evaluation_master_gate_complete": True,
        "regen_runtime_candidate_evaluation_master_gate_passed": ready,
        "regen_runtime_candidate_evaluation_master_gate_status": status,
        "regen_runtime_candidate_evaluation_master_gate_blockers": blockers,

        "phase_14b_complete": ready,
        "phase_14b_status": (
            "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_PHASE_14B"
            if ready else
            "FAIL_REGEN_RUNTIME_CANDIDATE_EVALUATION_PHASE_14B"
        ),

        "phase_14c_runtime_selection_allowed": ready,
        "phase_14_runtime_optimisation_allowed": False,

        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_generation_advance_execution_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    })

    return results
