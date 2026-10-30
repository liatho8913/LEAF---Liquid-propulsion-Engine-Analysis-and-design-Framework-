from calculation_bridge import calculate_with_full_bridge


def main():

    results = calculate_with_full_bridge(
        {
            "fuel_name": "RP-1",
            "oxidizer_name": "LOX",
            "chamber_pressure": 6.895e6,
            "mass_flow_rate": 1.15,
            "mixture_ratio": 1.875,
            "throat_area": 3.01e-4,
            "expansion_ratio": 9.12,

            "number_of_coolant_channels": 80,
            "coolant_channel_width": 0.0015,
            "coolant_channel_height": 0.0020,
            "rib_width": 0.0010,
            "hot_gas_wall_thickness": 0.0010,
            "coolant_flow_fraction": 0.35,
        }
    )

    print()
    print("=== CANDIDATE GENERATION AUDIT ===")
    print()

    print(
        "candidate_generator_status:",
        results.get(
            "regen_optimisation_candidate_generator_status"
        )
    )

    print(
        "candidate_count:",
        results.get(
            "regen_optimisation_candidate_generator_candidate_count"
        )
    )

    print(
        "blocking_reasons:",
        results.get(
            "regen_optimisation_candidate_generator_blocking_reasons"
        )
    )

    print(
        "recommended_status:",
        results.get(
            "recommended_geometry_status"
        )
    )

    print(
        "best_engine_status:",
        results.get(
            "best_full_engine_regen_status"
        )
    )

    print()

    candidates = results.get(
        "regen_optimisation_candidate_generator_candidates",
        []
    )

    print(
        "candidate_list_length:",
        len(candidates)
    )

    if candidates:
        print()
        print("FIRST CANDIDATE")
        print(candidates[0])

    print()
    print("PASS_POST16F4_CANDIDATE_AUDIT")


if __name__ == "__main__":
    main()
