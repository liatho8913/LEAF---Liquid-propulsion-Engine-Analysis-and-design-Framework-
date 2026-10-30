from material_strength_limit_integration_owner import (
    apply_material_strength_limit_integration,
)


def test_phase_10b6_applies_sourced_strength_and_passes():
    results = {
        "phase_10b5_material_temperature_limit_integration_owner_complete": True,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "material_yield_strength": 200_000_000.0,
        "wall_stress": 50_000_000.0,
        "wall_safety_factor": 2.0,
        "wall_joint_efficiency": 1.0,
        "material_property_interpolation_results": {
            "yield_strength": {
                "value": 240_000_000.0,
            }
        },
    }

    audit = apply_material_strength_limit_integration(results)

    assert audit["phase_10b6_material_strength_limit_integration_owner_complete"] is True
    assert audit["phase_10b6_material_strength_limit_integration_owner_status"] == (
        "PASS_PHASE_10B6_MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER"
    )
    assert audit["phase_10b6_material_strength_limit_integration_owner_applied"] is True
    assert results["effective_material_yield_strength"] == 240_000_000.0
    assert results["material_allowable_wall_stress"] == 120_000_000.0
    assert results["material_structural_margin"] == 70_000_000.0
    assert results["material_structural_pass"] == 1.0


def test_phase_10b6_applies_sourced_strength_and_fails_wall_stress():
    results = {
        "phase_10b5_material_temperature_limit_integration_owner_complete": True,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "wall_stress": 150_000_000.0,
        "wall_safety_factor": 2.0,
        "material_property_interpolation_results": {
            "yield_strength": {
                "value": 240_000_000.0,
            }
        },
    }

    audit = apply_material_strength_limit_integration(results)

    assert audit["phase_10b6_material_strength_limit_integration_owner_applied"] is True
    assert results["material_allowable_wall_stress"] == 120_000_000.0
    assert results["material_structural_margin"] == -30_000_000.0
    assert results["material_structural_pass"] == 0.0


def test_phase_10b6_blocks_placeholder_strength():
    results = {
        "phase_10b5_material_temperature_limit_integration_owner_complete": True,
        "material_source_validation_mode": "PLACEHOLDER_MODE",
        "material_source_is_placeholder": True,
        "material_yield_strength": 200_000_000.0,
        "wall_stress": 50_000_000.0,
        "material_property_interpolation_results": {
            "yield_strength": {
                "value": 240_000_000.0,
            }
        },
    }

    audit = apply_material_strength_limit_integration(results)

    assert audit["phase_10b6_material_strength_limit_integration_owner_complete"] is True
    assert audit["phase_10b6_material_strength_limit_integration_owner_applied"] is False
    assert results["material_structural_pass"] == 0.0


def test_phase_10b6_blocks_missing_10b5():
    results = {
        "phase_10b5_material_temperature_limit_integration_owner_complete": False,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,
        "wall_stress": 50_000_000.0,
        "material_property_interpolation_results": {
            "yield_strength": {
                "value": 240_000_000.0,
            }
        },
    }

    audit = apply_material_strength_limit_integration(results)

    assert audit["phase_10b6_material_strength_limit_integration_owner_complete"] is False
    assert audit["phase_10b6_material_strength_limit_integration_owner_applied"] is False


if __name__ == "__main__":
    test_phase_10b6_applies_sourced_strength_and_passes()
    test_phase_10b6_applies_sourced_strength_and_fails_wall_stress()
    test_phase_10b6_blocks_placeholder_strength()
    test_phase_10b6_blocks_missing_10b5()
    print("PASS_PHASE_10B6_MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER_TESTS")