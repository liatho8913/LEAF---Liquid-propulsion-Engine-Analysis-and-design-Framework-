from material_specific_heat_integration_owner import (
    apply_material_specific_heat_integration,
)


def test_phase_10b3_applies_sourced_cp():
    results = {
        "phase_10b2_material_thermal_conductivity_integration_owner_complete": True,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "material_specific_heat_cp": 385.0,
        "material_property_interpolation_results": {
            "specific_heat": {
                "value": 410.0,
            }
        },
    }

    audit = apply_material_specific_heat_integration(results)

    assert audit["phase_10b3_material_specific_heat_integration_owner_complete"] is True
    assert audit["phase_10b3_material_specific_heat_integration_owner_status"] == (
        "PASS_PHASE_10B3_MATERIAL_SPECIFIC_HEAT_INTEGRATION_OWNER"
    )
    assert audit["phase_10b3_material_specific_heat_integration_owner_applied"] is True
    assert results["material_specific_heat_cp"] == 410.0
    assert results["material_specific_heat_cp_source"] == "SOURCED_INTERPOLATED_MATERIAL_CP_T"


def test_phase_10b3_blocks_placeholder_cp():
    results = {
        "phase_10b2_material_thermal_conductivity_integration_owner_complete": True,
        "material_source_validation_mode": "PLACEHOLDER_MODE",
        "material_source_is_placeholder": True,
        "material_specific_heat_cp": 385.0,
        "material_property_interpolation_results": {
            "specific_heat": {
                "value": 410.0,
            }
        },
    }

    audit = apply_material_specific_heat_integration(results)

    assert audit["phase_10b3_material_specific_heat_integration_owner_complete"] is True
    assert audit["phase_10b3_material_specific_heat_integration_owner_applied"] is False
    assert results["material_specific_heat_cp"] == 385.0


def test_phase_10b3_blocks_partial_source_cp():
    results = {
        "phase_10b2_material_thermal_conductivity_integration_owner_complete": True,
        "material_source_validation_mode": "PARTIAL_SOURCE_MODE",
        "material_source_is_placeholder": False,
        "material_specific_heat_cp": 385.0,
        "material_property_interpolation_results": {
            "specific_heat": {
                "value": 410.0,
            }
        },
    }

    audit = apply_material_specific_heat_integration(results)

    assert audit["phase_10b3_material_specific_heat_integration_owner_complete"] is True
    assert audit["phase_10b3_material_specific_heat_integration_owner_applied"] is False
    assert results["material_specific_heat_cp"] == 385.0


def test_phase_10b3_blocks_missing_10b2():
    results = {
        "phase_10b2_material_thermal_conductivity_integration_owner_complete": False,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "material_specific_heat_cp": 385.0,
        "material_property_interpolation_results": {
            "specific_heat": {
                "value": 410.0,
            }
        },
    }

    audit = apply_material_specific_heat_integration(results)

    assert audit["phase_10b3_material_specific_heat_integration_owner_complete"] is False
    assert audit["phase_10b3_material_specific_heat_integration_owner_applied"] is False
    assert results["material_specific_heat_cp"] == 385.0


if __name__ == "__main__":
    test_phase_10b3_applies_sourced_cp()
    test_phase_10b3_blocks_placeholder_cp()
    test_phase_10b3_blocks_partial_source_cp()
    test_phase_10b3_blocks_missing_10b2()
    print("PASS_PHASE_10B3_MATERIAL_SPECIFIC_HEAT_INTEGRATION_OWNER_TESTS")