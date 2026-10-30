from project_maintenance.production_historical_artifacts.leaf_qt.regen_candidate_blueprint_generation_input_gate import attach_regen_candidate_blueprint_generation_input_gate
from regen_candidate_blueprint_session_owner import attach_regen_candidate_blueprint_session_owner
from regen_candidate_blueprint_registration_owner import attach_regen_candidate_blueprint_registration_owner
from regen_candidate_blueprint_report_owner import attach_regen_candidate_blueprint_report_owner
from regen_candidate_blueprint_completion_audit import attach_regen_candidate_blueprint_completion_audit
from regen_candidate_blueprint_generation_engine import attach_regen_candidate_blueprint_generation_engine
from regen_candidate_blueprint_geometry_builder import attach_regen_candidate_blueprint_geometry_builder
from regen_candidate_blueprint_thermal_builder import (
    PASS_STATUS,
    attach_regen_candidate_blueprint_thermal_builder,
)


def build_ready_12b2_results():
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
    return results


def test_regen_candidate_blueprint_thermal_builder():
    results = build_ready_12b2_results()
    results = attach_regen_candidate_blueprint_thermal_builder(results)

    blueprints = results["regen_candidate_blueprints"]
    first = blueprints[0]
    package = first["thermal_package"]

    assert results["phase_12b_3_regen_candidate_blueprint_thermal_builder_complete"] is True
    assert results["regen_candidate_blueprint_thermal_builder_ready"] is True
    assert results["regen_candidate_blueprint_thermal_builder_status"] == PASS_STATUS

    assert results["regen_candidate_blueprint_thermal_package_count"] == 4
    assert len(results["regen_candidate_blueprint_thermal_ready_ids"]) == 4

    assert first["blueprint_thermal_status"] == "THERMAL_PACKAGE_CREATED_NOT_SOLVED"
    assert first["blueprint_lifecycle_state"] == "BLUEPRINT_THERMAL_READY_VALIDATION_LOCKED"

    assert package["owner"] == "REGEN_CANDIDATE_BLUEPRINT_THERMAL_BUILDER"
    assert package["phase"] == "12B.3"
    assert package["status"] == "THERMAL_PACKAGE_CREATED_SOLVER_NOT_EXECUTED"

    assert package["thermal_state"]["regen_heat_flux_reference"] == 5.0e6
    assert package["thermal_state"]["regen_pressure_drop_reference"] == 150000.0
    assert package["thermal_state"]["hydraulic_diameter_m"] > 0.0
    assert package["thermal_state"]["total_coolant_flow_area_m2"] > 0.0

    assert package["thermal_constraints"]["status"] == "PASS_THERMAL_PACKAGE_CONSTRAINTS"
    assert package["thermal_readiness"]["thermal_ready_for_validation_builder"] is True
    assert package["thermal_readiness"]["thermal_ready_for_real_solver"] is False
    assert package["thermal_provenance"]["solver_executed"] is False
    assert package["thermal_provenance"]["bartz_executed"] is False
    assert package["thermal_provenance"]["coolant_solver_executed"] is False
    assert package["thermal_provenance"]["axial_marching_executed"] is False

    assert results["phase_12b_4_candidate_blueprint_validation_builder_allowed"] is True
    assert results["regen_candidate_blueprint_validation_builder_allowed"] is True

    assert results["regen_candidate_blueprint_generation_execution_allowed"] is False
    assert results["regen_candidate_blueprint_create_blueprints_allowed"] is False
    assert results["regen_candidate_creation_create_candidates_allowed"] is False
    assert results["regen_candidate_generation_create_candidates_allowed"] is False
    assert results["regen_optimisation_runtime_execution_allowed"] is False
    assert results["regen_optimisation_generation_advance_allowed"] is False
    assert results["regen_optimisation_mutation_execution_allowed"] is False
    assert results["regen_optimisation_candidate_acceptance_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False


def test_regen_candidate_blueprint_thermal_builder_blocks_without_12b2():
    results = attach_regen_candidate_blueprint_thermal_builder({})

    assert results["phase_12b_3_regen_candidate_blueprint_thermal_builder_complete"] is True
    assert results["regen_candidate_blueprint_thermal_builder_ready"] is False
    assert results["regen_candidate_blueprint_thermal_package_count"] == 0
    assert results["phase_12b_4_candidate_blueprint_validation_builder_allowed"] is False


if __name__ == "__main__":
    test_regen_candidate_blueprint_thermal_builder()
    test_regen_candidate_blueprint_thermal_builder_blocks_without_12b2()
    print("PASS_REGEN_CANDIDATE_BLUEPRINT_THERMAL_BUILDER_PHASE_12B3")
