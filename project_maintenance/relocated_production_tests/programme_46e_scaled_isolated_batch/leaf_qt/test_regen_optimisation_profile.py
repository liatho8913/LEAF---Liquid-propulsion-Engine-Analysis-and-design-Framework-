from regen_optimisation_profile import (
    attach_regen_optimisation_profile,
    build_regen_optimisation_profile,
)


def test_phase_8a_profile_builds_without_enabling_optimisation():
    results = {
        "stage_u_regen_validation_complete": True,
        "stage_v_scalability_complete": True,
        "stage_w_real_engine_benchmarking_complete": True,
    }

    profile = build_regen_optimisation_profile(results)

    assert profile["regen_optimisation_profile_status"] == "PASS_REGEN_OPTIMISATION_PROFILE"
    assert profile["phase_8a_regen_optimisation_profile_complete"] is True
    assert profile["regen_optimisation_profile_candidate_generation_allowed"] is False
    assert profile["regen_optimisation_profile_candidate_scoring_allowed"] is False
    assert profile["regen_optimisation_profile_automatic_selection_allowed"] is False


def test_phase_8a_blocks_automatic_selection_requests():
    profile = build_regen_optimisation_profile({
        "regen_optimisation_enabled": True,
        "regen_optimisation_candidate_generation_requested": True,
        "regen_optimisation_scoring_requested": True,
        "regen_optimisation_auto_select_requested": True,
    })

    blocking = profile["regen_optimisation_profile_blocking_reasons"]

    assert profile["regen_optimisation_profile_status"] == "PASS_REGEN_OPTIMISATION_PROFILE"
    assert profile["regen_optimisation_profile_automatic_selection_allowed"] is False
    assert any("not permitted in Phase 8A" in item for item in blocking)
    assert any("Phase 8B" in item for item in blocking)
    assert any("Phase 8C" in item for item in blocking)


def test_phase_8a_attach_preserves_existing_results():
    results = {
        "thrust": 1000,
    }

    updated = attach_regen_optimisation_profile(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_8a_regen_optimisation_profile_complete"] is True
    assert "regen_optimisation_profile_text" in updated