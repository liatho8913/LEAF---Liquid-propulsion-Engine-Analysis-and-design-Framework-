"""
PHASE 10C.7
Coating Integration Validation Owner

Purpose:
    Validate the complete coating integration stack as one system.

This owner does not add new coating physics.
It validates that existing coating integrations are present, conservative,
and ready for the Phase 10C.8 completion audit.
"""


REQUIRED_COATING_INTEGRATION_STAGES = {
    "10C.1": {
        "complete_key": "phase_10c1_coating_property_consumption_audit_owner_complete",
        "status_key": "phase_10c1_coating_property_consumption_audit_owner_status",
        "expected_status": "PASS_PHASE_10C1_COATING_PROPERTY_CONSUMPTION_AUDIT_OWNER",
        "description": "Coating property consumption audit",
    },
    "10C.2": {
        "complete_key": "phase_10c2_coating_thermal_conductivity_integration_owner_complete",
        "status_key": "phase_10c2_coating_thermal_conductivity_integration_owner_status",
        "expected_status": "PASS_PHASE_10C2_COATING_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER",
        "description": "Coating thermal conductivity integration",
    },
    "10C.3": {
        "complete_key": "phase_10c3_coating_thickness_integration_owner_complete",
        "status_key": "phase_10c3_coating_thickness_integration_owner_status",
        "expected_status": "PASS_PHASE_10C3_COATING_THICKNESS_INTEGRATION_OWNER",
        "description": "Coating thickness integration",
    },
    "10C.4": {
        "complete_key": "phase_10c4_coating_thermal_resistance_integration_owner_complete",
        "status_key": "phase_10c4_coating_thermal_resistance_integration_owner_status",
        "expected_status": "PASS_PHASE_10C4_COATING_THERMAL_RESISTANCE_INTEGRATION_OWNER",
        "description": "Coating thermal resistance integration",
    },
    "10C.5": {
        "complete_key": "phase_10c5_coating_temperature_limit_integration_owner_complete",
        "status_key": "phase_10c5_coating_temperature_limit_integration_owner_status",
        "expected_status": "PASS_PHASE_10C5_COATING_TEMPERATURE_LIMIT_INTEGRATION_OWNER",
        "description": "Coating temperature limit integration",
    },
    "10C.6": {
        "complete_key": "phase_10c6_bond_coat_integration_owner_complete",
        "status_key": "phase_10c6_bond_coat_integration_owner_status",
        "expected_status": "PASS_PHASE_10C6_BOND_COAT_INTEGRATION_OWNER",
        "description": "Bond coat integration",
    },
}


def attach_coating_integration_validation_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_coating_integration_validation(results)
    results.update(audit)
    return results


