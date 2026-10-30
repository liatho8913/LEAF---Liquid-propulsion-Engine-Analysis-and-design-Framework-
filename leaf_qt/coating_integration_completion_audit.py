"""
PHASE 10C.8
Coating Integration Completion Audit

Purpose:
    Final completion audit for Phase 10C coating solver integration.

This audit signs off the coating integration stack only when:
    - all Phase 10C stages exist
    - coating validation owner exists
    - conservative gates exist
    - report ownership exists
    - completion is explicit and auditable
"""


REQUIRED_COATING_COMPLETION_STAGES = {
    "10C.1": "phase_10c1_coating_property_consumption_audit_owner_complete",
    "10C.2": "phase_10c2_coating_thermal_conductivity_integration_owner_complete",
    "10C.3": "phase_10c3_coating_thickness_integration_owner_complete",
    "10C.4": "phase_10c4_coating_thermal_resistance_integration_owner_complete",
    "10C.5": "phase_10c5_coating_temperature_limit_integration_owner_complete",
    "10C.6": "phase_10c6_bond_coat_integration_owner_complete",
    "10C.7": "phase_10c7_coating_integration_validation_owner_complete",
}


def attach_coating_integration_completion_audit(results):
    if not isinstance(results, dict):
        return results

    audit = build_coating_integration_completion_audit(results)
    results.update(audit)
    return results


def build_coating_integration_completion_audit(results):
    results = results if isinstance(results, dict) else {}

    coating_selected = _coating_is_selected(results)
    bond_selected = _bond_coat_is_selected(results)

    coating_mode = str(
        results.get("coating_source_validation_mode")
        or results.get("coating_validation_mode")
        or "UNKNOWN"
    ).upper()

    coating_placeholder = bool(results.get("coating_source_is_placeholder", False))
    bond_placeholder = bool(results.get("bond_coat_source_is_placeholder", False))

    stage_rows = []
    blockers = []
    warnings = []

    for stage, key in REQUIRED_COATING_COMPLETION_STAGES.items():
        complete = bool(results.get(key, False))

        stage_rows.append({
            "stage": stage,
            "complete_key": key,
            "complete": complete,
        })

        if not complete:
            blockers.append(f"{stage} incomplete: {key}")

    validation_complete = bool(
        results.get("phase_10c7_coating_integration_validation_owner_complete", False)
    )

    validation_pass = bool(
        results.get("phase_10c7_coating_integration_validation_pass", False)
    )

    validation_status = results.get(
        "phase_10c7_coating_integration_validation_owner_status"
    )

    if not validation_complete:
        blockers.append("Phase 10C.7 coating integration validation owner is incomplete.")

    if validation_status is None:
        blockers.append("Phase 10C.7 validation status is missing.")

    if not validation_pass:
        warnings.append(
            "Coating integration validation pass flag is false. "
            "This is expected for conservative negative test cases."
        )

    if coating_selected:
        required_coating_keys = {
            "coating_thermal_conductivity": "coating conductivity",
            "effective_coating_thickness": "coating thickness",
            "effective_coating_thermal_resistance": "coating thermal resistance",
            "effective_coating_temperature_limit": "coating temperature limit",
        }

        for key, label in required_coating_keys.items():
            value = _safe_float(results.get(key))
            if value is None or value <= 0:
                blockers.append(f"Missing or invalid coating solver value: {label} ({key})")

        if coating_placeholder:
            blockers.append("Selected coating is placeholder-backed.")

        if coating_mode == "PLACEHOLDER_MODE":
            blockers.append("Coating mode is PLACEHOLDER_MODE.")

        if coating_mode == "PARTIAL_SOURCE_MODE":
            blockers.append("Coating mode is PARTIAL_SOURCE_MODE.")

        if coating_mode != "SOURCED_VALIDATION_MODE":
            blockers.append(f"Coating mode is not SOURCED_VALIDATION_MODE: {coating_mode}")

    else:
        warnings.append("No coating selected; coating completion audit is inactive but complete.")

    if bond_selected:
        required_bond_keys = {
            "bond_coat_thermal_conductivity": "bond coat conductivity",
            "bond_coat_thickness": "bond coat thickness",
            "effective_bond_coat_thermal_resistance": "bond coat thermal resistance",
        }

        for key, label in required_bond_keys.items():
            value = _safe_float(results.get(key))
            if value is None or value <= 0:
                blockers.append(f"Missing or invalid bond coat solver value: {label} ({key})")

        if bond_placeholder:
            blockers.append("Selected bond coat is placeholder-backed.")

    complete = all(row["complete"] for row in stage_rows)

    signoff_pass = (
        complete
        and validation_complete
        and validation_pass
        and not blockers
    )

    status = (
        "PASS_COATING_INTEGRATION_COMPLETION_AUDIT"
        if signoff_pass
        else "FAIL_COATING_INTEGRATION_COMPLETION_AUDIT"
    )

    text = build_coating_integration_completion_audit_text(
        status=status,
        complete=complete,
        signoff_pass=signoff_pass,
        coating_selected=coating_selected,
        bond_selected=bond_selected,
        coating_mode=coating_mode,
        coating_placeholder=coating_placeholder,
        bond_placeholder=bond_placeholder,
        validation_status=validation_status,
        validation_pass=validation_pass,
        stage_rows=stage_rows,
        blockers=blockers,
        warnings=warnings,
    )

    return {
        "phase_10c8_coating_integration_completion_audit_complete": complete,
        "phase_10c8_coating_integration_completion_audit_status": status,
        "phase_10c8_coating_integration_completion_audit_text": text,
        "phase_10c8_coating_integration_completion_audit_pass": signoff_pass,
        "phase_10c8_coating_integration_completion_audit_stage_rows": stage_rows,
        "phase_10c8_coating_integration_completion_audit_blockers": blockers,
        "phase_10c8_coating_integration_completion_audit_warnings": warnings,
        "stage_10c_coating_integration_complete": complete,
        "stage_10c_coating_integration_completion_status": status,
        "stage_10c_coating_integration_completion_pass": signoff_pass,
    }


