from regen_candidate_application_owner import (
    attach_regen_candidate_application_owner,
)


def test_application_owner_builds_patch_from_recommendation():
    results = {
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0010,
        "regen_candidate_recommendation": {
            "candidate_id": "RCG-0001",
            "inputs": {
                "number_of_coolant_channels": 96,
                "coolant_channel_width": 0.0012,
                "coolant_channel_height": 0.0025,
                "rib_width": 0.0008,
                "hot_gas_wall_thickness": 0.00125,
            },
        },
    }

    results = attach_regen_candidate_application_owner(results)

    assert results["phase_11b_1f_regen_candidate_application_owner_complete"] is True
    assert results["regen_candidate_application_owner_complete"] is True
    assert results["regen_candidate_application_owner_status"] == (
        "PASS_REGEN_CANDIDATE_APPLICATION_PATCH_READY"
    )
    assert results["regen_candidate_application_ready"] is True
    assert results["regen_candidate_geometry_application_allowed"] is True
    assert results["regen_candidate_geometry_applied"] is False
    assert results["regen_candidate_manual_overwrite_allowed"] is False

    patch = results["regen_candidate_application_patch"]

    assert patch["candidate_id"] == "RCG-0001"
    assert patch["patch_values"]["number_of_coolant_channels"] == 96
    assert patch["original_values"]["number_of_coolant_channels"] == 80
    assert patch["changes"]["number_of_coolant_channels"]["changed"] is True


def test_application_owner_blocks_missing_recommendation():
    results = {}

    results = attach_regen_candidate_application_owner(results)

    assert results["regen_candidate_application_owner_status"] == (
        "FAIL_REGEN_CANDIDATE_APPLICATION_BLOCKED"
    )
    assert results["regen_candidate_application_ready"] is False
    assert results["regen_candidate_application_patch"] is None