def build_coating_integration_validation(results):
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

    for stage, spec in REQUIRED_COATING_INTEGRATION_STAGES.items():
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

    if coating_selected:
        if coating_placeholder:
            conservative_pass = False
            blockers.append("Selected coating is placeholder-backed.")

        if coating_mode == "PLACEHOLDER_MODE":
            conservative_pass = False
            blockers.append("Coating validation mode is PLACEHOLDER_MODE.")

        if coating_mode == "PARTIAL_SOURCE_MODE":
            conservative_pass = False
            blockers.append("Coating validation mode is PARTIAL_SOURCE_MODE.")

        if coating_mode != "SOURCED_VALIDATION_MODE":
            conservative_pass = False
            blockers.append(
                f"Coating validation mode is not SOURCED_VALIDATION_MODE: {coating_mode}"
            )

    if bond_selected and bond_placeholder:
        conservative_pass = False
        blockers.append("Selected bond coat is placeholder-backed.")

    if coating_selected:
        required_coating_keys = {
            "coating_thermal_conductivity": "coating conductivity",
            "effective_coating_thickness": "coating thickness",
            "effective_coating_thermal_resistance": "coating thermal resistance",
            "effective_coating_temperature_limit": "coating temperature limit",
        }

        for key, description in required_coating_keys.items():
            value = _safe_float(results.get(key))
            if value is None or value <= 0:
                blockers.append(f"{description} missing or invalid: {key}={results.get(key)}")

        coating_temp_pass = results.get("coating_temperature_limit_pass")

        if coating_temp_pass is None:
            warnings.append("Coating temperature pass flag is not available.")
        elif float(coating_temp_pass) < 1.0:
            blockers.append("Coating temperature limit validation is failing.")

    else:
        warnings.append("No coating selected; coating validation is inactive but owner is complete.")

    if bond_selected:
        required_bond_keys = {
            "bond_coat_thermal_conductivity": "bond coat conductivity",
            "bond_coat_thickness": "bond coat thickness",
            "effective_bond_coat_thermal_resistance": "bond coat thermal resistance",
        }

        for key, description in required_bond_keys.items():
            value = _safe_float(results.get(key))
            if value is None or value <= 0:
                blockers.append(f"{description} missing or invalid: {key}={results.get(key)}")

        bond_pass = results.get("bond_coat_temperature_limit_pass")

        if bond_pass is None:
            warnings.append("Bond coat temperature pass flag is not available.")
        elif float(bond_pass) < 1.0:
            blockers.append("Bond coat temperature validation is failing.")

    complete = all(row["passed"] for row in stage_rows)

    validation_pass = complete and conservative_pass and not blockers

    status = (
        "PASS_PHASE_10C7_COATING_INTEGRATION_VALIDATION_OWNER"
        if validation_pass
        else "FAIL_PHASE_10C7_COATING_INTEGRATION_VALIDATION_OWNER"
    )

    text = build_coating_integration_validation_text(
        status=status,
        complete=complete,
        validation_pass=validation_pass,
        coating_selected=coating_selected,
        bond_selected=bond_selected,
        coating_mode=coating_mode,
        coating_placeholder=coating_placeholder,
        bond_placeholder=bond_placeholder,
        stage_rows=stage_rows,
        blockers=blockers,
        warnings=warnings,
    )

    return {
        "phase_10c7_coating_integration_validation_owner_complete": complete,
        "phase_10c7_coating_integration_validation_owner_status": status,
        "phase_10c7_coating_integration_validation_owner_text": text,
        "phase_10c7_coating_integration_validation_pass": validation_pass,
        "phase_10c7_coating_integration_validation_stage_rows": stage_rows,
        "phase_10c7_coating_integration_validation_blockers": blockers,
        "phase_10c7_coating_integration_validation_warnings": warnings,
        "stage_10c_coating_integration_validation_complete": complete,
        "stage_10c_coating_integration_validation_status": status,
        "stage_10c_coating_integration_validation_pass": validation_pass,
    }


def build_coating_integration_validation_text(
        status,
        complete,
        validation_pass,
        coating_selected,
        bond_selected,
        coating_mode,
        coating_placeholder,
        bond_placeholder,
        stage_rows,
        blockers,
        warnings,
):
    lines = []

    lines.append("PHASE 10C.7 — COATING INTEGRATION VALIDATION OWNER")
    lines.append("===================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append(f"Validation pass: {validation_pass}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Validates the complete Phase 10C coating integration stack.")
    lines.append("- Does not add new solver physics.")
    lines.append("- Blocks final validation for placeholder or partial-source coating authority.")
    lines.append("")
    lines.append("Coating State:")
    lines.append(f"- Coating selected: {coating_selected}")
    lines.append(f"- Bond coat selected: {bond_selected}")
    lines.append(f"- Coating validation mode: {coating_mode}")
    lines.append(f"- Coating placeholder: {coating_placeholder}")
    lines.append(f"- Bond coat placeholder: {bond_placeholder}")
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
            "The integrated coating stack is valid and ready for the Phase 10C.8 completion audit."
        )
    else:
        lines.append(
            "The integrated coating stack is not ready for completion audit. Resolve blockers first."
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