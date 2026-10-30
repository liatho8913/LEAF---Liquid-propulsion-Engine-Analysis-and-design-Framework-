from material_temperature_limit_integration_owner import (
    apply_material_temperature_limit_integration,
)


def test_phase_10b5_applies_sourced_temperature_limit_and_passes():
    results = {
        "phase_10b4_material_density_integration_owner_complete": True,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "effective_material_temperature_limit": 900.0,
        "max_hot_gas_wall_temperature": 800.0,
        "material_property_interpolation_results": {
            "max_temperature": {
                "value": 950.0,
            }
        },
    }

    audit = apply_material_temperature_limit_integration(results)

    assert audit["phase_10b5_material_temperature_limit_integration_owner_complete"] is True
    assert audit["phase_10b5_material_temperature_limit_integration_owner_status"] == (
        "PASS_PHASE_10B5_MATERIAL_TEMPERATURE_LIMIT_INTEGRATION_OWNER"
    )
    assert audit["phase_10b5_material_temperature_limit_integration_owner_applied"] is True
    assert results["effective_material_temperature_limit"] == 950.0
    assert results["material_temperature_limit_margin"] == 150.0
    assert results["material_temperature_limit_pass"] == 1.0


def test_phase_10b5_applies_sourced_temperature_limit_and_fails_hot_wall():
    results = {
        "phase_10b4_material_density_integration_owner_complete": True,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "effective_material_temperature_limit": 900.0,
        "max_hot_gas_wall_temperature": 1000.0,
        "material_property_interpolation_results": {
            "max_temperature": {
                "value": 950.0,
            }
        },
    }

    audit = apply_material_temperature_limit_integration(results)

    assert audit["phase_10b5_material_temperature_limit_integration_owner_applied"] is True
    assert results["effective_material_temperature_limit"] == 950.0
    assert results["material_temperature_limit_margin"] == -50.0
    assert results["material_temperature_limit_pass"] == 0.0


def test_phase_10b5_blocks_placeholder_temperature_limit():
    results = {
        "phase_10b4_material_density_integration_owner_complete": True,
        "material_source_validation_mode": "PLACEHOLDER_MODE",
        "material_source_is_placeholder": True,
        "effective_material_temperature_limit": 900.0,
        "max_hot_gas_wall_temperature": 800.0,
        "material_property_interpolation_results": {
            "max_temperature": {
                "value": 950.0,
            }
        },
    }

    audit = apply_material_temperature_limit_integration(results)

    assert audit["phase_10b5_material_temperature_limit_integration_owner_complete"] is True
    assert audit["phase_10b5_material_temperature_limit_integration_owner_applied"] is False
    assert results["material_temperature_limit_pass"] == 0.0


def test_phase_10b5_blocks_missing_10b4():
    results = {
        "phase_10b4_material_density_integration_owner_complete": False,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "effective_material_temperature_limit": 900.0,
        "max_hot_gas_wall_temperature": 800.0,
        "material_property_interpolation_results": {
            "max_temperature": {
                "value": 950.0,
            }
        },
    }

    audit = apply_material_temperature_limit_integration(results)

    assert audit["phase_10b5_material_temperature_limit_integration_owner_complete"] is False
    assert audit["phase_10b5_material_temperature_limit_integration_owner_applied"] is False


if __name__ == "__main__":
    test_phase_10b5_applies_sourced_temperature_limit_and_passes()
    test_phase_10b5_applies_sourced_temperature_limit_and_fails_hot_wall()
    test_phase_10b5_blocks_placeholder_temperature_limit()
    test_phase_10b5_blocks_missing_10b4()
    print("PASS_PHASE_10B5_MATERIAL_TEMPERATURE_LIMIT_INTEGRATION_OWNER_TESTS")