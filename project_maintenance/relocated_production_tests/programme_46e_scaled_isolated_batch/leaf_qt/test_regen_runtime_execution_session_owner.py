from regen_autonomous_optimisation_input_audit import attach_regen_autonomous_optimisation_input_audit
from regen_optimisation_session_owner import attach_regen_optimisation_session_owner
from regen_optimisation_report_owner import attach_regen_optimisation_report_owner
from regen_optimisation_registration_owner import attach_regen_optimisation_registration_owner
from regen_optimisation_completion_audit import attach_regen_optimisation_completion_audit
from regen_runtime_optimisation_input_gate import attach_regen_runtime_optimisation_input_gate
from regen_runtime_optimisation_session_owner import attach_regen_runtime_optimisation_session_owner
from regen_runtime_optimisation_report_owner import attach_regen_runtime_optimisation_report_owner
from regen_runtime_optimisation_registration_owner import attach_regen_runtime_optimisation_registration_owner
from regen_runtime_optimisation_completion_audit import attach_regen_runtime_optimisation_completion_audit
from regen_runtime_execution_input_gate import attach_regen_runtime_execution_input_gate
from regen_runtime_execution_session_owner import (
    PASS_STATUS,
    attach_regen_runtime_execution_session_owner,
)


def test_regen_runtime_execution_session_owner():
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
    results = attach_regen_runtime_optimisation_report_owner(results)
    results = attach_regen_runtime_optimisation_registration_owner(results)
    results = attach_regen_runtime_optimisation_completion_audit(results)
    results = attach_regen_runtime_execution_input_gate(results)
    results = attach_regen_runtime_execution_session_owner(results)

    session = results["regen_runtime_execution_session"]

    assert results["phase_11e_2_regen_runtime_execution_session_owner_complete"] is True
    assert results["regen_runtime_execution_session_owner_ready"] is True
    assert results["regen_runtime_execution_session_owner_status"] == PASS_STATUS
    assert session["execution_session_id"] == "OPT_SESSION_0001_RUNTIME_EXECUTION"
    assert session["execution_state"] == "PREPARED_EXECUTION_LOCKED"
    assert session["lifecycle_state"] == "NOT_STARTED"
    assert session["execution_progress_fraction"] == 0.0
    assert session["candidate_generation_enabled"] is False
    assert session["mutation_execution_enabled"] is False
    assert session["live_geometry_commit_enabled"] is False
    assert results["phase_11e_3_runtime_execution_report_owner_allowed"] is True
    assert results["regen_optimisation_runtime_execution_allowed"] is False


if __name__ == "__main__":
    test_regen_runtime_execution_session_owner()
    print("PASS_REGEN_RUNTIME_EXECUTION_SESSION_OWNER_PHASE_11E2")
