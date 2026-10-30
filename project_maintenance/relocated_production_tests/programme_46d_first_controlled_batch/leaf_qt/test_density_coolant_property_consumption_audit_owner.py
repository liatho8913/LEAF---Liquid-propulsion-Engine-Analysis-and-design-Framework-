from density_coolant_property_consumption_audit_owner import (
    attach_density_coolant_property_consumption_audit_owner,
)


def test_density_coolant_property_consumption_audit_owner_passes_when_outputs_move():
    results = {
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
        "phase_10d1_temperature_dependency_discovery_audit_owner_status": (
            "PASS_PHASE_10D1_TEMPERATURE_DEPENDENCY_DISCOVERY_AUDIT_OWNER"
        ),
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "phase_10d_verification_coolant_property_evidence": {
            "coolant_density": 810.0,
            "coolant_dynamic_viscosity": 0.0016,
            "coolant_mass_flow": 0.4,
            "coolant_flow_area": 0.00002,
            "hydraulic_diameter": 0.002,
            "flow_length": 0.5,
            "coolant_thermal_conductivity": 0.13,
        },
    }

    solved = attach_density_coolant_property_consumption_audit_owner(results)

    assert solved[
        "phase_10d4_density_coolant_property_consumption_audit_owner_complete"
    ] is True

    assert solved[
        "phase_10d4_density_coolant_property_consumption_audit_owner_status"
    ] == "PASS_PHASE_10D4_DENSITY_COOLANT_PROPERTY_CONSUMPTION_AUDIT_OWNER"

    assert solved[
        "phase_10d4_density_coolant_property_consumption_audit_owner_pass"
    ] is True

    perturbation = solved[
        "phase_10d4_density_coolant_property_consumption_audit_owner_perturbation"
    ]

    assert perturbation["d_velocity_density_low_to_high"] > 0.0
    assert perturbation["d_pressure_drop_density_low_to_high"] > 0.0
    assert perturbation["d_reynolds_viscosity_low_to_high"] > 0.0
    assert perturbation["d_friction_factor_viscosity_low_to_high"] > 0.0
    assert perturbation["d_heat_transfer_viscosity_low_to_high"] > 0.0
    assert perturbation["d_pressure_drop_viscosity_low_to_high"] > 0.0


def test_density_coolant_property_consumption_audit_owner_fails_without_sourced_mode():
    results = {
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
        "material_source_validation_mode": "PLACEHOLDER_MODE",
        "phase_10d_verification_coolant_property_evidence": {
            "coolant_density": 810.0,
            "coolant_dynamic_viscosity": 0.0016,
            "coolant_mass_flow": 0.4,
            "coolant_flow_area": 0.00002,
            "hydraulic_diameter": 0.002,
            "flow_length": 0.5,
            "coolant_thermal_conductivity": 0.13,
        },
    }

    solved = attach_density_coolant_property_consumption_audit_owner(results)

    assert solved[
        "phase_10d4_density_coolant_property_consumption_audit_owner_status"
    ] == "FAIL_PHASE_10D4_DENSITY_COOLANT_PROPERTY_CONSUMPTION_AUDIT_OWNER"

    assert solved[
        "phase_10d4_density_coolant_property_consumption_audit_owner_pass"
    ] is False


if __name__ == "__main__":
    test_density_coolant_property_consumption_audit_owner_passes_when_outputs_move()
    test_density_coolant_property_consumption_audit_owner_fails_without_sourced_mode()
    print("PASS_DENSITY_COOLANT_PROPERTY_CONSUMPTION_AUDIT_OWNER")