from coating_thermal_resistance_integration_owner import (
    apply_coating_thermal_resistance_integration,
)


def test_phase_10c4_no_coating_selected_does_not_apply():
    results = {
        "phase_10c3_coating_thickness_integration_owner_complete": True,
        "coating_source_validation_mode": "NONE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "NONE",
        "effective_coating_thickness": 0.0,
        "coating_thermal_conductivity": None,
    }

    audit = apply_coating_thermal_resistance_integration(results)

    assert audit["phase_10c4_coating_thermal_resistance_integration_owner_complete"] is True
    assert audit["phase_10c4_coating_thermal_resistance_integration_owner_status"] == (
        "PASS_PHASE_10C4_COATING_THERMAL_RESISTANCE_INTEGRATION_OWNER"
    )
    assert audit["phase_10c4_coating_thermal_resistance_integration_owner_applied"] is False
    assert audit["phase_10c4_coating_thermal_resistance_integration_owner_decision"] == (
        "NO_COATING_SELECTED"
    )


def test_phase_10c4_calculates_coating_thermal_resistance():
    results = {
        "phase_10c3_coating_thickness_integration_owner_complete": True,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "YBCO",
        "effective_coating_thickness": 0.0002,
        "coating_thermal_conductivity": 2.5,
    }

    audit = apply_coating_thermal_resistance_integration(results)

    expected_r = 0.0002 / 2.5

    assert audit["phase_10c4_coating_thermal_resistance_integration_owner_complete"] is True
    assert audit["phase_10c4_coating_thermal_resistance_integration_owner_applied"] is True
    assert results["effective_coating_thermal_resistance"] == expected_r
    assert results["coating_thermal_resistance"] == expected_r
    assert results["coating_thermal_resistance_source"] == (
        "CALCULATED_FROM_OWNED_COATING_THICKNESS_AND_CONDUCTIVITY"
    )


def test_phase_10c4_blocks_placeholder_coating_resistance():
    results = {
        "phase_10c3_coating_thickness_integration_owner_complete": True,
        "coating_source_validation_mode": "PLACEHOLDER_MODE",
        "coating_source_is_placeholder": True,
        "selected_coating_material": "PLACEHOLDER_COATING",
        "effective_coating_thickness": 0.0002,
        "coating_thermal_conductivity": 2.5,
    }

    audit = apply_coating_thermal_resistance_integration(results)

    assert audit["phase_10c4_coating_thermal_resistance_integration_owner_complete"] is True
    assert audit["phase_10c4_coating_thermal_resistance_integration_owner_applied"] is False
    assert results.get("effective_coating_thermal_resistance") is None


def test_phase_10c4_blocks_missing_10c3():
    results = {
        "phase_10c3_coating_thickness_integration_owner_complete": False,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "YBCO",
        "effective_coating_thickness": 0.0002,
        "coating_thermal_conductivity": 2.5,
    }

    audit = apply_coating_thermal_resistance_integration(results)

    assert audit["phase_10c4_coating_thermal_resistance_integration_owner_complete"] is False
    assert audit["phase_10c4_coating_thermal_resistance_integration_owner_applied"] is False


if __name__ == "__main__":
    test_phase_10c4_no_coating_selected_does_not_apply()
    test_phase_10c4_calculates_coating_thermal_resistance()
    test_phase_10c4_blocks_placeholder_coating_resistance()
    test_phase_10c4_blocks_missing_10c3()
    print("PASS_PHASE_10C4_COATING_THERMAL_RESISTANCE_INTEGRATION_OWNER_TESTS")