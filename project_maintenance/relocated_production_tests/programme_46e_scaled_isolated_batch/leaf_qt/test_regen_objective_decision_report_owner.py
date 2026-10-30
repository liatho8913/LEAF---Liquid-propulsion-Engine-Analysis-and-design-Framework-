from regen_objective_decision_report_owner import (
    attach_regen_objective_decision_report_owner,
)


def test_objective_decision_report_owner_builds_report():
    results = {
        "regen_automatic_geometry_objective": "THERMAL",
        "regen_automatic_geometry_decision": "CONTINUE_OPTIMISING",
        "regen_automatic_geometry_decision_status": (
            "WARN_AUTOMATIC_GEOMETRY_DECISION_CONTINUE"
        ),
        "regen_automatic_geometry_decision_score": 0.72,
        "regen_automatic_geometry_decision_reason": (
            "Candidate is promising but does not satisfy all gates."
        ),
        "regen_automatic_geometry_decision_blockers": [
            "Thermal validation is failing.",
        ],
        "regen_objective_weight_map": {
            "thermal": 0.45,
            "geometry": 0.15,
        },
        "regen_geometry_commit_staged_geometry": {
            "coolant_channel_width": 0.0018,
        },
    }

    results = attach_regen_objective_decision_report_owner(results)

    assert results["phase_11b_2q_regen_objective_decision_report_owner_complete"] is True
    assert results["regen_objective_decision_report_status"] == (
        "PASS_REGEN_OBJECTIVE_DECISION_REPORT_READY"
    )

    report = results["regen_objective_decision_report"]

    assert "Objective: THERMAL" in report
    assert "Decision: CONTINUE_OPTIMISING" in report
    assert "thermal: 0.45" in report
    assert "Thermal validation is failing." in report
    assert "coolant_channel_width" in report

    assert results["regen_objective_decision_report_solver_executed"] is False
    assert results["regen_objective_decision_report_live_geometry_modified"] is False
    assert results["regen_objective_decision_report_candidate_committed"] is False


if __name__ == "__main__":
    test_objective_decision_report_owner_builds_report()
    print("PASS_REGEN_OBJECTIVE_DECISION_REPORT_OWNER_PHASE_11B2Q")