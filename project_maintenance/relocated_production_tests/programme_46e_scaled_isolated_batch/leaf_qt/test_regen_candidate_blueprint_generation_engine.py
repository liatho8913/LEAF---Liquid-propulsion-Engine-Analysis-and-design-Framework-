from project_maintenance.production_historical_artifacts.leaf_qt.regen_candidate_blueprint_generation_input_gate import attach_regen_candidate_blueprint_generation_input_gate
from regen_candidate_blueprint_session_owner import attach_regen_candidate_blueprint_session_owner
from regen_candidate_blueprint_registration_owner import attach_regen_candidate_blueprint_registration_owner
from regen_candidate_blueprint_report_owner import attach_regen_candidate_blueprint_report_owner
from regen_candidate_blueprint_completion_audit import attach_regen_candidate_blueprint_completion_audit
from regen_candidate_blueprint_generation_engine import (
    PASS_STATUS,
    attach_regen_candidate_blueprint_generation_engine,
)


def build_ready_12a5_results():
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
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.002,
        "rib_width": 0.001,
        "hot_gas_wall_thickness": 0.0012,
        "coolant_flow_fraction": 1.0,

        "stage_u_regen_validation_complete": True,
        "regen_validation_status": "PASS_REGEN_VALIDATION",
        "regen_heat_flux": 5.0e6,
        "regen_pressure_drop": 150000.0,

        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_blueprint_create_blueprints_allowed": False,
        "regen_candidate_blueprint_generation_execution_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
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
    results = attach_regen_candidate_blueprint_completion_audit(results)
    return results


def test_regen_candidate_blueprint_generation_engine():
    results = build_ready_12a5_results()
    results = attach_regen_candidate_blueprint_generation_engine(results)

    blueprints = results["regen_candidate_blueprints"]

    assert results["phase_12b_1_regen_candidate_blueprint_generation_engine_complete"] is True
    assert results["regen_candidate_blueprint_generation_engine_ready"] is True
    assert results["regen_candidate_blueprint_generation_engine_status"] == PASS_STATUS

    assert results["regen_candidate_blueprint_count"] == 4
    assert len(blueprints) == 4
    assert len(results["regen_candidate_blueprint_ids"]) == 4

    first = blueprints[0]
    assert first["blueprint_owner"] == "REGEN_CANDIDATE_BLUEPRINT_GENERATION_ENGINE"
    assert first["blueprint_phase"] == "12B.1"
    assert first["blueprint_status"] == "CREATED_NOT_SOLVED"
    assert first["blueprint_lifecycle_state"] == "BLUEPRINT_OBJECT_CREATED_EXECUTION_LOCKED"

    assert first["geometry_record"]["number_of_coolant_channels"] == 80
    assert first["geometry_record"]["coolant_channel_width"] == 0.0015
    assert first["thermal_record"]["solver_executed"] is False
    assert first["validation_record"]["validated"] is False
    assert first["metadata_record"]["live_geometry_commit_allowed"] is False

    assert results["phase_12b_2_candidate_blueprint_geometry_builder_allowed"] is True
    assert results["regen_candidate_blueprint_geometry_builder_allowed"] is True

    assert results["regen_candidate_blueprint_generation_execution_allowed"] is False
    assert results["regen_candidate_blueprint_create_blueprints_allowed"] is False
    assert results["regen_candidate_creation_create_candidates_allowed"] is False
    assert results["regen_candidate_generation_create_candidates_allowed"] is False
    assert results["regen_optimisation_runtime_execution_allowed"] is False
    assert results["regen_optimisation_generation_advance_allowed"] is False
    assert results["regen_optimisation_mutation_execution_allowed"] is False
    assert results["regen_optimisation_candidate_acceptance_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False


def test_regen_candidate_blueprint_generation_engine_blocks_without_12a5():
    results = attach_regen_candidate_blueprint_generation_engine({})

    assert results["phase_12b_1_regen_candidate_blueprint_generation_engine_complete"] is True
    assert results["regen_candidate_blueprint_generation_engine_ready"] is False
    assert results["regen_candidate_blueprint_count"] == 0
    assert results["phase_12b_2_candidate_blueprint_geometry_builder_allowed"] is False


if __name__ == "__main__":
    test_regen_candidate_blueprint_generation_engine()
    test_regen_candidate_blueprint_generation_engine_blocks_without_12a5()
    print("PASS_REGEN_CANDIDATE_BLUEPRINT_GENERATION_ENGINE_PHASE_12B1")
