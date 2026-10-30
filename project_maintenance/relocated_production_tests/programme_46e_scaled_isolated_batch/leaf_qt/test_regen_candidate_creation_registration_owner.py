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
from regen_runtime_execution_report_owner import attach_regen_runtime_execution_report_owner
from regen_runtime_execution_registration_owner import attach_regen_runtime_execution_registration_owner
from regen_runtime_execution_completion_audit import attach_regen_runtime_execution_completion_audit
from regen_candidate_generation_input_gate import attach_regen_candidate_generation_input_gate
from regen_candidate_generation_session_owner import attach_regen_candidate_generation_session_owner
from regen_candidate_generation_report_owner import attach_regen_candidate_generation_report_owner
from regen_candidate_generation_registration_owner import attach_regen_candidate_generation_registration_owner
from regen_candidate_generation_completion_audit import attach_regen_candidate_generation_completion_audit
from regen_candidate_creation_input_audit import attach_regen_candidate_creation_input_audit
from regen_candidate_creation_session_owner import attach_regen_candidate_creation_session_owner
from regen_candidate_creation_report_owner import attach_regen_candidate_creation_report_owner
from regen_candidate_creation_registration_owner import (
    PASS_STATUS,
    attach_regen_candidate_creation_registration_owner,
)


def test_regen_candidate_creation_registration_owner():
    results = {
        "phase_11b_6f_regen_evolution_loop_master_gate_complete": True,
        "regen_evolution_loop_master_gate_ready": True,
        "channel_geometry_valid": True,
        "stage_u_regen_validation_complete": True,
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
    results = attach_regen_runtime_execution_registration_owner(results)
    results = attach_regen_runtime_execution_completion_audit(results)
    results = attach_regen_candidate_generation_input_gate(results)
    results = attach_regen_candidate_generation_session_owner(results)
    results = attach_regen_candidate_generation_report_owner(results)
    results = attach_regen_candidate_generation_registration_owner(results)
    results = attach_regen_candidate_generation_completion_audit(results)
    results = attach_regen_candidate_creation_input_audit(results)
    results = attach_regen_candidate_creation_session_owner(results)
    results = attach_regen_candidate_creation_report_owner(results)
    results = attach_regen_candidate_creation_registration_owner(results)

    registry = results["regen_candidate_creation_registry"]

    assert results["phase_11g_4_regen_candidate_creation_registration_owner_complete"] is True
    assert results["regen_candidate_creation_registration_owner_ready"] is True
    assert results["regen_candidate_creation_registration_owner_status"] == PASS_STATUS

    assert registry["candidate_creation_registry_id"] == "CANDIDATE_CREATION_REGISTRY_0001"
    assert registry["creation_session_registry"]["creation_session_count"] == 1
    assert registry["creation_report_registry"]["creation_report_count"] == 5
    assert registry["creation_state_registry"]["registered"] is True
    assert registry["creation_capability_registry"]["registered"] is True

    assert registry["candidate_creation_enabled"] is False
    assert registry["candidate_blueprint_creation_enabled"] is False
    assert registry["mutation_execution_enabled"] is False
    assert registry["solver_execution_enabled"] is False
    assert registry["live_geometry_commit_enabled"] is False

    assert results["phase_11g_5_candidate_creation_completion_audit_allowed"] is True
    assert results["regen_candidate_creation_create_candidates_allowed"] is False


if __name__ == "__main__":
    test_regen_candidate_creation_registration_owner()
    print("PASS_REGEN_CANDIDATE_CREATION_REGISTRATION_OWNER_PHASE_11G4")
