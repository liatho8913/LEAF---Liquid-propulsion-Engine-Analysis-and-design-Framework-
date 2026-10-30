from regen_autonomous_optimisation_input_audit import attach_regen_autonomous_optimisation_input_audit
from regen_optimisation_session_owner import attach_regen_optimisation_session_owner
from regen_optimisation_report_owner import attach_regen_optimisation_report_owner
from regen_optimisation_registration_owner import attach_regen_optimisation_registration_owner
from regen_optimisation_completion_audit import attach_regen_optimisation_completion_audit
from regen_runtime_optimisation_input_gate import attach_regen_runtime_optimisation_input_gate
from regen_runtime_optimisation_session_owner import attach_regen_runtime_optimisation_session_owner
from regen_runtime_optimisation_report_owner import attach_regen_runtime_optimisation_report_owner
from regen_runtime_optimisation_registration_owner import (
    PASS_STATUS,
    attach_regen_runtime_optimisation_registration_owner,
)


def test_regen_runtime_optimisation_registration_owner():
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

    registry = results["regen_runtime_optimisation_registry"]

    assert results["phase_11d_4_regen_runtime_optimisation_registration_owner_complete"] is True
    assert results["regen_runtime_optimisation_registration_owner_ready"] is True
    assert results["regen_runtime_optimisation_registration_owner_status"] == PASS_STATUS

    assert registry["runtime_registry_id"] == "RUNTIME_OPT_REGISTRY_0001"
    assert registry["runtime_session_registry"]["runtime_session_count"] == 1
    assert registry["runtime_report_registry"]["runtime_report_count"] == 5
    assert registry["runtime_state_registry"]["registered"] is True
    assert registry["runtime_candidate_registry"]["runtime_candidate_count"] == 0
    assert registry["runtime_generation_registry"]["runtime_generation_count"] == 0

    assert registry["runtime_execution_enabled"] is False
    assert registry["live_geometry_commit_enabled"] is False

    assert results["phase_11d_5_runtime_completion_audit_allowed"] is True
    assert results["regen_optimisation_runtime_execution_allowed"] is False


if __name__ == "__main__":
    test_regen_runtime_optimisation_registration_owner()
    print("PASS_REGEN_RUNTIME_OPTIMISATION_REGISTRATION_OWNER_PHASE_11D4")
