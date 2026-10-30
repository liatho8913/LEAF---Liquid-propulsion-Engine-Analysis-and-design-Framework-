OWNER_NAME = "REGEN_RUNTIME_CONVERGENCE_MASTER_GATE"
PHASE = "14E"

PASS_STATUS = "PASS_REGEN_RUNTIME_CONVERGENCE_MASTER_GATE_PHASE_14E"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CONVERGENCE_MASTER_GATE_PHASE_14E"


def attach_regen_runtime_convergence_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_runtime_convergence_completion_audit_ready") is not True:
        blockers.append("14E runtime convergence completion audit is not ready.")

    if results.get("regen_runtime_convergence_completion_audit_status") != "PASS_REGEN_RUNTIME_CONVERGENCE_PHASE_14E":
        blockers.append("14E runtime convergence completion audit has not passed.")

    if results.get("phase_14f_runtime_optimisation_audit_allowed") is not True:
        blockers.append("Phase 14F runtime optimisation audit has not been unlocked.")

    if results.get("regen_runtime_optimisation_complete") is not False:
        blockers.append("Runtime optimisation must not be marked complete until 14F.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_convergence_master_gate_complete": True,
        "phase_14e_runtime_convergence_master_gate_complete": True,
        "regen_runtime_convergence_master_gate_passed": ready,
        "regen_runtime_convergence_master_gate_status": status,
        "regen_runtime_convergence_master_gate_blockers": blockers,

        "phase_14e_complete": ready,
        "phase_14e_status": (
            "PASS_REGEN_RUNTIME_CONVERGENCE_PHASE_14E"
            if ready else
            "FAIL_REGEN_RUNTIME_CONVERGENCE_PHASE_14E"
        ),

        "phase_14f_runtime_optimisation_audit_allowed": ready,
        "phase_14_runtime_optimisation_allowed": False,
        "regen_runtime_optimisation_complete": False,
    })

    return results
