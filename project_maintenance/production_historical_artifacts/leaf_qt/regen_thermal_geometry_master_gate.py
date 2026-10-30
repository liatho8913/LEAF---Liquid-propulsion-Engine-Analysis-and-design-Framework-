try:
    from project_maintenance.production_historical_artifacts.leaf_qt.regen_thermal_geometry_completion_audit import (
        run_regen_thermal_geometry_completion_audit,
        flatten_regen_thermal_geometry_completion_audit_result,
    )
except Exception:
    from project_maintenance.production_historical_artifacts.leaf_qt.regen_thermal_geometry_completion_audit import (
        run_regen_thermal_geometry_completion_audit,
        flatten_regen_thermal_geometry_completion_audit_result,
    )


PASS_STATUS = "PASS_REGEN_THERMAL_GEOMETRY_MASTER_GATE"
FAIL_STATUS = "FAIL_REGEN_THERMAL_GEOMETRY_MASTER_GATE"


def run_regen_thermal_geometry_master_gate():
    errors = []
    warnings = []

    completion_result = run_regen_thermal_geometry_completion_audit()

    if not completion_result.get("regen_thermal_geometry_completion_audit_pass", False):
        errors.append("Thermal geometry completion audit did not pass.")

    validation_result = completion_result.get("validation_result") or {}

    if not validation_result.get("regen_thermal_geometry_validation_owner_pass", False):
        errors.append("Thermal geometry validation owner did not pass.")

    profile_result = validation_result.get("profile_result") or {}
    constraint_result = validation_result.get("constraint_result") or {}
    report_result = validation_result.get("report_result") or {}

    if not profile_result.get("regen_thermal_geometry_profile_pass", False):
        errors.append("Thermal geometry profile owner did not pass.")

    if not constraint_result.get("regen_thermal_geometry_constraint_owner_pass", False):
        errors.append("Thermal geometry constraint owner did not pass.")

    if not report_result.get("regen_thermal_geometry_report_owner_pass", False):
        errors.append("Thermal geometry report owner did not pass.")

    warnings.extend(validation_result.get("warnings", []))
    warnings.extend(completion_result.get("errors", []))

    gate_pass = len(errors) == 0

    return {
        "regen_thermal_geometry_master_gate_status": (
            PASS_STATUS if gate_pass else FAIL_STATUS
        ),
        "regen_thermal_geometry_master_gate_pass": gate_pass,
        "phase_4_thermal_geometry_architecturally_complete": gate_pass,
        "phase_5_thermal_geometry_coupling_allowed": gate_pass,
        "viewer_integration_allowed_after_phase_5_foundation": gate_pass,
        "completion_result": completion_result,
        "errors": errors,
        "warnings": warnings,
        "master_gate_statement": (
            "REGEN GEOMETRY PHASE 4 ACCEPTED FOR FUTURE THERMAL-GEOMETRY COUPLING"
            if gate_pass
            else "REGEN GEOMETRY PHASE 4 BLOCKED FROM FUTURE THERMAL-GEOMETRY COUPLING"
        ),
    }


def flatten_regen_thermal_geometry_master_gate_result(
    result,
    prefix="recommended",
):
    flat = {
        f"{prefix}_regen_thermal_geometry_master_gate_status": result.get(
            "regen_thermal_geometry_master_gate_status"
        ),
        f"{prefix}_regen_thermal_geometry_master_gate_pass": (
            1.0 if result.get("regen_thermal_geometry_master_gate_pass") else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_phase_4_architecturally_complete": (
            1.0
            if result.get("phase_4_thermal_geometry_architecturally_complete")
            else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_phase_5_coupling_allowed": (
            1.0 if result.get("phase_5_thermal_geometry_coupling_allowed") else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_viewer_integration_allowed_after_phase_5_foundation": (
            1.0
            if result.get("viewer_integration_allowed_after_phase_5_foundation")
            else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_master_gate_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_thermal_geometry_master_gate_warning_count": float(
            len(result.get("warnings", []))
        ),
        f"{prefix}_regen_thermal_geometry_master_gate_statement": result.get(
            "master_gate_statement"
        ),
    }

    flat.update(
        flatten_regen_thermal_geometry_completion_audit_result(
            result.get("completion_result", {}),
            prefix=prefix,
        )
    )

    return flat