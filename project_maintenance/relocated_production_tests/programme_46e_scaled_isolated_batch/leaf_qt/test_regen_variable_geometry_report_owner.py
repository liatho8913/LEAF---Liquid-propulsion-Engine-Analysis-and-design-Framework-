from regen_variable_geometry_report_owner import (
    generate_variable_geometry_profile_report,
    flatten_variable_geometry_report_owner_result,
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

    result = generate_variable_geometry_profile_report(profile_points)

    assert result["regen_variable_geometry_report_owner_status"] == "PASS_REGEN_VARIABLE_GEOMETRY_REPORT_OWNER"
    assert result["regen_variable_geometry_report_owner_pass"] is True
    assert "LEAF VARIABLE REGEN GEOMETRY PROFILE REPORT" in result["report_text"]
    assert "Profile Points" in result["report_text"]
    assert "Manufacturing Readiness Summary" in result["report_text"]

    flat = flatten_variable_geometry_report_owner_result(result)

    assert flat["recommended_regen_variable_geometry_report_owner_status"] == "PASS_REGEN_VARIABLE_GEOMETRY_REPORT_OWNER"
    assert flat["recommended_regen_variable_geometry_report_owner_pass"] == 1.0
    assert "recommended_regen_variable_geometry_report_text" in flat

    print("PASS_REGEN_VARIABLE_GEOMETRY_REPORT_OWNER")


if __name__ == "__main__":
    run_test()