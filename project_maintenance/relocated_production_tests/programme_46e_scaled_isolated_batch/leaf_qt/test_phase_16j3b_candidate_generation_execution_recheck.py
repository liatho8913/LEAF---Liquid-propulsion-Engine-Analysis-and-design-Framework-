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

print()
print("PHASE_16J3B_CANDIDATE_EXECUTION_RECHECK")
print("=======================================")

keys = [
    "regen_candidate_generator_data_source_repair_base_geometry_complete",

    "regen_optimisation_candidate_generator_enabled",
    "regen_optimisation_candidate_generator_generation_allowed",
    "regen_optimisation_candidate_generator_status",
    "regen_optimisation_candidate_generator_candidate_count",

    "regen_optimisation_scoring_allowed",
    "regen_optimisation_scored_candidate_count",

    "regen_optimisation_recommendation_allowed",
    "regen_optimisation_recommendation_ranked_candidate_count",
]

for key in keys:
    print(key, "=", results.get(key))

print()

candidates = (
    results.get("regen_optimisation_candidate_generator_candidates")
    or []
)

print("candidate_list_length =", len(candidates))

if candidates:
    print()
    print("FIRST CANDIDATE")
    print(candidates[0])

print()
print("PASS_PHASE_16J3B_EXECUTION_RECHECK")
