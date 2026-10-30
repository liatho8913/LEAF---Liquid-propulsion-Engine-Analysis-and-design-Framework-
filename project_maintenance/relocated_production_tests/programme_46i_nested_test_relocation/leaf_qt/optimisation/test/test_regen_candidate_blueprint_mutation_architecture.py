from project_maintenance.production_historical_artifacts.leaf_qt.regen_candidate_blueprint_generation_input_gate import attach_regen_candidate_blueprint_generation_input_gate
from regen_candidate_blueprint_session_owner import attach_regen_candidate_blueprint_session_owner
from regen_candidate_blueprint_registration_owner import attach_regen_candidate_blueprint_registration_owner
from regen_candidate_blueprint_report_owner import attach_regen_candidate_blueprint_report_owner
from regen_candidate_blueprint_completion_audit import attach_regen_candidate_blueprint_completion_audit
from regen_candidate_blueprint_generation_engine import attach_regen_candidate_blueprint_generation_engine
from regen_candidate_blueprint_geometry_builder import attach_regen_candidate_blueprint_geometry_builder
from regen_candidate_blueprint_thermal_builder import attach_regen_candidate_blueprint_thermal_builder
from regen_candidate_blueprint_validation_builder import attach_regen_candidate_blueprint_validation_builder
from regen_candidate_blueprint_engineering_completion_audit import attach_regen_candidate_blueprint_engineering_completion_audit
from regen_candidate_blueprint_population_builder import attach_regen_candidate_blueprint_population_builder
from regen_candidate_blueprint_population_registration_owner import attach_regen_candidate_blueprint_population_registration_owner
from regen_candidate_blueprint_population_validation_owner import attach_regen_candidate_blueprint_population_validation_owner
from regen_candidate_blueprint_population_completion_audit import attach_regen_candidate_blueprint_population_completion_audit
from regen_candidate_blueprint_mutation_architecture import (
    PASS_STATUS,
    attach_regen_candidate_blueprint_mutation_architecture,
)


def build_ready_12c4_results():
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
        "regen_candidate_blueprint_mutation_execution_allowed": False,
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
    results = attach_regen_candidate_blueprint_generation_engine(results)
    results = attach_regen_candidate_blueprint_geometry_builder(results)
    results = attach_regen_candidate_blueprint_thermal_builder(results)
    results = attach_regen_candidate_blueprint_validation_builder(results)
    results = attach_regen_candidate_blueprint_engineering_completion_audit(results)
    results = attach_regen_candidate_blueprint_population_builder(results)
    results = attach_regen_candidate_blueprint_population_registration_owner(results)
    results = attach_regen_candidate_blueprint_population_validation_owner(results)
    results = attach_regen_candidate_blueprint_population_completion_audit(results)
    return results


def test_regen_candidate_blueprint_mutation_architecture():
    results = build_ready_12c4_results()
    results = attach_regen_candidate_blueprint_mutation_architecture(results)

    architecture = results["regen_candidate_blueprint_mutation_architecture"]
    session = results["regen_candidate_blueprint_mutation_session"]
    registry = results["regen_candidate_blueprint_mutation_registry"]

    assert results["phase_12d_1_regen_candidate_blueprint_mutation_architecture_complete"] is True
    assert results["regen_candidate_blueprint_mutation_architecture_ready"] is True
    assert results["regen_candidate_blueprint_mutation_architecture_status"] == PASS_STATUS

    assert architecture["owner"] == "REGEN_CANDIDATE_BLUEPRINT_MUTATION_ARCHITECTURE"
    assert architecture["phase"] == "12D.1"
    assert architecture["architecture_state"] == "MUTATION_ARCHITECTURE_CREATED_EXECUTION_LOCKED"

    assert session["mutation_session_id"]
    assert session["mutation_execution_allowed"] is False
    assert session["lifecycle_state"] == "MUTATION_SESSION_CREATED_EXECUTION_LOCKED"

    assert registry["mutation_registry_id"]
    assert "coolant_channel_width" in registry["registered_mutation_scopes"]
    assert "bounded_float_step" in registry["registered_mutation_modes"]

    assert registry["permissions"]["mutation_validation_allowed"] is True
    assert registry["permissions"]["mutation_execution_allowed"] is False
    assert registry["permissions"]["solver_execution_allowed"] is False
    assert registry["permissions"]["candidate_acceptance_allowed"] is False
    assert registry["permissions"]["live_geometry_commit_allowed"] is False

    assert results["phase_12d_2_candidate_blueprint_mutation_validation_allowed"] is True
    assert results["regen_candidate_blueprint_mutation_validation_allowed"] is True

    assert results["regen_candidate_blueprint_mutation_execution_allowed"] is False
    assert results["regen_optimisation_mutation_execution_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False


def test_regen_candidate_blueprint_mutation_architecture_blocks_without_12c4():
    results = attach_regen_candidate_blueprint_mutation_architecture({})

    assert results["phase_12d_1_regen_candidate_blueprint_mutation_architecture_complete"] is True
    assert results["regen_candidate_blueprint_mutation_architecture_ready"] is False
    assert results["regen_candidate_blueprint_mutation_architecture"] is None
    assert results["phase_12d_2_candidate_blueprint_mutation_validation_allowed"] is False


if __name__ == "__main__":
    test_regen_candidate_blueprint_mutation_architecture()
    test_regen_candidate_blueprint_mutation_architecture_blocks_without_12c4()
    print("PASS_REGEN_CANDIDATE_BLUEPRINT_MUTATION_ARCHITECTURE_PHASE_12D1")
