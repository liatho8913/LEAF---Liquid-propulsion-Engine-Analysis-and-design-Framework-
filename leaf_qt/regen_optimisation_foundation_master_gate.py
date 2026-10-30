OWNER_NAME = "REGEN_OPTIMISATION_FOUNDATION_MASTER_GATE"
PHASE = "13L"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_FOUNDATION_MASTER_GATE_PHASE_13L"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_FOUNDATION_MASTER_GATE_PHASE_13L"


def attach_regen_optimisation_foundation_master_gate(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_foundation_master_gate(results)
    results.update(payload)
    return results


def build_regen_optimisation_foundation_master_gate(results):
    blockers = []

    completion_ready = results.get("regen_optimisation_foundation_completion_audit_ready") is True
    completion_status = results.get("regen_optimisation_foundation_completion_audit_status")

    if not completion_ready:
        blockers.append("13L optimisation foundation completion audit is not ready.")

    if completion_status != "PASS_REGEN_OPTIMISATION_FOUNDATION_PHASE_13L":
        blockers.append("13L optimisation foundation completion audit has not passed.")

    if results.get("phase_14a_runtime_mutation_execution_allowed") is not True:
        blockers.append("Phase 14A runtime mutation execution has not been unlocked.")

    runtime_still_locked = results.get("phase_14_runtime_optimisation_allowed") is False

    if not runtime_still_locked:
        blockers.append("Full Phase 14 runtime optimisation must remain locked after 13L.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_optimisation_foundation_master_gate_complete": True,
        "phase_13l_optimisation_foundation_master_gate_complete": True,
        "regen_optimisation_foundation_master_gate_passed": ready,
        "regen_optimisation_foundation_master_gate_status": status,
        "regen_optimisation_foundation_master_gate_blockers": blockers,

        "phase_13l_complete": ready,
        "phase_13l_status": (
            "PASS_REGEN_OPTIMISATION_FOUNDATION_PHASE_13L"
            if ready
            else "FAIL_REGEN_OPTIMISATION_FOUNDATION_PHASE_13L"
        ),

        "optimisation_foundation_complete": ready,
        "regen_optimisation_foundation_complete": ready,

        "phase_14a_runtime_mutation_execution_allowed": ready,
        "phase_14_runtime_optimisation_allowed": False,

        "regen_optimisation_runtime_execution_allowed": False,
        "regen_generation_advance_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }
