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

    assert results["regen_candidate_ranking_owner_complete"] is True
    assert results["phase_11b_4b_regen_candidate_ranking_owner_complete"] is True
    assert results["regen_candidate_ranking_ready"] is True

    assert (
        results["regen_candidate_ranking_status"]
        == "PASS_REGEN_CANDIDATE_RANKING_OWNER_PHASE_11B4B"
    )

    ranked = results["regen_candidate_ranked_population"]
    best = results["regen_candidate_best_candidate"]
    stats = results["regen_candidate_ranking_statistics"]

    assert isinstance(ranked, list)
    assert len(ranked) == 16
    assert results["regen_candidate_ranked_population_count"] == 16
    assert isinstance(best, dict)
    assert stats["population_size"] == 16
    assert stats["best_candidate_id"] == best["candidate_id"]

    previous_score = None

    for index, candidate in enumerate(ranked):
        ranking = candidate["ranking"]

        assert ranking["rank"] == index + 1
        assert 0.0 <= ranking["objective_score"] <= 1.0
        assert candidate["candidate_rank_status"] == "RANKED_NOT_MUTATED_NOT_SOLVED_NOT_COMMITTED"
        assert candidate["candidate_rank_owner"] == "REGEN_CANDIDATE_RANKING_OWNER"
        assert candidate["candidate_rank_phase"] == "11B.4B"

        if previous_score is not None:
            assert previous_score >= ranking["objective_score"]

        previous_score = ranking["objective_score"]

    assert ranked[0]["ranking"]["is_best_candidate"] is True
    assert results["regen_candidate_ranking_owner_ranking_executed"] is True
    assert results["regen_candidate_ranking_owner_scoring_executed"] is True

    assert results["regen_candidate_ranking_owner_mutation_executed"] is False
    assert results["regen_candidate_ranking_owner_evolution_executed"] is False
    assert results["regen_candidate_ranking_owner_solver_executed"] is False
    assert results["regen_candidate_ranking_owner_live_commit_executed"] is False
    assert results["regen_candidate_ranking_owner_candidate_acceptance_executed"] is False

    report = results["regen_candidate_ranking_report"]

    assert "LEAF PHASE 11B.4B" in report
    assert "Ranked Candidates" in report
    assert "Mutation executed: False" in report
    assert "Candidate solving executed: False" in report

    print("PASS_REGEN_CANDIDATE_RANKING_OWNER_PHASE_11B4B")
    return True


if __name__ == "__main__":
    run_test()
