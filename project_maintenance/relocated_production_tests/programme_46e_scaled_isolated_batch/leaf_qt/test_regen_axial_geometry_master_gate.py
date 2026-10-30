from project_maintenance.production_historical_artifacts.leaf_qt.regen_axial_geometry_master_gate import (
    run_regen_axial_geometry_master_gate,
    flatten_regen_axial_master_gate_result,
)


def run_test():
    result = run_regen_axial_geometry_master_gate()

    assert result["regen_axial_master_gate_status"] == "PASS_REGEN_AXIAL_GEOMETRY_MASTER_GATE"
    assert result["regen_axial_master_gate_pass"] is True
    assert result["phase_2_architecturally_complete"] is True
    assert result["phase_3_variable_geometry_allowed"] is True
    assert (
        result["master_gate_statement"]
        == "REGEN GEOMETRY PHASE 2 ACCEPTED FOR FUTURE VARIABLE-GEOMETRY DEVELOPMENT"
    )

    flat = flatten_regen_axial_master_gate_result(result)

    assert flat["recommended_regen_axial_master_gate_status"] == "PASS_REGEN_AXIAL_GEOMETRY_MASTER_GATE"
    assert flat["recommended_regen_axial_master_gate_pass"] == 1.0
    assert flat["recommended_regen_axial_phase_2_architecturally_complete"] == 1.0
    assert flat["recommended_regen_axial_phase_3_variable_geometry_allowed"] == 1.0

    print("PASS_REGEN_AXIAL_GEOMETRY_MASTER_GATE")


if __name__ == "__main__":
    run_test()