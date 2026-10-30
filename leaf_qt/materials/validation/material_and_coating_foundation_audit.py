"""
LEAF Material & Coating Foundation Audit
========================================

REGEN PHASE 9H

Final architectural signoff for material + coating foundation ownership.

This module audits:
- 9A material interpolation
- 9B material provenance
- 9C material source ranking
- 9D material validation
- 9E material completion audit
- 9F coating provenance
- 9G coating validation

It does NOT:
- replace solver constants
- modify materials automatically
- modify coatings automatically
"""

REQUIRED_FOUNDATION_PHASES = {
    "phase_9a_material_property_interpolation_owner_complete": "9A Material Property Interpolation Owner",
    "phase_9b_material_source_provenance_owner_complete": "9B Material Source / Provenance Owner",
    "phase_9c_material_source_quality_ranking_owner_complete": "9C Material Source Quality Ranking Owner",
    "phase_9d_material_validation_owner_complete": "9D Material Validation Owner",
    "phase_9e_material_completion_audit_complete": "9E Material Completion Audit",
    "phase_9f_coating_source_provenance_owner_complete": "9F Coating Source / Provenance Owner",
    "phase_9g_coating_validation_owner_complete": "9G Coating Validation Owner",
}


def attach_material_and_coating_foundation_audit(results):
    if not isinstance(results, dict):
        return results

    audit = build_material_and_coating_foundation_audit(results)
    results.update(audit)
    return results


def build_material_and_coating_foundation_audit(results):
    results = results if isinstance(results, dict) else {}

    phase_status = {
        key: bool(results.get(key, False))
        for key in REQUIRED_FOUNDATION_PHASES
    }

    missing_phases = [
        label
        for key, label in REQUIRED_FOUNDATION_PHASES.items()
        if not phase_status[key]
    ]

    material_completion_status = results.get(
        "material_completion_audit_status",
        "UNKNOWN",
    )

    material_validation_status = results.get(
        "material_validation_owner_status",
        "UNKNOWN",
    )

    coating_provenance_status = results.get(
        "coating_source_provenance_owner_status",
        "UNKNOWN",
    )

    coating_validation_status = results.get(
        "coating_validation_owner_status",
        "UNKNOWN",
    )

    material_validation_pass = bool(
        results.get("material_validation_pass", False)
    )

    coating_validation_pass = bool(
        results.get("coating_validation_pass", False)
    )

    material_foundation_complete = bool(
        results.get("stage_9_material_foundation_complete", False)
    )

    audit_blockers = []

    if missing_phases:
        audit_blockers.append(
            "Missing material/coating phases: " + ", ".join(missing_phases)
        )

    for label, status in (
        ("material completion audit", material_completion_status),
        ("material validation", material_validation_status),
        ("coating provenance", coating_provenance_status),
        ("coating validation", coating_validation_status),
    ):
        if not str(status).startswith(("PASS", "FAIL")):
            audit_blockers.append(
                f"{label} status is missing or unknown."
            )

    if not material_foundation_complete:
        audit_blockers.append(
            "Material foundation completion audit is not passing."
        )

    if not material_validation_pass:
        audit_blockers.append(
            "Material validation is not passing."
        )

    if not coating_validation_pass:
        audit_blockers.append(
            "Coating validation is not passing."
        )

    complete = not audit_blockers

    status = (
        "PASS_MATERIAL_AND_COATING_FOUNDATION_AUDIT"
        if complete
        else "FAIL_MATERIAL_AND_COATING_FOUNDATION_AUDIT"
    )

    text = build_material_and_coating_foundation_audit_text(
        status=status,
        complete=complete,
        phase_status=phase_status,
        missing_phases=missing_phases,
        material_completion_status=material_completion_status,
        material_validation_status=material_validation_status,
        coating_provenance_status=coating_provenance_status,
        coating_validation_status=coating_validation_status,
        material_validation_pass=material_validation_pass,
        coating_validation_pass=coating_validation_pass,
        material_foundation_complete=material_foundation_complete,
        audit_blockers=audit_blockers,
    )

    return {
        "material_and_coating_foundation_audit_status": status,
        "material_and_coating_foundation_audit_complete": complete,
        "material_and_coating_foundation_audit_phase_status": phase_status,
        "material_and_coating_foundation_audit_missing_phases": missing_phases,
        "material_and_coating_foundation_audit_blockers": audit_blockers,
        "material_and_coating_foundation_audit_material_completion_status": material_completion_status,
        "material_and_coating_foundation_audit_material_validation_status": material_validation_status,
        "material_and_coating_foundation_audit_coating_provenance_status": coating_provenance_status,
        "material_and_coating_foundation_audit_coating_validation_status": coating_validation_status,
        "material_and_coating_foundation_audit_material_validation_pass": material_validation_pass,
        "material_and_coating_foundation_audit_coating_validation_pass": coating_validation_pass,
        "material_and_coating_foundation_audit_material_foundation_complete": material_foundation_complete,
        "material_and_coating_foundation_audit_text": text,
        "phase_9h_material_and_coating_foundation_audit_complete": complete,
        "stage_9_material_and_coating_foundation_complete": complete,
    }


def build_material_and_coating_foundation_audit_text(
        status,
        complete,
        phase_status,
        missing_phases,
        material_completion_status,
        material_validation_status,
        coating_provenance_status,
        coating_validation_status,
        material_validation_pass,
        coating_validation_pass,
        material_foundation_complete,
        audit_blockers,
):
    lines = [
        "LEAF REGEN PHASE 9H MATERIAL & COATING FOUNDATION AUDIT",
        "========================================================",
        "",
        f"Status: {status}",
        f"Material & coating foundation complete: {complete}",
        f"Material foundation complete: {material_foundation_complete}",
        f"Material validation pass: {material_validation_pass}",
        f"Coating validation pass: {coating_validation_pass}",
        "",
        "Owned By:",
        "- material_and_coating_foundation_audit.py",
        "",
        "Scope:",
        "- Audits material interpolation ownership.",
        "- Audits material provenance ownership.",
        "- Audits material source ranking ownership.",
        "- Audits material validation ownership.",
        "- Audits material completion ownership.",
        "- Audits coating provenance ownership.",
        "- Audits coating validation ownership.",
        "- Does not replace solver constants.",
        "- Does not modify material/coating selections automatically.",
        "",
        "Phase Status:",
    ]

    for key, value in phase_status.items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        f"Material completion status: {material_completion_status}",
        f"Material validation status: {material_validation_status}",
        f"Coating provenance status: {coating_provenance_status}",
        f"Coating validation status: {coating_validation_status}",
        "",
        "Missing Phases:",
    ])

    if missing_phases:
        for phase in missing_phases:
            lines.append(f"- {phase}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Audit Blockers:")

    if audit_blockers:
        for blocker in audit_blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Next Required Action:")
    lines.append(
        "- After Phase 9H is verified, begin regen solver integration planning for sourced material/coating data."
    )

    return "\n".join(lines)