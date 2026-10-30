from regen_geometry_realism_optimisation_owner_phase_16q8 import evaluate_geometry_realism


def main() -> int:
    too_sparse = {
        "coolant_channel_width": 0.0012,
        "coolant_channel_height": 0.0025,
        "rib_width": 0.00075,
        "effective_rib_width": 0.0040,
        "cooling_coverage": 0.754,
        "number_of_coolant_channels": 30,
    }

    sparse = evaluate_geometry_realism(too_sparse)

    assert sparse["passed"] is False or sparse["score"] < 90.0
    assert sparse["channel_count"] == 30

    better = {
        "coolant_channel_width": 0.0011,
        "coolant_channel_height": 0.0022,
        "rib_width": 0.00045,
        "effective_rib_width": 0.00065,
        "cooling_coverage": 0.78,
        "number_of_coolant_channels": 48,
    }

    good = evaluate_geometry_realism(better)

    assert good["score"] > sparse["score"]




    print("PASS_REGEN_GEOMETRY_REALISM_OPTIMISATION_OWNER_PHASE_16Q8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
