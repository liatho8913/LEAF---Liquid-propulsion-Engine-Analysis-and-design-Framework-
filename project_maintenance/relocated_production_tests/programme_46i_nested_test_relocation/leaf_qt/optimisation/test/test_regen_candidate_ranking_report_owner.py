from regen_candidate_population_generation_owner import (
    build_regen_candidate_population_generation_owner,
)
from regen_candidate_population_report_owner import (
    build_regen_candidate_population_report_owner,
)
from regen_candidate_population_registration_owner import (
    build_regen_candidate_population_registration_owner,
)
from regen_candidate_population_completion_audit import (
    build_regen_candidate_population_completion_audit,
)
from regen_candidate_population_master_gate import (
    build_regen_candidate_population_master_gate,
)
from regen_candidate_ranking_input_audit import (
    build_regen_candidate_ranking_input_audit,
)
from regen_candidate_ranking_owner import (
    build_regen_candidate_ranking_owner,
)
from regen_candidate_ranking_report_owner import (
    build_regen_candidate_ranking_report_owner,
)


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
    }

    results.update(build_regen_candidate_population_generation_owner(results))
    results.update(build_regen_candidate_population_report_owner(results))
    results.update(build_regen_candidate_population_registration_owner(results))
    results.update(build_regen_candidate_population_completion_audit(results))
    results.update(build_regen_candidate_population_master_gate(results))
    results.update(build_regen_candidate_ranking_input_audit(results))
    results.update(build_regen_candidate_ranking_owner(results))
    results.update(build_regen_candidate_ranking_report_owner(results))

    assert results["regen_candidate_ranking_report_owner_complete"] is True
    assert results["phase_11b_4c_regen_candidate_ranking_report_owner_complete"] is True
    assert results["regen_candidate_ranking_report_owner_ready"] is True

    assert (
        results["regen_candidate_ranking_report_owner_status"]
        == "PASS_REGEN_CANDIDATE_RANKING_REPORT_OWNER_PHASE_11B4C"
    )

    summary = results["regen_candidate_ranking_summary"]
    explanation = results["regen_candidate_ranking_explanation"]
    bundle = results["regen_candidate_ranking_report_bundle"]
    export_bundle = results["regen_candidate_ranking_export_bundle"]
    text = results["regen_candidate_ranking_report_text"]

    assert summary["population_size"] == 16
    assert summary["best_candidate_id"] == results["regen_candidate_best_candidate"]["candidate_id"]
    assert summary["ranking_method"] == "architecture_safe_geometry_proxy"

    assert "best_candidate_reason" in explanation
    assert "score_distribution_reason" in explanation
    assert "methodology_reason" in explanation
    assert "safety_reason" in explanation

    assert bundle["report_key"] == "regen_candidate_ranking_report"
    assert bundle["owner"] == "REGEN_CANDIDATE_RANKING_REPORT_OWNER"
    assert bundle["phase"] == "11B.4C"
    assert bundle["ready"] is True
    assert bundle["complete"] is True
    assert bundle["architecture"]["ranking_report_owner_complete"] is True
    assert bundle["architecture"]["ranking_registration_owner_complete"] is False
    assert bundle["architecture"]["mutation_allowed"] is False
    assert bundle["architecture"]["evolution_allowed"] is False

    assert export_bundle["export_ready"] is True
    assert export_bundle["report_key"] == "regen_candidate_ranking_report"

    assert "LEAF PHASE 11B.4C" in text
    assert "Ranking Explanation" in text
    assert "Ranked Candidate Table" in text
    assert "Mutation executed: False" in text
    assert "Evolution executed: False" in text

    assert results["regen_candidate_ranking_report_registered"] is False
    assert results["regen_candidate_ranking_report_viewer_registered"] is False
    assert results["regen_candidate_ranking_report_export_registered"] is False

    assert results["regen_candidate_ranking_report_owner_mutation_executed"] is False
    assert results["regen_candidate_ranking_report_owner_evolution_executed"] is False
    assert results["regen_candidate_ranking_report_owner_solver_executed"] is False
    assert results["regen_candidate_ranking_report_owner_live_commit_executed"] is False
    assert results["regen_candidate_ranking_report_owner_candidate_acceptance_executed"] is False

    print("PASS_REGEN_CANDIDATE_RANKING_REPORT_OWNER_PHASE_11B4C")
    return True


if __name__ == "__main__":
    run_test()
