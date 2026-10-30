from calculation_bridge import calculate_with_full_bridge


def main():
    results = calculate_with_full_bridge({
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
    })

    keys = [
        "regen_optimisation_candidate_generator_candidate_count",
        "regen_optimisation_candidate_generator_candidates",
        "regen_optimisation_scored_candidate_count",
        "regen_optimisation_scored_candidates",
        "regen_optimisation_recommendation_ranked_candidate_count",
        "regen_optimisation_recommendation_ranked_candidates",
        "regen_optimisation_selection_ranked_candidates",
        "regen_candidate_ranking_inspector_ranked_candidates",
        "regen_candidate_ranking_payload_bridge_status",
        "regen_candidate_ranking_payload_bridge_source_key",
        "regen_candidate_ranking_payload_bridge_candidate_count",
        "regen_optimisation_scoring_owner_status",
        "regen_optimisation_scoring_enabled",
        "regen_optimisation_scoring_allowed",
        "regen_optimisation_scoring_blocking_reasons",
        "regen_optimisation_recommendation_owner_status",
        "regen_optimisation_recommendation_allowed",
        "regen_optimisation_recommendation_blocking_reasons",
    ]

    print()
    print("=== PHASE 16J.2 SCORING ACTIVATION AUDIT ===")
    print()

    for key in keys:
        value = results.get(key)
        if isinstance(value, list):
            print(f"{key}: list length = {len(value)}")
            if value:
                print(f"{key} first item = {value[0]}")
        else:
            print(f"{key}: {value}")

    print()
    print("PASS_PHASE_16J2_SCORING_ACTIVATION_AUDIT")


if __name__ == "__main__":
    main()
