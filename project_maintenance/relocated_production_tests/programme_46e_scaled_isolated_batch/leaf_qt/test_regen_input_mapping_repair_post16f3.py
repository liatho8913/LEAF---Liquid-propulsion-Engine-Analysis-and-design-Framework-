from regen_input_mapping_repair import attach_regen_input_mapping_repair


def main():
    results = {
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.002,
        "rib_width": 0.001,
        "minimum_wall_thickness": 0.001,
        "coolant_flow_fraction": 0.35,
        "throat_radius": 0.0098,
        "coolant_density": 800.0,
        "coolant_dynamic_viscosity": 0.0012,
        "mass_flow_rate": 1.15,
        "regen_candidate_generator_base_geometry": {
            "base_geometry_complete": False,
            "number_of_coolant_channels": None,
            "coolant_channel_width": None,
            "coolant_channel_height": None,
            "rib_width": None,
            "hot_gas_wall_thickness": None,
            "coolant_mass_flow_fraction": None,
            "channel_mid_radius": None,
            "coolant_density": None,
            "coolant_dynamic_viscosity": None,
            "coolant_mass_flow_rate": None,
        },
    }

    results = attach_regen_input_mapping_repair(results)

    assert results["regen_input_mapping_repair_complete"] is True
    assert results["regen_input_mapping_repair_status"] == "PASS_REGEN_INPUT_MAPPING_REPAIR_POST16F3"
    assert results["regen_input_mapping_repair_base_geometry_complete"] is True

    base = results["regen_candidate_generator_base_geometry"]
    assert base["base_geometry_complete"] is True
    assert base["number_of_coolant_channels"] == 80
    assert base["coolant_channel_width"] == 0.0015
    assert base["coolant_channel_height"] == 0.002
    assert base["rib_width"] == 0.001
    assert base["hot_gas_wall_thickness"] == 0.001
    assert base["coolant_mass_flow_fraction"] == 0.35
    assert base["channel_mid_radius"] > 0.0
    assert base["coolant_density"] == 800.0
    assert base["coolant_dynamic_viscosity"] == 0.0012
    assert base["coolant_mass_flow_rate"] > 0.0

    print("PASS_REGEN_INPUT_MAPPING_REPAIR_POST16F3")


if __name__ == "__main__":
    main()
