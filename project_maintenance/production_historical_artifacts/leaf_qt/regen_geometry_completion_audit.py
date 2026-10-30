from leaf_qt.structured_status_access import is_pass
try:
    from leaf_qt.regen_geometry_solver import solve_regen_geometry
except Exception:
    from regen_geometry_solver import solve_regen_geometry


REQUIRED_SOLVER_KEYS = [
    "solver_status",
    "solver_pass",
    "best_candidate",
    "candidate_report",
    "mapped_results",
    "solver_report",
    "regen_geometry_report",
    "regen_geometry_failure",
    "regen_geometry_master_gate",
]


REQUIRED_MAPPED_KEYS = [
    "recommended_regen_geometry_solver_status",
    "recommended_regen_geometry_solver_pass",
    "recommended_geometry_constraint_status",
    "recommended_geometry_constraints_pass",
    "recommended_geometry_iteration_history_status",
    "recommended_regen_geometry_report_status",
    "recommended_regen_geometry_failure_owner_status",
    "recommended_regen_geometry_master_gate_status",
    "recommended_regen_geometry_master_gate_pass",
    "recommended_number_of_coolant_channels",
    "recommended_coolant_channel_width",
    "recommended_coolant_channel_height",
    "recommended_effective_rib_width",
    "recommended_channel_fit_ratio",
    "recommended_channel_geometry_valid",
    "recommended_coolant_hydraulic_diameter",
    "recommended_coolant_velocity",
    "recommended_coolant_reynolds_number",
]


def audit_regen_geometry_completion(solver_result=None):
    failures = []
    warnings = []

    if solver_result is None:
        solver_result = solve_regen_geometry(
            channel_mid_radius=0.012,
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
            nozzle_length=0.15,
            minimum_cooling_coverage=0.25,
        )

    if not isinstance(solver_result, dict):
        return {
            "regen_geometry_completion_audit_status": "FAIL_REGEN_GEOMETRY_COMPLETION_AUDIT",
            "regen_geometry_phase_1_complete": False,
            "regen_geometry_completion_failures": ["SOLVER_RESULT_NOT_DICTIONARY"],
            "regen_geometry_completion_warnings": [],
        }

    for key in REQUIRED_SOLVER_KEYS:
        if key not in solver_result:
            failures.append(f"MISSING_SOLVER_KEY:{key}")

    mapped = solver_result.get("mapped_results", {})
    if not isinstance(mapped, dict) or not mapped:
        failures.append("MISSING_MAPPED_RESULTS")
    else:
        for key in REQUIRED_MAPPED_KEYS:
            if key not in mapped:
                failures.append(f"MISSING_MAPPED_KEY:{key}")

    if solver_result.get("solver_status") != "PASS_REGEN_GEOMETRY_SOLVER":
        failures.append("SOLVER_NOT_PASS")

    master_gate = solver_result.get("regen_geometry_master_gate", {})
    if master_gate.get("regen_geometry_master_gate_status") != "PASS_REGEN_GEOMETRY_MASTER_GATE":
        failures.append("MASTER_GATE_NOT_PASS")

    report = solver_result.get("regen_geometry_report", {})
    if report.get("regen_geometry_report_status") != "PASS_REGEN_GEOMETRY_REPORT_OWNER":
        failures.append("REPORT_OWNER_NOT_PASS")

    failure_owner = solver_result.get("regen_geometry_failure", {})
    if failure_owner.get("regen_geometry_failure_owner_status") != "PASS_REGEN_GEOMETRY_FAILURE_OWNER":
        failures.append("FAILURE_OWNER_NOT_PASS")

    candidate_report = solver_result.get("candidate_report", {})
    history = candidate_report.get("iteration_history", {})
    if not is_pass(history.get("iteration_history_status")):
        failures.append("ITERATION_HISTORY_NOT_PASS")

    if solver_result.get("best_candidate") is None:
        failures.append("NO_SELECTED_CANDIDATE")

    if mapped.get("recommended_geometry_constraints_pass") != 1.0:
        failures.append("CONSTRAINT_OWNER_NOT_PASS")

    if mapped.get("recommended_channel_geometry_valid") != 1.0:
        failures.append("CHANNEL_GEOMETRY_VALID_NOT_TRUE")

    report_text = mapped.get("recommended_regen_geometry_report_text", "")
    if isinstance(report_text, str) and len(report_text) > 250:
        warnings.append(
            "REPORT_TEXT_PRESENT_IN_MAPPED_RESULTS_FOR_UI_EXPOSURE_ONLY"
        )

    passed = len(failures) == 0

    return {
        "regen_geometry_completion_audit_status": (
            "PASS_REGEN_GEOMETRY_COMPLETION_AUDIT"
            if passed
            else "FAIL_REGEN_GEOMETRY_COMPLETION_AUDIT"
        ),
        "regen_geometry_phase_1_complete": passed,
        "regen_geometry_completion_failures": failures,
        "regen_geometry_completion_warnings": warnings,
    }


def flatten_regen_geometry_completion_audit(result, prefix="recommended"):
    failures = result.get("regen_geometry_completion_failures", [])
    warnings = result.get("regen_geometry_completion_warnings", [])

    return {
        f"{prefix}_regen_geometry_completion_audit_status": result.get(
            "regen_geometry_completion_audit_status",
            "FAIL_REGEN_GEOMETRY_COMPLETION_AUDIT",
        ),
        f"{prefix}_regen_geometry_phase_1_complete": 1.0
        if result.get("regen_geometry_phase_1_complete")
        else 0.0,
        f"{prefix}_regen_geometry_completion_failure_count": float(len(failures)),
        f"{prefix}_regen_geometry_completion_warning_count": float(len(warnings)),
        f"{prefix}_regen_geometry_completion_failures": "; ".join(failures),
        f"{prefix}_regen_geometry_completion_warnings": "; ".join(warnings),
    }