from specific_heat_consumption_audit_owner import (
    attach_specific_heat_consumption_audit_owner,
)


def test_specific_heat_consumption_audit_owner_passes_when_cp_moves_outputs():
    results = {
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
        "phase_10d1_temperature_dependency_discovery_audit_owner_status": (
            "PASS_PHASE_10D1_TEMPERATURE_DEPENDENCY_DISCOVERY_AUDIT_OWNER"
        ),
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "phase_10d_verification_specific_heat_evidence": {
            "specific_heat_cp": 2000.0,
            "heat_load": 180000.0,
            "coolant_mass_flow": 0.4,
            "coolant_inlet_temperature": 300.0,
        },
    }

    solved = attach_specific_heat_consumption_audit_owner(results)

    assert solved["phase_10d3_specific_heat_consumption_audit_owner_complete"] is True
    assert solved["phase_10d3_specific_heat_consumption_audit_owner_status"] == (
        "PASS_PHASE_10D3_SPECIFIC_HEAT_CONSUMPTION_AUDIT_OWNER"
    )
    assert solved["phase_10d3_specific_heat_consumption_audit_owner_pass"] is True
    assert solved["stage_10d_specific_heat_consumption_complete"] is True

    perturbation = solved[
        "phase_10d3_specific_heat_consumption_audit_owner_perturbation"
    ]

    assert perturbation["d_delta_t_low_to_high"] > 0.0
    assert perturbation["d_outlet_temperature_low_to_high"] > 0.0


def test_specific_heat_consumption_audit_owner_fails_without_sourced_mode():
    results = {
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": True,
        "material_source_validation_mode": "PLACEHOLDER_MODE",
        "phase_10d_verification_specific_heat_evidence": {
            "specific_heat_cp": 2000.0,
            "heat_load": 180000.0,
            "coolant_mass_flow": 0.4,
            "coolant_inlet_temperature": 300.0,
        },
    }

    solved = attach_specific_heat_consumption_audit_owner(results)

    assert solved["phase_10d3_specific_heat_consumption_audit_owner_status"] == (
        "FAIL_PHASE_10D3_SPECIFIC_HEAT_CONSUMPTION_AUDIT_OWNER"
    )
    assert solved["phase_10d3_specific_heat_consumption_audit_owner_pass"] is False
    assert solved["stage_10d_specific_heat_consumption_complete"] is False


if __name__ == "__main__":
    test_specific_heat_consumption_audit_owner_passes_when_cp_moves_outputs()
    test_specific_heat_consumption_audit_owner_fails_without_sourced_mode()
    print("PASS_SPECIFIC_HEAT_CONSUMPTION_AUDIT_OWNER")