from material_integration_completion_audit import (
    build_material_integration_completion_audit,
)


def _base_complete_results():
    return {
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_is_placeholder": False,

        "phase_10b1_material_property_consumption_audit_owner_complete": True,
        "phase_10b2_material_thermal_conductivity_integration_owner_complete": True,
        "phase_10b3_material_specific_heat_integration_owner_complete": True,
        "phase_10b4_material_density_integration_owner_complete": True,
        "phase_10b5_material_temperature_limit_integration_owner_complete": True,
        "phase_10b6_material_strength_limit_integration_owner_complete": True,
        "phase_10b7_material_integration_validation_owner_complete": True,

        "phase_10b7_material_integration_validation_owner_status": (
            "PASS_PHASE_10B7_MATERIAL_INTEGRATION_VALIDATION_OWNER"
        ),
        "phase_10b7_material_integration_validation_pass": True,

        "wall_thermal_conductivity": 250.0,
        "material_specific_heat_cp": 410.0,
        "material_density": 8920.0,
        "effective_material_temperature_limit": 950.0,
        "effective_material_yield_strength": 240_000_000.0,
    }


def test_phase_10b8_passes_complete_material_integration_stack():
    results = _base_complete_results()

    audit = build_material_integration_completion_audit(results)

    assert audit["phase_10b8_material_integration_completion_audit_complete"] is True
    assert audit["phase_10b8_material_integration_completion_audit_pass"] is True
    assert audit["phase_10b8_material_integration_completion_audit_status"] == (
        "PASS_MATERIAL_INTEGRATION_COMPLETION_AUDIT"
    )


def test_phase_10b8_fails_when_validation_fails():
    results = _base_complete_results()
    results["phase_10b7_material_integration_validation_owner_status"] = (
        "FAIL_PHASE_10B7_MATERIAL_INTEGRATION_VALIDATION_OWNER"
    )
    results["phase_10b7_material_integration_validation_pass"] = False

    audit = build_material_integration_completion_audit(results)

    assert audit["phase_10b8_material_integration_completion_audit_complete"] is True
    assert audit["phase_10b8_material_integration_completion_audit_pass"] is False
    assert audit["phase_10b8_material_integration_completion_audit_status"] == (
        "FAIL_MATERIAL_INTEGRATION_COMPLETION_AUDIT"
    )


def test_phase_10b8_fails_placeholder_material():
    results = _base_complete_results()
    results["material_source_validation_mode"] = "PLACEHOLDER_MODE"
    results["material_source_is_placeholder"] = True

    audit = build_material_integration_completion_audit(results)

    assert audit["phase_10b8_material_integration_completion_audit_pass"] is False
    assert any(
        "placeholder" in blocker.lower()
        for blocker in audit["phase_10b8_material_integration_completion_audit_blockers"]
    )


def test_phase_10b8_fails_missing_stage():
    results = _base_complete_results()
    results["phase_10b4_material_density_integration_owner_complete"] = False

    audit = build_material_integration_completion_audit(results)

    assert audit["phase_10b8_material_integration_completion_audit_complete"] is False
    assert audit["phase_10b8_material_integration_completion_audit_pass"] is False


if __name__ == "__main__":
    test_phase_10b8_passes_complete_material_integration_stack()
    test_phase_10b8_fails_when_validation_fails()
    test_phase_10b8_fails_placeholder_material()
    test_phase_10b8_fails_missing_stage()
    print("PASS_PHASE_10B8_MATERIAL_INTEGRATION_COMPLETION_AUDIT_TESTS")