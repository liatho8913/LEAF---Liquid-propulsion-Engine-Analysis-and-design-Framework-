from regen_autonomous_geometry_rewrite_engine import (
    attach_regen_autonomous_geometry_rewrite_engine,
)
from regen_autonomous_geometry_rewrite_history_owner import (
    attach_regen_autonomous_geometry_rewrite_history_owner,
)
from regen_autonomous_geometry_rewrite_report_owner import (
    attach_regen_autonomous_geometry_rewrite_report_owner,
)
from regen_autonomous_geometry_rewrite_master_gate import (
    attach_regen_autonomous_geometry_rewrite_master_gate,
)


def apply_chain(results):
    results = attach_regen_autonomous_geometry_rewrite_engine(results)
    results = attach_regen_autonomous_geometry_rewrite_history_owner(results)
    results = attach_regen_autonomous_geometry_rewrite_report_owner(results)
    results = attach_regen_autonomous_geometry_rewrite_master_gate(results)
    return results


def base_ready_results():
    return {
        "regen_optimisation_proof_master_gate_ready": True,
        "regen_rewrite_proof_ready": True,
        "regen_rewrite_proof_score": 0.91,
        "regen_recommendation_explanation": {
            "primary_action": "REDUCE_PRESSURE_DROP",
            "target_parameter": "coolant_channel_width",
            "direction": "increase",
            "expected_effect": "Expected to reduce coolant pressure loss.",
            "risk": "Wider channels may reduce coolant-side heat-transfer coefficient.",
        },
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0012,
        "channel_count": 80,
    }


def test_geometry_rewrite_increases_channel_width_for_pressure_drop():
    results = apply_chain(base_ready_results())

    assert results["phase_11b_2j_regen_autonomous_geometry_rewrite_complete"] is True
    assert results["phase_11b_2j_regen_autonomous_geometry_rewrite_history_complete"] is True
    assert results["phase_11b_2j_regen_autonomous_geometry_rewrite_report_complete"] is True
    assert results["phase_11b_2j_regen_autonomous_geometry_rewrite_master_gate_complete"] is True

    assert results["regen_autonomous_geometry_rewrite_status"] == (
        "PASS_REGEN_AUTONOMOUS_GEOMETRY_REWRITE_READY"
    )
    assert results["regen_autonomous_geometry_rewrite_master_gate_status"] == (
        "PASS_REGEN_AUTONOMOUS_GEOMETRY_REWRITE_GATE_READY"
    )

    patch = results["regen_autonomous_geometry_rewrite_patch"]

    assert "coolant_channel_width" in patch
    assert patch["coolant_channel_width"] > 0.0015

    assert results["regen_geometry_rewrite_candidate_ready"] is True

    assert results["regen_autonomous_geometry_rewrite_solver_executed"] is False
    assert results["regen_autonomous_geometry_rewrite_live_geometry_modified"] is False
    assert results["regen_autonomous_geometry_rewrite_candidate_committed"] is False


def test_geometry_rewrite_adjusts_channel_fit():
    results = base_ready_results()
    results["regen_recommendation_explanation"]["primary_action"] = "FIX_CHANNEL_FIT"
    results["regen_recommendation_explanation"]["target_parameter"] = (
        "channel_count_or_pitch"
    )
    results["regen_recommendation_explanation"]["direction"] = "adjust"

    results = apply_chain(results)

    patch = results["regen_autonomous_geometry_rewrite_patch"]

    assert "channel_count" in patch
    assert "coolant_channel_width" in patch
    assert "rib_width" in patch


def test_geometry_rewrite_blocks_without_proof_gate():
    results = {}

    results = apply_chain(results)

    assert results["regen_autonomous_geometry_rewrite_ready"] is False
    assert results["regen_autonomous_geometry_rewrite_master_gate_ready"] is False


if __name__ == "__main__":
    test_geometry_rewrite_increases_channel_width_for_pressure_drop()
    test_geometry_rewrite_adjusts_channel_fit()
    test_geometry_rewrite_blocks_without_proof_gate()
    print("PASS_REGEN_AUTONOMOUS_GEOMETRY_REWRITE_ENGINE_PHASE_11B2J")