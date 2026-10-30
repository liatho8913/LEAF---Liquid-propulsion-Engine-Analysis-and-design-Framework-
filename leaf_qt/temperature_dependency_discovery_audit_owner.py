"""
PHASE 10D.1
Temperature Dependency Discovery Audit Owner

Purpose:
    Discover every temperature-dependent property pathway before 10D begins
    perturbation/consumption tests.

Rules:
    - Audit only: this owner must not alter solver physics values.
    - Conservative: missing/placeholder/static pathways are findings, not hidden passes.
    - Reusable: all pathway evidence is reported as generic dependency evidence so
      later material, coating, fluid, hypersonic, and manufacturing modules can consume it.
"""

TEMPERATURE_DEPENDENCY_PATHS = {
    "material_thermal_conductivity": {
        "phase": "10D.2",
        "symbol": "k_material(T)",
        "input_keys": [
            "material_property_interpolation_results",
            "sourced_wall_thermal_conductivity",
            "material_thermal_conductivity",
            "wall_thermal_conductivity",
        ],
        "integration_keys": [
            "phase_10b2_material_thermal_conductivity_integration_owner_applied",
            "wall_thermal_conductivity_source",
        ],
        "affected_keys": [
            "wall_temperature_hot_gas",
            "hot_gas_side_wall_temperature",
            "wall_temperature_coolant_side",
            "coolant_side_wall_temperature",
            "regen_heat_flux",
            "heat_flux",
            "thermal_resistance_wall",
        ],
    },
    "material_specific_heat": {
        "phase": "10D.3",
        "symbol": "Cp_material(T)",
        "input_keys": [
            "material_property_interpolation_results",
            "material_specific_heat",
            "material_specific_heat_cp",
        ],
        "integration_keys": [
            "phase_10b3_material_specific_heat_integration_owner_applied",
            "material_specific_heat_source",
        ],
        "affected_keys": [
            "coolant_temperature_rise",
            "coolant_delta_t",
            "regen_coolant_temperature_rise",
            "energy_balance_status",
        ],
    },
    "material_density": {
        "phase": "10D.4",
        "symbol": "rho_material(T)",
        "input_keys": [
            "material_property_interpolation_results",
            "material_density",
            "sourced_material_density",
        ],
        "integration_keys": [
            "phase_10b4_material_density_integration_owner_applied",
            "material_density_source",
        ],
        "affected_keys": [
            "material_mass",
            "wall_mass",
            "structural_margin",
        ],
    },
    "coolant_density": {
        "phase": "10D.4",
        "symbol": "rho_coolant(T)",
        "input_keys": [
            "coolant_density",
            "coolant_bulk_temperature",
            "coolant_temperature",
        ],
        "integration_keys": [
            "coolant_density_source",
            "coolant_property_source",
        ],
        "affected_keys": [
            "regen_coolant_velocity",
            "coolant_velocity",
            "coolant_reynolds_number",
            "regen_reynolds_number",
            "regen_pressure_drop",
            "coolant_pressure_drop",
        ],
    },
    "coolant_viscosity": {
        "phase": "10D.4",
        "symbol": "mu_coolant(T)",
        "input_keys": [
            "coolant_dynamic_viscosity",
            "coolant_viscosity",
            "coolant_bulk_temperature",
        ],
        "integration_keys": [
            "coolant_viscosity_source",
            "coolant_property_source",
        ],
        "affected_keys": [
            "coolant_reynolds_number",
            "regen_reynolds_number",
            "coolant_nusselt_number",
            "regen_pressure_drop",
        ],
    },
    "coolant_specific_heat": {
        "phase": "10D.3",
        "symbol": "Cp_coolant(T)",
        "input_keys": [
            "coolant_specific_heat_cp",
            "coolant_cp",
            "coolant_bulk_temperature",
        ],
        "integration_keys": [
            "coolant_specific_heat_source",
            "coolant_property_source",
        ],
        "affected_keys": [
            "coolant_temperature_rise",
            "coolant_delta_t",
            "regen_coolant_temperature_rise",
        ],
    },
    "coating_thermal_conductivity": {
        "phase": "10D.5",
        "symbol": "k_coating(T)",
        "input_keys": [
            "coating_thermal_conductivity",
            "sourced_coating_thermal_conductivity",
            "coating_property_interpolation_results",
        ],
        "integration_keys": [
            "phase_10c2_coating_thermal_conductivity_integration_owner_applied",
            "coating_thermal_conductivity_source",
        ],
        "affected_keys": [
            "coating_thermal_resistance",
            "explicit_coating_liner_thermal_resistance",
            "hot_gas_side_wall_temperature",
            "wall_temperature_hot_gas",
        ],
    },
    "coating_thermal_resistance": {
        "phase": "10D.5",
        "symbol": "R_coating(T)",
        "input_keys": [
            "coating_thermal_resistance",
            "coating_thickness",
            "coating_thermal_conductivity",
        ],
        "integration_keys": [
            "phase_10c4_coating_thermal_resistance_integration_owner_applied",
            "coating_thermal_resistance_source",
        ],
        "affected_keys": [
            "total_thermal_resistance",
            "explicit_coating_liner_status",
            "wall_temperature_hot_gas",
            "hot_gas_side_wall_temperature",
        ],
    },
    "bond_coat_thermal_conductivity": {
        "phase": "10D.6",
        "symbol": "k_bond(T)",
        "input_keys": [
            "bond_coat_thermal_conductivity",
            "sourced_bond_coat_thermal_conductivity",
            "bond_coat_property_interpolation_results",
        ],
        "integration_keys": [
            "phase_10c6_bond_coat_integration_owner_applied",
            "bond_coat_thermal_conductivity_source",
        ],
        "affected_keys": [
            "bond_coat_thermal_resistance",
            "total_thermal_resistance",
            "wall_temperature_hot_gas",
            "hot_gas_side_wall_temperature",
        ],
    },
}


def attach_temperature_dependency_discovery_audit_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_temperature_dependency_discovery_audit(results)
    results.update(audit)
    return results


def build_temperature_dependency_discovery_audit(results):
    results = results if isinstance(results, dict) else {}

    findings = []
    blockers = []
    next_actions = []

    phase_10c8_complete = bool(
        results.get("phase_10c8_coating_integration_completion_audit_complete")
    )

    for path_name, spec in TEMPERATURE_DEPENDENCY_PATHS.items():
        input_presence = _presence_map(results, spec["input_keys"])
        integration_presence = _presence_map(results, spec["integration_keys"])
        affected_presence = _presence_map(results, spec["affected_keys"])

        sourced_status = _classify_source_status(results, path_name, input_presence)
        integration_status = _classify_integration_status(integration_presence)
        effect_status = _classify_effect_path_status(affected_presence)
        discovery_status = _classify_discovery_status(
            sourced_status=sourced_status,
            integration_status=integration_status,
            effect_status=effect_status,
        )

        finding = {
            "path": path_name,
            "symbol": spec["symbol"],
            "next_phase": spec["phase"],
            "sourced_status": sourced_status,
            "integration_status": integration_status,
            "effect_path_status": effect_status,
            "discovery_status": discovery_status,
            "present_inputs": _present_keys(input_presence),
            "missing_inputs": _missing_keys(input_presence),
            "present_integration_keys": _present_keys(integration_presence),
            "missing_integration_keys": _missing_keys(integration_presence),
            "present_affected_outputs": _present_keys(affected_presence),
            "missing_affected_outputs": _missing_keys(affected_presence),
        }

        findings.append(finding)

        if discovery_status != "DISCOVERED_READY_FOR_CONSUMPTION_TEST":
            blockers.append(f"{path_name}: {discovery_status}")

        next_actions.append(
            f"{spec['phase']}: perturb {spec['symbol']} and prove affected outputs move."
        )

    complete = phase_10c8_complete and bool(findings)

    status = (
        "PASS_PHASE_10D1_TEMPERATURE_DEPENDENCY_DISCOVERY_AUDIT_OWNER"
        if complete
        else "FAIL_PHASE_10D1_TEMPERATURE_DEPENDENCY_DISCOVERY_AUDIT_OWNER"
    )

    text = build_temperature_dependency_discovery_text(
        status=status,
        complete=complete,
        phase_10c8_complete=phase_10c8_complete,
        findings=findings,
        blockers=blockers,
        next_actions=next_actions,
    )

    return {
        "phase_10d1_temperature_dependency_discovery_audit_owner_complete": complete,
        "phase_10d1_temperature_dependency_discovery_audit_owner_status": status,
        "phase_10d1_temperature_dependency_discovery_audit_owner_findings": findings,
        "phase_10d1_temperature_dependency_discovery_audit_owner_blockers": blockers,
        "phase_10d1_temperature_dependency_discovery_audit_owner_actions": next_actions,
        "phase_10d1_temperature_dependency_discovery_audit_owner_text": text,
        "stage_10d_temperature_dependent_solver_audit_started": True,
        "stage_10d_temperature_dependency_discovery_complete": complete,
        "stage_10d_temperature_dependency_discovery_status": status,
    }


def build_temperature_dependency_discovery_text(
        status,
        complete,
        phase_10c8_complete,
        findings,
        blockers,
        next_actions,
):
    lines = []
    lines.append("PHASE 10D.1 — TEMPERATURE DEPENDENCY DISCOVERY AUDIT OWNER")
    lines.append("============================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Audit only; no solver physics values are changed.")
    lines.append("- Discovers material, coolant, coating, and bond-coat temperature-dependent pathways.")
    lines.append("- Prepares 10D.2–10D.6 consumption tests without claiming consumption proof yet.")
    lines.append("")
    lines.append("Prerequisites:")
    lines.append(f"- Phase 10C.8 coating integration completion audit complete: {phase_10c8_complete}")
    lines.append("")
    lines.append("Discovered Pathways:")

    for finding in findings:
        lines.append(
            f"- {finding['path']} | {finding['symbol']} | "
            f"{finding['discovery_status']} | next={finding['next_phase']}"
        )
        lines.append(f"  Source: {finding['sourced_status']}")
        lines.append(f"  Integration evidence: {finding['integration_status']}")
        lines.append(f"  Effect output evidence: {finding['effect_path_status']}")
        lines.append(f"  Present inputs: {', '.join(finding['present_inputs']) or 'None'}")
        lines.append(f"  Present affected outputs: {', '.join(finding['present_affected_outputs']) or 'None'}")

    lines.append("")
    lines.append("Discovery Blockers / Warnings:")
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None at discovery level.")

    lines.append("")
    lines.append("Next Required Actions:")
    for action in next_actions:
        lines.append(f"- {action}")

    lines.append("")
    lines.append("Conclusion:")
    lines.append(
        "10D.1 maps the temperature-dependent dependency graph. It does not prove numerical "
        "consumption; that proof begins in 10D.2 with conductivity perturbation testing."
    )

    return "\n".join(lines)


