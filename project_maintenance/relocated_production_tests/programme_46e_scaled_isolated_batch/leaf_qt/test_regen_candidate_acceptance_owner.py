from regen_candidate_acceptance_owner import (
    attach_regen_candidate_acceptance_owner,
)
from regen_candidate_acceptance_history_owner import (
    attach_regen_candidate_acceptance_history_owner,
)
from regen_candidate_acceptance_report_owner import (
    attach_regen_candidate_acceptance_report_owner,
)
from regen_candidate_acceptance_master_gate import (
    attach_regen_candidate_acceptance_master_gate,
)


def apply_chain(results):
    results = attach_regen_candidate_acceptance_owner(results)
    results = attach_regen_candidate_acceptance_history_owner(results)
    results = attach_regen_candidate_acceptance_report_owner(results)
    results = attach_regen_candidate_acceptance_master_gate(results)
    return results


def base_ready_results():
    return {
        "regen_candidate_rejection_master_gate_ready": True,
        "regen_candidate_rejected": False,
        "regen_candidate_rejection_decision": "KEEP_CANDIDATE",
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
        "regen_optimisation_narrative": {
            "decision": "CANDIDATE_STRONG_ACCEPTABLE",
        },
    }


def test_candidate_acceptance_accepts_strong_candidate():
    results = apply_chain(base_ready_results())

    assert results["phase_11b_2g_regen_candidate_acceptance_complete"] is True
    assert results["phase_11b_2g_regen_candidate_acceptance_history_complete"] is True
    assert results["phase_11b_2g_regen_candidate_acceptance_report_complete"] is True
    assert results["phase_11b_2g_regen_candidate_acceptance_master_gate_complete"] is True

    assert results["regen_candidate_acceptance_status"] == (
        "PASS_REGEN_CANDIDATE_ACCEPTANCE_READY"
    )
    assert results["regen_candidate_acceptance_master_gate_status"] == (
        "PASS_REGEN_CANDIDATE_ACCEPTANCE_GATE_READY"
    )

    assert results["regen_candidate_accepted"] is True
    assert results["regen_candidate_acceptance_decision"] == (
        "ACCEPT_STRONG_CANDIDATE"
    )
    assert results["regen_candidate_acceptance_class"] == "STRONG"
    assert results["regen_candidate_ready_for_geometry_rewrite"] is True

    assert results["regen_candidate_acceptance_solver_executed"] is False
    assert results["regen_candidate_acceptance_live_geometry_modified"] is False
    assert results["regen_candidate_acceptance_candidate_committed"] is False


def test_candidate_acceptance_accepts_for_refinement():
    results = base_ready_results()
    results["regen_multi_objective_total_score"] = 74.0
    results["regen_multi_objective_scores"]["manufacturability"] = 58.0
    results["regen_optimisation_narrative"]["decision"] = (
        "CANDIDATE_ACCEPTABLE_WITH_WARNINGS"
    )
    results["regen_candidate_rejection_decision"] = "REFINE_CANDIDATE"

    results = apply_chain(results)

    assert results["regen_candidate_accepted"] is True
    assert results["regen_candidate_acceptance_decision"] == "ACCEPT_FOR_REFINEMENT"
    assert results["regen_candidate_acceptance_class"] == "REFINEMENT"
    assert results["regen_candidate_ready_for_refinement"] is True


def test_candidate_acceptance_blocks_rejected_candidate():
    results = base_ready_results()
    results["regen_candidate_rejected"] = True
    results["regen_candidate_rejection_decision"] = "REJECT_CANDIDATE"

    results = apply_chain(results)

    assert results["regen_candidate_accepted"] is False
    assert results["regen_candidate_acceptance_decision"] == (
        "BLOCK_ACCEPTANCE_REJECTED"
    )
    assert results["regen_candidate_ready_for_geometry_rewrite"] is False


def test_candidate_acceptance_blocks_without_rejection_gate():
    results = {}

    results = apply_chain(results)

    assert results["regen_candidate_acceptance_ready"] is False
    assert results["regen_candidate_acceptance_master_gate_ready"] is False


if __name__ == "__main__":
    test_candidate_acceptance_accepts_strong_candidate()
    test_candidate_acceptance_accepts_for_refinement()
    test_candidate_acceptance_blocks_rejected_candidate()
    test_candidate_acceptance_blocks_without_rejection_gate()
    print("PASS_REGEN_CANDIDATE_ACCEPTANCE_OWNER_PHASE_11B2G")