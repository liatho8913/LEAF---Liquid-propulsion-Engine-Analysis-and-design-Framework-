OWNER_NAME = "REGEN_EVOLUTION_TREE_MASTER_GATE"
PHASE = "15C"

PASS_STATUS = "PASS_REGEN_EVOLUTION_TREE_MASTER_GATE_PHASE_15C"
FAIL_STATUS = "FAIL_REGEN_EVOLUTION_TREE_MASTER_GATE_PHASE_15C"


def attach_regen_evolution_tree_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_evolution_tree_completion_audit_ready") is not True:
        blockers.append("15C evolution tree completion audit is not ready.")

    if results.get("regen_evolution_tree_completion_audit_status") != "PASS_REGEN_EVOLUTION_TREE_BACKEND_PHASE_15C":
        blockers.append("15C evolution tree completion audit has not passed.")

    if results.get("phase_15d_optimisation_report_backend_allowed") is not True:
        blockers.append("Phase 15D optimisation report backend was not unlocked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_evolution_tree_master_gate_complete": True,
        "phase_15c_evolution_tree_master_gate_complete": True,
        "regen_evolution_tree_master_gate_passed": ready,
        "regen_evolution_tree_master_gate_status": status,
        "regen_evolution_tree_master_gate_blockers": blockers,

        "phase_15c_complete": ready,
        "phase_15c_status": (
            "PASS_REGEN_EVOLUTION_TREE_BACKEND_PHASE_15C"
            if ready else
            "FAIL_REGEN_EVOLUTION_TREE_BACKEND_PHASE_15C"
        ),

        "phase_15d_optimisation_report_backend_allowed": ready,
    })

    return results
