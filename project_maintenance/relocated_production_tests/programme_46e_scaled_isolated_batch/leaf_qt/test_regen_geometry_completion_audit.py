from regen_geometry_solver import solve_regen_geometry
from project_maintenance.production_historical_artifacts.leaf_qt.regen_geometry_completion_audit import audit_regen_geometry_completion


def run_test():
    solver_result = solve_regen_geometry(
        channel_mid_radius=0.012,
        coolant_mass_flow_rate=0.25,
        coolant_density=420.0,
        coolant_dynamic_viscosity=0.00018,
        target_reynolds_number=10000.0,
        minimum_rib_width=0.0005,
        minimum_channel_width=0.0005,
        maximum_channel_height=0.003,
        channel_aspect_ratio=3.0,
        minimum_channel_count=8,
        maximum_channel_count=220,
        maximum_coolant_velocity=80.0,
        minimum_hydraulic_diameter=0.00035,
        pressure_drop_limit=2.0e6,
        nozzle_length=0.15,
        minimum_cooling_coverage=0.25,
    )

    audit = audit_regen_geometry_completion(solver_result)

    assert audit["regen_geometry_completion_audit_status"] == "PASS_REGEN_GEOMETRY_COMPLETION_AUDIT"
    assert audit["regen_geometry_phase_1_complete"] is True

    broken = dict(solver_result)
    broken["regen_geometry_master_gate"] = {
        "regen_geometry_master_gate_status": "FAIL_REGEN_GEOMETRY_MASTER_GATE"
    }

    broken_audit = audit_regen_geometry_completion(broken)

    assert broken_audit["regen_geometry_completion_audit_status"] == "FAIL_REGEN_GEOMETRY_COMPLETION_AUDIT"
    assert "MASTER_GATE_NOT_PASS" in broken_audit["regen_geometry_completion_failures"]

    print("PASS_REGEN_GEOMETRY_COMPLETION_AUDIT")


if __name__ == "__main__":
    run_test()