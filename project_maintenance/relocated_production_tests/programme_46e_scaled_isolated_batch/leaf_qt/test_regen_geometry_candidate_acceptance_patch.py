from regen_geometry_candidate_acceptance_owner import (
    enforce_non_empty_regen_acceptance_patch,
)


def test_acceptance_patch_falls_back_to_recommended_candidate_inputs():
    results = {
        "recommended_regen_candidate_inputs": {
            "number_of_coolant_channels": 96,
            "coolant_channel_width": 0.0012,
            "coolant_channel_height": 0.0025,
            "rib_width": 0.0008,
            "hot_gas_wall_thickness": 0.00125,
        }
    }

    patch = enforce_non_empty_regen_acceptance_patch(results, {})

    assert len(patch) == 5
    assert patch["number_of_coolant_channels"] == 96
    assert results["regen_geometry_acceptance_patch_key_count"] == 5
    assert results["regen_geometry_candidate_acceptance_status"] == (
        "PASS_REGEN_GEOMETRY_ACCEPTANCE_PATCH_READY"
    )


def test_acceptance_patch_fails_when_empty():
    results = {}

    patch = enforce_non_empty_regen_acceptance_patch(results, {})

    assert patch == {}
    assert results["regen_geometry_acceptance_patch_key_count"] == 0
    assert results["regen_geometry_candidate_acceptance_status"] == (
        "FAIL_REGEN_GEOMETRY_EMPTY_ACCEPTANCE_PATCH"
    )