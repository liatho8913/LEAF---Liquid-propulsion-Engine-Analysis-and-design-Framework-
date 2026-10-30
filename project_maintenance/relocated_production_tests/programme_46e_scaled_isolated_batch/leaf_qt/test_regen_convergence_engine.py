from regen_convergence_engine import attach_regen_convergence_engine
from regen_convergence_history_owner import attach_regen_convergence_history_owner
from regen_convergence_master_gate import attach_regen_convergence_master_gate


def test_convergence_engine_running_with_improvement():
    solved = attach_regen_convergence_engine({
        "regen_candidate_best_candidate_score": 0.25,
        "regen_convergence_previous_best_score": 0.10,
        "regen_convergence_generation_count": 1,
        "regen_candidate_ranked_candidates": [
            {"candidate_id": "A", "score": 0.25}
        ],
        "regen_multi_candidate_population": [
            {"candidate_id": "A"}
        ],
    })

    assert solved["phase_11b_1m_regen_convergence_engine_complete"] is True
    assert solved["regen_convergence_status"] == "WARN_REGEN_CONVERGENCE_RUNNING"
    assert solved["regen_convergence_converged"] is False
    assert solved["regen_convergence_improvement"] > 0.0


def test_convergence_engine_detects_convergence():
    solved = attach_regen_convergence_engine({
        "regen_candidate_best_candidate_score": 0.2505,
        "regen_convergence_previous_best_score": 0.2500,
        "regen_convergence_generation_count": 2,
    })

    assert solved["regen_convergence_status"] == "PASS_REGEN_CONVERGENCE_REACHED"
    assert solved["regen_convergence_converged"] is True


def test_convergence_history_and_gate_pass_running():
    results = attach_regen_convergence_engine({
        "regen_candidate_best_candidate_score": 0.25,
        "regen_convergence_previous_best_score": 0.10,
        "regen_convergence_generation_count": 1,
    })

    results = attach_regen_convergence_history_owner(results)
    results = attach_regen_convergence_master_gate(results)

    assert results["phase_11b_1m_regen_convergence_history_complete"] is True
    assert results["phase_11b_1m_regen_convergence_master_gate_complete"] is True
    assert results["regen_convergence_ready"] is True
    assert results["regen_convergence_master_gate_status"] == (
        "WARN_REGEN_CONVERGENCE_MASTER_GATE_RUNNING"
    )


def test_convergence_blocks_without_best_score():
    results = attach_regen_convergence_engine({})
    results = attach_regen_convergence_history_owner(results)
    results = attach_regen_convergence_master_gate(results)

    assert results["regen_convergence_status"] == "FAIL_REGEN_CONVERGENCE_NO_BEST_SCORE"
    assert results["regen_convergence_ready"] is False