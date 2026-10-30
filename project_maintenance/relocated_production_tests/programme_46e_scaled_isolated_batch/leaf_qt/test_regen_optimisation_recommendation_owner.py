from regen_optimisation_recommendation_owner import (
    attach_regen_optimisation_recommendation_owner,
    build_regen_optimisation_recommendation_owner,
)


def _scored_candidates():
    return [
        {
            "candidate_id": "REGEN-OPT-8B-0001",
            "thermal_score": 0.70,
            "hydraulic_score": 0.70,
            "geometry_fit_score": 0.70,
            "manufacturability_score": 0.70,
            "total_score": 0.70,
        },
        {
            "candidate_id": "REGEN-OPT-8B-0002",
            "thermal_score": 0.95,
            "hydraulic_score": 0.90,
            "geometry_fit_score": 0.85,
            "manufacturability_score": 0.80,
            "total_score": 0.90,
        },
    ]


def test_phase_8f_recommendation_structure_exists_but_disabled_by_default():
    results = {
        "phase_8e_regen_optimisation_report_owner_complete": True,
        "regen_optimisation_scored_candidates": _scored_candidates(),
        "regen_optimisation_blocking_failure_count": 0,
    }

    recommendation = build_regen_optimisation_recommendation_owner(results)

    assert recommendation["regen_optimisation_recommendation_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_RECOMMENDATION_OWNER"
    )
    assert recommendation["phase_8f_regen_optimisation_recommendation_owner_complete"] is True
    assert recommendation["regen_optimisation_recommendation_allowed"] is False
    assert recommendation["regen_optimisation_recommendation_candidate"] is None
    assert recommendation["regen_optimisation_recommendation_approval_allowed"] is False
    assert recommendation["regen_optimisation_recommendation_automatic_selection_allowed"] is False
    assert recommendation["regen_optimisation_recommendation_geometry_application_allowed"] is False


def test_phase_8f_recommends_highest_scored_candidate_when_enabled():
    results = {
        "phase_8e_regen_optimisation_report_owner_complete": True,
        "regen_optimisation_recommendation_enabled": True,
        "regen_optimisation_scored_candidates": _scored_candidates(),
        "regen_optimisation_blocking_failure_count": 0,
    }

    recommendation = build_regen_optimisation_recommendation_owner(results)

    assert recommendation["regen_optimisation_recommendation_allowed"] is True
    assert recommendation["regen_optimisation_recommendation_ranked_candidate_count"] == 2

    candidate = recommendation["regen_optimisation_recommendation_candidate"]

    assert candidate["candidate_id"] == "REGEN-OPT-8B-0002"
    assert candidate["recommendation_rank"] == 1
    assert candidate["recommendation_approval_allowed"] is False
    assert candidate["automatic_selection_allowed"] is False
    assert candidate["geometry_application_allowed"] is False


def test_phase_8f_blocks_if_phase_8e_missing():
    results = {
        "phase_8e_regen_optimisation_report_owner_complete": False,
        "regen_optimisation_recommendation_enabled": True,
        "regen_optimisation_scored_candidates": _scored_candidates(),
        "regen_optimisation_blocking_failure_count": 0,
    }

    recommendation = build_regen_optimisation_recommendation_owner(results)

    assert recommendation["regen_optimisation_recommendation_allowed"] is False
    assert recommendation["regen_optimisation_recommendation_candidate"] is None

    blocking = recommendation["regen_optimisation_recommendation_blocking_reasons"]

    assert any("Phase 8E" in reason for reason in blocking)


def test_phase_8f_blocks_if_no_scored_candidates_exist():
    results = {
        "phase_8e_regen_optimisation_report_owner_complete": True,
        "regen_optimisation_recommendation_enabled": True,
        "regen_optimisation_scored_candidates": [],
        "regen_optimisation_blocking_failure_count": 0,
    }

    recommendation = build_regen_optimisation_recommendation_owner(results)

    assert recommendation["regen_optimisation_recommendation_allowed"] is False
    assert recommendation["regen_optimisation_recommendation_candidate"] is None

    blocking = recommendation["regen_optimisation_recommendation_blocking_reasons"]

    assert any("No scored candidates" in reason for reason in blocking)


def test_phase_8f_blocks_if_blocking_failures_exist():
    results = {
        "phase_8e_regen_optimisation_report_owner_complete": True,
        "regen_optimisation_recommendation_enabled": True,
        "regen_optimisation_scored_candidates": _scored_candidates(),
        "regen_optimisation_blocking_failure_count": 2,
    }

    recommendation = build_regen_optimisation_recommendation_owner(results)

    assert recommendation["regen_optimisation_recommendation_allowed"] is False
    assert recommendation["regen_optimisation_recommendation_candidate"] is None

    blocking = recommendation["regen_optimisation_recommendation_blocking_reasons"]

    assert any("Blocking optimisation failures" in reason for reason in blocking)


def test_phase_8f_blocks_auto_selection_and_geometry_application_requests():
    results = {
        "phase_8e_regen_optimisation_report_owner_complete": True,
        "regen_optimisation_recommendation_enabled": True,
        "regen_optimisation_scored_candidates": _scored_candidates(),
        "regen_optimisation_blocking_failure_count": 0,
        "regen_optimisation_auto_select_requested": True,
        "regen_optimisation_apply_geometry_requested": True,
    }

    recommendation = build_regen_optimisation_recommendation_owner(results)

    assert recommendation["regen_optimisation_recommendation_allowed"] is False
    assert recommendation["regen_optimisation_recommendation_automatic_selection_allowed"] is False
    assert recommendation["regen_optimisation_recommendation_geometry_application_allowed"] is False

    blocking = recommendation["regen_optimisation_recommendation_blocking_reasons"]

    assert any("Automatic geometry selection" in reason for reason in blocking)
    assert any("Automatic geometry application" in reason for reason in blocking)


def test_phase_8f_attach_preserves_existing_results():
    results = {
        "thrust": 1000,
        "phase_8e_regen_optimisation_report_owner_complete": True,
        "regen_optimisation_recommendation_enabled": True,
        "regen_optimisation_scored_candidates": _scored_candidates(),
        "regen_optimisation_blocking_failure_count": 0,
    }

    updated = attach_regen_optimisation_recommendation_owner(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_8f_regen_optimisation_recommendation_owner_complete"] is True
    assert "regen_optimisation_recommendation_text" in updated