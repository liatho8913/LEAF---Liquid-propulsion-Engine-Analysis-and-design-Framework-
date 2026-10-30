from regen_thermal_geometry_constraint_owner import (
    validate_thermal_geometry_profile_constraints,
    flatten_thermal_geometry_constraint_owner_result,
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

    result = validate_thermal_geometry_profile_constraints(
        thermal_points,
        max_allowable_wall_temperature=900.0,
        maximum_hot_wall_temperature=900.0,
        maximum_coolant_temperature=500.0,
        maximum_total_pressure_drop=2.0e6,
        minimum_thermal_margin=0.0,
    )

    assert result["regen_thermal_geometry_constraint_owner_status"] == "PASS_REGEN_THERMAL_GEOMETRY_CONSTRAINT_OWNER"
    assert result["regen_thermal_geometry_constraint_owner_pass"] is True
    assert result["point_constraint_fail_count"] == 0
    assert result["gradient_constraint_result"]["thermal_gradient_constraint_status"] == "PASS_REGEN_THERMAL_GEOMETRY_GRADIENT_CONSTRAINTS"

    flat = flatten_thermal_geometry_constraint_owner_result(result)

    assert flat["recommended_regen_thermal_geometry_constraint_owner_status"] == "PASS_REGEN_THERMAL_GEOMETRY_CONSTRAINT_OWNER"
    assert flat["recommended_regen_thermal_geometry_constraint_owner_pass"] == 1.0
    assert flat["recommended_regen_thermal_geometry_constraint_point_fail_count"] == 0.0

    failing_result = validate_thermal_geometry_profile_constraints(
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

    assert failing_result["regen_thermal_geometry_constraint_owner_status"] == "FAIL_REGEN_THERMAL_GEOMETRY_CONSTRAINT_OWNER"
    assert failing_result["regen_thermal_geometry_constraint_owner_pass"] is False
    assert failing_result["point_constraint_fail_count"] >= 1

    print("PASS_REGEN_THERMAL_GEOMETRY_CONSTRAINT_OWNER")


if __name__ == "__main__":
    run_test()