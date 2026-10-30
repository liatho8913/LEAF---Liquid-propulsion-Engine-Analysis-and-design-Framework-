from regen_optimisation_scoring_owner import (
    attach_regen_optimisation_scoring_owner,
    build_regen_optimisation_scoring_owner,
)


def _sample_candidates():
    return [
        {
            "candidate_id": "REGEN-OPT-8B-0001",
            "coolant_channel_count": 72,
            "coolant_channel_width": 0.001275,
            "coolant_channel_height": 0.0017,
            "coolant_rib_width": 0.00085,
            "regen_wall_thickness": 0.001,
            "selection_allowed": False,
        },
        {
            "candidate_id": "REGEN-OPT-8B-0002",
            "coolant_channel_count": 80,
            "coolant_channel_width": 0.0015,
            "coolant_channel_height": 0.002,
            "coolant_rib_width": 0.001,
            "regen_wall_thickness": 0.001,
            "selection_allowed": False,
        },
    ]


def test_phase_8c_scoring_structure_exists_but_is_disabled_by_default():
    results = {
        "phase_8b_regen_optimisation_candidate_generator_complete": True,
        "regen_optimisation_candidate_generator_candidates": _sample_candidates(),
    }

    scoring = build_regen_optimisation_scoring_owner(results)

    assert scoring["regen_optimisation_scoring_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_SCORING_OWNER"
    )
    assert scoring["phase_8c_regen_optimisation_scoring_owner_complete"] is True
    assert scoring["regen_optimisation_scoring_allowed"] is False
    assert scoring["regen_optimisation_scored_candidate_count"] == 0
    assert scoring["regen_optimisation_scoring_automatic_selection_allowed"] is False
    assert scoring["regen_optimisation_scoring_geometry_application_allowed"] is False


def test_phase_8c_scores_candidates_when_enabled_and_phase_8b_complete():
    results = {
        "phase_8b_regen_optimisation_candidate_generator_complete": True,
        "regen_optimisation_scoring_enabled": True,
        "regen_optimisation_candidate_generator_candidates": _sample_candidates(),
    }

    scoring = build_regen_optimisation_scoring_owner(results)

    assert scoring["regen_optimisation_scoring_allowed"] is True
    assert scoring["regen_optimisation_scored_candidate_count"] == 2

    first = scoring["regen_optimisation_scored_candidates"][0]

    assert "thermal_score" in first
    assert "hydraulic_score" in first
    assert "geometry_fit_score" in first
    assert "manufacturability_score" in first
    assert "total_score" in first
    assert first["automatic_selection_allowed"] is False
    assert first["geometry_application_allowed"] is False
    assert first["recommendation_approval_allowed"] is False


def test_phase_8c_blocks_if_phase_8b_missing():
    results = {
        "phase_8b_regen_optimisation_candidate_generator_complete": False,
        "regen_optimisation_scoring_enabled": True,
        "regen_optimisation_candidate_generator_candidates": _sample_candidates(),
    }

    scoring = build_regen_optimisation_scoring_owner(results)

    assert scoring["regen_optimisation_scoring_allowed"] is False
    assert scoring["regen_optimisation_scored_candidate_count"] == 0

    blocking = scoring["regen_optimisation_scoring_blocking_reasons"]

    assert any("Phase 8B" in reason for reason in blocking)


def test_phase_8c_blocks_if_no_candidates_exist():
    results = {
        "phase_8b_regen_optimisation_candidate_generator_complete": True,
        "regen_optimisation_scoring_enabled": True,
        "regen_optimisation_candidate_generator_candidates": [],
    }

    scoring = build_regen_optimisation_scoring_owner(results)

    assert scoring["regen_optimisation_scoring_allowed"] is False
    assert scoring["regen_optimisation_scored_candidate_count"] == 0

    blocking = scoring["regen_optimisation_scoring_blocking_reasons"]

    assert any("No generated candidates" in reason for reason in blocking)


def test_phase_8c_blocks_auto_selection_and_geometry_application_requests():
    results = {
        "phase_8b_regen_optimisation_candidate_generator_complete": True,
        "regen_optimisation_scoring_enabled": True,
        "regen_optimisation_candidate_generator_candidates": _sample_candidates(),
        "regen_optimisation_auto_select_requested": True,
        "regen_optimisation_apply_geometry_requested": True,
    }

    scoring = build_regen_optimisation_scoring_owner(results)

    assert scoring["regen_optimisation_scoring_allowed"] is False
    assert scoring["regen_optimisation_scoring_automatic_selection_allowed"] is False
    assert scoring["regen_optimisation_scoring_geometry_application_allowed"] is False

    blocking = scoring["regen_optimisation_scoring_blocking_reasons"]

    assert any("Automatic geometry selection" in reason for reason in blocking)
    assert any("geometry application" in reason for reason in blocking)


def test_phase_8c_attach_preserves_existing_results():
    results = {
        "thrust": 1000,
        "phase_8b_regen_optimisation_candidate_generator_complete": True,
        "regen_optimisation_candidate_generator_candidates": _sample_candidates(),
    }

    updated = attach_regen_optimisation_scoring_owner(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_8c_regen_optimisation_scoring_owner_complete"] is True
    assert "regen_optimisation_scoring_text" in updated