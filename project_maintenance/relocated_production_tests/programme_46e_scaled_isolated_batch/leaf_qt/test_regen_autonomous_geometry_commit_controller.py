from regen_autonomous_geometry_commit_controller import (
    attach_regen_autonomous_geometry_commit_controller,
)
from regen_autonomous_geometry_commit_history_owner import (
    attach_regen_autonomous_geometry_commit_history_owner,
)
from regen_autonomous_geometry_commit_report_owner import (
    attach_regen_autonomous_geometry_commit_report_owner,
)
from regen_autonomous_geometry_commit_master_gate import (
    attach_regen_autonomous_geometry_commit_master_gate,
)


def apply_chain(results):
    results = attach_regen_autonomous_geometry_commit_controller(results)
    results = attach_regen_autonomous_geometry_commit_history_owner(results)
    results = attach_regen_autonomous_geometry_commit_report_owner(results)
    results = attach_regen_autonomous_geometry_commit_master_gate(results)
    return results


def base_ready_results():
    return {
        "regen_autonomous_geometry_rewrite_master_gate_ready": True,
        "regen_autonomous_geometry_rewrite": {
            "base_geometry": {
                "coolant_channel_width": 0.0015,
                "coolant_channel_height": 0.0020,
                "rib_width": 0.0010,
                "hot_gas_wall_thickness": 0.0012,
                "channel_count": 80,
            },
            "patch": {
                "coolant_channel_width": 0.00165,
            },
        },
        "regen_autonomous_geometry_rewrite_patch": {
            "coolant_channel_width": 0.00165,
        },
        "regen_geometry_rewrite_candidate_patch": {
            "coolant_channel_width": 0.00165,
        },
    }


def test_geometry_commit_stages_safe_patch():
    results = apply_chain(base_ready_results())

    assert results["phase_11b_2k_regen_autonomous_geometry_commit_complete"] is True
    assert results["phase_11b_2k_regen_autonomous_geometry_commit_history_complete"] is True
    assert results["phase_11b_2k_regen_autonomous_geometry_commit_report_complete"] is True
    assert results["phase_11b_2k_regen_autonomous_geometry_commit_master_gate_complete"] is True

    assert results["regen_autonomous_geometry_commit_status"] == (
        "PASS_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_READY"
    )
    assert results["regen_autonomous_geometry_commit_master_gate_status"] == (
        "PASS_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_GATE_READY"
    )

    assert results["regen_geometry_commit_candidate_ready"] is True
    assert results["regen_geometry_commit_requires_user_acceptance"] is True

    staged = results["regen_autonomous_geometry_staged_candidate"]
    assert staged["staged_geometry"]["coolant_channel_width"] == 0.00165
    assert staged["rollback_geometry"]["coolant_channel_width"] == 0.0015
    assert staged["committed"] is False

    assert results["regen_autonomous_geometry_commit_solver_executed"] is False
    assert results["regen_autonomous_geometry_commit_live_geometry_modified"] is False
    assert results["regen_autonomous_geometry_commit_candidate_committed"] is False


def test_geometry_commit_blocks_unsafe_large_patch():
    results = base_ready_results()
    results["regen_geometry_rewrite_candidate_patch"] = {
        "coolant_channel_width": 0.0040,
    }

    results = apply_chain(results)

    assert results["regen_autonomous_geometry_commit_ready"] is False
    assert results["regen_autonomous_geometry_commit_master_gate_ready"] is False
    assert results["regen_autonomous_geometry_commit_review"]["issues"]


def test_geometry_commit_blocks_without_rewrite_gate():
    results = {}

    results = apply_chain(results)

    assert results["regen_autonomous_geometry_commit_ready"] is False
    assert results["regen_autonomous_geometry_commit_master_gate_ready"] is False


if __name__ == "__main__":
    test_geometry_commit_stages_safe_patch()
    test_geometry_commit_blocks_unsafe_large_patch()
    test_geometry_commit_blocks_without_rewrite_gate()
    print("PASS_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_CONTROLLER_PHASE_11B2K")