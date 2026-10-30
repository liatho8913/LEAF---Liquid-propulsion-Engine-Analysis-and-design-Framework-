def _as_number(value, default=None):
    try:
        if value in (None, "", "N/A", "None"):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _truthy_pass(value):
    return value in (True, 1, "1", "PASS", "pass", "Pass", "TRUE", "true")


def _status_text(value):
    if value is None:
        return "UNKNOWN"
    return str(value)


def build_regen_optimisation_proof(results):
    results = results if isinstance(results, dict) else {}

    lines = []
    proof_status = "UNKNOWN"
    failure_type = "UNKNOWN"
    next_step = "Run a calculation with regen validation enabled."

    lines.append("LEAF REGEN OPTIMISATION PROOF")
    lines.append("============================")
    lines.append("")

    lines.append("Purpose:")
    lines.append("- Prove what LEAF tried before accepting or rejecting the regen design.")
    lines.append("- Prevent silent pass/fail decisions.")
    lines.append("- Separate physical design failure from missing architecture or missing data.")
    lines.append("")

    # ---------------------------------------------------------
    # What was tried
    # ---------------------------------------------------------

    lines.append("What was tried:")
    lines.append("- Manual regen geometry.")
    lines.append("- Recommended regen geometry.")
    lines.append("- Full-engine axial regen validation.")
    lines.append("- Best full-engine regen candidate selection.")
    lines.append("")

    # ---------------------------------------------------------
    # Key evidence
    # ---------------------------------------------------------

    manual_valid = results.get("channel_geometry_valid")
    recommended_status = results.get("recommended_geometry_status")
    full_status = results.get("full_engine_regen_geometry_status")
    full_pass = results.get("full_engine_regen_geometry_pass")
    best_status = results.get("best_full_engine_regen_status")
    best_pass = results.get("best_full_engine_regen_pass")

    failed_fit = _as_number(results.get("full_engine_regen_failed_fit_count"), 0)
    failed_reynolds = _as_number(results.get("full_engine_regen_failed_reynolds_count"), 0)
    failed_velocity = _as_number(results.get("full_engine_regen_failed_velocity_count"), 0)
    failed_thermal = _as_number(results.get("full_engine_regen_failed_thermal_count"), 0)
    missing_data = _as_number(results.get("full_engine_regen_missing_data_count"), 0)

    min_re = _as_number(results.get("full_engine_regen_min_reynolds"))
    max_velocity = _as_number(results.get("full_engine_regen_max_velocity"))
    max_twg = _as_number(results.get("full_engine_regen_max_hot_wall_temperature"))
    material_limit = _as_number(
        results.get("material_max_wall_temperature")
        or results.get("material_aware_combined_best_material_limit")
    )
    pressure_drop_pass = results.get("full_engine_regen_pressure_drop_pass")

    lines.append("Evidence summary:")
    lines.append(f"- Manual geometry valid: {_status_text(manual_valid)}")
    lines.append(f"- Recommended geometry status: {_status_text(recommended_status)}")
    lines.append(f"- Full-engine regen status: {_status_text(full_status)}")
    lines.append(f"- Best full-engine regen status: {_status_text(best_status)}")
    lines.append(f"- Failed fit station count: {failed_fit:g}")
    lines.append(f"- Failed Reynolds station count: {failed_reynolds:g}")
    lines.append(f"- Failed velocity station count: {failed_velocity:g}")
    lines.append(f"- Failed thermal station count: {failed_thermal:g}")
    lines.append(f"- Missing data count: {missing_data:g}")

    if min_re is not None:
        lines.append(f"- Minimum Reynolds number: {min_re:.6g}")

    if max_velocity is not None:
        lines.append(f"- Maximum coolant velocity: {max_velocity:.6g}")

    if max_twg is not None:
        lines.append(f"- Maximum hot wall temperature: {max_twg:.6g} K")

    if material_limit is not None:
        lines.append(f"- Material wall temperature limit: {material_limit:.6g} K")

    if pressure_drop_pass is not None:
        lines.append(f"- Pressure-drop gate pass: {_status_text(pressure_drop_pass)}")

    lines.append("")

    # ---------------------------------------------------------
    # What improved
    # ---------------------------------------------------------

    lines.append("What improved:")
    improvement_found = False

    if _truthy_pass(manual_valid):
        lines.append("- Manual geometry already passed local geometry fit.")
        improvement_found = True
    elif str(recommended_status).upper() in ("PASS", "BEST_AVAILABLE_BELOW_TARGET"):
        lines.append("- Recommended geometry improved the design beyond the manual geometry.")
        improvement_found = True

    if best_status:
        lines.append("- Best-candidate selection produced a controlling candidate status.")
        improvement_found = True

    if not improvement_found:
        lines.append("- No clear improvement evidence was recorded.")
    lines.append("")

    # ---------------------------------------------------------
    # Why current design fails or passes
    # ---------------------------------------------------------

    lines.append("Current controlling explanation:")

    if _truthy_pass(best_pass) or str(best_status).upper() == "PASS":
        proof_status = "PASS_PROVEN"
        failure_type = "NONE"
        next_step = "Proceed to benchmarking and regression testing."
        lines.append("- Best full-engine candidate passes the available validation gates.")

    elif missing_data and missing_data > 0:
        proof_status = "SOURCE_BLOCKED"
        failure_type = "MISSING_DATA"
        next_step = "Complete missing data before accepting the design."
        lines.append("- LEAF cannot fully validate the design because required data is missing.")

    elif failed_thermal and failed_thermal > 0:
        proof_status = "FAIL_PROVEN"
        failure_type = "PHYSICAL_THERMAL_LIMIT"
        next_step = "Improve material limit, cooling geometry, coolant flow, film/coating model, or heat-load assumptions."
        lines.append("- The controlling failure appears to be thermal/material driven.")

    elif failed_reynolds and failed_reynolds > 0:
        proof_status = "FAIL_PROVEN"
        failure_type = "PHYSICAL_COOLANT_FLOW_LIMIT"
        next_step = "Increase coolant velocity/Reynolds number or revise channel geometry."
        lines.append("- The controlling failure appears to be coolant-flow/Reynolds driven.")

    elif failed_velocity and failed_velocity > 0:
        proof_status = "FAIL_PROVEN"
        failure_type = "PHYSICAL_VELOCITY_LIMIT"
        next_step = "Revise channel count, channel area, pressure-drop allowance, or coolant flow split."
        lines.append("- The controlling failure appears to be coolant velocity driven.")

    elif failed_fit and failed_fit > 0:
        proof_status = "FAIL_PROVEN"
        failure_type = "GEOMETRY_FIT_LIMIT"
        next_step = "Revise channel count, pitch, rib width, or nozzle local radius constraints."
        lines.append("- The controlling failure appears to be geometric fit driven.")

    elif str(best_status).upper() in ("FAIL_BEST_AVAILABLE", "BEST_AVAILABLE"):
        proof_status = "FAIL_BEST_AVAILABLE"
        failure_type = "BEST_AVAILABLE_NOT_VALIDATED"
        next_step = "Treat the selected candidate as the best found so far, not a validated pass."
        lines.append("- LEAF found a best available candidate, but it is not a validated pass.")

    else:
        proof_status = "INCOMPLETE"
        failure_type = "ARCHITECTURE_OR_REPORTING_GAP"
        next_step = "Improve validation reporting so the controlling failure can be identified."
        lines.append("- LEAF does not yet have enough structured evidence to prove the controlling reason.")

    lines.append("")
    lines.append(f"Proof status: {proof_status}")
    lines.append(f"Failure type: {failure_type}")
    lines.append(f"Next required action: {next_step}")
    lines.append("")

    return {
        "regen_optimisation_proof_status": proof_status,
        "regen_optimisation_proof_failure_type": failure_type,
        "regen_optimisation_proof_next_step": next_step,
        "regen_optimisation_proof_text": "\n".join(lines),
        "regen_optimisation_proof_lines": lines,
    }


def attach_regen_optimisation_proof(results):
    if results is None:
        return results

    proof = build_regen_optimisation_proof(results)

    for key, value in proof.items():
        results[key] = value

    return results