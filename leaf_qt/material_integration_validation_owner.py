"""
PHASE 10B.7
Material Integration Validation Owner

Purpose:
    Validate the complete material integration stack as one system.

Checks:
    - 10B.1 consumption audit
    - 10B.2 k(T)
    - 10B.3 Cp(T)
    - 10B.4 rho(T)
    - 10B.5 temperature limit
    - 10B.6 strength limit

This owner does not add new physics.
It validates that existing material integration is complete, conservative,
and ready for completion audit.
"""


REQUIRED_MATERIAL_INTEGRATION_STAGES = {
    "10B.1": {
        "complete_key": "phase_10b1_material_property_consumption_audit_owner_complete",
        "status_key": "phase_10b1_material_property_consumption_audit_owner_status",
        "expected_status": "PASS_PHASE_10B1_MATERIAL_PROPERTY_CONSUMPTION_AUDIT_OWNER",
        "description": "Material property consumption audit",
    },
    "10B.2": {
        "complete_key": "phase_10b2_material_thermal_conductivity_integration_owner_complete",
        "status_key": "phase_10b2_material_thermal_conductivity_integration_owner_status",
        "expected_status": "PASS_PHASE_10B2_MATERIAL_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER",
        "description": "Material thermal conductivity k(T) integration",
    },
    "10B.3": {
        "complete_key": "phase_10b3_material_specific_heat_integration_owner_complete",
        "status_key": "phase_10b3_material_specific_heat_integration_owner_status",
        "expected_status": "PASS_PHASE_10B3_MATERIAL_SPECIFIC_HEAT_INTEGRATION_OWNER",
        "description": "Material specific heat Cp(T) integration",
    },
    "10B.4": {
        "complete_key": "phase_10b4_material_density_integration_owner_complete",
        "status_key": "phase_10b4_material_density_integration_owner_status",
        "expected_status": "PASS_PHASE_10B4_MATERIAL_DENSITY_INTEGRATION_OWNER",
        "description": "Material density rho(T) integration",
    },
    "10B.5": {
        "complete_key": "phase_10b5_material_temperature_limit_integration_owner_complete",
        "status_key": "phase_10b5_material_temperature_limit_integration_owner_status",
        "expected_status": "PASS_PHASE_10B5_MATERIAL_TEMPERATURE_LIMIT_INTEGRATION_OWNER",
        "description": "Material temperature limit integration",
    },
    "10B.6": {
        "complete_key": "phase_10b6_material_strength_limit_integration_owner_complete",
        "status_key": "phase_10b6_material_strength_limit_integration_owner_status",
        "expected_status": "PASS_PHASE_10B6_MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER",
        "description": "Material strength limit integration",
    },
}


def attach_material_integration_validation_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_material_integration_validation(results)
    results.update(audit)
    return results


