from regen_candidate_generator import attach_regen_candidate_generator


def test_regen_candidate_generator_creates_candidates():
    results = {
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0010,
        "channel_mid_radius": 0.02258,
        "coolant_density": 810.0,
        "coolant_dynamic_viscosity": 0.0012,
        "coolant_mass_flow_rate": 0.4,
        "regen_target_reynolds_number": 10000.0,
        "regen_derived_maximum_coolant_velocity": 40.0,
    }

    updated = attach_regen_candidate_generator(results)

    assert updated["phase_11b_1a_regen_candidate_generator_complete"] is True
    assert updated["regen_candidate_generator_candidate_count"] > 0
    assert updated["regen_candidate_generator_status"] == (
        "PASS_CANDIDATES_GENERATED_REQUIRES_VALIDATION"
    )

    first = updated["regen_candidate_generator_candidates"][0]

    assert first["candidate_status"] == "GENERATED_REQUIRES_VALIDATION"
    assert first["validation_status"] == "NOT_VALIDATED"
    assert "inputs" in first
    assert "changes" in first
    assert "preview_metrics" in first


def test_regen_candidate_generator_blocks_incomplete_geometry():
    results = {
        "number_of_coolant_channels": 80,
        "coolant_channel_width": None,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0010,
    }

    updated = attach_regen_candidate_generator(results)

    assert updated["regen_candidate_generator_candidate_count"] == 0
    assert updated["regen_candidate_generator_status"] == "BLOCKED_REGEN_CANDIDATE_GENERATOR"