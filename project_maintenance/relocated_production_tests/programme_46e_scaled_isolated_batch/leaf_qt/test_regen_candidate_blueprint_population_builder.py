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
from regen_candidate_blueprint_population_builder import (
    PASS_STATUS,
    attach_regen_candidate_blueprint_population_builder,
)


def build_ready_12b5_results():
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
    results = attach_regen_candidate_blueprint_generation_engine(results)
    results = attach_regen_candidate_blueprint_geometry_builder(results)
    results = attach_regen_candidate_blueprint_thermal_builder(results)
    results = attach_regen_candidate_blueprint_validation_builder(results)
    results = attach_regen_candidate_blueprint_engineering_completion_audit(results)
    return results


def test_regen_candidate_blueprint_population_builder():
    results = build_ready_12b5_results()
    results = attach_regen_candidate_blueprint_population_builder(results)

    population = results["regen_candidate_blueprint_population"]

    assert results["phase_12c_1_regen_candidate_blueprint_population_builder_complete"] is True
    assert results["regen_candidate_blueprint_population_builder_ready"] is True
    assert results["regen_candidate_blueprint_population_builder_status"] == PASS_STATUS

    assert population["owner"] == "REGEN_CANDIDATE_BLUEPRINT_POPULATION_BUILDER"
    assert population["phase"] == "12C.1"
    assert population["ready"] is True
    assert population["member_count"] == 4
    assert len(population["members"]) == 4
    assert len(population["member_ids"]) == 4

    assert population["population_lifecycle_state"] == "BLUEPRINT_POPULATION_CREATED_EXECUTION_LOCKED"
    assert population["population_readiness"]["ready_for_population_registration"] is True
    assert population["population_readiness"]["ready_for_mutation"] is False
    assert population["population_readiness"]["ready_for_solver_execution"] is False
    assert population["population_readiness"]["ready_for_live_commit"] is False

    assert population["population_provenance"]["mutation_executed"] is False
    assert population["population_provenance"]["scoring_executed"] is False
    assert population["population_provenance"]["solver_executed"] is False
    assert population["population_provenance"]["candidate_acceptance_executed"] is False
    assert population["population_provenance"]["live_geometry_modified"] is False

    assert results["regen_candidate_blueprint_population_member_count"] == 4
    assert len(results["regen_candidate_blueprint_population_member_ids"]) == 4

    assert results["phase_12c_2_candidate_blueprint_population_registration_allowed"] is True
    assert results["regen_candidate_blueprint_population_registration_allowed"] is True

    assert results["regen_candidate_blueprint_generation_execution_allowed"] is False
    assert results["regen_candidate_blueprint_create_blueprints_allowed"] is False
    assert results["regen_candidate_creation_create_candidates_allowed"] is False
    assert results["regen_candidate_generation_create_candidates_allowed"] is False
    assert results["regen_optimisation_runtime_execution_allowed"] is False
    assert results["regen_optimisation_generation_advance_allowed"] is False
    assert results["regen_optimisation_mutation_execution_allowed"] is False
    assert results["regen_optimisation_candidate_acceptance_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False


def test_regen_candidate_blueprint_population_builder_blocks_without_12b5():
    results = attach_regen_candidate_blueprint_population_builder({})

    assert results["phase_12c_1_regen_candidate_blueprint_population_builder_complete"] is True
    assert results["regen_candidate_blueprint_population_builder_ready"] is False
    assert results["regen_candidate_blueprint_population"] is None
    assert results["regen_candidate_blueprint_population_member_count"] == 0
    assert results["phase_12c_2_candidate_blueprint_population_registration_allowed"] is False


if __name__ == "__main__":
    test_regen_candidate_blueprint_population_builder()
    test_regen_candidate_blueprint_population_builder_blocks_without_12b5()
    print("PASS_REGEN_CANDIDATE_BLUEPRINT_POPULATION_BUILDER_PHASE_12C1")
