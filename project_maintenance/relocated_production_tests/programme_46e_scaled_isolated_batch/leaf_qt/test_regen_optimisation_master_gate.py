from regen_optimisation_master_gate import (
    attach_regen_optimisation_master_gate,
    build_regen_optimisation_master_gate,
)


def _complete_results():
    return {
        "phase_8a_regen_optimisation_profile_complete": True,
        "phase_8b_regen_optimisation_candidate_generator_complete": True,
        "phase_8c_regen_optimisation_scoring_owner_complete": True,
        "phase_8d_regen_optimisation_failure_owner_complete": True,
        "phase_8e_regen_optimisation_report_owner_complete": True,
        "phase_8f_regen_optimisation_recommendation_owner_complete": True,
        "regen_optimisation_report_owner_complete": True,
        "regen_optimisation_recommendation_allowed": True,
        "regen_optimisation_blocking_failure_count": 0,
        "regen_optimisation_recommendation_candidate": {
            "candidate_id": "REGEN-OPT-8B-0002",
            "total_score": 0.9,
            "recommendation_rank": 1,
        },
    }


def test_phase_8g_master_gate_passes_when_all_dependencies_are_ready():
    gate = build_regen_optimisation_master_gate(_complete_results())

    assert gate["regen_optimisation_master_gate_status"] == (
        "PASS_REGEN_OPTIMISATION_MASTER_GATE"
    )
    assert gate["regen_optimisation_master_gate_complete"] is True
    assert gate["phase_8g_regen_optimisation_master_gate_complete"] is True
    assert gate["regen_optimisation_master_gate_approval_ready"] is True
    assert gate["regen_optimisation_master_gate_geometry_application_allowed"] is False
    assert gate["regen_optimisation_master_gate_automatic_selection_allowed"] is False


def test_phase_8g_master_gate_fails_if_dependency_missing():
    results = _complete_results()
    results["phase_8c_regen_optimisation_scoring_owner_complete"] = False

    gate = build_regen_optimisation_master_gate(results)

    assert gate["regen_optimisation_master_gate_status"] == (
        "FAIL_REGEN_OPTIMISATION_MASTER_GATE"
    )
    assert gate["regen_optimisation_master_gate_approval_ready"] is False

    reasons = gate["regen_optimisation_master_gate_reasons"]

    assert any("phase_8c" in reason for reason in reasons)


def test_phase_8g_master_gate_fails_if_recommendation_missing():
    results = _complete_results()
    results["regen_optimisation_recommendation_candidate"] = None

    gate = build_regen_optimisation_master_gate(results)

    assert gate["regen_optimisation_master_gate_approval_ready"] is False

    reasons = gate["regen_optimisation_master_gate_reasons"]

    assert any("No recommendation candidate" in reason for reason in reasons)


def test_phase_8g_master_gate_fails_if_blocking_failures_exist():
    results = _complete_results()
    results["regen_optimisation_blocking_failure_count"] = 2

    gate = build_regen_optimisation_master_gate(results)

    assert gate["regen_optimisation_master_gate_approval_ready"] is False

    reasons = gate["regen_optimisation_master_gate_reasons"]

    assert any("Blocking optimisation failures" in reason for reason in reasons)


def test_phase_8g_master_gate_blocks_geometry_application_requests():
    results = _complete_results()
    results["regen_optimisation_apply_geometry_requested"] = True

    gate = build_regen_optimisation_master_gate(results)

    assert gate["regen_optimisation_master_gate_approval_ready"] is False
    assert gate["regen_optimisation_master_gate_geometry_application_allowed"] is False

    reasons = gate["regen_optimisation_master_gate_reasons"]

    assert any("Geometry application" in reason for reason in reasons)


def test_phase_8g_attach_preserves_existing_results():
    results = _complete_results()
    results["thrust"] = 1000

    updated = attach_regen_optimisation_master_gate(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_8g_regen_optimisation_master_gate_complete"] is True
    assert "regen_optimisation_master_gate_text" in updated