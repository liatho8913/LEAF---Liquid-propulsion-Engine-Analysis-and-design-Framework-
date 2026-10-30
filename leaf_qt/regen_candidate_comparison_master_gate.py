OWNER_NAME = "REGEN_CANDIDATE_COMPARISON_MASTER_GATE"
PHASE = "15B"

PASS_STATUS = "PASS_REGEN_CANDIDATE_COMPARISON_MASTER_GATE_PHASE_15B"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_COMPARISON_MASTER_GATE_PHASE_15B"


def attach_regen_candidate_comparison_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_candidate_comparison_completion_audit_ready") is not True:
        blockers.append("15B candidate comparison completion audit is not ready.")

    if results.get("regen_candidate_comparison_completion_audit_status") != "PASS_REGEN_CANDIDATE_COMPARISON_VIEWER_BACKEND_PHASE_15B":
        blockers.append("15B candidate comparison completion audit has not passed.")

    if results.get("phase_15c_evolution_tree_backend_allowed") is not True:
        blockers.append("Phase 15C evolution tree backend was not unlocked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_candidate_comparison_master_gate_complete": True,
        "phase_15b_candidate_comparison_master_gate_complete": True,
        "regen_candidate_comparison_master_gate_passed": ready,
        "regen_candidate_comparison_master_gate_status": status,
        "regen_candidate_comparison_master_gate_blockers": blockers,

        "phase_15b_complete": ready,
        "phase_15b_status": (
            "PASS_REGEN_CANDIDATE_COMPARISON_VIEWER_BACKEND_PHASE_15B"
            if ready else
            "FAIL_REGEN_CANDIDATE_COMPARISON_VIEWER_BACKEND_PHASE_15B"
        ),

        "phase_15c_evolution_tree_backend_allowed": ready,
    })

    return results
