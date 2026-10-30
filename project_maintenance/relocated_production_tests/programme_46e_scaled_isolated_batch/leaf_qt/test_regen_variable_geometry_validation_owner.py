from regen_variable_geometry_validation_owner import (
    validate_variable_geometry_system,
    flatten_variable_geometry_validation_owner_result,
    validate_variable_geometry_system_to_engine_results,
)


def run_test():
    profile_points = [
        {
            "axial_position": 0.0,
            "channel_width": 0.0010,
            "channel_height": 0.0020,
            "rib_width": 0.0005,
        },
        {
            "axial_position": 0.15,
            "channel_width": 0.0009,
            "channel_height": 0.0018,
            "rib_width": 0.00045,
        },
        {
            "axial_position": 0.30,
            "channel_width": 0.0011,
            "channel_height": 0.0022,
            "rib_width": 0.00055,
        },
    ]

    result = validate_variable_geometry_system(profile_points)

    assert result["regen_variable_geometry_validation_owner_status"] == "PASS_REGEN_VARIABLE_GEOMETRY_VALIDATION_OWNER"
    assert result["regen_variable_geometry_validation_owner_pass"] is True
    assert "profile_result" in result
    assert "constraint_result" in result
    assert "report_result" in result

    flat = flatten_variable_geometry_validation_owner_result(result)

    assert flat["recommended_regen_variable_geometry_validation_owner_status"] == "PASS_REGEN_VARIABLE_GEOMETRY_VALIDATION_OWNER"
    assert flat["recommended_regen_variable_geometry_validation_owner_pass"] == 1.0
    assert "recommended_regen_variable_geometry_profile_status" in flat
    assert "recommended_regen_variable_geometry_constraint_owner_status" in flat
    assert "recommended_regen_variable_geometry_report_owner_status" in flat
    assert "recommended_regen_variable_geometry_report_text" in flat

    engine_results = validate_variable_geometry_system_to_engine_results(profile_points)

    assert "recommended_regen_variable_geometry_validation_owner_status" in engine_results
    assert "recommended_regen_variable_geometry_profile_point_count" in engine_results

    failing_result = validate_variable_geometry_system(
        [
            {
                "axial_position": 0.0,
                "channel_width": 0.00001,
                "channel_height": 0.002,
                "rib_width": 0.0005,
            },
            {
                "axial_position": 0.1,
                "channel_width": 0.001,
                "channel_height": 0.002,
                "rib_width": 0.0005,
            },
        ]
    )

    assert failing_result["regen_variable_geometry_validation_owner_status"] == "FAIL_REGEN_VARIABLE_GEOMETRY_VALIDATION_OWNER"
    assert failing_result["regen_variable_geometry_validation_owner_pass"] is False

    print("PASS_REGEN_VARIABLE_GEOMETRY_VALIDATION_OWNER")


if __name__ == "__main__":
    run_test()