from project_maintenance.production_historical_artifacts.leaf_qt.regen_variable_geometry_master_gate import (
    run_regen_variable_geometry_master_gate,
    flatten_regen_variable_geometry_master_gate_result,
)


def run_test():
    result = run_regen_variable_geometry_master_gate()

    assert result["regen_variable_geometry_master_gate_status"] == "PASS_REGEN_VARIABLE_GEOMETRY_MASTER_GATE"
    assert result["regen_variable_geometry_master_gate_pass"] is True
    assert result["phase_3_variable_geometry_architecturally_complete"] is True
    assert result["phase_4_thermal_coupling_allowed"] is True
    assert result["viewer_integration_allowed_after_phase_4_foundation"] is True
    assert (
        result["master_gate_statement"]
        == "REGEN GEOMETRY PHASE 3 ACCEPTED FOR FUTURE THERMAL-COUPLED DEVELOPMENT"
    )

    flat = flatten_regen_variable_geometry_master_gate_result(result)

    assert flat["recommended_regen_variable_geometry_master_gate_status"] == "PASS_REGEN_VARIABLE_GEOMETRY_MASTER_GATE"
    assert flat["recommended_regen_variable_geometry_master_gate_pass"] == 1.0
    assert flat["recommended_regen_variable_geometry_phase_3_architecturally_complete"] == 1.0
    assert flat["recommended_regen_variable_geometry_phase_4_thermal_coupling_allowed"] == 1.0
    assert flat["recommended_regen_variable_geometry_master_gate_error_count"] == 0.0

    print("PASS_REGEN_VARIABLE_GEOMETRY_MASTER_GATE")


if __name__ == "__main__":
    run_test()