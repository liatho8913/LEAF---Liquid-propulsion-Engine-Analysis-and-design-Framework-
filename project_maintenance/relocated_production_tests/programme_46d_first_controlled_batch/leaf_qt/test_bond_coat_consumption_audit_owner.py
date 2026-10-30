from bond_coat_consumption_audit_owner import (
    attach_bond_coat_consumption_audit_owner,
)


def test_bond_coat_consumption_audit_owner_passes_when_no_bond_selected():
    results = {
        "bond_coat_name": "NONE",
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
    }

    solved = attach_bond_coat_consumption_audit_owner(results)

    assert solved["phase_10d6_bond_coat_consumption_audit_owner_complete"] is True
    assert solved["phase_10d6_bond_coat_consumption_audit_owner_status"] == (
        "PASS_PHASE_10D6_BOND_COAT_CONSUMPTION_AUDIT_OWNER"
    )
    assert solved["phase_10d6_bond_coat_consumption_audit_owner_mode"] == (
        "OPTIONAL_LAYER_NOT_SELECTED"
    )


def test_bond_coat_consumption_audit_owner_passes_when_active_bond_moves_outputs():
    results = {
        "bond_coat_name": "MCrAlY",
        "bond_coat_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "bond_coat_temperature_table_status": "PASS_TABLE_AVAILABLE",
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
        "phase_10d_verification_bond_coat_evidence": {
            "bond_coat_thermal_conductivity": 8.0,
            "bond_coat_thickness": 0.000075,
            "coating_thermal_resistance": 0.0001666667,
            "hot_gas_heat_transfer_coefficient": 8200.0,
            "coolant_heat_transfer_coefficient": 25000.0,
            "adiabatic_wall_temperature": 2800.0,
            "coolant_bulk_temperature": 300.0,
            "wall_thermal_resistance": 0.000004,
            "bond_coat_temperature_limit": 1450.0,
        },
    }

    solved = attach_bond_coat_consumption_audit_owner(results)

    assert solved["phase_10d6_bond_coat_consumption_audit_owner_status"] == (
        "PASS_PHASE_10D6_BOND_COAT_CONSUMPTION_AUDIT_OWNER"
    )
    assert solved["phase_10d6_bond_coat_consumption_audit_owner_pass"] is True

    perturbation = solved[
        "phase_10d6_bond_coat_consumption_audit_owner_perturbation"
    ]

    assert perturbation["d_bond_resistance_k_low_to_high"] > 0.0
    assert perturbation["d_total_resistance_k_low_to_high"] > 0.0
    assert perturbation["d_heat_flux_k_low_to_high"] > 0.0
    assert perturbation["d_bond_wall_interface_temperature_k_low_to_high"] > 0.0
    assert perturbation["d_bond_resistance_thickness_low_to_high"] > 0.0
    assert perturbation["d_total_resistance_thickness_low_to_high"] > 0.0
    assert perturbation["d_heat_flux_thickness_low_to_high"] > 0.0
    assert perturbation["d_bond_margin_thickness_low_to_high"] > 0.0


def test_bond_coat_consumption_audit_owner_fails_when_selected_bond_missing_table():
    results = {
        "bond_coat_name": "MCrAlY",
        "bond_coat_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "bond_coat_temperature_table_status": "MISSING",
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
        "phase_10d_verification_bond_coat_evidence": {
            "bond_coat_thermal_conductivity": 8.0,
            "bond_coat_thickness": 0.000075,
            "coating_thermal_resistance": 0.0001666667,
            "hot_gas_heat_transfer_coefficient": 8200.0,
            "coolant_heat_transfer_coefficient": 25000.0,
            "adiabatic_wall_temperature": 2800.0,
            "coolant_bulk_temperature": 300.0,
            "wall_thermal_resistance": 0.000004,
            "bond_coat_temperature_limit": 1450.0,
        },
    }

    solved = attach_bond_coat_consumption_audit_owner(results)

    assert solved["phase_10d6_bond_coat_consumption_audit_owner_status"] == (
        "FAIL_PHASE_10D6_BOND_COAT_CONSUMPTION_AUDIT_OWNER"
    )
    assert solved["phase_10d6_bond_coat_consumption_audit_owner_pass"] is False


if __name__ == "__main__":
    test_bond_coat_consumption_audit_owner_passes_when_no_bond_selected()
    test_bond_coat_consumption_audit_owner_passes_when_active_bond_moves_outputs()
    test_bond_coat_consumption_audit_owner_fails_when_selected_bond_missing_table()
    print("PASS_BOND_COAT_CONSUMPTION_AUDIT_OWNER")