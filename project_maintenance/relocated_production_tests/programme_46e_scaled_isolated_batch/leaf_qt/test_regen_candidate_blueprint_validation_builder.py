from project_maintenance.production_historical_artifacts.leaf_qt.regen_candidate_blueprint_generation_input_gate import attach_regen_candidate_blueprint_generation_input_gate
from regen_candidate_blueprint_session_owner import attach_regen_candidate_blueprint_session_owner
from regen_candidate_blueprint_registration_owner import attach_regen_candidate_blueprint_registration_owner
from regen_candidate_blueprint_report_owner import attach_regen_candidate_blueprint_report_owner
from regen_candidate_blueprint_completion_audit import attach_regen_candidate_blueprint_completion_audit
from regen_candidate_blueprint_generation_engine import attach_regen_candidate_blueprint_generation_engine
from regen_candidate_blueprint_geometry_builder import attach_regen_candidate_blueprint_geometry_builder
from regen_candidate_blueprint_thermal_builder import attach_regen_candidate_blueprint_thermal_builder
from regen_candidate_blueprint_validation_builder import (
    PASS_STATUS,
    attach_regen_candidate_blueprint_validation_builder,
)


def build_ready_12b3_results():
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
    return results


def test_regen_candidate_blueprint_validation_builder():
    results = build_ready_12b3_results()
    results = attach_regen_candidate_blueprint_validation_builder(results)

    blueprints = results["regen_candidate_blueprints"]
    first = blueprints[0]
    package = first["validation_package"]

    assert results["phase_12b_4_regen_candidate_blueprint_validation_builder_complete"] is True
    assert results["regen_candidate_blueprint_validation_builder_ready"] is True
    assert results["regen_candidate_blueprint_validation_builder_status"] == PASS_STATUS

    assert results["regen_candidate_blueprint_validation_package_count"] == 4
    assert len(results["regen_candidate_blueprint_validation_ready_ids"]) == 4

    assert first["blueprint_validation_status"] == "BLUEPRINT_VALIDATION_PACKAGE_PASS"
    assert first["blueprint_engineering_status"] == "ENGINEERING_BLUEPRINT_READY_FOR_COMPLETION_AUDIT"
    assert first["blueprint_lifecycle_state"] == "BLUEPRINT_VALIDATION_READY_COMPLETION_AUDIT_LOCKED"

    assert package["owner"] == "REGEN_CANDIDATE_BLUEPRINT_VALIDATION_BUILDER"
    assert package["phase"] == "12B.4"
    assert package["status"] == "PASS_BLUEPRINT_VALIDATION_PACKAGE"

    assert package["validation_readiness"]["blueprint_ready_for_completion_audit"] is True
    assert package["validation_readiness"]["blueprint_ready_for_population_builder"] is False
    assert package["validation_readiness"]["blueprint_ready_for_mutation"] is False
    assert package["validation_readiness"]["blueprint_ready_for_solver_execution"] is False
    assert package["validation_readiness"]["blueprint_ready_for_candidate_acceptance"] is False
    assert package["validation_readiness"]["blueprint_ready_for_live_commit"] is False

    assert package["validation_provenance"]["real_solver_executed"] is False
    assert package["validation_provenance"]["mutation_executed"] is False
    assert package["validation_provenance"]["candidate_acceptance_executed"] is False
    assert package["validation_provenance"]["live_geometry_modified"] is False

    assert results["phase_12b_5_candidate_blueprint_completion_audit_allowed"] is True
    assert results["regen_candidate_blueprint_completion_builder_audit_allowed"] is True

    assert results["regen_candidate_blueprint_generation_execution_allowed"] is False
    assert results["regen_candidate_blueprint_create_blueprints_allowed"] is False
    assert results["regen_candidate_creation_create_candidates_allowed"] is False
    assert results["regen_candidate_generation_create_candidates_allowed"] is False
    assert results["regen_optimisation_runtime_execution_allowed"] is False
    assert results["regen_optimisation_generation_advance_allowed"] is False
    assert results["regen_optimisation_mutation_execution_allowed"] is False
    assert results["regen_optimisation_candidate_acceptance_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False


def test_regen_candidate_blueprint_validation_builder_blocks_without_12b3():
    results = attach_regen_candidate_blueprint_validation_builder({})

    assert results["phase_12b_4_regen_candidate_blueprint_validation_builder_complete"] is True
    assert results["regen_candidate_blueprint_validation_builder_ready"] is False
    assert results["regen_candidate_blueprint_validation_package_count"] == 0
    assert results["phase_12b_5_candidate_blueprint_completion_audit_allowed"] is False


if __name__ == "__main__":
    test_regen_candidate_blueprint_validation_builder()
    test_regen_candidate_blueprint_validation_builder_blocks_without_12b3()
    print("PASS_REGEN_CANDIDATE_BLUEPRINT_VALIDATION_BUILDER_PHASE_12B4")
