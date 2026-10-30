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
from regen_candidate_creation_registration_owner import attach_regen_candidate_creation_registration_owner
from regen_candidate_creation_completion_audit import (
    PASS_STATUS,
    attach_regen_candidate_creation_completion_audit,
)


def test_regen_candidate_creation_completion_audit():
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
    results = attach_regen_candidate_creation_completion_audit(results)

    assert results["phase_11g_5_regen_candidate_creation_completion_audit_complete"] is True
    assert results["regen_candidate_creation_completion_audit_ready"] is True
    assert results["regen_candidate_creation_completion_audit_status"] == PASS_STATUS

    assert results["phase_11g_complete"] is True
    assert results["regen_candidate_creation_architecture_complete"] is True
    assert results["phase_12a_candidate_blueprint_generation_allowed"] is True
    assert results["regen_candidate_blueprint_generation_allowed"] is True

    assert results["regen_candidate_creation_create_candidates_allowed"] is False
    assert results["regen_candidate_blueprint_create_blueprints_allowed"] is False
    assert results["regen_optimisation_mutation_execution_allowed"] is False
    assert results["regen_optimisation_candidate_acceptance_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False


if __name__ == "__main__":
    test_regen_candidate_creation_completion_audit()
    print("PASS_REGEN_CANDIDATE_CREATION_COMPLETION_AUDIT_PHASE_11G5")
