from regen_scalability_profile import attach_regen_scalability_profile
from regen_scalability_constraint_owner import attach_regen_scalability_constraint_owner
from regen_scalability_report_owner import attach_regen_scalability_report_owner
from regen_scalability_failure_owner import attach_regen_scalability_failure_owner


def _base_results():
    return {
        "stage_u_regen_validation_complete": True,
        "full_engine_regen_geometry_status": "PASS_FULL_ENGINE_REGEN_GEOMETRY",
        "regen_validation_master_gate_status": "PASS_REGEN_VALIDATION_MASTER_GATE",
        "regen_completion_audit_status": "PASS_REGEN_COMPLETION_AUDIT",
        "thrust": 845000,
        "chamber_pressure": 9700000,
        "mass_flow_rate": 320,
        "throat_area": 0.09,
        "regen_coolant_velocity": 25,
        "regen_pressure_drop": 1200000,
        "regen_heat_flux": 18000000,
        "hot_gas_side_wall_temperature": 800,
    }


def _run_stage_v_to_failure_owner(results):
    attach_regen_scalability_profile(results)
    attach_regen_scalability_constraint_owner(results)
    attach_regen_scalability_report_owner(results)
    attach_regen_scalability_failure_owner(results)
    return results


def test_scalability_failure_owner_passes_clean_case():
    results = _run_stage_v_to_failure_owner(_base_results())

    assert results["regen_scalability_failure_owner_status"] == (
        "PASS_REGEN_SCALABILITY_FAILURE_OWNER"
    )
    assert results["regen_scalability_failure_owner_trust_level"] == (
        "TRUSTED_SCALABILITY_READY"
    )
    assert results["regen_scalability_failure_owner_can_proceed_to_master_gate"] is True
    assert results["stage_v3_regen_scalability_failure_owner_complete"] is True


def test_scalability_failure_owner_warns_when_constraint_owner_warns():
    results = _base_results()
    results["regen_coolant_velocity"] = 0.5

    _run_stage_v_to_failure_owner(results)

    assert results["regen_scalability_failure_owner_status"] == (
        "WARN_REGEN_SCALABILITY_FAILURE_OWNER_REVIEW_REQUIRED"
    )
    assert results["regen_scalability_failure_owner_trust_level"] == (
        "PARTIAL_SCALABILITY_REVIEW_REQUIRED"
    )
    assert results["regen_scalability_failure_owner_can_proceed_to_master_gate"] is False
    assert results["stage_v3_regen_scalability_failure_owner_complete"] is False


def test_scalability_failure_owner_fails_without_stage_u():
    results = _base_results()
    results["stage_u_regen_validation_complete"] = False

    _run_stage_v_to_failure_owner(results)

    assert results["regen_scalability_failure_owner_status"] == (
        "FAIL_REGEN_SCALABILITY_FAILURE_OWNER"
    )
    assert results["regen_scalability_failure_owner_trust_level"] == (
        "UNTRUSTED_SCALABILITY_BLOCKED"
    )
    assert "SCALABILITY_BLOCKED" in (
        results["regen_scalability_failure_owner_failure_categories"]
    )


def test_scalability_failure_owner_fails_without_report_owner():
    results = _base_results()

    attach_regen_scalability_profile(results)
    attach_regen_scalability_constraint_owner(results)
    attach_regen_scalability_failure_owner(results)

    assert results["regen_scalability_failure_owner_status"] == (
        "WARN_REGEN_SCALABILITY_FAILURE_OWNER_REVIEW_REQUIRED"
    )
    assert "REPORT_OWNER_INCOMPLETE" in (
        results["regen_scalability_failure_owner_failure_categories"]
    )