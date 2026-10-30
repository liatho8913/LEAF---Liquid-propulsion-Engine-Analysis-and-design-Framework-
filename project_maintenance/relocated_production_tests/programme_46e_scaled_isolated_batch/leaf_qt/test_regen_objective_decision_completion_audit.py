from regen_objective_decision_completion_audit import (
    attach_regen_objective_decision_completion_audit,
)


def build_complete_results():
    return {
        "phase_11b_2o_regen_automatic_geometry_objective_selector_complete": True,
        "phase_11b_2p_regen_objective_weight_owner_complete": True,
        "phase_11b_2n_regen_automatic_geometry_decision_owner_complete": True,
        "phase_11b_2q_regen_objective_decision_report_owner_complete": True,
        "phase_11b_2r_regen_objective_decision_report_registration_owner_complete": True,
        "regen_objective_decision_report_registered": True,

        "regen_automatic_geometry_objective": "BALANCED",
        "regen_objective_weight_map": {"geometry": 0.25, "thermal": 0.25},
        "regen_automatic_geometry_decision": "CONTINUE_OPTIMISING",
        "regen_automatic_geometry_decision_score": 0.75,
        "regen_objective_decision_report": "Example report.",
        "foundation_report_viewer_bundle": {
            "reports": {
                "regen_objective_decision_report": {
                    "title": "Regen Objective Decision Report",
                    "text": "Example report.",
                }
            }
        },

        "regen_automatic_geometry_objective_solver_executed": False,
        "regen_automatic_geometry_objective_live_geometry_modified": False,
        "regen_automatic_geometry_objective_candidate_committed": False,
        "regen_objective_weight_solver_executed": False,
        "regen_objective_weight_live_geometry_modified": False,
        "regen_objective_weight_candidate_committed": False,
        "regen_automatic_geometry_decision_solver_executed": False,
        "regen_automatic_geometry_decision_live_geometry_modified": False,
        "regen_automatic_geometry_decision_candidate_committed": False,
        "regen_objective_decision_report_solver_executed": False,
        "regen_objective_decision_report_live_geometry_modified": False,
        "regen_objective_decision_report_candidate_committed": False,
        "regen_objective_decision_report_registration_solver_executed": False,
        "regen_objective_decision_report_registration_live_geometry_modified": False,
        "regen_objective_decision_report_registration_candidate_committed": False,
    }


def test_objective_decision_completion_audit_passes_complete_stack():
    results = attach_regen_objective_decision_completion_audit(
        build_complete_results()
    )

    assert results["phase_11b_2s_regen_objective_decision_completion_audit_complete"] is True
    assert results["regen_objective_decision_stack_complete"] is True
    assert results["regen_objective_decision_completion_audit_ready"] is True
    assert results["regen_objective_decision_completion_audit_status"] == (
        "PASS_REGEN_OBJECTIVE_DECISION_COMPLETION_AUDIT"
    )


def test_objective_decision_completion_audit_fails_missing_report_registration():
    results = build_complete_results()
    del results["foundation_report_viewer_bundle"]["reports"][
        "regen_objective_decision_report"
    ]

    results = attach_regen_objective_decision_completion_audit(results)

    assert results["regen_objective_decision_stack_complete"] is False
    assert results["regen_objective_decision_completion_missing_values"]


def test_objective_decision_completion_audit_fails_safety_violation():
    results = build_complete_results()
    results["regen_automatic_geometry_decision_live_geometry_modified"] = True

    results = attach_regen_objective_decision_completion_audit(results)

    assert results["regen_objective_decision_stack_complete"] is False
    assert results["regen_objective_decision_completion_safety_violations"]


if __name__ == "__main__":
    test_objective_decision_completion_audit_passes_complete_stack()
    test_objective_decision_completion_audit_fails_missing_report_registration()
    test_objective_decision_completion_audit_fails_safety_violation()
    print("PASS_REGEN_OBJECTIVE_DECISION_COMPLETION_AUDIT_PHASE_11B2S")