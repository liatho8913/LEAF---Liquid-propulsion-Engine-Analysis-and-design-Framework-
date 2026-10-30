from regen_candidate_population_generation_owner import build_regen_candidate_population_generation_owner
from regen_candidate_population_report_owner import build_regen_candidate_population_report_owner
from regen_candidate_population_registration_owner import build_regen_candidate_population_registration_owner
from regen_candidate_population_completion_audit import build_regen_candidate_population_completion_audit
from regen_candidate_population_master_gate import build_regen_candidate_population_master_gate
from regen_candidate_ranking_input_audit import build_regen_candidate_ranking_input_audit
from regen_candidate_ranking_owner import build_regen_candidate_ranking_owner
from regen_candidate_ranking_report_owner import build_regen_candidate_ranking_report_owner
from regen_candidate_ranking_registration_owner import build_regen_candidate_ranking_registration_owner
from regen_candidate_ranking_completion_audit import build_regen_candidate_ranking_completion_audit
from regen_candidate_ranking_master_gate import build_regen_candidate_ranking_master_gate
from regen_candidate_mutation_input_audit import build_regen_candidate_mutation_input_audit
from regen_candidate_mutation_owner import build_regen_candidate_mutation_owner
from regen_candidate_mutation_report_owner import build_regen_candidate_mutation_report_owner
from regen_candidate_mutation_registration_owner import build_regen_candidate_mutation_registration_owner
from regen_candidate_mutation_completion_audit import build_regen_candidate_mutation_completion_audit
from regen_candidate_mutation_master_gate import build_regen_candidate_mutation_master_gate
from regen_evolution_loop_input_audit import build_regen_evolution_loop_input_audit
from regen_evolution_loop_owner import build_regen_evolution_loop_owner
from regen_evolution_loop_report_owner import build_regen_evolution_loop_report_owner
from regen_evolution_loop_registration_owner import build_regen_evolution_loop_registration_owner


def run_test():
    results = {
        "phase_11b_2t_regen_objective_decision_master_gate_complete": True,
        "regen_objective_decision_architecture_complete": True,
        "regen_candidate_ranking_objective_requested": "BALANCED",
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0012,
        "coolant_flow_fraction": 1.0,
        "regen_population_requested_size": 16,
        "regen_evolution_population_size": 16,
        "regen_evolution_generation_limit": 1,
        "regen_evolution_elite_count": 1,
        "regen_evolution_mutation_count": 1,
        "regen_evolution_mutation_rate": 0.06,
        "regen_evolution_convergence_tolerance": 0.001,
    }

    results.update(build_regen_candidate_population_generation_owner(results))
    results.update(build_regen_candidate_population_report_owner(results))
    results.update(build_regen_candidate_population_registration_owner(results))
    results.update(build_regen_candidate_population_completion_audit(results))
    results.update(build_regen_candidate_population_master_gate(results))
    results.update(build_regen_candidate_ranking_input_audit(results))
    results.update(build_regen_candidate_ranking_owner(results))
    results.update(build_regen_candidate_ranking_report_owner(results))
    results.update(build_regen_candidate_ranking_registration_owner(results))
    results.update(build_regen_candidate_ranking_completion_audit(results))
    results.update(build_regen_candidate_ranking_master_gate(results))
    results.update(build_regen_candidate_mutation_input_audit(results))
    results.update(build_regen_candidate_mutation_owner(results))
    results.update(build_regen_candidate_mutation_report_owner(results))
    results.update(build_regen_candidate_mutation_registration_owner(results))
    results.update(build_regen_candidate_mutation_completion_audit(results))
    results.update(build_regen_candidate_mutation_master_gate(results))
    results.update(build_regen_evolution_loop_input_audit(results))
    results.update(build_regen_evolution_loop_owner(results))
    results.update(build_regen_evolution_loop_report_owner(results))
    results.update(build_regen_evolution_loop_registration_owner(results))

    assert results["regen_evolution_loop_registration_owner_complete"] is True
    assert results["phase_11b_6d_regen_evolution_loop_registration_owner_complete"] is True
    assert results["regen_evolution_loop_registration_ready"] is True

    assert (
        results["regen_evolution_loop_registration_status"]
        == "PASS_REGEN_EVOLUTION_LOOP_REGISTRATION_OWNER_PHASE_11B6D"
    )

    assert results["regen_evolution_loop_report_registered"] is True
    assert results["regen_evolution_loop_report_viewer_registered"] is True
    assert results["regen_evolution_loop_report_export_registered"] is True

    assert "regen_evolution_loop_report" in results["regen_evolution_loop_registered_report_keys"]
    assert "regen_evolution_loop_report_bundle" in results["regen_evolution_loop_registered_bundle_keys"]
    assert "regen_evolution_loop_export" in results["regen_evolution_loop_registered_export_keys"]

    entry = results["regen_evolution_loop_registry_entry"]
    assert entry["registered"] is True
    assert entry["viewer_visible"] is True
    assert entry["export_visible"] is True
    assert entry["future_optimisation_visible"] is True
    assert entry["generation_advance_allowed"] is False
    assert entry["runtime_evolution_allowed"] is False
    assert entry["selection_allowed"] is False
    assert entry["convergence_allowed"] is False

    assert "regen_evolution_loop_report" in results["regen_evolution_loop_report_registry"]["registered_report_keys"]
    assert "regen_evolution_loop_report" in results["regen_evolution_loop_viewer_registry"]["viewer_report_keys"]
    assert "regen_evolution_loop_report" in results["regen_evolution_loop_export_registry"]["export_report_keys"]

    future_keys = results["regen_evolution_loop_future_optimisation_registry"]["optimisation_keys"]
    assert "evolution_loop_state" in future_keys
    assert "generation_records" in future_keys
    assert "loop_history" in future_keys

    assert results["regen_evolution_loop_completion_audit_allowed"] is True
    assert results["phase_11b_6e_evolution_loop_completion_audit_allowed"] is True

    assert results["regen_evolution_loop_registration_generation_advanced"] is False
    assert results["regen_evolution_loop_registration_evolution_executed"] is False
    assert results["regen_evolution_loop_registration_selection_executed"] is False
    assert results["regen_evolution_loop_registration_convergence_checked"] is False

    report = results["regen_evolution_loop_registration_report"]
    assert "LEAF PHASE 11B.6D" in report
    assert "Registered Report Keys" in report
    assert "Future Optimisation Keys" in report
    assert "Runtime evolution allowed: False" in report

    print("PASS_REGEN_EVOLUTION_LOOP_REGISTRATION_OWNER_PHASE_11B6D")
    return True


if __name__ == "__main__":
    run_test()
