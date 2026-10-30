from calculation_bridge import calculate_with_full_bridge

results = calculate_with_full_bridge({
    "fuel_name": "RP-1",
    "oxidizer_name": "LOX",
    "chamber_pressure": 6.895e6,
    "mass_flow_rate": 1.15,
    "mixture_ratio": 1.875,

    "number_of_coolant_channels": 80,
    "coolant_channel_width": 0.0015,
    "coolant_channel_height": 0.0020,
    "rib_width": 0.0010,
    "hot_gas_wall_thickness": 0.0010,
    "coolant_flow_fraction": 0.35,
})

keys = [
    "regen_optimisation_candidate_generator_enabled",
    "regen_optimisation_candidate_generator_generation_allowed",
    "regen_optimisation_candidate_generator_status",
    "regen_optimisation_candidate_generator_candidate_count",

    "regen_optimisation_scoring_enabled",
    "regen_optimisation_scoring_allowed",
    "regen_optimisation_scored_candidate_count",

    "regen_optimisation_recommendation_allowed",
    "regen_optimisation_recommendation_ranked_candidate_count",

    "best_full_engine_regen_status",
]

print()
print("PHASE_16J2B_CANDIDATE_PIPELINE_AUDIT")
print("====================================")
print()

for key in keys:
    print(key, "=", results.get(key))
