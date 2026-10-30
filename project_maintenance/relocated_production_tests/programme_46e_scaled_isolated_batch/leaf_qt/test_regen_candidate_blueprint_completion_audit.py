from project_maintenance.production_historical_artifacts.leaf_qt.regen_candidate_blueprint_generation_input_gate import attach_regen_candidate_blueprint_generation_input_gate
from regen_candidate_blueprint_session_owner import attach_regen_candidate_blueprint_session_owner
from regen_candidate_blueprint_registration_owner import attach_regen_candidate_blueprint_registration_owner
from regen_candidate_blueprint_report_owner import attach_regen_candidate_blueprint_report_owner
from regen_candidate_blueprint_completion_audit import (
    PASS_STATUS,
    attach_regen_candidate_blueprint_completion_audit,
)


def build_ready_12a4_results():
    results = {
        "phase_11g_complete": True,
        "regen_candidate_creation_architecture_complete": True,
        "phase_12a_candidate_blueprint_generation_allowed": True,
        "regen_candidate_blueprint_generation_allowed": True,

        "regen_candidate_creation_completion_audit": {"complete": True},
        "regen_candidate_creation_registry": {
            "candidate_creation_registry_id": "CANDIDATE_CREATION_REGISTRY_TEST"
        },
        "regen_candidate_creation_session": {
            "candidate_creation_session_id": "CANDIDATE_CREATION_SESSION_TEST"
        },

        "channel_geometry_valid": True,
        "coolant_channel_width_m": 0.0015,
        "coolant_channel_height_m": 0.002,
        "rib_width_m": 0.001,
        "channel_count": 80,

        "stage_u_regen_validation_complete": True,
        "regen_validation_status": "PASS_REGEN_VALIDATION",
        "regen_heat_flux": 5.0e6,
        "regen_pressure_drop": 150000.0,

        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_blueprint_create_blueprints_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }

    results = attach_regen_candidate_blueprint_generation_input_gate(results)
    results = attach_regen_candidate_blueprint_session_owner(results)
    results = attach_regen_candidate_blueprint_registration_owner(results)
    results = attach_regen_candidate_blueprint_report_owner(results)
    return results


def test_regen_candidate_blueprint_completion_audit():
    results = build_ready_12a4_results()
    results = attach_regen_candidate_blueprint_completion_audit(results)

    audit = results["regen_candidate_blueprint_completion_audit"]

    assert results["phase_12a_5_regen_candidate_blueprint_completion_audit_complete"] is True
    assert results["regen_candidate_blueprint_completion_audit_ready"] is True
    assert results["regen_candidate_blueprint_completion_audit_status"] == PASS_STATUS

    assert audit["owner"] == "REGEN_CANDIDATE_BLUEPRINT_COMPLETION_AUDIT"
    assert audit["phase"] == "12A.5"
    assert audit["complete"] is True
    assert audit["ready"] is True
    assert audit["blueprint_architecture_state"] == (
        "BLUEPRINT_OWNERSHIP_ARCHITECTURE_COMPLETE_GENERATION_LOCKED"
    )

    assert results["phase_12a_blueprint_ownership_architecture_complete"] is True
    assert results["regen_candidate_blueprint_ownership_architecture_complete"] is True
    assert results["phase_12b_1_candidate_blueprint_generation_engine_allowed"] is True
    assert results["regen_candidate_blueprint_generation_engine_allowed"] is True

    assert results["regen_candidate_blueprint_generation_execution_allowed"] is False
    assert results["regen_candidate_blueprint_create_blueprints_allowed"] is False
    assert results["regen_candidate_creation_create_candidates_allowed"] is False
    assert results["regen_candidate_generation_create_candidates_allowed"] is False
    assert results["regen_optimisation_runtime_execution_allowed"] is False
    assert results["regen_optimisation_generation_advance_allowed"] is False
    assert results["regen_optimisation_mutation_execution_allowed"] is False
    assert results["regen_optimisation_candidate_acceptance_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False


def test_regen_candidate_blueprint_completion_audit_blocks_without_12a4():
    results = attach_regen_candidate_blueprint_completion_audit({})

    assert results["phase_12a_5_regen_candidate_blueprint_completion_audit_complete"] is True
    assert results["regen_candidate_blueprint_completion_audit_ready"] is False
    assert results["phase_12a_blueprint_ownership_architecture_complete"] is False
    assert results["phase_12b_1_candidate_blueprint_generation_engine_allowed"] is False


if __name__ == "__main__":
    test_regen_candidate_blueprint_completion_audit()
    test_regen_candidate_blueprint_completion_audit_blocks_without_12a4()
    print("PASS_REGEN_CANDIDATE_BLUEPRINT_COMPLETION_AUDIT_PHASE_12A5")
