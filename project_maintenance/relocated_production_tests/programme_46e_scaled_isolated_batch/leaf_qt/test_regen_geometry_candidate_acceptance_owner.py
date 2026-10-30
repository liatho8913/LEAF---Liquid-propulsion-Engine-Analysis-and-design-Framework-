from regen_geometry_candidate_acceptance_owner import (
    attach_regen_geometry_candidate_acceptance_owner,
)


def test_regen_geometry_candidate_acceptance_owner_builds_patch():
    results = {
        "phase_11a5_regen_geometry_apply_recommendation_owner_baseline_geometry": {
            "channel_count": 80,
            "channel_width": 0.0015,
            "channel_height": 0.002,
            "rib_width": 0.001,
        },
        "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry": {
            "channel_count": 60,
            "channel_width": 0.0012,
            "channel_height": 0.0017,
            "rib_width": 0.0008,
        },
        "phase_11a5_regen_geometry_apply_recommendation_owner_improvement": {
            "changed_keys": [
                "channel_count",
                "channel_width",
                "channel_height",
                "rib_width",
            ],
        },
        "phase_11a4_regen_geometry_recommendation_engine_owner_recommendations": [
            {
                "recommendation_id": "reduce_channel_pitch_demand",
            }
        ],
    }

    solved = attach_regen_geometry_candidate_acceptance_owner(results)

    print(
        "DEBUG_KEYS:",
        solved.get("phase_11a8_candidate_geometry_debug_keys", [])
    )
    print(
        "INPUT_PATCH:",
        solved.get("phase_11a8_regen_geometry_candidate_acceptance_owner_input_patch", {})
    )

    assert solved[
        "phase_11a8_regen_geometry_candidate_acceptance_owner_complete"
    ] is True

    assert solved[
        "phase_11a8_regen_geometry_candidate_acceptance_owner_status"
    ] == "PASS_PHASE_11A8_REGEN_GEOMETRY_CANDIDATE_ACCEPTANCE_OWNER"

    assert solved[
        "phase_11a8_regen_geometry_candidate_acceptance_owner_ready"
    ] is True

    patch = solved[
        "phase_11a8_regen_geometry_candidate_acceptance_owner_input_patch"
    ]

    assert patch["number_of_coolant_channels"] == 60
    assert abs(patch["coolant_channel_width"] - 0.0012) < 1.0e-12
    assert abs(patch["coolant_channel_height"] - 0.0017) < 1.0e-12
    assert abs(patch["rib_width"] - 0.0008) < 1.0e-12


def test_regen_geometry_candidate_acceptance_owner_handles_no_candidate_change():
    results = {
        "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry": {},
        "phase_11a5_regen_geometry_apply_recommendation_owner_improvement": {
            "changed_keys": [],
        },
    }

    solved = attach_regen_geometry_candidate_acceptance_owner(results)

    print(
        "NO_CHANGE_DEBUG_KEYS:",
        solved.get("phase_11a8_candidate_geometry_debug_keys", [])
    )
    print(
        "NO_CHANGE_INPUT_PATCH:",
        solved.get("phase_11a8_regen_geometry_candidate_acceptance_owner_input_patch", {})
    )

    assert solved[
        "phase_11a8_regen_geometry_candidate_acceptance_owner_complete"
    ] is True

    assert solved[
        "phase_11a8_regen_geometry_candidate_acceptance_owner_ready"
    ] is False

    assert solved[
        "phase_11a8_regen_geometry_candidate_acceptance_owner_input_patch"
    ] == {}


if __name__ == "__main__":
    test_regen_geometry_candidate_acceptance_owner_builds_patch()
    test_regen_geometry_candidate_acceptance_owner_handles_no_candidate_change()
    print("PASS_REGEN_GEOMETRY_CANDIDATE_ACCEPTANCE_OWNER")