def _presence_map(results, keys):
    return {key: results.get(key) is not None for key in keys}


def _present_keys(presence):
    return [key for key, present in presence.items() if present]


def _missing_keys(presence):
    return [key for key, present in presence.items() if not present]


def _classify_source_status(results, path_name, input_presence):
    if path_name.startswith("material_"):
        mode = str(
            results.get("material_source_validation_mode")
            or results.get("material_property_interpolation_mode")
            or "UNKNOWN"
        ).upper()
        if mode == "SOURCED_VALIDATION_MODE":
            return "SOURCED_VALIDATION_MODE"
        if mode == "PARTIAL_SOURCE_MODE":
            return "PARTIAL_SOURCE_MODE_BLOCKED_FOR_PASS"
        if mode == "PLACEHOLDER_MODE":
            return "PLACEHOLDER_MODE_BLOCKED_FOR_PASS"
        return "UNKNOWN_OR_UNSOURCED_MATERIAL_MODE"

    if path_name.startswith("coating_"):
        mode = str(
            results.get("coating_source_validation_mode")
            or "UNKNOWN"
        ).upper()
        coating_name = str(results.get("coating_name") or results.get("selected_coating") or "NONE").upper()
        if coating_name in ("NONE", "NO_COATING", "N/A") and mode in ("NONE", "UNKNOWN"):
            return "NO_COATING_SELECTED"
        if mode == "SOURCED_VALIDATION_MODE":
            return "SOURCED_VALIDATION_MODE"
        if mode == "PARTIAL_SOURCE_MODE":
            return "PARTIAL_SOURCE_MODE_BLOCKED_FOR_PASS"
        if mode == "PLACEHOLDER_MODE":
            return "PLACEHOLDER_MODE_BLOCKED_FOR_PASS"
        return "UNKNOWN_OR_UNSOURCED_COATING_MODE"

    if path_name.startswith("bond_coat_"):
        mode = str(results.get("bond_coat_source_validation_mode") or "UNKNOWN").upper()
        bond_name = str(results.get("bond_coat_name") or results.get("selected_bond_coat") or "NONE").upper()
        if bond_name in ("NONE", "NO_BOND_COAT", "N/A") and mode in ("NONE", "UNKNOWN"):
            return "NO_BOND_COAT_SELECTED"
        if mode == "SOURCED_VALIDATION_MODE":
            return "SOURCED_VALIDATION_MODE"
        if mode == "PARTIAL_SOURCE_MODE":
            return "PARTIAL_SOURCE_MODE_BLOCKED_FOR_PASS"
        if mode == "PLACEHOLDER_MODE":
            return "PLACEHOLDER_MODE_BLOCKED_FOR_PASS"
        return "UNKNOWN_OR_UNSOURCED_BOND_COAT_MODE"

    if any(input_presence.values()):
        return "PRESENT_SOURCE_NOT_YET_CLASSIFIED"

    return "MISSING_SOURCE_PATH"


def _classify_integration_status(integration_presence):
    if any(integration_presence.values()):
        return "INTEGRATION_EVIDENCE_PRESENT"
    return "NO_INTEGRATION_EVIDENCE_FOUND"


def _classify_effect_path_status(affected_presence):
    if any(affected_presence.values()):
        return "AFFECTED_OUTPUT_PATH_PRESENT"
    return "NO_AFFECTED_OUTPUT_PATH_FOUND"


def _classify_discovery_status(sourced_status, integration_status, effect_status):
    if sourced_status in (
        "PLACEHOLDER_MODE_BLOCKED_FOR_PASS",
        "PARTIAL_SOURCE_MODE_BLOCKED_FOR_PASS",
    ):
        return "DISCOVERED_BUT_CONSERVATIVELY_BLOCKED"

    if sourced_status in ("NO_COATING_SELECTED", "NO_BOND_COAT_SELECTED"):
        return "OPTIONAL_LAYER_NOT_SELECTED"

    if integration_status != "INTEGRATION_EVIDENCE_PRESENT":
        return "DISCOVERED_MISSING_INTEGRATION_EVIDENCE"

    if effect_status != "AFFECTED_OUTPUT_PATH_PRESENT":
        return "DISCOVERED_MISSING_EFFECT_OUTPUT_EVIDENCE"

    return "DISCOVERED_READY_FOR_CONSUMPTION_TEST"