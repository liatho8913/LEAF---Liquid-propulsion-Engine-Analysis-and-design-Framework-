PASS_STATUS = "PASS_REGEN_AXIAL_GEOMETRY_COMPLETION_AUDIT"
FAIL_STATUS = "FAIL_REGEN_AXIAL_GEOMETRY_COMPLETION_AUDIT"


def run_regen_axial_geometry_completion_audit():
    errors = []

    try:
        from regen_axial_geometry_solver import solve_regen_axial_geometry
    except Exception as exc:
        errors.append(f"Missing axial solver interface: {exc}")
        solve_regen_axial_geometry = None

    try:
        from regen_axial_geometry_constraint_owner import validate_regen_axial_geometry_constraints
    except Exception as exc:
        errors.append(f"Missing axial constraint owner interface: {exc}")
        validate_regen_axial_geometry_constraints = None

    try:
        from regen_axial_geometry_report_owner import generate_regen_axial_geometry_report
    except Exception as exc:
        errors.append(f"Missing axial report owner interface: {exc}")
        generate_regen_axial_geometry_report = None

    try:
        from regen_axial_geometry_validation_owner import validate_regen_axial_geometry_system
    except Exception as exc:
        errors.append(f"Missing axial validation owner interface: {exc}")
        validate_regen_axial_geometry_system = None

    required_interfaces_pass = len(errors) == 0

    validation_result = None

    if validate_regen_axial_geometry_system is not None:
        validation_result = validate_regen_axial_geometry_system(
            chamber_radius=0.03,
            throat_radius=0.01,
            exit_radius=0.04,
            engine_length=0.30,
            coolant_mass_flow_rate=0.25,
            coolant_density=420.0,
            coolant_dynamic_viscosity=0.00018,
            target_reynolds_number=10000.0,
            minimum_rib_width=0.0005,
            minimum_channel_width=0.0005,
            maximum_channel_height=0.003,
            channel_aspect_ratio=3.0,
            minimum_channel_count=8,
            maximum_channel_count=220,
            maximum_coolant_velocity=80.0,
            minimum_hydraulic_diameter=0.00035,
            pressure_drop_limit=2.0e6,
            axial_segment_length=0.05,
            minimum_cooling_coverage=0.25,
        )

        required_keys = [
            "regen_axial_validation_owner_status",
            "regen_axial_validation_owner_pass",
            "axial_solver_result",
            "axial_constraint_result",
            "axial_report_result",
        ]

        for key in required_keys:
            if key not in validation_result:
                errors.append(f"Validation result missing required key: {key}")

        if validation_result.get("regen_axial_validation_owner_status") not in {
            "PASS_REGEN_AXIAL_GEOMETRY_VALIDATION_OWNER",
            "FAIL_REGEN_AXIAL_GEOMETRY_VALIDATION_OWNER",
        }:
            errors.append("Validation owner returned an invalid status string.")

    audit_pass = len(errors) == 0 and required_interfaces_pass

    return {
        "regen_axial_completion_audit_status": PASS_STATUS if audit_pass else FAIL_STATUS,
        "regen_axial_completion_audit_pass": audit_pass,
        "required_interfaces_pass": required_interfaces_pass,
        "validation_result_available": validation_result is not None,
        "validation_result": validation_result,
        "errors": errors,
        "completion_statement": (
            "REGEN GEOMETRY PHASE 2 ARCHITECTURALLY COMPLETE"
            if audit_pass
            else "REGEN GEOMETRY PHASE 2 NOT COMPLETE"
        ),
    }


def flatten_regen_axial_completion_audit_result(result, prefix="recommended"):
    return {
        f"{prefix}_regen_axial_completion_audit_status": result.get(
            "regen_axial_completion_audit_status"
        ),
        f"{prefix}_regen_axial_completion_audit_pass": (
            1.0 if result.get("regen_axial_completion_audit_pass") else 0.0
        ),
        f"{prefix}_regen_axial_completion_required_interfaces_pass": (
            1.0 if result.get("required_interfaces_pass") else 0.0
        ),
        f"{prefix}_regen_axial_completion_validation_result_available": (
            1.0 if result.get("validation_result_available") else 0.0
        ),
        f"{prefix}_regen_axial_completion_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_axial_completion_statement": result.get(
            "completion_statement"
        ),
    }