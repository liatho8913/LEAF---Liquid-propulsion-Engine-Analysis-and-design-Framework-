from regen_optimisation_controller import attach_regen_optimisation_controller
from regen_optimisation_history_owner import attach_regen_optimisation_history_owner
from regen_optimisation_controller_master_gate import (
    attach_regen_optimisation_controller_master_gate,
)


def test_optimisation_controller_next_generation_ready():
    results = attach_regen_optimisation_controller({
        "regen_multi_candidate_search_ready": True,
        "regen_candidate_ranking_complete": True,
        "regen_convergence_complete": True,
        "regen_convergence_ready": True,
        "regen_convergence_converged": False,
        "regen_candidate_best_candidate": {
            "candidate_id": "RMC-0001",
            "score": 0.25,
            "decision": "BEST_SO_FAR",
        },
        "regen_candidate_best_candidate_score": 0.25,
        "regen_convergence_generation_count": 1,
    })

    assert results["phase_11b_1n_regen_optimisation_controller_complete"] is True
    assert results["regen_optimisation_next_action"] == "GENERATE_NEXT_GENERATION"
    assert results["regen_optimisation_ready"] is True


def test_optimisation_controller_converged():
    results = attach_regen_optimisation_controller({
        "regen_multi_candidate_search_ready": True,
        "regen_candidate_ranking_complete": True,
        "regen_convergence_complete": True,
        "regen_convergence_ready": True,
        "regen_convergence_converged": True,
        "regen_candidate_best_candidate_score": 0.25,
        "regen_convergence_generation_count": 3,
    })

    assert results["regen_optimisation_next_action"] == "STOP_CONVERGED"
    assert results["regen_optimisation_controller_status"] == (
        "PASS_REGEN_OPTIMISATION_CONTROLLER_CONVERGED"
    )


def test_optimisation_controller_blocks_without_population():
    results = attach_regen_optimisation_controller({
        "regen_candidate_ranking_complete": True,
        "regen_convergence_complete": True,
    })

    assert results["regen_optimisation_next_action"] == "BLOCKED"
    assert results["regen_optimisation_controller_status"] == (
        "FAIL_REGEN_OPTIMISATION_CONTROLLER_BLOCKED"
    )


def test_optimisation_history_and_master_gate_next_generation_ready():
    results = attach_regen_optimisation_controller({
        "regen_multi_candidate_search_ready": True,
        "regen_candidate_ranking_complete": True,
        "regen_convergence_complete": True,
        "regen_convergence_ready": True,
        "regen_convergence_converged": False,
        "regen_candidate_best_candidate_score": 0.25,
        "regen_convergence_generation_count": 1,
    })

    results = attach_regen_optimisation_history_owner(results)
    results = attach_regen_optimisation_controller_master_gate(results)

    assert results["phase_11b_1n_regen_optimisation_history_complete"] is True
    assert results["phase_11b_1n_regen_optimisation_master_gate_complete"] is True
    assert results["regen_optimisation_master_gate_ready"] is True
    assert results["regen_optimisation_master_gate_status"] == (
        "WARN_REGEN_OPTIMISATION_MASTER_GATE_NEXT_GENERATION_READY"
    )