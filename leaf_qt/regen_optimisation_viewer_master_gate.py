OWNER_NAME = "REGEN_OPTIMISATION_VIEWER_MASTER_GATE"
PHASE = "15A"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_VIEWER_MASTER_GATE_PHASE_15A"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_VIEWER_MASTER_GATE_PHASE_15A"


def attach_regen_optimisation_viewer_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_optimisation_viewer_completion_audit_ready") is not True:
        blockers.append("15A optimisation viewer completion audit is not ready.")

    if results.get("regen_optimisation_viewer_completion_audit_status") != "PASS_REGEN_OPTIMISATION_VIEWER_BACKEND_PHASE_15A":
        blockers.append("15A optimisation viewer completion audit has not passed.")

    if results.get("phase_15b_candidate_comparison_viewer_backend_allowed") is not True:
        blockers.append("Phase 15B candidate comparison backend was not unlocked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_optimisation_viewer_master_gate_complete": True,
        "phase_15a_optimisation_viewer_master_gate_complete": True,
        "regen_optimisation_viewer_master_gate_passed": ready,
        "regen_optimisation_viewer_master_gate_status": status,
        "regen_optimisation_viewer_master_gate_blockers": blockers,

        "phase_15a_complete": ready,
        "phase_15a_status": (
            "PASS_REGEN_OPTIMISATION_VIEWER_BACKEND_PHASE_15A"
            if ready else
            "FAIL_REGEN_OPTIMISATION_VIEWER_BACKEND_PHASE_15A"
        ),

        "phase_15b_candidate_comparison_viewer_backend_allowed": ready,
    })

    return results
