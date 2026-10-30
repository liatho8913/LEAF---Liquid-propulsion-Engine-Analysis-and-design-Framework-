PASS_STATUS = "PASS_REGEN_VARIABLE_GEOMETRY_COMPLETION_AUDIT"
FAIL_STATUS = "FAIL_REGEN_VARIABLE_GEOMETRY_COMPLETION_AUDIT"


def run_regen_variable_geometry_completion_audit():
    errors = []

    try:
        from regen_variable_geometry_profile import build_variable_geometry_profile
    except Exception as exc:
        errors.append(f"Missing variable geometry profile interface: {exc}")
        build_variable_geometry_profile = None

    try:
        from regen_variable_geometry_constraint_owner import (
            validate_variable_geometry_profile_constraints,
        )
    except Exception as exc:
        errors.append(f"Missing variable geometry constraint owner interface: {exc}")
        validate_variable_geometry_profile_constraints = None

    try:
        from regen_variable_geometry_report_owner import (
            generate_variable_geometry_profile_report,
        )
    except Exception as exc:
        errors.append(f"Missing variable geometry report owner interface: {exc}")
        generate_variable_geometry_profile_report = None

    try:
        from regen_variable_geometry_validation_owner import (
            validate_variable_geometry_system,
        )
    except Exception as exc:
        errors.append(f"Missing variable geometry validation owner interface: {exc}")
        validate_variable_geometry_system = None

    required_interfaces_pass = len(errors) == 0

    profile_points = [
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

    validation_result = None

    if validate_variable_geometry_system is not None:
        validation_result = validate_variable_geometry_system(profile_points)

        required_keys = [
            "regen_variable_geometry_validation_owner_status",
            "regen_variable_geometry_validation_owner_pass",
            "profile_result",
            "constraint_result",
            "report_result",
        ]

        for key in required_keys:
            if key not in validation_result:
                errors.append(f"Validation result missing required key: {key}")

        if validation_result.get("regen_variable_geometry_validation_owner_status") not in {
            "PASS_REGEN_VARIABLE_GEOMETRY_VALIDATION_OWNER",
            "FAIL_REGEN_VARIABLE_GEOMETRY_VALIDATION_OWNER",
        }:
            errors.append("Validation owner returned an invalid status string.")

    audit_pass = len(errors) == 0 and required_interfaces_pass

    return {
        "regen_variable_geometry_completion_audit_status": (
            PASS_STATUS if audit_pass else FAIL_STATUS
        ),
        "regen_variable_geometry_completion_audit_pass": audit_pass,
        "required_interfaces_pass": required_interfaces_pass,
        "validation_result_available": validation_result is not None,
        "validation_result": validation_result,
        "errors": errors,
        "completion_statement": (
            "REGEN GEOMETRY PHASE 3 VARIABLE GEOMETRY ARCHITECTURALLY COMPLETE"
            if audit_pass
            else "REGEN GEOMETRY PHASE 3 VARIABLE GEOMETRY NOT COMPLETE"
        ),
    }


def flatten_regen_variable_geometry_completion_audit_result(
    result,
    prefix="recommended",
):
    return {
        f"{prefix}_regen_variable_geometry_completion_audit_status": result.get(
            "regen_variable_geometry_completion_audit_status"
        ),
        f"{prefix}_regen_variable_geometry_completion_audit_pass": (
            1.0 if result.get("regen_variable_geometry_completion_audit_pass") else 0.0
        ),
        f"{prefix}_regen_variable_geometry_completion_required_interfaces_pass": (
            1.0 if result.get("required_interfaces_pass") else 0.0
        ),
        f"{prefix}_regen_variable_geometry_completion_validation_result_available": (
            1.0 if result.get("validation_result_available") else 0.0
        ),
        f"{prefix}_regen_variable_geometry_completion_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_variable_geometry_completion_statement": result.get(
            "completion_statement"
        ),
    }