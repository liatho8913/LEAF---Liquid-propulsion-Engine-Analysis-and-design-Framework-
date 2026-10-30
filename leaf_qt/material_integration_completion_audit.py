"""
PHASE 10B.8
Material Integration Completion Audit

Purpose:
    Final completion audit for Phase 10B material solver integration.

This audit signs off the full material integration stack only when:
    - all Phase 10B stages exist
    - material validation owner exists
    - sourced mode rules are enforced
    - solver pathways exist
    - completion is explicit and auditable
"""


REQUIRED_COMPLETION_STAGES = {
    "10B.1": "phase_10b1_material_property_consumption_audit_owner_complete",
    "10B.2": "phase_10b2_material_thermal_conductivity_integration_owner_complete",
    "10B.3": "phase_10b3_material_specific_heat_integration_owner_complete",
    "10B.4": "phase_10b4_material_density_integration_owner_complete",
    "10B.5": "phase_10b5_material_temperature_limit_integration_owner_complete",
    "10B.6": "phase_10b6_material_strength_limit_integration_owner_complete",
    "10B.7": "phase_10b7_material_integration_validation_owner_complete",
}


def attach_material_integration_completion_audit(results):
    if not isinstance(results, dict):
        return results

    audit = build_material_integration_completion_audit(results)
    results.update(audit)
    return results


def build_material_integration_completion_audit(results):
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

    for stage, key in REQUIRED_COMPLETION_STAGES.items():
        complete = bool(results.get(key, False))

        stage_rows.append({
            "stage": stage,
            "complete_key": key,
            "complete": complete,
        })

        if not complete:
            blockers.append(f"{stage} incomplete: {key}")

    validation_complete = bool(
        results.get("phase_10b7_material_integration_validation_owner_complete", False)
    )

    validation_pass = bool(
        results.get("phase_10b7_material_integration_validation_pass", False)
    )

    validation_status = results.get(
        "phase_10b7_material_integration_validation_owner_status"
    )

    if not validation_complete:
        blockers.append("Phase 10B.7 material integration validation owner is incomplete.")

    if validation_status is None:
        blockers.append("Phase 10B.7 validation status is missing.")

    # Completion audit can exist even when validation correctly fails in negative
    # test cases, but final material integration signoff only passes when the
    # validation pass flag is true.
    if not validation_pass:
        warnings.append(
            "Material integration validation pass flag is false. "
            "This is expected for conservative negative test cases."
        )

    required_solver_keys = {
        "wall_thermal_conductivity": "k(T)",
        "material_specific_heat_cp": "Cp(T)",
        "material_density": "rho(T)",
        "effective_material_temperature_limit": "temperature limit",
        "effective_material_yield_strength": "yield / strength limit",
    }

    for key, label in required_solver_keys.items():
        value = _safe_float(results.get(key))
        if value is None or value <= 0:
            blockers.append(f"Missing or invalid integrated material solver value: {label} ({key})")

    conservative_authority_ok = True

    if material_placeholder:
        conservative_authority_ok = False
        blockers.append("Material source is placeholder-backed.")

    if material_mode == "PLACEHOLDER_MODE":
        conservative_authority_ok = False
        blockers.append("Material mode is PLACEHOLDER_MODE.")

    if material_mode == "PARTIAL_SOURCE_MODE":
        conservative_authority_ok = False
        blockers.append("Material mode is PARTIAL_SOURCE_MODE.")

    if material_mode != "SOURCED_VALIDATION_MODE":
        conservative_authority_ok = False
        blockers.append(
            f"Material mode is not SOURCED_VALIDATION_MODE: {material_mode}"
        )

    complete = all(row["complete"] for row in stage_rows)

    signoff_pass = (
        complete
        and validation_complete
        and validation_pass
        and conservative_authority_ok
        and not blockers
    )

    status = (
        "PASS_MATERIAL_INTEGRATION_COMPLETION_AUDIT"
        if signoff_pass
        else "FAIL_MATERIAL_INTEGRATION_COMPLETION_AUDIT"
    )

    text = build_material_integration_completion_audit_text(
        status=status,
        complete=complete,
        signoff_pass=signoff_pass,
        material_mode=material_mode,
        material_placeholder=material_placeholder,
        validation_status=validation_status,
        validation_pass=validation_pass,
        stage_rows=stage_rows,
        blockers=blockers,
        warnings=warnings,
    )

    return {
        "phase_10b8_material_integration_completion_audit_complete": complete,
        "phase_10b8_material_integration_completion_audit_status": status,
        "phase_10b8_material_integration_completion_audit_text": text,
        "phase_10b8_material_integration_completion_audit_pass": signoff_pass,
        "phase_10b8_material_integration_completion_audit_stage_rows": stage_rows,
        "phase_10b8_material_integration_completion_audit_blockers": blockers,
        "phase_10b8_material_integration_completion_audit_warnings": warnings,
        "stage_10b_material_integration_complete": complete,
        "stage_10b_material_integration_completion_status": status,
        "stage_10b_material_integration_completion_pass": signoff_pass,
    }


def build_material_integration_completion_audit_text(
        status,
        complete,
        signoff_pass,
        material_mode,
        material_placeholder,
        validation_status,
        validation_pass,
        stage_rows,
        blockers,
        warnings,
):
    lines = []

    lines.append("PHASE 10B.8 — MATERIAL INTEGRATION COMPLETION AUDIT")
    lines.append("===================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append(f"Final signoff pass: {signoff_pass}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Final completion audit for Phase 10B material solver integration.")
    lines.append("- Does not add new solver physics.")
    lines.append("- Confirms the integrated material stack is ready for coating integration only when sourced validation passes.")
    lines.append("")
    lines.append("Material Source State:")
    lines.append(f"- Material validation mode: {material_mode}")
    lines.append(f"- Material placeholder: {material_placeholder}")
    lines.append("")
    lines.append("Validation Owner:")
    lines.append(f"- Phase 10B.7 status: {validation_status}")
    lines.append(f"- Phase 10B.7 validation pass: {validation_pass}")
    lines.append("")
    lines.append("Stage Completion:")
    for row in stage_rows:
        lines.append(
            f"- {row['stage']} | complete={row['complete']} | key={row['complete_key']}"
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
    if signoff_pass:
        lines.append(
            "Phase 10B material solver integration is complete and ready for coating integration."
        )
    else:
        lines.append(
            "Phase 10B material solver integration is not signed off. Resolve blockers before coating integration."
        )

    return "\n".join(lines)


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None