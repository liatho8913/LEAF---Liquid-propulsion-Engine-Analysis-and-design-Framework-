from coating_thermal_consumption_audit_owner import (
    attach_coating_thermal_consumption_audit_owner,
)


def test_coating_thermal_consumption_audit_owner_passes_when_no_coating_selected():
    results = {
        "coating_name": "NONE",
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
    }

    solved = attach_coating_thermal_consumption_audit_owner(results)

    assert solved["phase_10d5_coating_thermal_consumption_audit_owner_complete"] is True
    assert solved["phase_10d5_coating_thermal_consumption_audit_owner_status"] == (
        "PASS_PHASE_10D5_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER"
    )
    assert solved["phase_10d5_coating_thermal_consumption_audit_owner_mode"] == (
        "OPTIONAL_LAYER_NOT_SELECTED"
    )


def test_coating_thermal_consumption_audit_owner_passes_when_active_coating_moves_outputs():
    results = {
        "coating_name": "TBC",
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_temperature_table_status": "PASS_TABLE_AVAILABLE",
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
        "phase_10d_verification_coating_thermal_evidence": {
            "coating_thermal_conductivity": 1.5,
            "coating_thickness": 0.00025,
            "hot_gas_heat_transfer_coefficient": 8200.0,
            "coolant_heat_transfer_coefficient": 25000.0,
            "adiabatic_wall_temperature": 2800.0,
            "coolant_bulk_temperature": 300.0,
            "wall_thermal_resistance": 0.000004,
            "coating_temperature_limit": 1600.0,
        },
    }

    solved = attach_coating_thermal_consumption_audit_owner(results)

    assert solved["phase_10d5_coating_thermal_consumption_audit_owner_status"] == (
        "PASS_PHASE_10D5_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER"
    )
    assert solved["phase_10d5_coating_thermal_consumption_audit_owner_pass"] is True

    perturbation = solved[
        "phase_10d5_coating_thermal_consumption_audit_owner_perturbation"
    ]

    assert perturbation["d_coating_resistance_k_low_to_high"] > 0.0
    assert perturbation["d_total_resistance_k_low_to_high"] > 0.0
    assert perturbation["d_heat_flux_k_low_to_high"] > 0.0
    assert perturbation["d_protected_wall_temperature_k_low_to_high"] > 0.0
    assert perturbation["d_coating_resistance_thickness_low_to_high"] > 0.0
    assert perturbation["d_total_resistance_thickness_low_to_high"] > 0.0
    assert perturbation["d_heat_flux_thickness_low_to_high"] > 0.0
    assert perturbation["d_coating_margin_thickness_low_to_high"] > 0.0


def test_coating_thermal_consumption_audit_owner_fails_when_selected_coating_missing_table():
    results = {
        "coating_name": "TBC",
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_temperature_table_status": "MISSING",
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
        "phase_10d_verification_coating_thermal_evidence": {
            "coating_thermal_conductivity": 1.5,
            "coating_thickness": 0.00025,
            "hot_gas_heat_transfer_coefficient": 8200.0,
            "coolant_heat_transfer_coefficient": 25000.0,
            "adiabatic_wall_temperature": 2800.0,
            "coolant_bulk_temperature": 300.0,
            "wall_thermal_resistance": 0.000004,
            "coating_temperature_limit": 1600.0,
        },
    }

    solved = attach_coating_thermal_consumption_audit_owner(results)

    assert solved["phase_10d5_coating_thermal_consumption_audit_owner_status"] == (
        "FAIL_PHASE_10D5_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER"
    )
    assert solved["phase_10d5_coating_thermal_consumption_audit_owner_pass"] is False


if __name__ == "__main__":
    test_coating_thermal_consumption_audit_owner_passes_when_no_coating_selected()
    test_coating_thermal_consumption_audit_owner_passes_when_active_coating_moves_outputs()
    test_coating_thermal_consumption_audit_owner_fails_when_selected_coating_missing_table()
    print("PASS_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER")