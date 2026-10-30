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
from regen_candidate_blueprint_mutation_architecture import attach_regen_candidate_blueprint_mutation_architecture
from regen_candidate_blueprint_mutation_validation import attach_regen_candidate_blueprint_mutation_validation
from regen_candidate_blueprint_diversity_controller import attach_regen_candidate_blueprint_diversity_controller
from regen_candidate_blueprint_convergence_monitor import (
    PASS_STATUS,
    attach_regen_candidate_blueprint_convergence_monitor,
)


def build_ready_12d3_results():
    results = {
        "phase_11g_complete": True,
        "regen_candidate_creation_architecture_complete": True,
        "phase_12a_candidate_blueprint_generation_allowed": True,
        "regen_candidate_blueprint_generation_allowed": True,
        "regen_candidate_creation_completion_audit": {"complete": True},
        "regen_candidate_creation_registry": {"candidate_creation_registry_id": "TEST_REG"},
        "regen_candidate_creation_session": {"candidate_creation_session_id": "TEST_SESSION"},
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

    for attach in [
        attach_regen_candidate_blueprint_generation_input_gate,
        attach_regen_candidate_blueprint_session_owner,
        attach_regen_candidate_blueprint_registration_owner,
        attach_regen_candidate_blueprint_report_owner,
        attach_regen_candidate_blueprint_completion_audit,
        attach_regen_candidate_blueprint_generation_engine,
        attach_regen_candidate_blueprint_geometry_builder,
        attach_regen_candidate_blueprint_thermal_builder,
        attach_regen_candidate_blueprint_validation_builder,
        attach_regen_candidate_blueprint_engineering_completion_audit,
        attach_regen_candidate_blueprint_population_builder,
        attach_regen_candidate_blueprint_population_registration_owner,
        attach_regen_candidate_blueprint_population_validation_owner,
        attach_regen_candidate_blueprint_population_completion_audit,
        attach_regen_candidate_blueprint_mutation_architecture,
        attach_regen_candidate_blueprint_mutation_validation,
        attach_regen_candidate_blueprint_diversity_controller,
    ]:
        results = attach(results)

    return results


def test_regen_candidate_blueprint_convergence_monitor():
    results = build_ready_12d3_results()
    results = attach_regen_candidate_blueprint_convergence_monitor(results)

    monitor = results["regen_candidate_blueprint_convergence_monitor"]
    registry = results["regen_candidate_blueprint_convergence_registry"]
    metrics = results["regen_candidate_blueprint_convergence_metrics"]

    assert results["phase_12d_4_regen_candidate_blueprint_convergence_monitor_complete"] is True
    assert results["regen_candidate_blueprint_convergence_monitor_ready"] is True
    assert results["regen_candidate_blueprint_convergence_monitor_status"] == PASS_STATUS

    assert monitor["owner"] == "REGEN_CANDIDATE_BLUEPRINT_CONVERGENCE_MONITOR"
    assert monitor["phase"] == "12D.4"
    assert monitor["ready"] is True

    assert registry["permissions"]["termination_owner_allowed"] is True
    assert registry["permissions"]["mutation_execution_allowed"] is False
    assert registry["permissions"]["solver_execution_allowed"] is False
    assert registry["permissions"]["candidate_acceptance_allowed"] is False
    assert registry["permissions"]["live_geometry_commit_allowed"] is False

    assert metrics["population_size"] == 4
    assert metrics["geometry_uniqueness_ratio"] > 0.0
    assert metrics["convergence_state"]

    assert results["phase_12d_5_candidate_blueprint_termination_owner_allowed"] is True
    assert results["regen_candidate_blueprint_termination_owner_allowed"] is True

    assert results["regen_candidate_blueprint_mutation_execution_allowed"] is False
    assert results["regen_optimisation_mutation_execution_allowed"] is False
    assert results["regen_optimisation_live_geometry_commit_allowed"] is False


def test_regen_candidate_blueprint_convergence_monitor_blocks_without_12d3():
    results = attach_regen_candidate_blueprint_convergence_monitor({})

    assert results["phase_12d_4_regen_candidate_blueprint_convergence_monitor_complete"] is True
    assert results["regen_candidate_blueprint_convergence_monitor_ready"] is False
    assert results["regen_candidate_blueprint_convergence_monitor"] is None
    assert results["phase_12d_5_candidate_blueprint_termination_owner_allowed"] is False


if __name__ == "__main__":
    test_regen_candidate_blueprint_convergence_monitor()
    test_regen_candidate_blueprint_convergence_monitor_blocks_without_12d3()
    print("PASS_REGEN_CANDIDATE_BLUEPRINT_CONVERGENCE_MONITOR_PHASE_12D4")
