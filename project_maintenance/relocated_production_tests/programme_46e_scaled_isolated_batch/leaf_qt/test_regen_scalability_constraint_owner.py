from regen_scalability_constraint_owner import evaluate_regen_scalability_constraints
from regen_scalability_framework import audit_regen_scalability


def _base_results():
    return {
        "stage_u_regen_validation_complete": True,
        "stage_v0_regen_scalability_profile_complete": True,
        "regen_scalability_profile_scale_class": "LARGE_ENGINE",
        "full_engine_regen_geometry_status": "PASS_FULL_ENGINE_REGEN_GEOMETRY",
        "regen_validation_master_gate_status": "PASS_REGEN_VALIDATION_MASTER_GATE",
        "regen_completion_audit_status": "PASS_REGEN_COMPLETION_AUDIT",
        "chamber_pressure": 9700000,
        "mass_flow_rate": 320,
        "throat_area": 0.09,
        "regen_coolant_velocity": 25,
        "regen_pressure_drop": 1200000,
        "regen_heat_flux": 18000000,
        "hot_gas_side_wall_temperature": 800,
    }


def test_scalability_constraint_owner_passes_clean_case():
    audit = evaluate_regen_scalability_constraints(_base_results())

    assert audit["regen_scalability_constraint_owner_status"] == (
        "PASS_REGEN_SCALABILITY_CONSTRAINT_OWNER"
    )
    assert audit["stage_v1_regen_scalability_constraint_owner_complete"] is True
    assert audit["stage_v1_regen_scalability_framework_complete"] is True


def test_scalability_constraint_owner_blocks_without_stage_u():
    results = _base_results()
    results["stage_u_regen_validation_complete"] = False

    audit = evaluate_regen_scalability_constraints(results)

    assert audit["regen_scalability_constraint_owner_status"] == (
        "FAIL_REGEN_SCALABILITY_CONSTRAINT_OWNER"
    )
    assert audit["stage_v1_regen_scalability_constraint_owner_complete"] is False


def test_scalability_constraint_owner_warns_for_low_coolant_velocity():
    results = _base_results()
    results["regen_coolant_velocity"] = 0.5

    audit = evaluate_regen_scalability_constraints(results)

    assert audit["regen_scalability_constraint_owner_status"] == (
        "WARN_REGEN_SCALABILITY_CONSTRAINT_OWNER_REVIEW_REQUIRED"
    )
    assert audit["stage_v1_regen_scalability_constraint_owner_complete"] is False


def test_framework_delegates_to_constraint_owner():
    audit = audit_regen_scalability(_base_results())

    assert audit["regen_scalability_framework_status"] == (
        "PASS_REGEN_SCALABILITY_CONSTRAINT_OWNER"
    )
    assert audit["regen_scalability_constraint_owner_status"] == (
        "PASS_REGEN_SCALABILITY_CONSTRAINT_OWNER"
    )