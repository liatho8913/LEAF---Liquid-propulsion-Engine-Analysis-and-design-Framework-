from project_maintenance.production_historical_artifacts.leaf_qt.regen_thermal_geometry_coupling_master_gate import (
    run_regen_thermal_geometry_coupling_master_gate,
    flatten_regen_thermal_geometry_coupling_master_gate_result,
)


def run_test():
    result = run_regen_thermal_geometry_coupling_master_gate()

    assert (
        result["regen_thermal_geometry_coupling_master_gate_status"]
        == "PASS_REGEN_THERMAL_GEOMETRY_COUPLING_MASTER_GATE"
    )
    assert result["regen_thermal_geometry_coupling_master_gate_pass"] is True
    assert result["phase_5_thermal_geometry_coupling_architecturally_trusted"] is True
    assert result["phase_5_completion_audit_allowed"] is True
    assert (
        result["future_thermal_geometry_optimisation_allowed_after_completion_audit"]
        is True
    )
    assert (
        result["master_gate_statement"]
        == "REGEN GEOMETRY PHASE 5 ACCEPTED FOR COMPLETION AUDIT"
    )

    flat = flatten_regen_thermal_geometry_coupling_master_gate_result(result)

    assert (
        flat["recommended_regen_thermal_geometry_coupling_master_gate_status"]
        == "PASS_REGEN_THERMAL_GEOMETRY_COUPLING_MASTER_GATE"
    )
    assert flat["recommended_regen_thermal_geometry_coupling_master_gate_pass"] == 1.0
    assert flat["recommended_regen_thermal_geometry_coupling_phase_5_trusted"] == 1.0
    assert (
        flat["recommended_regen_thermal_geometry_coupling_completion_audit_allowed"]
        == 1.0
    )
    assert (
        flat[
            "recommended_regen_thermal_geometry_optimisation_allowed_after_completion_audit"
        ]
        == 1.0
    )

    print("PASS_REGEN_THERMAL_GEOMETRY_COUPLING_MASTER_GATE")


if __name__ == "__main__":
    run_test()