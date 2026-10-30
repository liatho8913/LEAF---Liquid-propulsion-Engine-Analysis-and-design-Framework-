try:
    from regen_thermal_geometry_profile import (
        build_thermal_geometry_profile,
        flatten_thermal_geometry_profile_result,
    )
    from regen_thermal_geometry_constraint_owner import (
        validate_thermal_geometry_profile_constraints,
        flatten_thermal_geometry_constraint_owner_result,
    )
    from regen_thermal_geometry_report_owner import (
        generate_thermal_geometry_profile_report,
        flatten_thermal_geometry_report_owner_result,
    )
except Exception:
    from leaf_qt.regen_thermal_geometry_profile import (
        build_thermal_geometry_profile,
        flatten_thermal_geometry_profile_result,
    )
    from leaf_qt.regen_thermal_geometry_constraint_owner import (
        validate_thermal_geometry_profile_constraints,
        flatten_thermal_geometry_constraint_owner_result,
    )
    from leaf_qt.regen_thermal_geometry_report_owner import (
        generate_thermal_geometry_profile_report,
        flatten_thermal_geometry_report_owner_result,
    )


PASS_STATUS = "PASS_REGEN_THERMAL_GEOMETRY_VALIDATION_OWNER"
FAIL_STATUS = "FAIL_REGEN_THERMAL_GEOMETRY_VALIDATION_OWNER"


def validate_thermal_geometry_system(
    profile_points,
    max_allowable_wall_temperature=900.0,
    **limits,
):
    errors = []
    warnings = []

    profile_result = build_thermal_geometry_profile(
        profile_points,
        max_allowable_wall_temperature=max_allowable_wall_temperature,
    )

    if not profile_result.get("regen_thermal_geometry_profile_pass", False):
        errors.append("Thermal geometry profile failed.")

    constraint_result = validate_thermal_geometry_profile_constraints(
        profile_points,
        max_allowable_wall_temperature=max_allowable_wall_temperature,
        **limits,
    )

    if not constraint_result.get("regen_thermal_geometry_constraint_owner_pass", False):
        errors.append("Thermal geometry constraint owner rejected the profile.")

    report_result = generate_thermal_geometry_profile_report(
        profile_points,
        constraint_result=constraint_result,
        max_allowable_wall_temperature=max_allowable_wall_temperature,
    )

    if not report_result.get("regen_thermal_geometry_report_owner_pass", False):
        errors.append("Thermal geometry report owner failed.")

    warnings.extend(constraint_result.get("warnings", []))
    warnings.extend(report_result.get("warnings", []))

    validation_pass = (
        profile_result.get("regen_thermal_geometry_profile_pass", False)
        and constraint_result.get("regen_thermal_geometry_constraint_owner_pass", False)
        and report_result.get("regen_thermal_geometry_report_owner_pass", False)
        and len(errors) == 0
    )

    return {
        "regen_thermal_geometry_validation_owner_status": (
            PASS_STATUS if validation_pass else FAIL_STATUS
        ),
        "regen_thermal_geometry_validation_owner_pass": validation_pass,
        "profile_result": profile_result,
        "constraint_result": constraint_result,
        "report_result": report_result,
        "errors": errors,
        "warnings": warnings,
    }


def flatten_thermal_geometry_validation_owner_result(result, prefix="recommended"):
    flat = {
        f"{prefix}_regen_thermal_geometry_validation_owner_status": result.get(
            "regen_thermal_geometry_validation_owner_status"
        ),
        f"{prefix}_regen_thermal_geometry_validation_owner_pass": (
            1.0 if result.get("regen_thermal_geometry_validation_owner_pass") else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_validation_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_thermal_geometry_validation_warning_count": float(
            len(result.get("warnings", []))
        ),
    }

    flat.update(
        flatten_thermal_geometry_profile_result(
            result.get("profile_result", {}),
            prefix=prefix,
        )
    )

    flat.update(
        flatten_thermal_geometry_constraint_owner_result(
            result.get("constraint_result", {}),
            prefix=prefix,
        )
    )

    flat.update(
        flatten_thermal_geometry_report_owner_result(
            result.get("report_result", {}),
            prefix=prefix,
        )
    )

    return flat


def validate_thermal_geometry_system_to_engine_results(
    profile_points,
    max_allowable_wall_temperature=900.0,
    **limits,
):
    result = validate_thermal_geometry_system(
        profile_points,
        max_allowable_wall_temperature=max_allowable_wall_temperature,
        **limits,
    )
    return flatten_thermal_geometry_validation_owner_result(result)