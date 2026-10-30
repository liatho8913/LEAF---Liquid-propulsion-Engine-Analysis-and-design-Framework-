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
from regen_runtime_execution_session_owner import attach_regen_runtime_execution_session_owner
from regen_runtime_execution_report_owner import (
    PASS_STATUS,
    attach_regen_runtime_execution_report_owner,
)


def test_regen_runtime_execution_report_owner():
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
    results = attach_regen_runtime_execution_report_owner(results)

    bundle = results["regen_runtime_execution_report_bundle"]

    assert results["phase_11e_3_regen_runtime_execution_report_owner_complete"] is True
    assert results["regen_runtime_execution_report_owner_ready"] is True
    assert results["regen_runtime_execution_report_owner_status"] == PASS_STATUS
    assert bundle["execution_session_id"] == "OPT_SESSION_0001_RUNTIME_EXECUTION"
    assert bool(bundle["execution_session_report"]) is True
    assert bool(bundle["execution_lifecycle_report"]) is True
    assert bool(bundle["execution_progress_report"]) is True
    assert bool(bundle["execution_safety_report"]) is True
    assert bool(bundle["execution_lock_report"]) is True
    assert bundle["candidate_generation_enabled"] is False
    assert bundle["mutation_execution_enabled"] is False
    assert bundle["live_geometry_commit_enabled"] is False
    assert results["phase_11e_4_runtime_execution_registration_owner_allowed"] is True
    assert results["regen_optimisation_runtime_execution_allowed"] is False


if __name__ == "__main__":
    test_regen_runtime_execution_report_owner()
    print("PASS_REGEN_RUNTIME_EXECUTION_REPORT_OWNER_PHASE_11E3")
