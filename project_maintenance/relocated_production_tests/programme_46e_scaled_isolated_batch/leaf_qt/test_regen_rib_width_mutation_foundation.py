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
from regen_candidate_blueprint_convergence_monitor import attach_regen_candidate_blueprint_convergence_monitor
from regen_candidate_blueprint_termination_owner import attach_regen_candidate_blueprint_termination_owner
from regen_candidate_blueprint_optimisation_completion_audit import attach_regen_candidate_blueprint_optimisation_completion_audit
from regen_autonomous_blueprint_mutation_execution_foundation import attach_regen_autonomous_blueprint_mutation_execution_foundation
from regen_channel_count_mutation_foundation import attach_regen_channel_count_mutation_foundation
from regen_channel_width_mutation_foundation import attach_regen_channel_width_mutation_foundation
from regen_channel_height_mutation_foundation import attach_regen_channel_height_mutation_foundation
from regen_rib_width_mutation_foundation import PASS_STATUS, attach_regen_rib_width_mutation_foundation

def build_ready_13d_results():
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
        "regen_real_geometry_mutation_allowed": False,
        "regen_solver_execution_from_mutation_allowed": False,
        "regen_candidate_acceptance_from_mutation_allowed": False,
        "regen_live_geometry_commit_from_mutation_allowed": False,
        "regen_channel_height_mutation_execution_allowed": False,
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
        attach_regen_candidate_blueprint_convergence_monitor,
        attach_regen_candidate_blueprint_termination_owner,
        attach_regen_candidate_blueprint_optimisation_completion_audit,
        attach_regen_autonomous_blueprint_mutation_execution_foundation,
        attach_regen_channel_count_mutation_foundation,
        attach_regen_channel_width_mutation_foundation,
        attach_regen_channel_height_mutation_foundation,
    ]:
        results = attach(results)

    return results

def test_regen_rib_width_mutation_foundation():
    results = build_ready_13d_results()
    results = attach_regen_rib_width_mutation_foundation(results)

    foundation = results["regen_rib_width_mutation_foundation"]
    registry = results["regen_rib_width_mutation_registry"]
    proposals = results["regen_rib_width_mutation_proposals"]
    history = results["regen_rib_width_mutation_history"]

    assert results["phase_13e_regen_rib_width_mutation_foundation_complete"] is True
    assert results["regen_rib_width_mutation_foundation_ready"] is True
    assert results["regen_rib_width_mutation_foundation_status"] == PASS_STATUS
    assert foundation["owner"] == "REGEN_RIB_WIDTH_MUTATION_FOUNDATION"
    assert foundation["phase"] == "13E"
    assert foundation["ready"] is True

    assert registry["mutation_axis"] == "rib_width"
    assert registry["permissions"]["wall_thickness_mutation_allowed"] is True
    assert registry["permissions"]["rib_width_mutation_execution_allowed"] is False
    assert registry["permissions"]["solver_execution_allowed"] is False
    assert registry["permissions"]["candidate_acceptance_allowed"] is False
    assert registry["permissions"]["live_geometry_commit_allowed"] is False

    assert len(proposals) == 16
    assert history["proposal_count"] == 16
    assert history["valid_proposal_count"] == 16
    assert history["mutation_execution_count"] == 0
    assert history["solver_execution_count"] == 0
    assert history["live_commit_count"] == 0

    assert results["phase_13f_wall_thickness_mutation_allowed"] is True
    assert results["regen_wall_thickness_mutation_allowed"] is True
    assert results["regen_rib_width_mutation_execution_allowed"] is False
    assert results["regen_real_geometry_mutation_allowed"] is False
    assert results["regen_solver_execution_from_mutation_allowed"] is False
    assert results["regen_live_geometry_commit_from_mutation_allowed"] is False

def test_regen_rib_width_mutation_foundation_blocks_without_13d():
    results = attach_regen_rib_width_mutation_foundation({})
    assert results["phase_13e_regen_rib_width_mutation_foundation_complete"] is True
    assert results["regen_rib_width_mutation_foundation_ready"] is False
    assert results["regen_rib_width_mutation_foundation"] is None
    assert results["phase_13f_wall_thickness_mutation_allowed"] is False

if __name__ == "__main__":
    test_regen_rib_width_mutation_foundation()
    test_regen_rib_width_mutation_foundation_blocks_without_13d()
    print("PASS_REGEN_RIB_WIDTH_MUTATION_FOUNDATION_PHASE_13E")
