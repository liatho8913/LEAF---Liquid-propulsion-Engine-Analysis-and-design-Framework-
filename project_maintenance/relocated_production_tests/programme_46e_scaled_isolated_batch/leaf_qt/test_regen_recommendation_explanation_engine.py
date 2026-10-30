from regen_recommendation_explanation_engine import (
    attach_regen_recommendation_explanation_engine,
)
from regen_recommendation_explanation_history_owner import (
    attach_regen_recommendation_explanation_history_owner,
)
from regen_recommendation_explanation_report_owner import (
    attach_regen_recommendation_explanation_report_owner,
)
from regen_recommendation_explanation_master_gate import (
    attach_regen_recommendation_explanation_master_gate,
)


def apply_chain(results):
    results = attach_regen_recommendation_explanation_engine(results)
    results = attach_regen_recommendation_explanation_history_owner(results)
    results = attach_regen_recommendation_explanation_report_owner(results)
    results = attach_regen_recommendation_explanation_master_gate(results)
    return results


def base_ready_results():
    return {
        "regen_candidate_acceptance_master_gate_ready": True,
        "regen_candidate_rejection_master_gate_ready": True,
        "regen_candidate_accepted": True,
        "regen_candidate_rejected": False,
        "regen_candidate_acceptance_decision": "ACCEPT_FOR_REFINEMENT",
        "regen_candidate_rejection_decision": "REFINE_CANDIDATE",
        "regen_candidate_rejection_recovery_action": (
            "RECOVER_BY_REDUCING_PRESSURE_DROP"
        ),
        "regen_multi_objective_scores": {
            "thermal_margin": 80.0,
            "pressure_drop": 42.0,
            "coolant_velocity": 75.0,
            "geometry_fit": 82.0,
            "manufacturability": 70.0,
            "material_margin": 85.0,
            "safety_margin": 90.0,
        },
    }


def test_recommendation_explains_refinement_candidate():
    results = apply_chain(base_ready_results())

    assert results["phase_11b_2h_regen_recommendation_explanation_complete"] is True
    assert results["phase_11b_2h_regen_recommendation_explanation_history_complete"] is True
    assert results["phase_11b_2h_regen_recommendation_explanation_report_complete"] is True
    assert results["phase_11b_2h_regen_recommendation_explanation_master_gate_complete"] is True

    assert results["regen_recommendation_explanation_status"] == (
        "PASS_REGEN_RECOMMENDATION_EXPLANATION_READY"
    )
    assert results["regen_recommendation_explanation_master_gate_status"] == (
        "PASS_REGEN_RECOMMENDATION_EXPLANATION_GATE_READY"
    )

    recommendation = results["regen_recommendation_explanation"]

    assert recommendation["mode"] == "ACCEPTED_REFINEMENT"
    assert recommendation["primary_action"] == "REDUCE_PRESSURE_DROP"
    assert recommendation["target_parameter"] == "coolant_channel_width"
    assert recommendation["direction"] == "increase"

    assert results["regen_recommendation_explanation_solver_executed"] is False
    assert results["regen_recommendation_explanation_live_geometry_modified"] is False
    assert results["regen_recommendation_explanation_candidate_committed"] is False


def test_recommendation_explains_rejected_candidate():
    results = base_ready_results()
    results["regen_candidate_accepted"] = False
    results["regen_candidate_rejected"] = True
    results["regen_candidate_acceptance_decision"] = "BLOCK_ACCEPTANCE_REJECTED"
    results["regen_candidate_rejection_decision"] = "REJECT_CANDIDATE"

    results = apply_chain(results)

    recommendation = results["regen_recommendation_explanation"]

    assert recommendation["mode"] == "REJECTION_RECOVERY"
    assert recommendation["primary_action"] == "RECOVER_BY_REDUCING_PRESSURE_DROP"
    assert recommendation["target_parameter"] == "coolant_channel_width"


def test_recommendation_explanation_blocks_without_gates():
    results = {}

    results = apply_chain(results)

    assert results["regen_recommendation_explanation_ready"] is False
    assert results["regen_recommendation_explanation_master_gate_ready"] is False


if __name__ == "__main__":
    test_recommendation_explains_refinement_candidate()
    test_recommendation_explains_rejected_candidate()
    test_recommendation_explanation_blocks_without_gates()
    print("PASS_REGEN_RECOMMENDATION_EXPLANATION_ENGINE_PHASE_11B2H")