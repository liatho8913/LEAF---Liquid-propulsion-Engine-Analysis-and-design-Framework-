from regen_autonomous_optimisation_input_audit import (
    PASS_STATUS,
    attach_regen_autonomous_optimisation_input_audit,
)


def test_regen_autonomous_optimisation_input_audit():
    results = {
        "phase_11b_6f_regen_evolution_loop_master_gate_complete": True,
        "regen_evolution_loop_master_gate_ready": True,
    }

    results = attach_regen_autonomous_optimisation_input_audit(results)

    assert results["phase_11c_1_regen_autonomous_optimisation_input_audit_complete"] is True
    assert results["regen_autonomous_optimisation_input_audit_ready"] is True
    assert results["regen_autonomous_optimisation_input_audit_status"] == PASS_STATUS
    assert results["phase_11c_2_optimisation_session_owner_allowed"] is True
    assert results["regen_autonomous_optimisation_runtime_allowed"] is False
    assert results["regen_autonomous_optimisation_live_commit_allowed"] is False


if __name__ == "__main__":
    test_regen_autonomous_optimisation_input_audit()
    print("PASS_REGEN_AUTONOMOUS_OPTIMISATION_INPUT_AUDIT_PHASE_11C1")
