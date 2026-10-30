OWNER_NAME = "REGEN_RUNTIME_EVOLUTION_MASTER_GATE"
PHASE = "14D"

PASS_STATUS = "PASS_REGEN_RUNTIME_EVOLUTION_MASTER_GATE_PHASE_14D"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_EVOLUTION_MASTER_GATE_PHASE_14D"


def attach_regen_runtime_evolution_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_runtime_evolution_completion_audit_ready") is not True:
        blockers.append("14D runtime evolution completion audit is not ready.")

    if results.get("regen_runtime_evolution_completion_audit_status") != "PASS_REGEN_RUNTIME_EVOLUTION_PHASE_14D":
        blockers.append("14D runtime evolution completion audit has not passed.")

    if results.get("phase_14e_runtime_convergence_allowed") is not True:
        blockers.append("Phase 14E runtime convergence has not been unlocked.")

    if results.get("phase_14_runtime_optimisation_allowed") is not False:
        blockers.append("Full runtime optimisation must remain locked after 14D.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_evolution_master_gate_complete": True,
        "phase_14d_runtime_evolution_master_gate_complete": True,
        "regen_runtime_evolution_master_gate_passed": ready,
        "regen_runtime_evolution_master_gate_status": status,
        "regen_runtime_evolution_master_gate_blockers": blockers,

        "phase_14d_complete": ready,
        "phase_14d_status": (
            "PASS_REGEN_RUNTIME_EVOLUTION_PHASE_14D"
            if ready else
            "FAIL_REGEN_RUNTIME_EVOLUTION_PHASE_14D"
        ),

        "phase_14e_runtime_convergence_allowed": ready,
        "phase_14_runtime_optimisation_allowed": False,
    })

    return results
