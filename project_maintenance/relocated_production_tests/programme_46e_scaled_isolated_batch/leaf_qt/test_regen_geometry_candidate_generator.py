from regen_geometry_candidate_generator import generate_regen_geometry_candidates


def run_test():
    report = generate_regen_geometry_candidates(
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

    assert report["status"] in {"PASS", "NO_VALID_GEOMETRY_FOUND"}
    assert report["candidates_checked"] > 0

    if report["best_candidate"] is not None:
        c = report["best_candidate"]
        assert c["effective_rib_width"] >= 0.0005
        assert c["channel_width"] >= 0.0005
        assert c["fit_ratio"] >= 1.0

    print("PASS_REGEN_GEOMETRY_CANDIDATE_GENERATOR")


if __name__ == "__main__":
    run_test()