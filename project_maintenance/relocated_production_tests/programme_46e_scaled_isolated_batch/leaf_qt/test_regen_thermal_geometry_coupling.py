from regen_thermal_geometry_coupling import (
    build_coupled_thermal_geometry_profile,
    flatten_coupled_thermal_geometry_profile_result,
)


def run_test():
    variable_points = [
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

    result = build_coupled_thermal_geometry_profile(
        variable_points,
        thermal_points,
        sample_positions=[0.0, 0.075, 0.15, 0.225, 0.30],
        max_allowable_wall_temperature=900.0,
    )

    assert result["regen_thermal_geometry_coupling_status"] == "PASS_REGEN_THERMAL_GEOMETRY_COUPLING"
    assert result["regen_thermal_geometry_coupling_pass"] is True
    assert result["coupled_point_count"] == 5

    first = result["coupled_points"][0]

    assert first["channel_width"] > 0
    assert first["channel_height"] > 0
    assert first["rib_width"] > 0
    assert first["hydraulic_diameter"] > 0
    assert first["heat_flux"] > 0
    assert first["hot_wall_temperature"] > 0
    assert first["coolant_temperature"] > 0

    flat = flatten_coupled_thermal_geometry_profile_result(result)

    assert flat["recommended_regen_thermal_geometry_coupling_status"] == "PASS_REGEN_THERMAL_GEOMETRY_COUPLING"
    assert flat["recommended_regen_thermal_geometry_coupling_pass"] == 1.0
    assert flat["recommended_regen_thermal_geometry_coupled_point_count"] == 5.0
    assert "recommended_regen_thermal_geometry_coupled_point_1_channel_width" in flat
    assert "recommended_regen_thermal_geometry_coupled_point_1_heat_flux" in flat

    failing_result = build_coupled_thermal_geometry_profile(
        variable_geometry_points=[
            {
                "axial_position": 0.0,
                "channel_width": 0.001,
                "channel_height": 0.002,
                "rib_width": 0.0005,
            }
        ],
        thermal_geometry_points=thermal_points,
    )

    assert failing_result["regen_thermal_geometry_coupling_status"] == "FAIL_REGEN_THERMAL_GEOMETRY_COUPLING"
    assert failing_result["regen_thermal_geometry_coupling_pass"] is False

    print("PASS_REGEN_THERMAL_GEOMETRY_COUPLING")


if __name__ == "__main__":
    run_test()