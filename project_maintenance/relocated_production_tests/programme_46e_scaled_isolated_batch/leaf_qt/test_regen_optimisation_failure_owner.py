from regen_optimisation_failure_owner import (
    attach_regen_optimisation_failure_owner,
    build_regen_optimisation_failure_owner,
)


def test_phase_8d_reports_no_active_failures_when_no_blockers_exist():
    results = {}

    failure = build_regen_optimisation_failure_owner(results)

    assert failure["regen_optimisation_failure_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_FAILURE_OWNER"
    )
    assert failure["phase_8d_regen_optimisation_failure_owner_complete"] is True
    assert failure["regen_optimisation_failure_count"] == 1
    assert failure["regen_optimisation_blocking_failure_count"] == 0
    assert failure["regen_optimisation_failure_selection_locked"] is True
    assert failure["regen_optimisation_failure_geometry_application_locked"] is True


def test_phase_8d_converts_profile_blockers_to_failure_items():
    results = {
        "regen_optimisation_profile_blocking_reasons": [
            "Automatic optimisation is not permitted in Phase 8A; this phase only defines the optimisation profile."
        ],
    }

    failure = build_regen_optimisation_failure_owner(results)

    assert failure["regen_optimisation_blocking_failure_count"] == 1

    item = failure["regen_optimisation_failure_items"][0]

    assert item["source"] == "profile"
    assert item["phase"] == "8A"
    assert item["blocks_recommendation"] is True
    assert item["blocks_selection"] is True
    assert item["blocks_geometry_application"] is True


def test_phase_8d_converts_candidate_generator_blockers_to_failure_items():
    results = {
        "regen_optimisation_candidate_generator_blocking_reasons": [
            "Candidate generation is disabled by default. Enable it with regen_optimisation_candidate_generation_enabled=True."
        ],
    }

    failure = build_regen_optimisation_failure_owner(results)

    assert failure["regen_optimisation_blocking_failure_count"] == 1

    item = failure["regen_optimisation_failure_items"][0]

    assert item["source"] == "candidate_generator"
    assert item["phase"] == "8B"
    assert item["severity"] == "BLOCKED_BY_CONFIGURATION"


def test_phase_8d_converts_scoring_blockers_to_failure_items():
    results = {
        "regen_optimisation_scoring_blocking_reasons": [
            "No generated candidates are available to score."
        ],
    }

    failure = build_regen_optimisation_failure_owner(results)

    assert failure["regen_optimisation_blocking_failure_count"] == 1

    item = failure["regen_optimisation_failure_items"][0]

    assert item["source"] == "scoring_owner"
    assert item["phase"] == "8C"
    assert item["severity"] == "BLOCKED_BY_MISSING_CANDIDATES"


def test_phase_8d_adds_selection_locks_for_scored_candidates():
    results = {
        "regen_optimisation_scored_candidates": [
            {
                "candidate_id": "REGEN-OPT-8B-0001",
                "total_score": 0.9,
                "selection_allowed": False,
            }
        ]
    }

    failure = build_regen_optimisation_failure_owner(results)

    assert failure["regen_optimisation_failure_count"] == 1
    assert failure["regen_optimisation_blocking_failure_count"] == 0

    item = failure["regen_optimisation_failure_items"][0]

    assert item["source"] == "scored_candidate_selection_lock"
    assert item["candidate_id"] == "REGEN-OPT-8B-0001"
    assert item["blocks_selection"] is True
    assert item["blocks_geometry_application"] is True


def test_phase_8d_attach_preserves_existing_results():
    results = {
        "thrust": 1000,
        "regen_optimisation_scoring_blocking_reasons": [
            "Phase 8B candidate generator foundation is not complete, so Phase 8C scoring is blocked."
        ],
    }

    updated = attach_regen_optimisation_failure_owner(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_8d_regen_optimisation_failure_owner_complete"] is True
    assert "regen_optimisation_failure_text" in updated