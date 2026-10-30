from regen_objective_decision_master_gate import (
    attach_regen_objective_decision_master_gate,
)


def build_complete_results():
    return {
        "phase_11b_2o_regen_automatic_geometry_objective_selector_complete": True,
        "phase_11b_2p_regen_objective_weight_owner_complete": True,
        "phase_11b_2n_regen_automatic_geometry_decision_owner_complete": True,
        "phase_11b_2q_regen_objective_decision_report_owner_complete": True,
        "phase_11b_2r_regen_objective_decision_report_registration_owner_complete": True,
        "phase_11b_2s_regen_objective_decision_completion_audit_complete": True,
        "regen_objective_decision_stack_complete": True,
        "regen_objective_decision_completion_audit_ready": True,

        "regen_objective_decision_completion_audit_solver_executed": False,
        "regen_objective_decision_completion_audit_live_geometry_modified": False,
        "regen_objective_decision_completion_audit_candidate_committed": False,
    }


def test_objective_decision_master_gate_passes_complete_stack():
    results = attach_regen_objective_decision_master_gate(
        build_complete_results()
    )

    assert results["phase_11b_2t_regen_objective_decision_master_gate_complete"] is True
    assert results["regen_objective_decision_master_gate_ready"] is True
    assert results["regen_objective_decision_architecture_complete"] is True
    assert results["regen_objective_decision_master_gate_status"] == (
        "PASS_REGEN_OBJECTIVE_DECISION_MASTER_GATE_READY"
    )

    assert results["regen_objective_decision_master_gate_solver_executed"] is False
    assert results["regen_objective_decision_master_gate_live_geometry_modified"] is False
    assert results["regen_objective_decision_master_gate_candidate_committed"] is False


def test_objective_decision_master_gate_blocks_missing_layer():
    results = build_complete_results()
    results["phase_11b_2q_regen_objective_decision_report_owner_complete"] = False

    results = attach_regen_objective_decision_master_gate(results)

    assert results["regen_objective_decision_master_gate_ready"] is False
    assert results["regen_objective_decision_architecture_complete"] is False
    assert results["regen_objective_decision_master_gate_missing"]


def test_objective_decision_master_gate_blocks_safety_violation():
    results = build_complete_results()
    results["regen_objective_decision_completion_audit_live_geometry_modified"] = True

    results = attach_regen_objective_decision_master_gate(results)

    assert results["regen_objective_decision_master_gate_ready"] is False
    assert results["regen_objective_decision_master_gate_safety_violations"]


if __name__ == "__main__":
    test_objective_decision_master_gate_passes_complete_stack()
    test_objective_decision_master_gate_blocks_missing_layer()
    test_objective_decision_master_gate_blocks_safety_violation()
    print("PASS_REGEN_OBJECTIVE_DECISION_MASTER_GATE_PHASE_11B2T")