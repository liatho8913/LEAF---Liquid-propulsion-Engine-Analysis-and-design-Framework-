from regen_candidate_rejection_owner import (
    attach_regen_candidate_rejection_owner,
)
from regen_candidate_rejection_history_owner import (
    attach_regen_candidate_rejection_history_owner,
)
from regen_candidate_rejection_report_owner import (
    attach_regen_candidate_rejection_report_owner,
)
from regen_candidate_rejection_master_gate import (
    attach_regen_candidate_rejection_master_gate,
)


def apply_chain(results):
    results = attach_regen_candidate_rejection_owner(results)
    results = attach_regen_candidate_rejection_history_owner(results)
    results = attach_regen_candidate_rejection_report_owner(results)
    results = attach_regen_candidate_rejection_master_gate(results)
    return results


def base_ready_results():
    return {
        "regen_optimisation_narrative_master_gate_ready": True,
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
            "weakest_objective": {
                "name": "manufacturability",
                "score": 75.0,
            },
        },
    }


def test_candidate_rejection_keeps_strong_candidate():
    results = apply_chain(base_ready_results())

    assert results["phase_11b_2f_regen_candidate_rejection_complete"] is True
    assert results["phase_11b_2f_regen_candidate_rejection_history_complete"] is True
    assert results["phase_11b_2f_regen_candidate_rejection_report_complete"] is True
    assert results["phase_11b_2f_regen_candidate_rejection_master_gate_complete"] is True

    assert results["regen_candidate_rejection_status"] == (
        "PASS_REGEN_CANDIDATE_REJECTION_READY"
    )
    assert results["regen_candidate_rejection_master_gate_status"] == (
        "PASS_REGEN_CANDIDATE_REJECTION_GATE_READY"
    )

    assert results["regen_candidate_rejected"] is False
    assert results["regen_candidate_rejection_decision"] == "KEEP_CANDIDATE"
    assert results["regen_candidate_survives_rejection_gate"] is True

    assert results["regen_candidate_rejection_solver_executed"] is False
    assert results["regen_candidate_rejection_live_geometry_modified"] is False
    assert results["regen_candidate_rejection_candidate_committed"] is False


def test_candidate_rejection_rejects_critical_pressure_drop():
    results = base_ready_results()
    results["regen_multi_objective_total_score"] = 42.0
    results["regen_multi_objective_scores"]["pressure_drop"] = 20.0
    results["regen_optimisation_narrative"]["decision"] = "CANDIDATE_REJECT_OR_RECOVER"
    results["regen_optimisation_narrative"]["weakest_objective"] = {
        "name": "pressure_drop",
        "score": 20.0,
    }

    results = apply_chain(results)

    assert results["regen_candidate_rejected"] is True
    assert results["regen_candidate_rejection_decision"] == "REJECT_CANDIDATE"
    assert results["regen_candidate_rejection_severity"] == "HIGH"
    assert results["regen_candidate_rejection_category"] == "pressure_drop"
    assert results["regen_candidate_rejection_recovery_action"] == (
        "RECOVER_BY_REDUCING_PRESSURE_DROP"
    )


def test_candidate_rejection_refines_mid_score_candidate():
    results = base_ready_results()
    results["regen_multi_objective_total_score"] = 62.0
    results["regen_multi_objective_scores"]["geometry_fit"] = 55.0
    results["regen_optimisation_narrative"]["decision"] = (
        "CANDIDATE_NEEDS_REFINEMENT"
    )
    results["regen_optimisation_narrative"]["weakest_objective"] = {
        "name": "geometry_fit",
        "score": 55.0,
    }

    results = apply_chain(results)

    assert results["regen_candidate_rejected"] is False
    assert results["regen_candidate_rejection_decision"] == "REFINE_CANDIDATE"
    assert results["regen_candidate_rejection_severity"] == "MEDIUM"
    assert results["regen_candidate_rejection_recovery_action"] == (
        "RECOVER_BY_FIXING_CHANNEL_FIT"
    )


def test_candidate_rejection_blocks_without_narrative_gate():
    results = {}

    results = apply_chain(results)

    assert results["regen_candidate_rejection_ready"] is False
    assert results["regen_candidate_rejection_master_gate_ready"] is False


if __name__ == "__main__":
    test_candidate_rejection_keeps_strong_candidate()
    test_candidate_rejection_rejects_critical_pressure_drop()
    test_candidate_rejection_refines_mid_score_candidate()
    test_candidate_rejection_blocks_without_narrative_gate()
    print("PASS_REGEN_CANDIDATE_REJECTION_OWNER_PHASE_11B2F")