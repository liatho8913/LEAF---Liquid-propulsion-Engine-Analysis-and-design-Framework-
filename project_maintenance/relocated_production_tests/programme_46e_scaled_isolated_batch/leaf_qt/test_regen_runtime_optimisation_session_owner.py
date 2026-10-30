from regen_autonomous_optimisation_input_audit import attach_regen_autonomous_optimisation_input_audit
from regen_optimisation_session_owner import attach_regen_optimisation_session_owner
from regen_optimisation_report_owner import attach_regen_optimisation_report_owner
from regen_optimisation_registration_owner import attach_regen_optimisation_registration_owner
from regen_optimisation_completion_audit import attach_regen_optimisation_completion_audit
from regen_runtime_optimisation_input_gate import attach_regen_runtime_optimisation_input_gate
from regen_runtime_optimisation_session_owner import (
    PASS_STATUS,
    attach_regen_runtime_optimisation_session_owner,
)


def test_regen_runtime_optimisation_session_owner():
    results = {
        "phase_11b_6f_regen_evolution_loop_master_gate_complete": True,
        "regen_evolution_loop_master_gate_ready": True,
    }

    results = attach_regen_autonomous_optimisation_input_audit(results)
    results = attach_regen_optimisation_session_owner(results)
    results = attach_regen_optimisation_report_owner(results)
    results = attach_regen_optimisation_registration_owner(results)
    results = attach_regen_optimisation_completion_audit(results)
    results = attach_regen_runtime_optimisation_input_gate(results)
    results = attach_regen_runtime_optimisation_session_owner(results)

    runtime_session = results["regen_runtime_optimisation_session"]

    assert results["phase_11d_2_regen_runtime_optimisation_session_owner_complete"] is True
    assert results["regen_runtime_optimisation_session_owner_ready"] is True
    assert results["regen_runtime_optimisation_session_owner_status"] == PASS_STATUS
    assert runtime_session["runtime_session_id"] == "OPT_SESSION_0001_RUNTIME"
    assert runtime_session["current_generation_index"] == 0
    assert runtime_session["execution_state"] == "READY_RUNTIME_EXECUTION_LOCKED"
    assert runtime_session["runtime_execution_enabled"] is False
    assert runtime_session["solver_execution_enabled"] is False
    assert runtime_session["live_geometry_commit_enabled"] is False
    assert results["phase_11d_3_runtime_report_owner_allowed"] is True
    assert results["regen_optimisation_runtime_execution_allowed"] is False


if __name__ == "__main__":
    test_regen_runtime_optimisation_session_owner()
    print("PASS_REGEN_RUNTIME_OPTIMISATION_SESSION_OWNER_PHASE_11D2")
