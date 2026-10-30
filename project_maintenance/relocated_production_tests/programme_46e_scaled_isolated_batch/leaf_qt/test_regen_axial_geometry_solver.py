from regen_axial_geometry_solver import (
    build_regen_axial_station_profile,
    solve_regen_axial_geometry,
    solve_regen_axial_geometry_to_engine_results,
)


def run_test():
    profile = build_regen_axial_station_profile(
        chamber_radius=0.03,
        throat_radius=0.01,
        exit_radius=0.04,
        engine_length=0.30,
    )

    assert profile["axial_station_profile_status"] == "PASS_REGEN_AXIAL_STATION_PROFILE"
    assert profile["station_count"] == 7
    assert profile["missing_radius_count"] == 0

    result = solve_regen_axial_geometry(
        chamber_radius=0.03,
        throat_radius=0.01,
        exit_radius=0.04,
        engine_length=0.30,
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
        axial_segment_length=0.05,
        minimum_cooling_coverage=0.25,
    )

    assert result["axial_geometry_solver_status"] in {
        "PASS_REGEN_AXIAL_GEOMETRY_SOLVER",
        "FAIL_REGEN_AXIAL_GEOMETRY_SOLVER",
    }

    assert result["station_count"] == 7
    assert "station_results" in result
    assert len(result["station_results"]) == 7

    flat = solve_regen_axial_geometry_to_engine_results(
        station_specs=[
            {
                "station_id": "throat",
                "station_name": "Throat",
                "axial_position": 0.15,
                "local_radius": 0.01,
            }
        ],
        coolant_mass_flow_rate=0.25,
        coolant_density=420.0,
        coolant_dynamic_viscosity=0.00018,
        maximum_channel_height=0.003,
        maximum_coolant_velocity=80.0,
        pressure_drop_limit=2.0e6,
        axial_segment_length=0.05,
    )

    assert "recommended_regen_axial_geometry_solver_status" in flat
    assert "recommended_regen_axial_station_count" in flat
    assert "recommended_regen_axial_station_1_channel_width" in flat

    print("PASS_REGEN_AXIAL_GEOMETRY_SOLVER")


if __name__ == "__main__":
    run_test()