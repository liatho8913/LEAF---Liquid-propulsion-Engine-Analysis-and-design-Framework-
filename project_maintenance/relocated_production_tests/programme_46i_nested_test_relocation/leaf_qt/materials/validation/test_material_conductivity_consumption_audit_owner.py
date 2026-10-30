from material_conductivity_consumption_audit_owner import (
    attach_material_conductivity_consumption_audit_owner,
)


def test_material_conductivity_consumption_audit_owner_passes_when_k_moves_outputs():
    results = {
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
        "phase_10d1_temperature_dependency_discovery_audit_owner_status": (
            "PASS_PHASE_10D1_TEMPERATURE_DEPENDENCY_DISCOVERY_AUDIT_OWNER"
        ),
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",

        "sourced_wall_thermal_conductivity": 300.0,
        "wall_thermal_conductivity": 300.0,
        "inner_wall_thickness": 0.0012,

        "hot_gas_heat_transfer_coefficient": 8200.0,
        "coolant_heat_transfer_coefficient": 25000.0,
        "adiabatic_wall_temperature": 2800.0,
        "coolant_bulk_temperature": 300.0,

        "coating_thermal_resistance": 0.0,
        "bond_coat_thermal_resistance": 0.0,
    }

    solved = attach_material_conductivity_consumption_audit_owner(results)

    assert solved["phase_10d2_material_conductivity_consumption_audit_owner_complete"] is True
    assert solved["phase_10d2_material_conductivity_consumption_audit_owner_status"] == (
        "PASS_PHASE_10D2_MATERIAL_CONDUCTIVITY_CONSUMPTION_AUDIT_OWNER"
    )
    assert solved["phase_10d2_material_conductivity_consumption_audit_owner_pass"] is True
    assert solved["stage_10d_material_conductivity_consumption_complete"] is True

    perturbation = solved[
        "phase_10d2_material_conductivity_consumption_audit_owner_perturbation"
    ]

    assert perturbation["d_wall_resistance_low_to_high"] > 0.0
    assert perturbation["d_heat_flux_low_to_high"] > 0.0
    assert perturbation["d_twg_low_to_high"] > 0.0
    assert perturbation["d_twc_low_to_high"] > 0.0


def test_material_conductivity_consumption_audit_owner_fails_without_sourced_mode():
    results = {
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
        "material_source_validation_mode": "PLACEHOLDER_MODE",
        "sourced_wall_thermal_conductivity": 300.0,
        "inner_wall_thickness": 0.0012,
        "hot_gas_heat_transfer_coefficient": 8200.0,
        "coolant_heat_transfer_coefficient": 25000.0,
        "adiabatic_wall_temperature": 2800.0,
        "coolant_bulk_temperature": 300.0,
    }

    solved = attach_material_conductivity_consumption_audit_owner(results)

    assert solved["phase_10d2_material_conductivity_consumption_audit_owner_status"] == (
        "FAIL_PHASE_10D2_MATERIAL_CONDUCTIVITY_CONSUMPTION_AUDIT_OWNER"
    )
    assert solved["phase_10d2_material_conductivity_consumption_audit_owner_pass"] is False
    assert solved["stage_10d_material_conductivity_consumption_complete"] is False


if __name__ == "__main__":
    test_material_conductivity_consumption_audit_owner_passes_when_k_moves_outputs()
    test_material_conductivity_consumption_audit_owner_fails_without_sourced_mode()
    print("PASS_MATERIAL_CONDUCTIVITY_CONSUMPTION_AUDIT_OWNER")