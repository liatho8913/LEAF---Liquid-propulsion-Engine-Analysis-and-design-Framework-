from regen_geometry_solver import solve_regen_geometry
from regen_geometry_master_gate import evaluate_regen_geometry_master_gate


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

    gate = solver_result["regen_geometry_master_gate"]

    assert gate["regen_geometry_master_gate_status"] in {
        "PASS_REGEN_GEOMETRY_MASTER_GATE",
        "FAIL_REGEN_GEOMETRY_MASTER_GATE",
    }

    assert "recommended_regen_geometry_master_gate_status" in solver_result["mapped_results"]
    assert "recommended_regen_geometry_master_gate_pass" in solver_result["mapped_results"]

    broken = dict(solver_result)
    broken["best_candidate"] = None

    broken_gate = evaluate_regen_geometry_master_gate(broken)

    assert broken_gate["regen_geometry_master_gate_status"] == "FAIL_REGEN_GEOMETRY_MASTER_GATE"
    assert "NO_SELECTED_CANDIDATE" in broken_gate["regen_geometry_master_gate_failures"]

    print("PASS_REGEN_GEOMETRY_MASTER_GATE")


if __name__ == "__main__":
    run_test()