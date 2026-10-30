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
from regen_candidate_creation_completion_audit import attach_regen_candidate_creation_completion_audit

from project_maintenance.production_historical_artifacts.leaf_qt.regen_candidate_blueprint_generation_input_gate import attach_regen_candidate_blueprint_generation_input_gate
from regen_candidate_blueprint_session_owner import (
    PASS_STATUS,
    attach_regen_candidate_blueprint_session_owner,
)


def build_ready_12a1_results():
    results = {
        "phase_11b_6f_regen_evolution_loop_master_gate_complete": True,
        "regen_evolution_loop_master_gate_ready": True,

        "channel_geometry_valid": True,
        "coolant_channel_width_m": 0.0015,
        "coolant_channel_height_m": 0.002,
        "rib_width_m": 0.001,
        "channel_count": 80,

        "stage_u_regen_validation_complete": True,
        "regen_validation_status": "PASS_REGEN_VALIDATION",
        "regen_heat_flux": 5.0e6,
        "regen_pressure_drop": 150000.0,
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

    results = attach_regen_candidate_blueprint_generation_input_gate(results)

    return results


def test_regen_candidate_blueprint_session_owner():
    results = build_ready_12a1_results()
    results = attach_regen_candidate_blueprint_session_owner(results)

    session = results["regen_candidate_blueprint_session"]

    assert results["phase_12a_2_regen_candidate_blueprint_session_owner_complete"] is True
    assert results["regen_candidate_blueprint_session_owner_ready"] is True
    assert results["regen_candidate_blueprint_session_owner_status"] == PASS_STATUS

    assert session["owner"] == "REGEN_CANDIDATE_BLUEPRINT_SESSION_OWNER"
    assert session["phase"] == "12A.2"
    assert session["ready"] is True
    assert session["candidate_blueprint_session_id"]
    assert session["lifecycle_state"] == "BLUEPRINT_SESSION_CREATED_BLUEPRINT_CREATION_LOCKED"

    assert results["phase_12a_3_candidate_blueprint_registration_owner_allowed"] is True
    assert results["regen_candidate_blueprint_registration_owner_allowed"] is True

    assert results["regen_candidate_blueprint_generation_execution_allowed"] is False
    assert results["regen_candidate_blueprint_create_blueprints_allowed"] is False
    assert results["regen_candidate_creation_create_candidates_allowed"] is False
    assert results["regen_optimisation_runtime_execution_allowed"] is False
    assert results["regen_optimisation_generation_advance_allowed"] is False
    assert results["regen_optimisation_mutation_execution_allowed"] is False
    assert results["regen_optimisation_candidate_acceptance_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False


def test_regen_candidate_blueprint_session_owner_blocks_without_12a1():
    results = attach_regen_candidate_blueprint_session_owner({})

    assert results["phase_12a_2_regen_candidate_blueprint_session_owner_complete"] is True
    assert results["regen_candidate_blueprint_session_owner_ready"] is False
    assert results["regen_candidate_blueprint_session"] is None
    assert results["phase_12a_3_candidate_blueprint_registration_owner_allowed"] is False


if __name__ == "__main__":
    test_regen_candidate_blueprint_session_owner()
    test_regen_candidate_blueprint_session_owner_blocks_without_12a1()
    print("PASS_REGEN_CANDIDATE_BLUEPRINT_SESSION_OWNER_PHASE_12A2")
