from regen_scalability_profile import attach_regen_scalability_profile
from regen_scalability_constraint_owner import attach_regen_scalability_constraint_owner
from regen_scalability_report_owner import attach_regen_scalability_report_owner
from regen_scalability_failure_owner import attach_regen_scalability_failure_owner
from regen_scalability_master_gate import attach_regen_scalability_master_gate
from regen_scalability_completion_audit import attach_regen_scalability_completion_audit


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


def _run_stage_v(results):
    attach_regen_scalability_profile(results)
    attach_regen_scalability_constraint_owner(results)
    attach_regen_scalability_report_owner(results)
    attach_regen_scalability_failure_owner(results)
    attach_regen_scalability_master_gate(results)
    attach_regen_scalability_completion_audit(results)
    return results


def test_scalability_master_gate_and_completion_audit_pass_clean_case():
    results = _run_stage_v(_base_results())

    assert results["regen_scalability_master_gate_status"] == (
        "PASS_REGEN_SCALABILITY_MASTER_GATE"
    )
    assert results["stage_v4_regen_scalability_master_gate_complete"] is True

    assert results["regen_scalability_completion_audit_status"] == (
        "PASS_REGEN_SCALABILITY_COMPLETION_AUDIT"
    )
    assert results["stage_v5_regen_scalability_completion_audit_complete"] is True
    assert results["stage_v_regen_scalability_complete"] is True


def test_scalability_master_gate_blocks_low_coolant_velocity_case():
    results = _base_results()
    results["regen_coolant_velocity"] = 0.5

    _run_stage_v(results)

    assert results["regen_scalability_master_gate_status"] == (
        "FAIL_REGEN_SCALABILITY_MASTER_GATE"
    )
    assert results["stage_v4_regen_scalability_master_gate_complete"] is False

    assert results["regen_scalability_completion_audit_status"] == (
        "FAIL_REGEN_SCALABILITY_COMPLETION_AUDIT"
    )
    assert results["stage_v_regen_scalability_complete"] is False


def test_scalability_completion_audit_fails_without_master_gate():
    results = _base_results()

    attach_regen_scalability_profile(results)
    attach_regen_scalability_constraint_owner(results)
    attach_regen_scalability_report_owner(results)
    attach_regen_scalability_failure_owner(results)
    attach_regen_scalability_completion_audit(results)

    assert results["regen_scalability_completion_audit_status"] == (
        "FAIL_REGEN_SCALABILITY_COMPLETION_AUDIT"
    )
    assert results["stage_v_regen_scalability_complete"] is False