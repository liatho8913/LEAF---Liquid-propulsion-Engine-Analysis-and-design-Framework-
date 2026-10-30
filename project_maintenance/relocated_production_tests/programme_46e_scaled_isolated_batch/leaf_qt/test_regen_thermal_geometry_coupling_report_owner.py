from regen_thermal_geometry_coupling_report_owner import (
    generate_coupled_thermal_geometry_report,
    flatten_coupled_thermal_geometry_report_owner_result,
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

    result = generate_coupled_thermal_geometry_report(
        variable_points,
        thermal_points,
        sample_positions=[0.0, 0.075, 0.15, 0.225, 0.30],
        max_allowable_wall_temperature=900.0,
    )

    assert result["regen_thermal_geometry_coupling_report_owner_status"] == "PASS_REGEN_THERMAL_GEOMETRY_COUPLING_REPORT_OWNER"
    assert result["regen_thermal_geometry_coupling_report_owner_pass"] is True
    assert "LEAF THERMAL-GEOMETRY COUPLING REPORT" in result["report_text"]
    assert "Coupled Station Results" in result["report_text"]
    assert "Coupled Safety Summary" in result["report_text"]
    assert "Coupled Readiness Summary" in result["report_text"]

    flat = flatten_coupled_thermal_geometry_report_owner_result(result)

    assert flat["recommended_regen_thermal_geometry_coupling_report_owner_status"] == "PASS_REGEN_THERMAL_GEOMETRY_COUPLING_REPORT_OWNER"
    assert flat["recommended_regen_thermal_geometry_coupling_report_owner_pass"] == 1.0
    assert "recommended_regen_thermal_geometry_coupling_report_text" in flat

    print("PASS_REGEN_THERMAL_GEOMETRY_COUPLING_REPORT_OWNER")


if __name__ == "__main__":
    run_test()