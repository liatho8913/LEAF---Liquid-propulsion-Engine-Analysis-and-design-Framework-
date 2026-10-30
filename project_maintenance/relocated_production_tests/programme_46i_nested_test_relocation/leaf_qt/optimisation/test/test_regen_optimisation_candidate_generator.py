from regen_optimisation_candidate_generator import (
    attach_regen_optimisation_candidate_generator,
    build_regen_optimisation_candidate_generator,
)


def test_phase_8b_generator_structure_exists_but_generation_is_disabled_by_default():
    results = {
        "phase_8a_regen_optimisation_profile_complete": True,
    }

    generated = build_regen_optimisation_candidate_generator(results)

    assert generated["regen_optimisation_candidate_generator_status"] == (
        "PASS_REGEN_OPTIMISATION_CANDIDATE_GENERATOR"
    )
    assert generated["phase_8b_regen_optimisation_candidate_generator_complete"] is True
    assert generated["regen_optimisation_candidate_generator_generation_allowed"] is False
    assert generated["regen_optimisation_candidate_generator_candidate_count"] == 0
    assert generated["regen_optimisation_candidate_generator_scoring_allowed"] is False
    assert generated["regen_optimisation_candidate_generator_automatic_selection_allowed"] is False


def test_phase_8b_generates_reproducible_candidates_when_enabled_and_phase_8a_complete():
    results = {
        "phase_8a_regen_optimisation_profile_complete": True,
        "regen_optimisation_candidate_generation_enabled": True,
        "coolant_channel_count": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "coolant_rib_width": 0.0010,
        "regen_wall_thickness": 0.0010,
    }

    first = build_regen_optimisation_candidate_generator(results)
    second = build_regen_optimisation_candidate_generator(results)

    assert first["regen_optimisation_candidate_generator_generation_allowed"] is True
    assert first["regen_optimisation_candidate_generator_candidate_count"] == 81
    assert first["regen_optimisation_candidate_generator_candidates"] == (
        second["regen_optimisation_candidate_generator_candidates"]
    )

    first_candidate = first["regen_optimisation_candidate_generator_candidates"][0]

    assert first_candidate["candidate_id"] == "REGEN-OPT-8B-0001"
    assert first_candidate["scoring_allowed"] is False
    assert first_candidate["automatic_selection_allowed"] is False
    assert first_candidate["selection_allowed"] is False


def test_phase_8b_blocks_generation_if_phase_8a_is_missing():
    results = {
        "regen_optimisation_candidate_generation_enabled": True,
        "phase_8a_regen_optimisation_profile_complete": False,
    }

    generated = build_regen_optimisation_candidate_generator(results)

    assert generated["regen_optimisation_candidate_generator_generation_allowed"] is False
    assert generated["regen_optimisation_candidate_generator_candidate_count"] == 0

    blocking = generated["regen_optimisation_candidate_generator_blocking_reasons"]

    assert any("Phase 8A" in reason for reason in blocking)


def test_phase_8b_blocks_scoring_and_auto_selection_requests():
    results = {
        "phase_8a_regen_optimisation_profile_complete": True,
        "regen_optimisation_candidate_generation_enabled": True,
        "regen_optimisation_scoring_requested": True,
        "regen_optimisation_auto_select_requested": True,
    }

    generated = build_regen_optimisation_candidate_generator(results)

    assert generated["regen_optimisation_candidate_generator_generation_allowed"] is False
    assert generated["regen_optimisation_candidate_generator_candidate_count"] == 0
    assert generated["regen_optimisation_candidate_generator_scoring_allowed"] is False
    assert generated["regen_optimisation_candidate_generator_automatic_selection_allowed"] is False

    blocking = generated["regen_optimisation_candidate_generator_blocking_reasons"]

    assert any("Phase 8C" in reason for reason in blocking)
    assert any("Automatic geometry selection" in reason for reason in blocking)


def test_phase_8b_attach_preserves_existing_results():
    results = {
        "thrust": 1000,
        "phase_8a_regen_optimisation_profile_complete": True,
    }

    updated = attach_regen_optimisation_candidate_generator(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_8b_regen_optimisation_candidate_generator_complete"] is True
    assert "regen_optimisation_candidate_generator_text" in updated