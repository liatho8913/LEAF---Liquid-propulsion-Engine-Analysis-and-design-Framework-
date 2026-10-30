from regen_autonomous_optimisation_input_audit import (
    attach_regen_autonomous_optimisation_input_audit,
)
from regen_optimisation_session_owner import (
    PASS_STATUS,
    attach_regen_optimisation_session_owner,
)


def test_regen_optimisation_session_owner():
    results = {
        "phase_11b_6f_regen_evolution_loop_master_gate_complete": True,
        "regen_evolution_loop_master_gate_ready": True,
    }

    results = attach_regen_autonomous_optimisation_input_audit(results)
    results = attach_regen_optimisation_session_owner(results)

    session = results["regen_optimisation_session"]

    assert results["phase_11c_2_regen_optimisation_session_owner_complete"] is True
    assert results["regen_optimisation_session_owner_ready"] is True
    assert results["regen_optimisation_session_owner_status"] == PASS_STATUS
    assert session["session_id"] == "OPT_SESSION_0001"
    assert session["generation_count"] == 0
    assert session["best_candidate_id"] is None
    assert session["runtime_execution_enabled"] is False
    assert session["live_geometry_commit_enabled"] is False
    assert results["phase_11c_3_optimisation_report_owner_allowed"] is True
    assert results["regen_optimisation_runtime_execution_allowed"] is False


if __name__ == "__main__":
    test_regen_optimisation_session_owner()
    print("PASS_REGEN_OPTIMISATION_SESSION_OWNER_PHASE_11C2")
