def _num(value, default=None):
    try:
        if value in (None, "", "N/A", "None"):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _is_positive(value):
    value = _num(value, 0)
    return value is not None and value > 0


def _truthy_pass(value):
    return value in (True, 1, "1", "PASS", "pass", "Pass", "TRUE", "true")


def _add_cause(causes, category, title, evidence=None, likely_reason=None, next_check=None):
    causes.append({
        "category": category,
        "title": title,
        "evidence": evidence or [],
        "likely_reason": likely_reason or "",
        "next_check": next_check or "",
    })


def build_regen_failure_root_cause(results):
    results = results if isinstance(results, dict) else {}

    causes = []

    failed_fit = results.get("full_engine_regen_failed_fit_count")
    failed_reynolds = results.get("full_engine_regen_failed_reynolds_count")
    below_target_reynolds = results.get("full_engine_regen_below_target_reynolds_count")
    failed_velocity = results.get("full_engine_regen_failed_velocity_count")
    failed_thermal = results.get("full_engine_regen_failed_thermal_count")
    missing_data = results.get("full_engine_regen_missing_data_count")

    min_re = results.get("full_engine_regen_min_reynolds")
    target_re = results.get("full_engine_regen_target_reynolds")
    turbulent_re = results.get("full_engine_regen_minimum_turbulent_reynolds")
    max_velocity = results.get("full_engine_regen_max_velocity")
    max_twg = results.get("full_engine_regen_max_hot_wall_temperature")
    max_pressure_drop = results.get("full_engine_regen_max_pressure_drop")
    pressure_drop_pass = results.get("full_engine_regen_pressure_drop_pass")

    material_limit = (
        results.get("material_max_wall_temperature")
        or results.get("material_aware_combined_best_material_limit")
    )

    best_status = results.get("best_full_engine_regen_status")
    best_reason = results.get("best_full_engine_regen_reason")
    proof_status = results.get("regen_optimisation_proof_status")
    proof_failure_type = results.get("regen_optimisation_proof_failure_type")

    # Geometry root cause
    if _is_positive(failed_fit):
        _add_cause(
            causes,
            category="GEOMETRY_FIT",
            title="Coolant channel geometry does not fit all axial stations.",
            evidence=[
                f"Failed fit station count: {failed_fit}",
                f"Recommended geometry status: {results.get('recommended_geometry_status')}",
                f"Channel fit ratio: {results.get('channel_fit_ratio')}",
                f"Effective rib width: {results.get('effective_rib_width')}",
            ],
            likely_reason=(
                "The requested channel count, channel width, rib width, or pitch exceeds the "
                "available local circumference at one or more stations."
            ),
            next_check=(
                "Check throat and tight-radius stations first. Reduce channel count, reduce channel width, "
                "or allow variable geometry."
            ),
        )

    # Reynolds / flow root cause
    if _is_positive(failed_reynolds) or _is_positive(below_target_reynolds):
        _add_cause(
            causes,
            category="COOLANT_REYNOLDS",
            title="Coolant Reynolds number is below the required target.",
            evidence=[
                f"Failed Reynolds station count: {failed_reynolds}",
                f"Below target Reynolds station count: {below_target_reynolds}",
                f"Minimum Reynolds number: {min_re}",
                f"Target Reynolds number: {target_re}",
                f"Minimum turbulent Reynolds number: {turbulent_re}",
            ],
            likely_reason=(
                "Coolant velocity, hydraulic diameter, density, or viscosity produces insufficient turbulence. "
                "Heat transfer may be too weak even if the geometry fits."
            ),
            next_check=(
                "Increase coolant velocity, reduce flow area, revise channel dimensions, or use coolant properties "
                "at the correct temperature."
            ),
        )

    # Velocity root cause
    if _is_positive(failed_velocity):
        _add_cause(
            causes,
            category="COOLANT_VELOCITY",
            title="Coolant velocity exceeds allowed design limits.",
            evidence=[
                f"Failed velocity station count: {failed_velocity}",
                f"Maximum coolant velocity: {max_velocity}",
            ],
            likely_reason=(
                "The design may require excessive coolant velocity to reach the target Reynolds number or heat-transfer coefficient."
            ),
            next_check=(
                "Increase total coolant flow area, revise channel count, or relax velocity limits only if justified."
            ),
        )

    # Thermal/material root cause
    if _is_positive(failed_thermal):
        evidence = [
            f"Failed thermal station count: {failed_thermal}",
            f"Maximum hot wall temperature: {max_twg}",
            f"Material wall temperature limit: {material_limit}",
            f"Material-aware combined status: {results.get('material_aware_combined_status')}",
        ]

        _add_cause(
            causes,
            category="THERMAL_MATERIAL_LIMIT",
            title="Hot-wall temperature exceeds material capability.",
            evidence=evidence,
            likely_reason=(
                "The heat load is too high for the current coolant-side heat transfer, wall thickness, material limit, "
                "coating model, or assumed chamber conditions."
            ),
            next_check=(
                "Check throat-region heat flux, material max wall temperature, coolant heat-transfer coefficient, "
                "coating assumptions, and wall thickness."
            ),
        )

    # Pressure-drop root cause
    if pressure_drop_pass not in (None, "", "N/A") and not _truthy_pass(pressure_drop_pass):
        _add_cause(
            causes,
            category="PRESSURE_DROP",
            title="Pressure-drop gate prevents accepting the cooling solution.",
            evidence=[
                f"Pressure-drop pass: {pressure_drop_pass}",
                f"Maximum pressure drop: {max_pressure_drop}",
            ],
            likely_reason=(
                "The coolant circuit may need too much pressure drop to achieve the required heat transfer."
            ),
            next_check=(
                "Review channel hydraulic diameter, length, friction factor, coolant velocity, and pump/feed pressure budget."
            ),
        )

    # Missing data root cause
    if _is_positive(missing_data):
        _add_cause(
            causes,
            category="MISSING_DATA",
            title="Validation is blocked by missing required data.",
            evidence=[
                f"Missing data count: {missing_data}",
                f"Coating source data gate: {results.get('coating_stack_source_data_gate')}",
                f"Coating database readiness: {results.get('coating_database_readiness')}",
            ],
            likely_reason=(
                "LEAF does not yet have enough sourced material, coating, coolant, or validation data to make a trusted pass/fail decision."
            ),
            next_check=(
                "Complete material/coating source metadata and temperature-dependent property tables."
            ),
        )

    # Best available failure
    if str(best_status).upper() in ("FAIL_BEST_AVAILABLE", "BEST_AVAILABLE"):
        _add_cause(
            causes,
            category="BEST_AVAILABLE_NOT_VALIDATED",
            title="Best available candidate is not a validated pass.",
            evidence=[
                f"Best full-engine regen status: {best_status}",
                f"Best full-engine regen reason: {best_reason}",
                f"Optimisation proof status: {proof_status}",
                f"Optimisation proof failure type: {proof_failure_type}",
            ],
            likely_reason=(
                "LEAF found the strongest candidate in the available search/selection path, but one or more validation gates still failed."
            ),
            next_check=(
                "Do not treat this as a pass. Use the failure categories above to decide whether to revise geometry, materials, cooling, or source data."
            ),
        )

    # If no cause is found
    if not causes:
        if str(proof_status).upper() in ("PASS_PROVEN", "PASS"):
            status = "NO_FAILURE_DETECTED"
            summary = "No root-cause failure detected because the proof layer reports a pass."
        else:
            status = "INCOMPLETE"
            summary = "No clear root cause could be extracted from current result keys."
            _add_cause(
                causes,
                category="ARCHITECTURE_OR_REPORTING_GAP",
                title="Root cause could not be identified from available structured outputs.",
                evidence=[
                    f"Optimisation proof status: {proof_status}",
                    f"Optimisation proof failure type: {proof_failure_type}",
                    f"Best full-engine regen status: {best_status}",
                ],
                likely_reason=(
                    "The solver may be calculating the failure, but the result is not yet exposed through a recognised key."
                ),
                next_check=(
                    "Add explicit validation keys for the missing gate or connect the relevant solver output to the registry."
                ),
            )
    else:
        status = "ROOT_CAUSE_RECORDED"
        summary = f"{len(causes)} root-cause category/categories recorded."

    text = build_root_cause_text(status, summary, causes)

    return {
        "failure_root_cause_status": status,
        "failure_root_cause_summary": summary,
        "failure_root_cause_count": len(causes),
        "failure_root_cause_categories": [cause["category"] for cause in causes],
        "failure_root_cause_items": causes,
        "failure_root_cause_text": text,
    }


def build_root_cause_text(status, summary, causes):
    lines = []
    lines.append("LEAF FAILURE ROOT CAUSE ANALYSIS")
    lines.append("================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Summary: {summary}")
    lines.append("")

    for index, cause in enumerate(causes, start=1):
        lines.append(f"Cause {index}: {cause.get('title', 'Untitled cause')}")
        lines.append(f"Category: {cause.get('category', 'UNKNOWN')}")
        lines.append("")

        evidence = cause.get("evidence") or []
        lines.append("Evidence:")

        if evidence:
            for item in evidence:
                if item not in (None, "", "N/A", "None"):
                    lines.append(f"- {item}")
        else:
            lines.append("- None recorded.")

        lines.append("")
        lines.append("Likely reason:")
        lines.append(f"- {cause.get('likely_reason') or 'No likely reason recorded.'}")
        lines.append("")
        lines.append("Next check:")
        lines.append(f"- {cause.get('next_check') or 'No next check recorded.'}")
        lines.append("")
        lines.append("-" * 50)
        lines.append("")

    return "\n".join(lines)


def attach_regen_failure_root_cause(results):
    if results is None:
        return results

    root_cause = build_regen_failure_root_cause(results)

    for key, value in root_cause.items():
        results[key] = value

    return results