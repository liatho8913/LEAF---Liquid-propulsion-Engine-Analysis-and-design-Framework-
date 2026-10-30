from coating_temperature_limit_integration_owner import (
    apply_coating_temperature_limit_integration,
)


def test_phase_10c5_no_coating_selected_does_not_apply():
    results = {
        "phase_10c4_coating_thermal_resistance_integration_owner_complete": True,
        "coating_source_validation_mode": "NONE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "NONE",
        "effective_coating_thickness": 0.0,
    }

    audit = apply_coating_temperature_limit_integration(results)

    assert audit["phase_10c5_coating_temperature_limit_integration_owner_complete"] is True
    assert audit["phase_10c5_coating_temperature_limit_integration_owner_status"] == (
        "PASS_PHASE_10C5_COATING_TEMPERATURE_LIMIT_INTEGRATION_OWNER"
    )
    assert audit["phase_10c5_coating_temperature_limit_integration_owner_applied"] is False
    assert audit["phase_10c5_coating_temperature_limit_integration_owner_decision"] == (
        "NO_COATING_SELECTED"
    )


def test_phase_10c5_applies_sourced_temperature_limit_and_passes():
    results = {
        "phase_10c4_coating_thermal_resistance_integration_owner_complete": True,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "YBCO",
        "effective_coating_thickness": 0.0002,
        "coating_surface_temperature": 1200.0,
        "coating_property_interpolation_results": {
            "max_temperature": {
                "value": 1500.0,
            }
        },
    }

    audit = apply_coating_temperature_limit_integration(results)

    assert audit["phase_10c5_coating_temperature_limit_integration_owner_complete"] is True
    assert audit["phase_10c5_coating_temperature_limit_integration_owner_applied"] is True
    assert results["effective_coating_temperature_limit"] == 1500.0
    assert results["coating_temperature_limit_margin"] == 300.0
    assert results["coating_temperature_limit_pass"] == 1.0


def test_phase_10c5_applies_sourced_temperature_limit_and_fails():
    results = {
        "phase_10c4_coating_thermal_resistance_integration_owner_complete": True,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "YBCO",
        "effective_coating_thickness": 0.0002,
        "coating_surface_temperature": 1600.0,
        "coating_property_interpolation_results": {
            "max_temperature": {
                "value": 1500.0,
            }
        },
    }

    audit = apply_coating_temperature_limit_integration(results)

    assert audit["phase_10c5_coating_temperature_limit_integration_owner_applied"] is True
    assert results["effective_coating_temperature_limit"] == 1500.0
    assert results["coating_temperature_limit_margin"] == -100.0
    assert results["coating_temperature_limit_pass"] == 0.0


def test_phase_10c5_blocks_placeholder_temperature_limit():
    results = {
        "phase_10c4_coating_thermal_resistance_integration_owner_complete": True,
        "coating_source_validation_mode": "PLACEHOLDER_MODE",
        "coating_source_is_placeholder": True,
        "selected_coating_material": "PLACEHOLDER_COATING",
        "effective_coating_thickness": 0.0002,
        "coating_surface_temperature": 1200.0,
        "coating_property_interpolation_results": {
            "max_temperature": {
                "value": 1500.0,
            }
        },
    }

    audit = apply_coating_temperature_limit_integration(results)

    assert audit["phase_10c5_coating_temperature_limit_integration_owner_complete"] is True
    assert audit["phase_10c5_coating_temperature_limit_integration_owner_applied"] is False
    assert results["coating_temperature_limit_pass"] == 0.0


def test_phase_10c5_blocks_missing_10c4():
    results = {
        "phase_10c4_coating_thermal_resistance_integration_owner_complete": False,
        "coating_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_is_placeholder": False,
        "selected_coating_material": "YBCO",
        "effective_coating_thickness": 0.0002,
        "coating_surface_temperature": 1200.0,
        "coating_property_interpolation_results": {
            "max_temperature": {
                "value": 1500.0,
            }
        },
    }

    audit = apply_coating_temperature_limit_integration(results)

    assert audit["phase_10c5_coating_temperature_limit_integration_owner_complete"] is False
    assert audit["phase_10c5_coating_temperature_limit_integration_owner_applied"] is False


if __name__ == "__main__":
    test_phase_10c5_no_coating_selected_does_not_apply()
    test_phase_10c5_applies_sourced_temperature_limit_and_passes()
    test_phase_10c5_applies_sourced_temperature_limit_and_fails()
    test_phase_10c5_blocks_placeholder_temperature_limit()
    test_phase_10c5_blocks_missing_10c4()
    print("PASS_PHASE_10C5_COATING_TEMPERATURE_LIMIT_INTEGRATION_OWNER_TESTS")