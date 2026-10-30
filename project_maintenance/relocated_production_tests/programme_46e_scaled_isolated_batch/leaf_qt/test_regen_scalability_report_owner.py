from regen_scalability_profile import attach_regen_scalability_profile
from regen_scalability_constraint_owner import attach_regen_scalability_constraint_owner
from regen_scalability_report_owner import attach_regen_scalability_report_owner


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


def test_scalability_report_owner_passes_after_profile_and_constraint_owner():
    results = _base_results()

    attach_regen_scalability_profile(results)
    attach_regen_scalability_constraint_owner(results)
    attach_regen_scalability_report_owner(results)

    assert results["regen_scalability_report_owner_status"] == (
        "PASS_REGEN_SCALABILITY_REPORT_OWNER"
    )
    assert results["stage_v2_regen_scalability_report_owner_complete"] is True
    assert results["stage_v2_regen_scalability_report_ownership_complete"] is True
    assert "LEAF STAGE V.2 REGEN SCALABILITY REPORT OWNER" in (
        results["regen_scalability_report_owner_text"]
    )


def test_scalability_report_owner_fails_without_constraint_owner():
    results = _base_results()

    attach_regen_scalability_profile(results)
    attach_regen_scalability_report_owner(results)

    assert results["regen_scalability_report_owner_status"] == (
        "FAIL_REGEN_SCALABILITY_REPORT_OWNER"
    )
    assert results["stage_v2_regen_scalability_report_owner_complete"] is False


def test_scalability_report_owner_reports_warning_reasons():
    results = _base_results()
    results["regen_coolant_velocity"] = 0.5

    attach_regen_scalability_profile(results)
    attach_regen_scalability_constraint_owner(results)
    attach_regen_scalability_report_owner(results)

    assert results["regen_scalability_report_owner_status"] == (
        "PASS_REGEN_SCALABILITY_REPORT_OWNER"
    )
    assert "Coolant velocity" in results["regen_scalability_report_owner_text"]
    assert "Review or resolve scalability warnings" in (
        results["regen_scalability_report_owner_text"]
    )