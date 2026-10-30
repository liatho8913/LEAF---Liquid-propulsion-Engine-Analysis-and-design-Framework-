"""
PHASE 10D.7
Temperature-Dependent Solver Completion Audit Owner

Purpose:
    Final master gate for Phase 10D.

Rules:
    - Audit only.
    - Does not alter solver physics.
    - Passes only when all required 10D owners are complete and passing.
    - Fails conservatively if any 10D owner is missing, incomplete, or failed.
"""


REQUIRED_10D_PHASES = {
    "10D.1 Temperature Dependency Discovery": {
        "complete_key": "phase_10d1_temperature_dependency_discovery_audit_owner_complete",
        "status_key": "phase_10d1_temperature_dependency_discovery_audit_owner_status",
        "pass_status": "PASS_PHASE_10D1_TEMPERATURE_DEPENDENCY_DISCOVERY_AUDIT_OWNER",
    },
    "10D.2 Material Conductivity Consumption": {
        "complete_key": "phase_10d2_material_conductivity_consumption_audit_owner_complete",
        "status_key": "phase_10d2_material_conductivity_consumption_audit_owner_status",
        "pass_status": "PASS_PHASE_10D2_MATERIAL_CONDUCTIVITY_CONSUMPTION_AUDIT_OWNER",
    },
    "10D.3 Specific Heat Consumption": {
        "complete_key": "phase_10d3_specific_heat_consumption_audit_owner_complete",
        "status_key": "phase_10d3_specific_heat_consumption_audit_owner_status",
        "pass_status": "PASS_PHASE_10D3_SPECIFIC_HEAT_CONSUMPTION_AUDIT_OWNER",
    },
    "10D.4 Density/Coolant Property Consumption": {
        "complete_key": "phase_10d4_density_coolant_property_consumption_audit_owner_complete",
        "status_key": "phase_10d4_density_coolant_property_consumption_audit_owner_status",
        "pass_status": "PASS_PHASE_10D4_DENSITY_COOLANT_PROPERTY_CONSUMPTION_AUDIT_OWNER",
    },
    "10D.5 Coating Thermal Consumption": {
        "complete_key": "phase_10d5_coating_thermal_consumption_audit_owner_complete",
        "status_key": "phase_10d5_coating_thermal_consumption_audit_owner_status",
        "pass_status": "PASS_PHASE_10D5_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER",
    },
    "10D.6 Bond-Coat Consumption": {
        "complete_key": "phase_10d6_bond_coat_consumption_audit_owner_complete",
        "status_key": "phase_10d6_bond_coat_consumption_audit_owner_status",
        "pass_status": "PASS_PHASE_10D6_BOND_COAT_CONSUMPTION_AUDIT_OWNER",
    },
}


def attach_temperature_dependent_solver_completion_audit_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_temperature_dependent_solver_completion_audit(results)
    results.update(audit)
    return results


def build_temperature_dependent_solver_completion_audit(results):
    results = results if isinstance(results, dict) else {}

    phase_findings = []
    blockers = []

    for phase_name, spec in REQUIRED_10D_PHASES.items():
        complete = bool(results.get(spec["complete_key"]))
        status = results.get(spec["status_key"])
        expected = spec["pass_status"]
        passed = complete and status == expected

        finding = {
            "phase": phase_name,
            "complete_key": spec["complete_key"],
            "status_key": spec["status_key"],
            "complete": complete,
            "status": status,
            "expected_status": expected,
            "passed": passed,
        }

        phase_findings.append(finding)

        if not passed:
            blockers.append(
                f"{phase_name}: complete={complete}; status={status}; expected={expected}"
            )

    result_key_status = results.get("foundation_result_key_audit_status")
    result_key_pass = result_key_status in (None, "PASS")

    if not result_key_pass:
        blockers.append(f"Result key audit is not passing: {result_key_status}")

    report_bundle_status = results.get("foundation_report_bundle_status")
    if report_bundle_status not in (None, "PASS"):
        blockers.append(f"Report bundle status is not passing: {report_bundle_status}")

    completion_pass = not blockers

    status = (
        "PASS_PHASE_10D7_TEMPERATURE_DEPENDENT_SOLVER_COMPLETION_AUDIT_OWNER"
        if completion_pass
        else "FAIL_PHASE_10D7_TEMPERATURE_DEPENDENT_SOLVER_COMPLETION_AUDIT_OWNER"
    )

    text = build_temperature_dependent_solver_completion_audit_text(
        status=status,
        phase_findings=phase_findings,
        blockers=blockers,
        result_key_status=result_key_status,
        report_bundle_status=report_bundle_status,
    )

    return {
        "phase_10d7_temperature_dependent_solver_completion_audit_owner_complete": True,
        "phase_10d7_temperature_dependent_solver_completion_audit_owner_status": status,
        "phase_10d7_temperature_dependent_solver_completion_audit_owner_pass": completion_pass,
        "phase_10d7_temperature_dependent_solver_completion_audit_owner_findings": phase_findings,
        "phase_10d7_temperature_dependent_solver_completion_audit_owner_blockers": blockers,
        "phase_10d7_temperature_dependent_solver_completion_audit_owner_text": text,
        "stage_10d_temperature_dependent_solver_completion_complete": completion_pass,
        "stage_10d_temperature_dependent_solver_completion_status": status,
        "stage_10d_temperature_dependent_solver_framework_complete": completion_pass,
    }


def build_temperature_dependent_solver_completion_audit_text(
        status,
        phase_findings,
        blockers,
        result_key_status,
        report_bundle_status,
):
    lines = []
    lines.append("PHASE 10D.7 — TEMPERATURE-DEPENDENT SOLVER COMPLETION AUDIT")
    lines.append("===========================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append("")
    lines.append("Purpose:")
    lines.append("- Final master gate for the complete Phase 10D temperature-dependent solver framework.")
    lines.append("- Confirms 10D.1 through 10D.6 are complete and passing together.")
    lines.append("")
    lines.append("Phase Findings:")

    for finding in phase_findings:
        lines.append(
            f"- {finding['phase']}: "
            f"complete={finding['complete']}; "
            f"status={finding['status']}; "
            f"expected={finding['expected_status']}; "
            f"passed={finding['passed']}"
        )

    lines.append("")
    lines.append("Ownership Hygiene:")
    lines.append(f"- foundation_result_key_audit_status: {result_key_status}")
    lines.append(f"- foundation_report_bundle_status: {report_bundle_status}")
    lines.append("")
    lines.append("Blockers:")

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Conclusion:")
    lines.append(
        "PASS means the full 10D temperature-dependent solver framework is complete, "
        "owned, reported, and ready to support Regen Geometry Completion Phase 1."
    )

    return "\n".join(lines)