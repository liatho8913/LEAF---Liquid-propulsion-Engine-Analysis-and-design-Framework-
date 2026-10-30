from regen_variable_geometry_constraint_owner import (
    validate_variable_geometry_profile_constraints,
    flatten_variable_geometry_constraint_owner_result,
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

    result = validate_variable_geometry_profile_constraints(profile_points)

    assert result["regen_variable_geometry_constraint_owner_status"] == "PASS_REGEN_VARIABLE_GEOMETRY_CONSTRAINT_OWNER"
    assert result["regen_variable_geometry_constraint_owner_pass"] is True
    assert result["point_constraint_fail_count"] == 0
    assert result["gradient_constraint_result"]["variable_geometry_gradient_constraint_status"] == "PASS_REGEN_VARIABLE_GEOMETRY_GRADIENT_CONSTRAINTS"

    flat = flatten_variable_geometry_constraint_owner_result(result)

    assert flat["recommended_regen_variable_geometry_constraint_owner_status"] == "PASS_REGEN_VARIABLE_GEOMETRY_CONSTRAINT_OWNER"
    assert flat["recommended_regen_variable_geometry_constraint_owner_pass"] == 1.0
    assert flat["recommended_regen_variable_geometry_constraint_point_fail_count"] == 0.0

    failing_result = validate_variable_geometry_profile_constraints(
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

    assert failing_result["regen_variable_geometry_constraint_owner_status"] == "FAIL_REGEN_VARIABLE_GEOMETRY_CONSTRAINT_OWNER"
    assert failing_result["regen_variable_geometry_constraint_owner_pass"] is False
    assert failing_result["point_constraint_fail_count"] >= 1

    print("PASS_REGEN_VARIABLE_GEOMETRY_CONSTRAINT_OWNER")


if __name__ == "__main__":
    run_test()