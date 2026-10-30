from project_maintenance.production_historical_artifacts.leaf_qt.regen_thermal_geometry_completion_audit import (
    run_regen_thermal_geometry_completion_audit,
    flatten_regen_thermal_geometry_completion_audit_result,
)


def run_test():
    result = run_regen_thermal_geometry_completion_audit()

    assert result["regen_thermal_geometry_completion_audit_status"] == "PASS_REGEN_THERMAL_GEOMETRY_COMPLETION_AUDIT"
    assert result["regen_thermal_geometry_completion_audit_pass"] is True
    assert result["required_interfaces_pass"] is True
    assert result["validation_result_available"] is True
    assert (
        result["completion_statement"]
        == "REGEN GEOMETRY PHASE 4 THERMAL PROFILE ARCHITECTURALLY COMPLETE"
    )

    flat = flatten_regen_thermal_geometry_completion_audit_result(result)

    assert flat["recommended_regen_thermal_geometry_completion_audit_status"] == "PASS_REGEN_THERMAL_GEOMETRY_COMPLETION_AUDIT"
    assert flat["recommended_regen_thermal_geometry_completion_audit_pass"] == 1.0
    assert flat["recommended_regen_thermal_geometry_completion_error_count"] == 0.0

    print("PASS_REGEN_THERMAL_GEOMETRY_COMPLETION_AUDIT")


if __name__ == "__main__":
    run_test()