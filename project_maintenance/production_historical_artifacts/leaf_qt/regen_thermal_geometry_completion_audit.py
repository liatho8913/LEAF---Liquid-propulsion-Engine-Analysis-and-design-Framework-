PASS_STATUS = "PASS_REGEN_THERMAL_GEOMETRY_COMPLETION_AUDIT"
FAIL_STATUS = "FAIL_REGEN_THERMAL_GEOMETRY_COMPLETION_AUDIT"


def run_regen_thermal_geometry_completion_audit():
    errors = []

    try:
        from regen_thermal_geometry_profile import build_thermal_geometry_profile
    except Exception as exc:
        errors.append(f"Missing thermal geometry profile interface: {exc}")
        build_thermal_geometry_profile = None

    try:
        from regen_thermal_geometry_constraint_owner import (
            validate_thermal_geometry_profile_constraints,
        )
    except Exception as exc:
        errors.append(f"Missing thermal geometry constraint owner interface: {exc}")
        validate_thermal_geometry_profile_constraints = None

    try:
        from regen_thermal_geometry_report_owner import (
            generate_thermal_geometry_profile_report,
        )
    except Exception as exc:
        errors.append(f"Missing thermal geometry report owner interface: {exc}")
        generate_thermal_geometry_profile_report = None

    try:
        from regen_thermal_geometry_validation_owner import (
            validate_thermal_geometry_system,
        )
    except Exception as exc:
        errors.append(f"Missing thermal geometry validation owner interface: {exc}")
        validate_thermal_geometry_system = None

    required_interfaces_pass = len(errors) == 0

    thermal_points = [
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

    validation_result = None

    if validate_thermal_geometry_system is not None:
        validation_result = validate_thermal_geometry_system(
            thermal_points,
            max_allowable_wall_temperature=900.0,
            maximum_hot_wall_temperature=900.0,
            maximum_coolant_temperature=500.0,
            maximum_total_pressure_drop=2.0e6,
            minimum_thermal_margin=0.0,
        )

        required_keys = [
            "regen_thermal_geometry_validation_owner_status",
            "regen_thermal_geometry_validation_owner_pass",
            "profile_result",
            "constraint_result",
            "report_result",
        ]

        for key in required_keys:
            if key not in validation_result:
                errors.append(f"Validation result missing required key: {key}")

        if validation_result.get("regen_thermal_geometry_validation_owner_status") not in {
            "PASS_REGEN_THERMAL_GEOMETRY_VALIDATION_OWNER",
            "FAIL_REGEN_THERMAL_GEOMETRY_VALIDATION_OWNER",
        }:
            errors.append("Thermal validation owner returned an invalid status string.")

    audit_pass = len(errors) == 0 and required_interfaces_pass

    return {
        "regen_thermal_geometry_completion_audit_status": (
            PASS_STATUS if audit_pass else FAIL_STATUS
        ),
        "regen_thermal_geometry_completion_audit_pass": audit_pass,
        "required_interfaces_pass": required_interfaces_pass,
        "validation_result_available": validation_result is not None,
        "validation_result": validation_result,
        "errors": errors,
        "completion_statement": (
            "REGEN GEOMETRY PHASE 4 THERMAL PROFILE ARCHITECTURALLY COMPLETE"
            if audit_pass
            else "REGEN GEOMETRY PHASE 4 THERMAL PROFILE NOT COMPLETE"
        ),
    }


def flatten_regen_thermal_geometry_completion_audit_result(
    result,
    prefix="recommended",
):
    return {
        f"{prefix}_regen_thermal_geometry_completion_audit_status": result.get(
            "regen_thermal_geometry_completion_audit_status"
        ),
        f"{prefix}_regen_thermal_geometry_completion_audit_pass": (
            1.0 if result.get("regen_thermal_geometry_completion_audit_pass") else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_completion_required_interfaces_pass": (
            1.0 if result.get("required_interfaces_pass") else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_completion_validation_result_available": (
            1.0 if result.get("validation_result_available") else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_completion_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_thermal_geometry_completion_statement": result.get(
            "completion_statement"
        ),
    }