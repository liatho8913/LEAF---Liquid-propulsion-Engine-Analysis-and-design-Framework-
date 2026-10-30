from regen_adaptive_diversity_controller import (
    attach_regen_adaptive_diversity_controller,
)
from regen_adaptive_diversity_history_owner import (
    attach_regen_adaptive_diversity_history_owner,
)
from regen_adaptive_diversity_report_owner import (
    attach_regen_adaptive_diversity_report_owner,
)
from regen_adaptive_diversity_master_gate import (
    attach_regen_adaptive_diversity_master_gate,
)


def apply_chain(results):
    results = attach_regen_adaptive_diversity_controller(results)
    results = attach_regen_adaptive_diversity_history_owner(results)
    results = attach_regen_adaptive_diversity_report_owner(results)
    results = attach_regen_adaptive_diversity_master_gate(results)
    return results


def base_ready_results():
    return {
        "regen_population_diversity_master_gate_ready": True,
        "regen_adaptive_mutation_master_gate_ready": True,
        "regen_population_diversity_metrics": {
            "population_count": 10,
            "unique_candidate_count": 8,
            "duplicate_candidate_count": 2,
            "mean_normalised_spread": 0.05,
        },
        "regen_adaptive_mutation_mode": "STABLE_REFINEMENT",
        "regen_adaptive_mutation_strength": 0.05,
    }


def test_adaptive_diversity_stable():
    results = apply_chain(base_ready_results())

    assert results["phase_11b_2b_regen_adaptive_diversity_complete"] is True
    assert results["phase_11b_2b_regen_adaptive_diversity_history_complete"] is True
    assert results["phase_11b_2b_regen_adaptive_diversity_report_complete"] is True
    assert results["phase_11b_2b_regen_adaptive_diversity_master_gate_complete"] is True

    assert results["regen_adaptive_diversity_status"] == (
        "PASS_REGEN_ADAPTIVE_DIVERSITY_READY"
    )
    assert results["regen_adaptive_diversity_master_gate_status"] == (
        "PASS_REGEN_ADAPTIVE_DIVERSITY_GATE_READY"
    )
    assert results["regen_adaptive_diversity_mode"] == "DIVERSITY_STABLE"

    assert results["regen_adaptive_diversity_solver_executed"] is False
    assert results["regen_adaptive_diversity_live_geometry_modified"] is False
    assert results["regen_adaptive_diversity_candidate_committed"] is False


def test_adaptive_diversity_detects_collapse():
    results = base_ready_results()
    results["regen_population_diversity_metrics"]["unique_candidate_count"] = 1
    results["regen_population_diversity_metrics"]["duplicate_candidate_count"] = 9
    results["regen_population_diversity_metrics"]["mean_normalised_spread"] = 0.0

    results = apply_chain(results)

    assert results["regen_adaptive_diversity_mode"] == "COLLAPSE_RECOVERY"
    assert results["regen_adaptive_diversity_action"] == (
        "INJECT_EXPLORATION_CANDIDATES"
    )


def test_adaptive_diversity_detects_over_broad_population():
    results = base_ready_results()
    results["regen_population_diversity_metrics"]["mean_normalised_spread"] = 0.25

    results = apply_chain(results)

    assert results["regen_adaptive_diversity_mode"] == "FOCUS_DIVERSITY"
    assert results["regen_adaptive_diversity_action"] == (
        "FOCUS_AROUND_BEST_CANDIDATES"
    )


def test_adaptive_diversity_blocks_without_required_gates():
    results = {}

    results = apply_chain(results)

    assert results["regen_adaptive_diversity_ready"] is False
    assert results["regen_adaptive_diversity_master_gate_ready"] is False


if __name__ == "__main__":
    test_adaptive_diversity_stable()
    test_adaptive_diversity_detects_collapse()
    test_adaptive_diversity_detects_over_broad_population()
    test_adaptive_diversity_blocks_without_required_gates()
    print("PASS_REGEN_ADAPTIVE_DIVERSITY_CONTROLLER_PHASE_11B2B")