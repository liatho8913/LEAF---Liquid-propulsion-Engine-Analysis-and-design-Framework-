from regen_thermal_geometry_coupling_validation_owner import (
    validate_coupled_thermal_geometry_system,
    flatten_coupled_thermal_geometry_validation_owner_result,
    validate_coupled_thermal_geometry_system_to_engine_results,
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

    result = validate_coupled_thermal_geometry_system(
        variable_points,
        thermal_points,
        sample_positions=[0.0, 0.075, 0.15, 0.225, 0.30],
        max_allowable_wall_temperature=900.0,
        maximum_hot_wall_temperature=900.0,
        maximum_coolant_temperature=500.0,
        maximum_total_pressure_drop=2.0e6,
        maximum_point_pressure_drop=2.0e6,
        minimum_thermal_margin=0.0,
    )

    assert result["regen_thermal_geometry_coupling_validation_owner_status"] == "PASS_REGEN_THERMAL_GEOMETRY_COUPLING_VALIDATION_OWNER"
    assert result["regen_thermal_geometry_coupling_validation_owner_pass"] is True
    assert "coupling_result" in result
    assert "constraint_result" in result
    assert "report_result" in result

    flat = flatten_coupled_thermal_geometry_validation_owner_result(result)

    assert flat["recommended_regen_thermal_geometry_coupling_validation_owner_status"] == "PASS_REGEN_THERMAL_GEOMETRY_COUPLING_VALIDATION_OWNER"
    assert flat["recommended_regen_thermal_geometry_coupling_validation_owner_pass"] == 1.0
    assert "recommended_regen_thermal_geometry_coupling_status" in flat
    assert "recommended_regen_thermal_geometry_coupling_constraint_owner_status" in flat
    assert "recommended_regen_thermal_geometry_coupling_report_owner_status" in flat
    assert "recommended_regen_thermal_geometry_coupling_report_text" in flat

    engine_results = validate_coupled_thermal_geometry_system_to_engine_results(
        variable_points,
        thermal_points,
        sample_positions=[0.0, 0.15, 0.30],
        max_allowable_wall_temperature=900.0,
    )

    assert "recommended_regen_thermal_geometry_coupling_validation_owner_status" in engine_results
    assert "recommended_regen_thermal_geometry_coupled_point_count" in engine_results

    failing_result = validate_coupled_thermal_geometry_system(
        variable_points,
        [
            {
                "axial_position": 0.0,
                "heat_flux": 8.0e6,
                "hot_wall_temperature": 950.0,
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
        ],
        max_allowable_wall_temperature=900.0,
        maximum_hot_wall_temperature=900.0,
    )

    assert failing_result["regen_thermal_geometry_coupling_validation_owner_status"] == "FAIL_REGEN_THERMAL_GEOMETRY_COUPLING_VALIDATION_OWNER"
    assert failing_result["regen_thermal_geometry_coupling_validation_owner_pass"] is False

    print("PASS_REGEN_THERMAL_GEOMETRY_COUPLING_VALIDATION_OWNER")


if __name__ == "__main__":
    run_test()