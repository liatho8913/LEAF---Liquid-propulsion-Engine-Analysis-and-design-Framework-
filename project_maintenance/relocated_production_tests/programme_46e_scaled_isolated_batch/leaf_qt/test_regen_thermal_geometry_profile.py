from regen_thermal_geometry_profile import (
    build_thermal_geometry_profile,
    interpolate_thermal_geometry_profile,
    sample_thermal_geometry_profile,
    flatten_thermal_geometry_profile_result,
)


def run_test():
    thermal_points = [
        {
            "axial_position": 0.0,
            "heat_flux": 8.0e6,
            "hot_wall_temperature": 700.0,
            "coolant_temperature": 110.0,
            "pressure_drop": 10000.0,
        },
        {
            "axial_position": 0.15,
            "heat_flux": 18.0e6,
            "hot_wall_temperature": 850.0,
            "coolant_temperature": 160.0,
            "pressure_drop": 30000.0,
        },
        {
            "axial_position": 0.30,
            "heat_flux": 6.0e6,
            "hot_wall_temperature": 650.0,
            "coolant_temperature": 220.0,
            "pressure_drop": 20000.0,
        },
    ]

    profile = build_thermal_geometry_profile(
        thermal_points,
        max_allowable_wall_temperature=900.0,
    )

    assert profile["regen_thermal_geometry_profile_status"] == "PASS_REGEN_THERMAL_GEOMETRY_PROFILE"
    assert profile["regen_thermal_geometry_profile_pass"] is True
    assert profile["point_count"] == 3
    assert profile["maximum_heat_flux"] == 18.0e6
    assert profile["maximum_hot_wall_temperature"] == 850.0
    assert profile["total_pressure_drop"] == 60000.0
    assert profile["minimum_thermal_margin"] == 50.0

    midpoint = interpolate_thermal_geometry_profile(
        thermal_points,
        0.075,
        max_allowable_wall_temperature=900.0,
    )

    assert midpoint is not None
    assert midpoint["axial_position"] == 0.075
    assert midpoint["heat_flux"] > 0
    assert midpoint["hot_wall_temperature"] > 0
    assert midpoint["coolant_temperature"] > 0
    assert midpoint["pressure_drop"] >= 0
    assert midpoint["thermal_margin"] is not None

    sampled = sample_thermal_geometry_profile(
        thermal_points,
        [0.0, 0.075, 0.15, 0.225, 0.30],
        max_allowable_wall_temperature=900.0,
    )

    assert sampled["regen_thermal_geometry_sampling_status"] == "PASS_REGEN_THERMAL_GEOMETRY_SAMPLING"
    assert sampled["regen_thermal_geometry_sampling_pass"] is True
    assert sampled["sample_count"] == 5

    flat = flatten_thermal_geometry_profile_result(profile)

    assert flat["recommended_regen_thermal_geometry_profile_status"] == "PASS_REGEN_THERMAL_GEOMETRY_PROFILE"
    assert flat["recommended_regen_thermal_geometry_profile_pass"] == 1.0
    assert flat["recommended_regen_thermal_geometry_profile_point_count"] == 3.0
    assert "recommended_regen_thermal_geometry_point_1_heat_flux" in flat

    failing_profile = build_thermal_geometry_profile(
        [
            {
                "axial_position": 0.0,
                "heat_flux": -1.0,
                "hot_wall_temperature": 700.0,
                "coolant_temperature": 110.0,
                "pressure_drop": 10000.0,
            }
        ]
    )

    assert failing_profile["regen_thermal_geometry_profile_status"] == "FAIL_REGEN_THERMAL_GEOMETRY_PROFILE"
    assert failing_profile["regen_thermal_geometry_profile_pass"] is False

    print("PASS_REGEN_THERMAL_GEOMETRY_PROFILE")


if __name__ == "__main__":
    run_test()