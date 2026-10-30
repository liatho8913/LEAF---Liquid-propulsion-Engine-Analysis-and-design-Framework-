from __future__ import annotations

from project_maintenance.engine_solver_status_adapter import attach_engine_solver_status_adapter


VALID_SOLVER_OUTPUT = {
    "thrust": 3332.0,
    "specific_impulse": 320.0,
    "vacuum_specific_impulse": 330.0,
    "sea_level_specific_impulse": 285.0,
    "chamber_pressure": 6.895e6,
    "chamber_temperature": 3500.0,
    "mass_flow_rate": 1.15,
    "throat_area": 3.01e-4,
    "exit_area": 0.002745,
    "characteristic_velocity": 1580.0,
    "hot_gas_wall_thickness": 0.001104,
    "coolant_channel_width": 0.0015,
    "coolant_channel_height": 0.002,
    "rib_width": 0.001,
    "material_temperature_margin": 200.0,
    "regen_axial_worst_material_margin": 200.0,
    "regen_geometry_status": "PASS",
    "regen_thermal_status": "PASS",
    "regen_coolant_status": "PASS",
    "regen_material_status": "PASS",
    "regen_overall_status": "PASS",
}


def test_phase_16t3k9_valid_solver_output_passes_status_adapter() -> None:
    data = dict(VALID_SOLVER_OUTPUT)
    returned = attach_engine_solver_status_adapter(data)

    assert returned is data
    assert data["engine_solver_status_adapter_status"] == "PASS_ENGINE_SOLVER_STATUS_ADAPTER"
    assert data["engine_solver_global_status"] == "PASS"
    assert data["phase_16t3k9_status_adapter_complete"] is True


def test_phase_16t3k9_adds_structured_findings_and_report() -> None:
    data = dict(VALID_SOLVER_OUTPUT)
    attach_engine_solver_status_adapter(data)

    assert data["engine_solver_structured_findings"]
    assert data["engine_solver_global_status_payload"]["passed"] is True
    assert "ENGINE SOLVER STATUS ADAPTER" in data["engine_solver_status_adapter_report"]


def test_phase_16t3k9_regen_warning_blocks_production_signoff() -> None:
    data = dict(VALID_SOLVER_OUTPUT)
    data["regen_coolant_status"] = "WARN"
    data["regen_overall_status"] = "WARN"

    attach_engine_solver_status_adapter(data)

    assert data["engine_solver_status_adapter_status"] == "WARN_ENGINE_SOLVER_STATUS_ADAPTER_REVIEW_REQUIRED"
    assert data["engine_solver_global_status"] == "BLOCKED"


def test_phase_16t3k9_regen_failure_fails_global_status() -> None:
    data = dict(VALID_SOLVER_OUTPUT)
    data["regen_geometry_status"] = "FAIL"
    data["regen_overall_status"] = "FAIL"

    attach_engine_solver_status_adapter(data)

    assert data["engine_solver_status_adapter_status"] == "FAIL_ENGINE_SOLVER_STATUS_ADAPTER"
    assert data["engine_solver_global_status"] == "FAIL"


def test_phase_16t3k9_negative_thrust_fails_physics() -> None:
    data = dict(VALID_SOLVER_OUTPUT)
    data["thrust"] = -1.0

    attach_engine_solver_status_adapter(data)

    assert data["engine_solver_status_adapter_status"] == "FAIL_ENGINE_SOLVER_STATUS_ADAPTER"
    assert data["engine_solver_global_status"] == "FAIL"


def test_phase_16t3k9_negative_wall_thickness_fails_physics() -> None:
    data = dict(VALID_SOLVER_OUTPUT)
    data["hot_gas_wall_thickness"] = -0.001

    attach_engine_solver_status_adapter(data)

    assert data["engine_solver_status_adapter_status"] == "FAIL_ENGINE_SOLVER_STATUS_ADAPTER"
    assert data["engine_solver_global_status"] == "FAIL"


def test_phase_16t3k9_high_thermo_error_blocks_review() -> None:
    data = dict(VALID_SOLVER_OUTPUT)
    data["thermo_r_error_percent"] = 8.0

    attach_engine_solver_status_adapter(data)

    assert data["engine_solver_status_adapter_status"] == "WARN_ENGINE_SOLVER_STATUS_ADAPTER_REVIEW_REQUIRED"
    assert data["engine_solver_global_status"] == "BLOCKED"


def test_phase_16t3k9_non_dict_is_preserved() -> None:
    assert attach_engine_solver_status_adapter(None) is None
