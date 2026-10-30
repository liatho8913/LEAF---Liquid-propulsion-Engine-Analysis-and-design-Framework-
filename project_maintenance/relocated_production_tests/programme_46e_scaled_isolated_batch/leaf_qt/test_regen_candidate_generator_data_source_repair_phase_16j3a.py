from regen_candidate_generator_data_source_repair import attach_regen_candidate_generator_data_source_repair


def main():
    results = {
        "fuel_name": "RP-1",
        "mass_flow_rate": 1.15,
        "fuel_mass_flow_rate": 0.4,
        "throat_area": 3.01e-4,
        "expansion_ratio": 9.12,
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.002,
        "rib_width": 0.001,
        "hot_gas_wall_thickness": 0.001,
        "coolant_flow_fraction": 0.35,
    }

    results = attach_regen_candidate_generator_data_source_repair(results)

    assert results["phase_16j3a_complete"] is True
    assert results["phase_16j3a_status"] == "PASS_REGEN_CANDIDATE_GENERATOR_DATA_SOURCE_REPAIR_PHASE_16J3A"
    assert results["regen_candidate_generator_data_source_repair_base_geometry_complete"] is True

    base = results["regen_candidate_generator_base_geometry"]
    assert base["base_geometry_complete"] is True
    assert base["number_of_coolant_channels"] == 80
    assert base["coolant_channel_width"] == 0.0015
    assert base["coolant_channel_height"] == 0.002
    assert base["rib_width"] == 0.001
    assert base["hot_gas_wall_thickness"] == 0.001
    assert base["coolant_mass_flow_fraction"] == 0.35
    assert base["channel_mid_radius"] > 0.0
    assert base["coolant_density"] > 0.0
    assert base["coolant_dynamic_viscosity"] > 0.0
    assert base["coolant_mass_flow_rate"] > 0.0

    print("PASS_REGEN_CANDIDATE_GENERATOR_DATA_SOURCE_REPAIR_PHASE_16J3A")


if __name__ == "__main__":
    main()
