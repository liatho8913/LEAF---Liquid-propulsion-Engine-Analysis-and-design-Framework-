from regen_automatic_geometry_decision_owner import (
    attach_regen_automatic_geometry_decision_owner,
)


def test_automatic_geometry_decision_accepts_valid_candidate():
    results = {
        "regen_geometry_commit_staged_geometry": {
            "coolant_channel_width": 0.0017,
            "coolant_channel_height": 0.0022,
            "rib_width": 0.0010,
            "channel_count": 72,
        },
        "regen_autonomous_geometry_commit_master_gate_ready": True,
        "channel_geometry_valid": 1,
        "thermal_margin_pass": 1,
        "pressure_drop_pass": 1,
        "coolant_reynolds_pass": 1,
        "manufacturability_pass": True,
        "minimum_mass_pass": True,
        "regen_optimisation_objective": "BALANCED",
    }

    results = attach_regen_automatic_geometry_decision_owner(results)

    assert results["phase_11b_2n_regen_automatic_geometry_decision_owner_complete"] is True
    assert results["regen_automatic_geometry_decision"] == "ACCEPT_AUTOMATIC_GEOMETRY"
    assert results["regen_automatic_geometry_decision_ready"] is True
    assert results["regen_automatic_geometry_decision_score"] >= 0.80

    assert results["regen_automatic_geometry_decision_solver_executed"] is False
    assert results["regen_automatic_geometry_decision_live_geometry_modified"] is False
    assert results["regen_automatic_geometry_decision_candidate_committed"] is False


def test_automatic_geometry_decision_continues_without_candidate():
    results = {}

    results = attach_regen_automatic_geometry_decision_owner(results)

    assert results["regen_automatic_geometry_decision"] == "CONTINUE_OPTIMISING"
    assert results["regen_automatic_geometry_decision_ready"] is False
    assert results["regen_automatic_geometry_decision_blockers"]


def test_automatic_geometry_decision_rejects_bad_candidate():
    results = {
        "regen_geometry_commit_staged_geometry": {
            "coolant_channel_width": 0.0001,
        },
        "regen_autonomous_geometry_commit_master_gate_ready": False,
        "channel_geometry_valid": 0,
        "thermal_margin_pass": 0,
        "pressure_drop_pass": 0,
        "coolant_reynolds_pass": 0,
    }

    results = attach_regen_automatic_geometry_decision_owner(results)

    assert results["regen_automatic_geometry_decision"] == "REJECT_AUTOMATIC_GEOMETRY"
    assert results["regen_automatic_geometry_decision_ready"] is False
    assert results["regen_automatic_geometry_decision_score"] < 0.55


if __name__ == "__main__":
    test_automatic_geometry_decision_accepts_valid_candidate()
    test_automatic_geometry_decision_continues_without_candidate()
    test_automatic_geometry_decision_rejects_bad_candidate()
    print("PASS_REGEN_AUTOMATIC_GEOMETRY_DECISION_OWNER_PHASE_11B2N")