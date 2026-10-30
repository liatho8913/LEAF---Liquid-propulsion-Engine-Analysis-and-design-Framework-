from regen_candidate_generator import attach_regen_candidate_generator
from regen_candidate_validator import attach_regen_candidate_validator


def test_regen_candidate_validator_runs_after_generator():
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
        "regen_derived_minimum_coolant_velocity": 0.1,
        "regen_derived_maximum_coolant_velocity": 80.0,
        "minimum_hot_gas_wall_thickness": 0.00075,
        "maximum_hot_gas_wall_thickness": 0.006,
        "material_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_validation_mode": "SOURCED_VALIDATION_MODE",
    }

    results = attach_regen_candidate_generator(results)
    results = attach_regen_candidate_validator(results)

    assert results["phase_11b_1b_regen_candidate_validator_complete"] is True
    assert results["regen_candidate_validator_complete"] is True
    assert results["regen_candidate_validator_pass_count"] >= 0
    assert results["regen_candidate_validator_fail_count"] >= 0

    total = (
        results["regen_candidate_validator_pass_count"]
        + results["regen_candidate_validator_fail_count"]
    )

    assert total == results["regen_candidate_generator_candidate_count"]


def test_regen_candidate_validator_blocks_placeholder_sources():
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
        "regen_derived_minimum_coolant_velocity": 0.1,
        "regen_derived_maximum_coolant_velocity": 80.0,
        "minimum_hot_gas_wall_thickness": 0.00075,
        "maximum_hot_gas_wall_thickness": 0.006,
        "material_validation_mode": "PLACEHOLDER_MODE",
        "coating_validation_mode": "SOURCED_VALIDATION_MODE",
    }

    results = attach_regen_candidate_generator(results)
    results = attach_regen_candidate_validator(results)

    assert results["regen_candidate_validator_complete"] is True
    assert results["regen_candidate_validator_pass_count"] == 0
    assert results["regen_candidate_validator_fail_count"] == (
        results["regen_candidate_generator_candidate_count"]
    )