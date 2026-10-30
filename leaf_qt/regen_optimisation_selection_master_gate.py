OWNER_NAME = "REGEN_OPTIMISATION_SELECTION_MASTER_GATE"
PHASE = "13K"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_SELECTION_MASTER_GATE_PHASE_13K"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_SELECTION_MASTER_GATE_PHASE_13K"


def attach_regen_optimisation_selection_master_gate(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_selection_master_gate(results)
    results.update(payload)
    return results


def build_regen_optimisation_selection_master_gate(results):
    blockers = []

    completion_ready = results.get("regen_optimisation_selection_completion_audit_ready") is True
    completion_status = results.get("regen_optimisation_selection_completion_audit_status")

    if not completion_ready:
        blockers.append("13K selection completion audit is not ready.")

    if completion_status != "PASS_REGEN_OPTIMISATION_SELECTION_FRAMEWORK_PHASE_13K":
        blockers.append("13K selection completion audit has not passed.")

    ranked = results.get("regen_optimisation_selection_ranked_candidates", [])
    parent_pool = results.get("regen_optimisation_parent_pool", [])

    if not isinstance(ranked, list) or not ranked:
        blockers.append("Master gate cannot pass without ranked candidates.")

    if not isinstance(parent_pool, list) or not parent_pool:
        blockers.append("Master gate cannot pass without a parent pool.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_optimisation_selection_master_gate_complete": True,
        "phase_13k_selection_master_gate_complete": True,
        "regen_optimisation_selection_master_gate_passed": ready,
        "regen_optimisation_selection_master_gate_status": status,
        "regen_optimisation_selection_master_gate_blockers": blockers,

        "phase_13k_complete": ready,
        "phase_13k_status": (
            "PASS_REGEN_OPTIMISATION_SELECTION_FRAMEWORK_PHASE_13K"
            if ready
            else "FAIL_REGEN_OPTIMISATION_SELECTION_FRAMEWORK_PHASE_13K"
        ),

        "phase_13l_optimisation_foundation_allowed": ready,
        "regen_optimisation_foundation_phase_13l_allowed": ready,

        "regen_optimisation_runtime_execution_allowed": False,
        "regen_generation_advance_execution_allowed": False,
        "regen_evolution_engine_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }
