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

    assert results["regen_evolution_loop_report_owner_complete"] is True
    assert results["phase_11b_6c_regen_evolution_loop_report_owner_complete"] is True
    assert results["regen_evolution_loop_report_owner_ready"] is True

    assert (
        results["regen_evolution_loop_report_owner_status"]
        == "PASS_REGEN_EVOLUTION_LOOP_REPORT_OWNER_PHASE_11B6C"
    )

    summary = results["regen_evolution_loop_summary"]
    explanation = results["regen_evolution_loop_explanation"]
    bundle = results["regen_evolution_loop_report_bundle"]
    export_bundle = results["regen_evolution_loop_export_bundle"]
    text = results["regen_evolution_loop_report_text"]

    assert summary["loop_id"] == "REGEN_EVOLUTION_LOOP_001"
    assert summary["generation_history_count"] == 2
    assert summary["generation_1_id"] == "GEN_001"
    assert summary["generation_2_id"] == "GEN_002"
    assert summary["runtime_evolution_allowed"] is False

    assert "loop_architecture_reason" in explanation
    assert "generation_1_reason" in explanation
    assert "generation_2_reason" in explanation
    assert "safety_reason" in explanation

    assert bundle["report_key"] == "regen_evolution_loop_report"
    assert bundle["owner"] == "REGEN_EVOLUTION_LOOP_REPORT_OWNER"
    assert bundle["phase"] == "11B.6C"
    assert bundle["ready"] is True
    assert bundle["architecture"]["evolution_loop_report_owner_complete"] is True
    assert bundle["architecture"]["runtime_evolution_allowed"] is False

    assert export_bundle["export_ready"] is True
    assert export_bundle["report_key"] == "regen_evolution_loop_report"

    assert "LEAF PHASE 11B.6C" in text
    assert "Generation 1 Record" in text
    assert "Generation 2 Record" in text
    assert "Loop State" in text
    assert "Runtime evolution executed: False" in text

    assert results["regen_evolution_loop_report_registered"] is False
    assert results["regen_evolution_loop_report_viewer_registered"] is False
    assert results["regen_evolution_loop_report_export_registered"] is False

    assert results["regen_evolution_loop_registration_owner_allowed"] is True
    assert results["phase_11b_6d_evolution_loop_registration_owner_allowed"] is True

    print("PASS_REGEN_EVOLUTION_LOOP_REPORT_OWNER_PHASE_11B6C")
    return True


if __name__ == "__main__":
    run_test()
