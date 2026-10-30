from regen_geometry_solver import (
    solve_regen_geometry,
    solve_regen_geometry_to_engine_results,
)


def run_test():
    result = solve_regen_geometry(
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

    assert result["solver_status"] in {
        "PASS_REGEN_GEOMETRY_SOLVER",
        "FAIL_REGEN_GEOMETRY_SOLVER",
    }

    assert "candidate_report" in result
    assert "mapped_results" in result
    assert "solver_report" in result

    mapped = result["mapped_results"]

    assert "recommended_regen_geometry_solver_status" in mapped
    assert "recommended_regen_geometry_solver_pass" in mapped
    assert "recommended_geometry_candidates_checked" in mapped
    assert "recommended_geometry_iteration_history_status" in mapped

    flat = solve_regen_geometry_to_engine_results(
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

    assert "recommended_regen_geometry_solver_status" in flat
    assert "recommended_regen_geometry_solver_pass" in flat

    print("PASS_REGEN_GEOMETRY_SOLVER")


if __name__ == "__main__":
    run_test()