def build_material_integration_validation(results):
    results = results if isinstance(results, dict) else {}

    material_mode = str(
        results.get("material_source_validation_mode")
        or results.get("material_property_interpolation_mode")
        or "UNKNOWN"
    ).upper()

    material_placeholder = bool(results.get("material_source_is_placeholder", False))

    stage_rows = []
    blockers = []
    warnings = []

    for stage, spec in REQUIRED_MATERIAL_INTEGRATION_STAGES.items():
        complete = bool(results.get(spec["complete_key"], False))
        status = results.get(spec["status_key"])

        passed = complete and status == spec["expected_status"]

        if not passed:
            blockers.append(
                f"{stage}: {spec['description']} incomplete or not passing "
                f"(status={status}, complete={complete})"
            )

        stage_rows.append({
            "stage": stage,
            "description": spec["description"],
            "complete": complete,
            "status": status,
            "expected_status": spec["expected_status"],
            "passed": passed,
        })

    conservative_pass = True

    if material_placeholder:
        conservative_pass = False
        blockers.append("Material source is placeholder-backed.")

    if material_mode == "PLACEHOLDER_MODE":
        conservative_pass = False
        blockers.append("Material validation mode is PLACEHOLDER_MODE.")

    if material_mode == "PARTIAL_SOURCE_MODE":
        conservative_pass = False
        blockers.append("Material validation mode is PARTIAL_SOURCE_MODE.")

    if material_mode != "SOURCED_VALIDATION_MODE":
        conservative_pass = False
        blockers.append(
            f"Material validation mode is not SOURCED_VALIDATION_MODE: {material_mode}"
        )

    required_solver_keys = {
        "wall_thermal_conductivity": "k(T) solver pathway",
        "material_specific_heat_cp": "Cp(T) solver pathway",
        "material_density": "rho(T) solver pathway",
        "effective_material_temperature_limit": "temperature limit pathway",
        "effective_material_yield_strength": "strength limit pathway",
    }

    for key, description in required_solver_keys.items():
        value = _safe_float(results.get(key))
        if value is None or value <= 0:
            blockers.append(f"{description} missing or invalid: {key}={results.get(key)}")

    material_temperature_pass = results.get("material_temperature_limit_pass")
    material_structural_pass = results.get("material_structural_pass")

    if material_temperature_pass is None:
        warnings.append("Temperature limit pass flag is not available.")
    elif float(material_temperature_pass) < 1.0:
        blockers.append("Material temperature limit validation is failing.")

    if material_structural_pass is None:
        warnings.append("Structural pass flag is not available.")
    elif float(material_structural_pass) < 1.0:
        blockers.append("Material structural validation is failing.")

    complete = all(row["passed"] for row in stage_rows)

    validation_pass = complete and conservative_pass and not blockers

    status = (
        "PASS_PHASE_10B7_MATERIAL_INTEGRATION_VALIDATION_OWNER"
        if validation_pass
        else "FAIL_PHASE_10B7_MATERIAL_INTEGRATION_VALIDATION_OWNER"
    )

    text = build_material_integration_validation_text(
        status=status,
        complete=complete,
        validation_pass=validation_pass,
        material_mode=material_mode,
        material_placeholder=material_placeholder,
        stage_rows=stage_rows,
        blockers=blockers,
        warnings=warnings,
    )

    return {
        "phase_10b7_material_integration_validation_owner_complete": complete,
        "phase_10b7_material_integration_validation_owner_status": status,
        "phase_10b7_material_integration_validation_owner_text": text,
        "phase_10b7_material_integration_validation_pass": validation_pass,
        "phase_10b7_material_integration_validation_stage_rows": stage_rows,
        "phase_10b7_material_integration_validation_blockers": blockers,
        "phase_10b7_material_integration_validation_warnings": warnings,
        "stage_10b_material_integration_validation_complete": complete,
        "stage_10b_material_integration_validation_status": status,
        "stage_10b_material_integration_validation_pass": validation_pass,
    }


def build_material_integration_validation_text(
        status,
        complete,
        validation_pass,
        material_mode,
        material_placeholder,
        stage_rows,
        blockers,
        warnings,
):
    lines = []

    lines.append("PHASE 10B.7 — MATERIAL INTEGRATION VALIDATION OWNER")
    lines.append("===================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append(f"Validation pass: {validation_pass}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Validates the complete Phase 10B material integration stack.")
    lines.append("- Does not add new solver physics.")
    lines.append("- Blocks final validation for placeholder or partial-source material authority.")
    lines.append("")
    lines.append("Material Source State:")
    lines.append(f"- Material validation mode: {material_mode}")
    lines.append(f"- Material placeholder: {material_placeholder}")
    lines.append("")
    lines.append("Stage Validation:")
    for row in stage_rows:
        lines.append(
            f"- {row['stage']} | {row['description']} | "
            f"complete={row['complete']} | passed={row['passed']} | "
            f"status={row['status']}"
        )

    lines.append("")
    lines.append("Warnings:")
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Blockers:")
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Conclusion:")
    if validation_pass:
        lines.append(
            "The integrated material stack is valid and ready for the Phase 10B.8 completion audit."
        )
    else:
        lines.append(
            "The integrated material stack is not ready for completion audit. Resolve blockers first."
        )

    return "\n".join(lines)


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None