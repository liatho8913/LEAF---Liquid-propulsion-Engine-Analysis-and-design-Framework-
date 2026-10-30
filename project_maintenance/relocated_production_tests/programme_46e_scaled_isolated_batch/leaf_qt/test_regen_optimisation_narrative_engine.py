from regen_optimisation_narrative_engine import (
    attach_regen_optimisation_narrative_engine,
)
from regen_optimisation_narrative_history_owner import (
    attach_regen_optimisation_narrative_history_owner,
)
from regen_optimisation_narrative_report_owner import (
    attach_regen_optimisation_narrative_report_owner,
)
from regen_optimisation_narrative_master_gate import (
    attach_regen_optimisation_narrative_master_gate,
)


def apply_chain(results):
    results = attach_regen_optimisation_narrative_engine(results)
    results = attach_regen_optimisation_narrative_history_owner(results)
    results = attach_regen_optimisation_narrative_report_owner(results)
    results = attach_regen_optimisation_narrative_master_gate(results)
    return results


def base_ready_results():
    return {
        "regen_multi_objective_scoring_master_gate_ready": True,
        "regen_exploration_master_gate_ready": True,
        "regen_multi_objective_total_score": 88.0,
        "regen_multi_objective_scores": {
            "thermal_margin": 90.0,
            "pressure_drop": 85.0,
            "coolant_velocity": 80.0,
            "geometry_fit": 95.0,
            "manufacturability": 75.0,
            "material_margin": 90.0,
            "safety_margin": 90.0,
        },
        "regen_exploration_mode": "LOCAL_REFINEMENT",
        "regen_exploration_action": "SMALL_REFINEMENT_STEPS",
        "regen_exploration_pressure": 0.25,
    }


def test_narrative_engine_passes_strong_candidate():
    results = apply_chain(base_ready_results())

    assert results["phase_11b_2e_regen_optimisation_narrative_complete"] is True
    assert results["phase_11b_2e_regen_optimisation_narrative_history_complete"] is True
    assert results["phase_11b_2e_regen_optimisation_narrative_report_complete"] is True
    assert results["phase_11b_2e_regen_optimisation_narrative_master_gate_complete"] is True

    assert results["regen_optimisation_narrative_status"] == (
        "PASS_REGEN_OPTIMISATION_NARRATIVE_READY"
    )
    assert results["regen_optimisation_narrative_master_gate_status"] == (
        "PASS_REGEN_OPTIMISATION_NARRATIVE_GATE_READY"
    )

    narrative = results["regen_optimisation_narrative"]

    assert narrative["decision"] == "CANDIDATE_STRONG_ACCEPTABLE"
    assert narrative["summary"]
    assert narrative["reasons"]
    assert narrative["recommended_actions"]

    assert results["regen_optimisation_narrative_solver_executed"] is False
    assert results["regen_optimisation_narrative_live_geometry_modified"] is False
    assert results["regen_optimisation_narrative_candidate_committed"] is False


def test_narrative_engine_detects_refinement_candidate():
    results = base_ready_results()
    results["regen_multi_objective_total_score"] = 58.0
    results["regen_multi_objective_scores"]["pressure_drop"] = 25.0

    results = apply_chain(results)

    narrative = results["regen_optimisation_narrative"]

    assert narrative["decision"] == "CANDIDATE_NEEDS_REFINEMENT"
    assert narrative["weakest_objective"]["name"] == "pressure_drop"
    assert any("pressure drop" in action.lower() for action in narrative["recommended_actions"])


def test_narrative_engine_blocks_without_required_gates():
    results = {}

    results = apply_chain(results)

    assert results["regen_optimisation_narrative_ready"] is False
    assert results["regen_optimisation_narrative_master_gate_ready"] is False


if __name__ == "__main__":
    test_narrative_engine_passes_strong_candidate()
    test_narrative_engine_detects_refinement_candidate()
    test_narrative_engine_blocks_without_required_gates()
    print("PASS_REGEN_OPTIMISATION_NARRATIVE_ENGINE_PHASE_11B2E")