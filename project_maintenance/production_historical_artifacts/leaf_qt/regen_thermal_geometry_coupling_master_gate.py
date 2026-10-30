try:
    from regen_thermal_geometry_coupling_validation_owner import (
        validate_coupled_thermal_geometry_system,
        flatten_coupled_thermal_geometry_validation_owner_result,
    )
except Exception:
    from leaf_qt.regen_thermal_geometry_coupling_validation_owner import (
        validate_coupled_thermal_geometry_system,
        flatten_coupled_thermal_geometry_validation_owner_result,
    )


PASS_STATUS = "PASS_REGEN_THERMAL_GEOMETRY_COUPLING_MASTER_GATE"
FAIL_STATUS = "FAIL_REGEN_THERMAL_GEOMETRY_COUPLING_MASTER_GATE"


def _sample_variable_points():
    return [
        {
            "axial_position": 0.0,
            "channel_width": 0.0010,
            "channel_height": 0.0020,
            "rib_width": 0.0005,
        },
        {
            "axial_position": 0.15,
            "channel_width": 0.0009,
            "channel_height": 0.0018,
            "rib_width": 0.00045,
        },
        {
            "axial_position": 0.30,
            "channel_width": 0.0011,
            "channel_height": 0.0022,
            "rib_width": 0.00055,
        },
    ]


def _sample_thermal_points():
    return [
        {
            "axial_position": 0.0,
            "heat_flux": 8.0e6,
            "hot_wall_temperature": 700.0,
            "coolant_temperature": 110.0,
            "pressure_drop": 10000.0,
        },
        {
            "axial_position": 0.15,
            "heat_flux": 18.0e6,
            "hot_wall_temperature": 850.0,
            "coolant_temperature": 160.0,
            "pressure_drop": 30000.0,
        },
        {
            "axial_position": 0.30,
            "heat_flux": 6.0e6,
            "hot_wall_temperature": 650.0,
            "coolant_temperature": 220.0,
            "pressure_drop": 20000.0,
        },
    ]


def run_regen_thermal_geometry_coupling_master_gate():
    errors = []
    warnings = []

    validation_result = validate_coupled_thermal_geometry_system(
        variable_geometry_points=_sample_variable_points(),
        thermal_geometry_points=_sample_thermal_points(),
        sample_positions=[0.0, 0.075, 0.15, 0.225, 0.30],
        max_allowable_wall_temperature=900.0,
        maximum_hot_wall_temperature=900.0,
        maximum_coolant_temperature=500.0,
        maximum_total_pressure_drop=2.0e6,
        maximum_point_pressure_drop=2.0e6,
        minimum_thermal_margin=0.0,
    )

    if not validation_result.get(
        "regen_thermal_geometry_coupling_validation_owner_pass",
        False,
    ):
        errors.append("Thermal-geometry coupling validation owner did not pass.")

    coupling_result = validation_result.get("coupling_result") or {}
    constraint_result = validation_result.get("constraint_result") or {}
    report_result = validation_result.get("report_result") or {}

    if not coupling_result.get("regen_thermal_geometry_coupling_pass", False):
        errors.append("Thermal-geometry coupling profile did not pass.")

    if not constraint_result.get(
        "regen_thermal_geometry_coupling_constraint_owner_pass",
        False,
    ):
        errors.append("Thermal-geometry coupling constraint owner did not pass.")

    if not report_result.get(
        "regen_thermal_geometry_coupling_report_owner_pass",
        False,
    ):
        errors.append("Thermal-geometry coupling report owner did not pass.")

    warnings.extend(validation_result.get("warnings", []))

    gate_pass = len(errors) == 0

    return {
        "regen_thermal_geometry_coupling_master_gate_status": (
            PASS_STATUS if gate_pass else FAIL_STATUS
        ),
        "regen_thermal_geometry_coupling_master_gate_pass": gate_pass,
        "phase_5_thermal_geometry_coupling_architecturally_trusted": gate_pass,
        "phase_5_completion_audit_allowed": gate_pass,
        "future_thermal_geometry_optimisation_allowed_after_completion_audit": gate_pass,
        "validation_result": validation_result,
        "errors": errors,
        "warnings": warnings,
        "master_gate_statement": (
            "REGEN GEOMETRY PHASE 5 ACCEPTED FOR COMPLETION AUDIT"
            if gate_pass
            else "REGEN GEOMETRY PHASE 5 BLOCKED FROM COMPLETION AUDIT"
        ),
    }


def flatten_regen_thermal_geometry_coupling_master_gate_result(
    result,
    prefix="recommended",
):
    flat = {
        f"{prefix}_regen_thermal_geometry_coupling_master_gate_status": result.get(
            "regen_thermal_geometry_coupling_master_gate_status"
        ),
        f"{prefix}_regen_thermal_geometry_coupling_master_gate_pass": (
            1.0
            if result.get("regen_thermal_geometry_coupling_master_gate_pass")
            else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_coupling_phase_5_trusted": (
            1.0
            if result.get("phase_5_thermal_geometry_coupling_architecturally_trusted")
            else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_coupling_completion_audit_allowed": (
            1.0 if result.get("phase_5_completion_audit_allowed") else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_optimisation_allowed_after_completion_audit": (
            1.0
            if result.get("future_thermal_geometry_optimisation_allowed_after_completion_audit")
            else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_coupling_master_gate_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_thermal_geometry_coupling_master_gate_warning_count": float(
            len(result.get("warnings", []))
        ),
        f"{prefix}_regen_thermal_geometry_coupling_master_gate_statement": result.get(
            "master_gate_statement"
        ),
    }

    flat.update(
        flatten_coupled_thermal_geometry_validation_owner_result(
            result.get("validation_result", {}),
            prefix=prefix,
        )
    )

    return flat