try:
    from regen_axial_geometry_solver import (
        solve_regen_axial_geometry,
        flatten_regen_axial_geometry_result,
    )
    from regen_axial_geometry_constraint_owner import (
        validate_regen_axial_geometry_constraints,
        flatten_regen_axial_constraint_owner_result,
    )
    from regen_axial_geometry_report_owner import (
        generate_regen_axial_geometry_report,
        flatten_regen_axial_report_owner_result,
    )
except Exception:
    from leaf_qt.regen_axial_geometry_solver import (
        solve_regen_axial_geometry,
        flatten_regen_axial_geometry_result,
    )
    from leaf_qt.regen_axial_geometry_constraint_owner import (
        validate_regen_axial_geometry_constraints,
        flatten_regen_axial_constraint_owner_result,
    )
    from leaf_qt.regen_axial_geometry_report_owner import (
        generate_regen_axial_geometry_report,
        flatten_regen_axial_report_owner_result,
    )


PASS_STATUS = "PASS_REGEN_AXIAL_GEOMETRY_VALIDATION_OWNER"
FAIL_STATUS = "FAIL_REGEN_AXIAL_GEOMETRY_VALIDATION_OWNER"


def validate_regen_axial_geometry_system(station_specs=None, **defaults):
    errors = []
    warnings = []

    axial_solver_result = solve_regen_axial_geometry(
        station_specs=station_specs,
        **defaults,
    )

    if not axial_solver_result.get("axial_geometry_solver_pass", False):
        errors.append("Axial geometry solver did not produce a fully passing station set.")

    axial_constraint_result = validate_regen_axial_geometry_constraints(
        axial_solver_result
    )

    if not axial_constraint_result.get("regen_axial_constraint_owner_pass", False):
        errors.append("Axial constraint owner rejected the station geometry.")

    axial_report_result = generate_regen_axial_geometry_report(
        axial_geometry_result=axial_solver_result,
        axial_constraint_result=axial_constraint_result,
    )

    if not axial_report_result.get("regen_axial_report_owner_pass", False):
        errors.append("Axial report owner failed to generate a valid report.")

    warnings.extend(axial_constraint_result.get("warnings", []))
    warnings.extend(axial_report_result.get("warnings", []))

    validation_pass = (
        axial_solver_result.get("axial_geometry_solver_pass", False)
        and axial_constraint_result.get("regen_axial_constraint_owner_pass", False)
        and axial_report_result.get("regen_axial_report_owner_pass", False)
        and len(errors) == 0
    )

    return {
        "regen_axial_validation_owner_status": (
            PASS_STATUS if validation_pass else FAIL_STATUS
        ),
        "regen_axial_validation_owner_pass": validation_pass,
        "axial_solver_result": axial_solver_result,
        "axial_constraint_result": axial_constraint_result,
        "axial_report_result": axial_report_result,
        "errors": errors,
        "warnings": warnings,
    }


def flatten_regen_axial_validation_owner_result(result, prefix="recommended"):
    flat = {
        f"{prefix}_regen_axial_validation_owner_status": result.get(
            "regen_axial_validation_owner_status"
        ),
        f"{prefix}_regen_axial_validation_owner_pass": (
            1.0 if result.get("regen_axial_validation_owner_pass") else 0.0
        ),
        f"{prefix}_regen_axial_validation_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_axial_validation_warning_count": float(
            len(result.get("warnings", []))
        ),
    }

    flat.update(
        flatten_regen_axial_geometry_result(
            result.get("axial_solver_result", {}),
            prefix=prefix,
        )
    )

    flat.update(
        flatten_regen_axial_constraint_owner_result(
            result.get("axial_constraint_result", {}),
            prefix=prefix,
        )
    )

    flat.update(
        flatten_regen_axial_report_owner_result(
            result.get("axial_report_result", {}),
            prefix=prefix,
        )
    )

    return flat


def validate_regen_axial_geometry_system_to_engine_results(
    station_specs=None,
    **defaults,
):
    result = validate_regen_axial_geometry_system(
        station_specs=station_specs,
        **defaults,
    )
    return flatten_regen_axial_validation_owner_result(result)