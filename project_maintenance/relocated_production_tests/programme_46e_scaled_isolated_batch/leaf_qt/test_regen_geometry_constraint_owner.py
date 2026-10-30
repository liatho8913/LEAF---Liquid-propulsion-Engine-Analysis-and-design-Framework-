from regen_geometry_constraint_owner import evaluate_regen_geometry_constraints


def run_test():
    valid_candidate = {
        "channel_width": 0.001,
        "channel_height": 0.0015,
        "effective_rib_width": 0.0006,
        "pitch": 0.0016,
        "fit_ratio": 1.05,
        "hydraulic_diameter": 0.0012,
        "coolant_velocity": 20.0,
        "estimated_pressure_drop": 100000.0,
        "circumferential_coverage": 0.5,
    }

    valid_result = evaluate_regen_geometry_constraints(
        valid_candidate,
        minimum_rib_width=0.0005,
        minimum_channel_width=0.0005,
        minimum_channel_height=0.0005,
        minimum_hydraulic_diameter=0.0003,
        maximum_coolant_velocity=80.0,
        pressure_drop_limit=2.0e6,
        minimum_cooling_coverage=0.25,
    )

    assert valid_result["geometry_constraints_pass"] is True
    assert valid_result["constraint_status"] == "PASS"

    collapsed_rib_candidate = dict(valid_candidate)
    collapsed_rib_candidate["effective_rib_width"] = 0.0002

    collapsed_result = evaluate_regen_geometry_constraints(
        collapsed_rib_candidate,
        minimum_rib_width=0.0005,
    )

    assert collapsed_result["geometry_constraints_pass"] is False
    assert "EFFECTIVE_RIB_WIDTH_BELOW_MINIMUM" in collapsed_result["failures"]

    bad_fit_candidate = dict(valid_candidate)
    bad_fit_candidate["fit_ratio"] = 0.8

    bad_fit_result = evaluate_regen_geometry_constraints(bad_fit_candidate)

    assert bad_fit_result["geometry_constraints_pass"] is False
    assert "REQUESTED_GEOMETRY_DOES_NOT_FIT_CIRCUMFERENCE" in bad_fit_result["failures"]

    print("PASS_REGEN_GEOMETRY_CONSTRAINT_OWNER")


if __name__ == "__main__":
    run_test()