def build_coating_integration_completion_audit_text(
        status,
        complete,
        signoff_pass,
        coating_selected,
        bond_selected,
        coating_mode,
        coating_placeholder,
        bond_placeholder,
        validation_status,
        validation_pass,
        stage_rows,
        blockers,
        warnings,
):
    lines = []

    lines.append("PHASE 10C.8 — COATING INTEGRATION COMPLETION AUDIT")
    lines.append("==================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append(f"Final signoff pass: {signoff_pass}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Final completion audit for Phase 10C coating solver integration.")
    lines.append("- Does not add new solver physics.")
    lines.append("- Confirms coating integration is ready for temperature-dependent solver audit.")
    lines.append("")
    lines.append("Coating State:")
    lines.append(f"- Coating selected: {coating_selected}")
    lines.append(f"- Bond coat selected: {bond_selected}")
    lines.append(f"- Coating validation mode: {coating_mode}")
    lines.append(f"- Coating placeholder: {coating_placeholder}")
    lines.append(f"- Bond coat placeholder: {bond_placeholder}")
    lines.append("")
    lines.append("Validation Owner:")
    lines.append(f"- Phase 10C.7 status: {validation_status}")
    lines.append(f"- Phase 10C.7 validation pass: {validation_pass}")
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
            "Phase 10C coating integration is complete and ready for the temperature-dependent solver audit."
        )
    else:
        lines.append(
            "Phase 10C coating integration is not signed off. Resolve blockers before moving forward."
        )

    return "\n".join(lines)


def _coating_is_selected(results):
    coating_name = str(
        results.get("selected_coating_material")
        or results.get("coating_material")
        or results.get("coating_name")
        or ""
    ).strip().upper()

    thickness = _safe_float(
        results.get("effective_coating_thickness")
        or results.get("coating_thickness")
    )

    if coating_name in ("", "NONE", "NO_COATING", "N/A"):
        return False

    if thickness is not None and thickness > 0:
        return True

    return bool(coating_name)


def _bond_coat_is_selected(results):
    enabled = results.get("bond_coat_enabled", None)

    if isinstance(enabled, bool):
        if not enabled:
            return False
        if enabled:
            return True

    name = str(
        results.get("selected_bond_coat_material")
        or results.get("bond_coat_material")
        or results.get("bond_coat_name")
        or ""
    ).strip().upper()

    thickness = _safe_float(results.get("bond_coat_thickness"))

    if name in ("", "NONE", "NO_BOND_COAT", "NO_BONDCOAT", "N/A"):
        return False

    if thickness is not None and thickness > 0:
        return True

    return bool(name)


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None