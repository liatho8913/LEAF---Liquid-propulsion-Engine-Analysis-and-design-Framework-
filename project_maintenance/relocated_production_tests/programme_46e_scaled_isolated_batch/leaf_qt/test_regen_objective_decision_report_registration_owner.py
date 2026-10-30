from regen_objective_decision_report_registration_owner import (
    attach_regen_objective_decision_report_registration_owner,
)


def test_objective_decision_report_registration_owner_registers_report():
    results = {
        "regen_objective_decision_report": "Example decision report.",
        "foundation_report_viewer_bundle": {
            "reports": {}
        },
    }

    results = attach_regen_objective_decision_report_registration_owner(results)

    assert results[
        "phase_11b_2r_regen_objective_decision_report_registration_owner_complete"
    ] is True

    assert results["regen_objective_decision_report_registered"] is True
    assert results["regen_objective_decision_report_registration_status"] == (
        "PASS_REGEN_OBJECTIVE_DECISION_REPORT_REGISTERED"
    )

    reports = results["foundation_report_viewer_bundle"]["reports"]

    assert "regen_objective_decision_report" in reports
    assert reports["regen_objective_decision_report"]["text"] == (
        "Example decision report."
    )

    assert (
        results["regen_objective_decision_report_registration_solver_executed"]
        is False
    )
    assert (
        results[
            "regen_objective_decision_report_registration_live_geometry_modified"
        ]
        is False
    )
    assert (
        results[
            "regen_objective_decision_report_registration_candidate_committed"
        ]
        is False
    )


if __name__ == "__main__":
    test_objective_decision_report_registration_owner_registers_report()
    print("PASS_REGEN_OBJECTIVE_DECISION_REPORT_REGISTRATION_OWNER_PHASE_11B2R")