from temperature_dependency_discovery_audit_owner import (
    attach_temperature_dependency_discovery_audit_owner,
)


def test_temperature_dependency_discovery_audit_owner():
    results = {
        "phase_10c8_coating_integration_completion_audit_complete": True,
        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_property_interpolation_results": {
            "thermal_conductivity": {"value": 250.0},
            "specific_heat": {"value": 455.0},
            "density": {"value": 8750.0},
        },
        "sourced_wall_thermal_conductivity": 250.0,
        "wall_thermal_conductivity": 250.0,
        "phase_10b2_material_thermal_conductivity_integration_owner_applied": True,
        "wall_thermal_conductivity_source": "SOURCED_INTERPOLATED_MATERIAL_KT",
        "hot_gas_side_wall_temperature": 850.0,
        "regen_heat_flux": 18_000_000.0,
        "material_specific_heat": 455.0,
        "phase_10b3_material_specific_heat_integration_owner_applied": True,
        "coolant_temperature_rise": 25.0,
        "material_density": 8750.0,
        "phase_10b4_material_density_integration_owner_applied": True,
        "coolant_density": 810.0,
        "coolant_dynamic_viscosity": 0.0016,
        "coolant_specific_heat_cp": 2000.0,
        "regen_coolant_velocity": 25.0,
        "regen_reynolds_number": 50000.0,
        "regen_pressure_drop": 1_200_000.0,
        "coating_name": "NONE",
    }

    solved = attach_temperature_dependency_discovery_audit_owner(results)

    assert solved["phase_10d1_temperature_dependency_discovery_audit_owner_complete"] is True
    assert solved["phase_10d1_temperature_dependency_discovery_audit_owner_status"] == (
        "PASS_PHASE_10D1_TEMPERATURE_DEPENDENCY_DISCOVERY_AUDIT_OWNER"
    )
    assert solved["stage_10d_temperature_dependent_solver_audit_started"] is True
    assert solved["phase_10d1_temperature_dependency_discovery_audit_owner_findings"]
    assert "PHASE 10D.1" in solved["phase_10d1_temperature_dependency_discovery_audit_owner_text"]


if __name__ == "__main__":
    test_temperature_dependency_discovery_audit_owner()
    print("PASS_TEMPERATURE_DEPENDENCY_DISCOVERY_AUDIT_OWNER")