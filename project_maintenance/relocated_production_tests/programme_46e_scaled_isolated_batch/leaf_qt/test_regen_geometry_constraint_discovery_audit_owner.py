from regen_geometry_constraint_discovery_audit_owner import (
    attach_regen_geometry_constraint_discovery_audit_owner,
)


def test_regen_geometry_constraint_discovery_audit_owner_discovers_available_constraints():
    results = {
        "coolant_channel_count": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.002,
        "rib_width": 0.001,
        "channel_fit_ratio": 0.71,
        "effective_rib_width": 0.000273,
        "inner_wall_thickness": 0.0012,
        "regen_coolant_velocity": 25.0,
        "regen_reynolds_number": 50000,
        "regen_pressure_drop": 1200000,
        "regen_heat_flux": 18000000,
        "hot_gas_side_wall_temperature": 850,
        "coolant_side_wall_temperature": 450,
    }

    solved = attach_regen_geometry_constraint_discovery_audit_owner(results)

    assert solved[
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_complete"
    ] is True

    assert solved[
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_status"
    ] == "PASS_PHASE_11A1_REGEN_GEOMETRY_CONSTRAINT_DISCOVERY_AUDIT_OWNER"

    constraints = solved[
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_constraints"
    ]

    assert isinstance(constraints, list)
    assert len(constraints) > 0

    discovered_count = solved[
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_discovered_count"
    ]

    missing_count = solved[
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_missing_count"
    ]

    assert discovered_count > 0
    assert missing_count >= 0

    discovered_ids = {
        item["constraint_id"]
        for item in constraints
        if item["available"]
    }

    assert "channel_count" in discovered_ids
    assert "channel_width" in discovered_ids
    assert "channel_height" in discovered_ids
    assert "rib_width" in discovered_ids
    assert "channel_fit_ratio" in discovered_ids
    assert "coolant_velocity" in discovered_ids
    assert "pressure_drop" in discovered_ids


def test_regen_geometry_constraint_discovery_audit_owner_handles_empty_results():
    solved = attach_regen_geometry_constraint_discovery_audit_owner({})

    assert solved[
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_complete"
    ] is True

    assert solved[
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_status"
    ] == "PASS_PHASE_11A1_REGEN_GEOMETRY_CONSTRAINT_DISCOVERY_AUDIT_OWNER"

    assert solved[
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_discovered_count"
    ] == 0

    assert solved[
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_missing_count"
    ] > 0


if __name__ == "__main__":
    test_regen_geometry_constraint_discovery_audit_owner_discovers_available_constraints()
    test_regen_geometry_constraint_discovery_audit_owner_handles_empty_results()
    print("PASS_REGEN_GEOMETRY_CONSTRAINT_DISCOVERY_AUDIT_OWNER")