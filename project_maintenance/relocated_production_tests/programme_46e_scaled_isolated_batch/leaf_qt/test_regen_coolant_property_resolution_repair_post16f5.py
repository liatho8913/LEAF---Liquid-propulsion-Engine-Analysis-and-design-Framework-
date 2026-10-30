from regen_coolant_property_resolution_repair import attach_regen_coolant_property_resolution_repair


def main():
    results = {
        "fuel_name": "RP-1",
        "mass_flow_rate": 1.15,
        "coolant_flow_fraction": 0.35,
        "recommended_geometry_status": "BLOCKED_NO_COOLANT_FLOW",
        "recommended_geometry_reason": "Cannot autosize recommended regen geometry because coolant mass flow is missing.",
    }

    results = attach_regen_coolant_property_resolution_repair(results)

    assert results["regen_coolant_property_resolution_repair_complete"] is True
    assert results["regen_coolant_property_resolution_repair_status"] == (
        "PASS_REGEN_COOLANT_PROPERTY_RESOLUTION_REPAIR_POST16F5"
    )

    assert results["coolant_mass_flow_rate"] > 0.0
    assert results["coolant_density"] > 0.0
    assert results["coolant_dynamic_viscosity"] > 0.0
    assert results["coolant_specific_heat_cp"] > 0.0
    assert results["coolant_thermal_conductivity"] > 0.0
    assert results["coolant_inlet_temperature"] > 0.0

    assert results["recommended_geometry_status"] == "COOLANT_FLOW_RESOLVED_REQUIRES_REGEN_RECALC"

    print("PASS_REGEN_COOLANT_PROPERTY_RESOLUTION_REPAIR_POST16F5")


if __name__ == "__main__":
    main()
