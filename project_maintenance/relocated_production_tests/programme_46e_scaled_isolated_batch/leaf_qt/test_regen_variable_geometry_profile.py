from regen_variable_geometry_profile import (
    build_variable_geometry_profile,
    interpolate_variable_geometry_profile,
    sample_variable_geometry_profile,
    flatten_variable_geometry_profile_result,
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
            "channel_width": 0.0008,
            "channel_height": 0.0015,
            "rib_width": 0.00045,
        },
        {
            "axial_position": 0.30,
            "channel_width": 0.0012,
            "channel_height": 0.0025,
            "rib_width": 0.0006,
        },
    ]

    profile = build_variable_geometry_profile(profile_points)

    assert profile["regen_variable_geometry_profile_status"] == "PASS_REGEN_VARIABLE_GEOMETRY_PROFILE"
    assert profile["regen_variable_geometry_profile_pass"] is True
    assert profile["point_count"] == 3

    midpoint = interpolate_variable_geometry_profile(profile_points, 0.075)

    assert midpoint is not None
    assert midpoint["axial_position"] == 0.075
    assert midpoint["channel_width"] > 0
    assert midpoint["channel_height"] > 0
    assert midpoint["rib_width"] > 0
    assert midpoint["hydraulic_diameter"] > 0

    sampled = sample_variable_geometry_profile(
        profile_points,
        [0.0, 0.075, 0.15, 0.225, 0.30],
    )

    assert sampled["regen_variable_geometry_sampling_status"] == "PASS_REGEN_VARIABLE_GEOMETRY_SAMPLING"
    assert sampled["regen_variable_geometry_sampling_pass"] is True
    assert sampled["sample_count"] == 5

    flat = flatten_variable_geometry_profile_result(profile)

    assert flat["recommended_regen_variable_geometry_profile_status"] == "PASS_REGEN_VARIABLE_GEOMETRY_PROFILE"
    assert flat["recommended_regen_variable_geometry_profile_pass"] == 1.0
    assert flat["recommended_regen_variable_geometry_profile_point_count"] == 3.0
    assert "recommended_regen_variable_geometry_point_1_channel_width" in flat

    failing_profile = build_variable_geometry_profile(
        [
            {
                "axial_position": 0.0,
                "channel_width": 0.001,
                "channel_height": 0.002,
                "rib_width": 0.0005,
            }
        ]
    )

    assert failing_profile["regen_variable_geometry_profile_status"] == "FAIL_REGEN_VARIABLE_GEOMETRY_PROFILE"
    assert failing_profile["regen_variable_geometry_profile_pass"] is False

    print("PASS_REGEN_VARIABLE_GEOMETRY_PROFILE")


if __name__ == "__main__":
    run_test()