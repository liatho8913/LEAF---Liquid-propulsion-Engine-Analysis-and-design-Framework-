from regen_optimisation_proof_system import (
    attach_regen_optimisation_proof_system,
)
from regen_optimisation_proof_history_owner import (
    attach_regen_optimisation_proof_history_owner,
)
from regen_optimisation_proof_report_owner import (
    attach_regen_optimisation_proof_report_owner,
)
from regen_optimisation_proof_master_gate import (
    attach_regen_optimisation_proof_master_gate,
)


def apply_chain(results):
    results = attach_regen_optimisation_proof_system(results)
    results = attach_regen_optimisation_proof_history_owner(results)
    results = attach_regen_optimisation_proof_report_owner(results)
    results = attach_regen_optimisation_proof_master_gate(results)
    return results


def base_ready_results():
    return {
        "regen_recommendation_explanation_master_gate_ready": True,
        "regen_candidate_acceptance_master_gate_ready": True,
        "regen_candidate_rejection_master_gate_ready": True,
        "regen_candidate_accepted": True,
        "regen_candidate_rejected": False,
        "regen_candidate_acceptance_decision": "ACCEPT_FOR_REFINEMENT",
        "regen_candidate_rejection_decision": "REFINE_CANDIDATE",
        "regen_multi_objective_total_score": 76.0,
        "regen_multi_objective_scores": {
            "thermal_margin": 80.0,
            "pressure_drop": 42.0,
            "coolant_velocity": 75.0,
            "geometry_fit": 82.0,
            "manufacturability": 70.0,
            "material_margin": 85.0,
            "safety_margin": 90.0,
        },
        "regen_recommendation_explanation": {
            "primary_action": "REDUCE_PRESSURE_DROP",
            "target_parameter": "coolant_channel_width",
            "direction": "increase",
            "expected_effect": "Expected to reduce coolant pressure loss.",
            "risk": "Wider channels may reduce coolant-side heat-transfer coefficient.",
        },
        "regen_optimisation_narrative": {
            "summary": "Candidate accepted for refinement due to pressure drop weakness.",
        },
    }


def test_optimisation_proof_passes_valid_recommendation():
    results = apply_chain(base_ready_results())

    assert results["phase_11b_2i_regen_optimisation_proof_complete"] is True
    assert results["phase_11b_2i_regen_optimisation_proof_history_complete"] is True
    assert results["phase_11b_2i_regen_optimisation_proof_report_complete"] is True
    assert results["phase_11b_2i_regen_optimisation_proof_master_gate_complete"] is True

    assert results["regen_optimisation_proof_status"] == (
        "PASS_REGEN_OPTIMISATION_PROOF_READY"
    )
    assert results["regen_optimisation_proof_master_gate_status"] == (
        "PASS_REGEN_OPTIMISATION_PROOF_GATE_READY"
    )

    proof = results["regen_optimisation_proof"]

    assert proof["proof_score"] >= 0.70
    assert proof["contradictions"] == []
    assert results["regen_rewrite_proof_ready"] is True

    assert results["regen_optimisation_proof_solver_executed"] is False
    assert results["regen_optimisation_proof_live_geometry_modified"] is False
    assert results["regen_optimisation_proof_candidate_committed"] is False


def test_optimisation_proof_detects_contradiction():
    results = base_ready_results()

    results["regen_candidate_accepted"] = True
    results["regen_candidate_rejected"] = True

    results = apply_chain(results)

    assert results["regen_optimisation_proof"]["contradictions"]

    assert (
        results["regen_optimisation_proof_master_gate_ready"]
        is False
    )

    assert (
        results["regen_optimisation_proof_master_gate_status"]
        ==
        "FAIL_REGEN_OPTIMISATION_PROOF_GATE_CONTRADICTIONS"
    )


def test_optimisation_proof_blocks_without_required_gates():
    results = {}

    results = apply_chain(results)

    assert results["regen_optimisation_proof_ready"] is False
    assert results["regen_optimisation_proof_master_gate_ready"] is False


if __name__ == "__main__":
    test_optimisation_proof_passes_valid_recommendation()
    test_optimisation_proof_detects_contradiction()
    test_optimisation_proof_blocks_without_required_gates()
    print("PASS_REGEN_OPTIMISATION_PROOF_SYSTEM_PHASE_11B2I")