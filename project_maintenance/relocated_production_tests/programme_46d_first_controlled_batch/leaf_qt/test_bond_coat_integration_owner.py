from bond_coat_integration_owner import (
    apply_bond_coat_integration,
)


def test_phase_10c6_no_bond_coat_selected_does_not_apply():
    results = {
        "phase_10c5_coating_temperature_limit_integration_owner_complete": True,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "bond_coat_enabled": False,
    }

    audit = apply_bond_coat_integration(results)

    assert audit["phase_10c6_bond_coat_integration_owner_complete"] is True
    assert audit["phase_10c6_bond_coat_integration_owner_status"] == (
        "PASS_PHASE_10C6_BOND_COAT_INTEGRATION_OWNER"
    )
    assert audit["phase_10c6_bond_coat_integration_owner_applied"] is False
    assert audit["phase_10c6_bond_coat_integration_owner_decision"] == (
        "NO_BOND_COAT_SELECTED"
    )


def test_phase_10c6_applies_bond_coat_resistance_and_temperature_pass():
    results = {
        "phase_10c5_coating_temperature_limit_integration_owner_complete": True,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "bond_coat_source_is_placeholder": False,
        "bond_coat_enabled": True,
        "selected_bond_coat_material": "MCrAlY",
        "bond_coat_thickness": 0.0001,
        "bond_coat_thermal_conductivity": 12.5,
        "bond_coat_temperature_limit": 1350.0,
        "bond_coat_temperature": 1100.0,
    }

    audit = apply_bond_coat_integration(results)

    expected_r = 0.0001 / 12.5

    assert audit["phase_10c6_bond_coat_integration_owner_complete"] is True
    assert audit["phase_10c6_bond_coat_integration_owner_applied"] is True
    assert results["effective_bond_coat_thermal_resistance"] == expected_r
    assert results["bond_coat_temperature_limit_margin"] == 250.0
    assert results["bond_coat_temperature_limit_pass"] == 1.0


def test_phase_10c6_applies_bond_coat_and_fails_temperature():
    results = {
        "phase_10c5_coating_temperature_limit_integration_owner_complete": True,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "bond_coat_source_is_placeholder": False,
        "bond_coat_enabled": True,
        "selected_bond_coat_material": "MCrAlY",
        "bond_coat_thickness": 0.0001,
        "bond_coat_thermal_conductivity": 12.5,
        "bond_coat_temperature_limit": 1000.0,
        "bond_coat_temperature": 1100.0,
    }

    audit = apply_bond_coat_integration(results)

    assert audit["phase_10c6_bond_coat_integration_owner_applied"] is True
    assert results["bond_coat_temperature_limit_margin"] == -100.0
    assert results["bond_coat_temperature_limit_pass"] == 0.0


def test_phase_10c6_blocks_placeholder_bond_coat():
    results = {
        "phase_10c5_coating_temperature_limit_integration_owner_complete": True,
        "coating_source_validation_mode": "PLACEHOLDER_MODE",
        "bond_coat_source_is_placeholder": True,
        "bond_coat_enabled": True,
        "selected_bond_coat_material": "PLACEHOLDER_BOND",
        "bond_coat_thickness": 0.0001,
        "bond_coat_thermal_conductivity": 12.5,
    }

    audit = apply_bond_coat_integration(results)

    assert audit["phase_10c6_bond_coat_integration_owner_complete"] is True
    assert audit["phase_10c6_bond_coat_integration_owner_applied"] is False
    assert results["bond_coat_temperature_limit_pass"] == 0.0


def test_phase_10c6_blocks_missing_10c5():
    results = {
        "phase_10c5_coating_temperature_limit_integration_owner_complete": False,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "bond_coat_enabled": True,
        "selected_bond_coat_material": "MCrAlY",
        "bond_coat_thickness": 0.0001,
        "bond_coat_thermal_conductivity": 12.5,
    }

    audit = apply_bond_coat_integration(results)

    assert audit["phase_10c6_bond_coat_integration_owner_complete"] is False
    assert audit["phase_10c6_bond_coat_integration_owner_applied"] is False


if __name__ == "__main__":
    test_phase_10c6_no_bond_coat_selected_does_not_apply()
    test_phase_10c6_applies_bond_coat_resistance_and_temperature_pass()
    test_phase_10c6_applies_bond_coat_and_fails_temperature()
    test_phase_10c6_blocks_placeholder_bond_coat()
    test_phase_10c6_blocks_missing_10c5()
    print("PASS_PHASE_10C6_BOND_COAT_INTEGRATION_OWNER_TESTS")