from regen_coolant_flow_activation_layer import attach_regen_coolant_flow_activation_layer


def main():
    results = {
        "fuel_name": "RP-1",
        "mass_flow_rate": 1.15,
        "fuel_mass_flow_rate": 0.4,
        "coolant_flow_fraction": 0.35,
        "recommended_geometry_status": "BLOCKED_NO_COOLANT_FLOW",
        "recommended_geometry_reason": "Cannot autosize recommended regen geometry because coolant mass flow is missing.",
    }

    results = attach_regen_coolant_flow_activation_layer(results)

    assert results["phase_16j2a_complete"] is True
    assert results["phase_16j2a_status"] == "PASS_REGEN_COOLANT_FLOW_ACTIVATION_LAYER_PHASE_16J2A"
    assert results["selected_coolant_name"] == "RP-1"
    assert results["coolant_mass_flow_fraction"] == 0.35
    assert results["coolant_flow_fraction"] == 0.35
    assert abs(results["coolant_mass_flow_rate"] - 0.14) < 1e-12
    assert results["regen_coolant_mass_flow_rate"] == results["coolant_mass_flow_rate"]
    assert results["recommended_geometry_status"] == "COOLANT_FLOW_AVAILABLE_RECALC_REQUIRED"
    assert results["phase_16j2b_candidate_generation_recheck_allowed"] is True

    print("PASS_REGEN_COOLANT_FLOW_ACTIVATION_LAYER_PHASE_16J2A")


if __name__ == "__main__":
    main()
