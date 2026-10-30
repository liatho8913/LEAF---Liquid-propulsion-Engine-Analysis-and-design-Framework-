"""
LEAF Material Completion Audit
==============================

REGEN PHASE 9E

Final architectural signoff for the material foundation stack.

This module audits:
- Phase 9A material property interpolation owner
- Phase 9B material source/provenance owner
- Phase 9C material source quality ranking owner
- Phase 9D material validation owner

It does NOT:
- validate coatings
- replace solver constants
- apply material changes automatically
"""

REQUIRED_MATERIAL_PHASE_KEYS = {
    "phase_9a_material_property_interpolation_owner_complete": "Material Property Interpolation Owner",
    "phase_9b_material_source_provenance_owner_complete": "Material Source / Provenance Owner",
    "phase_9c_material_source_quality_ranking_owner_complete": "Material Source Quality Ranking Owner",
    "phase_9d_material_validation_owner_complete": "Material Validation Owner",
}


def attach_material_completion_audit(results):
    if not isinstance(results, dict):
        return results

    audit = build_material_completion_audit(results)
    results.update(audit)
    return results


def build_material_completion_audit(results):
    results = results if isinstance(results, dict) else {}

    phase_status = {
        key: bool(results.get(key, False))
        for key in REQUIRED_MATERIAL_PHASE_KEYS
    }

    missing_phases = [
        label
        for key, label in REQUIRED_MATERIAL_PHASE_KEYS.items()
        if not phase_status[key]
    ]

    interpolation_status = results.get(
        "material_property_interpolation_owner_status",
        "UNKNOWN",
    )

    provenance_status = results.get(
        "material_source_provenance_owner_status",
        "UNKNOWN",
    )

    ranking_status = results.get(
        "material_source_quality_ranking_owner_status",
        "UNKNOWN",
    )

    validation_status = results.get(
        "material_validation_owner_status",
        "UNKNOWN",
    )

    material_validation_pass = bool(
        results.get("material_validation_pass", False)
    )

    conservative_pass_allowed = bool(
        results.get("material_validation_pass", False)
    )

    completion_blockers = []

    if missing_phases:
        completion_blockers.append(
            "Missing material phases: " + ", ".join(missing_phases)
        )

    for label, status in (
        ("interpolation", interpolation_status),
        ("provenance", provenance_status),
        ("source ranking", ranking_status),
        ("material validation", validation_status),
    ):
        if not str(status).startswith(("PASS", "FAIL")):
            completion_blockers.append(
                f"Material {label} status is missing or unknown."
            )

    if not material_validation_pass:
        completion_blockers.append(
            "Material validation is not passing; material foundation cannot sign off as sourced-valid."
        )

    complete = not completion_blockers

    status = (
        "PASS_MATERIAL_COMPLETION_AUDIT"
        if complete
        else "FAIL_MATERIAL_COMPLETION_AUDIT"
    )

    text = build_material_completion_audit_text(
        status=status,
        complete=complete,
        phase_status=phase_status,
        missing_phases=missing_phases,
        interpolation_status=interpolation_status,
        provenance_status=provenance_status,
        ranking_status=ranking_status,
        validation_status=validation_status,
        material_validation_pass=material_validation_pass,
        conservative_pass_allowed=conservative_pass_allowed,
        completion_blockers=completion_blockers,
    )

    return {
        "material_completion_audit_status": status,
        "material_completion_audit_complete": complete,
        "material_completion_audit_phase_status": phase_status,
        "material_completion_audit_missing_phases": missing_phases,
        "material_completion_audit_blockers": completion_blockers,
        "material_completion_audit_interpolation_status": interpolation_status,
        "material_completion_audit_provenance_status": provenance_status,
        "material_completion_audit_ranking_status": ranking_status,
        "material_completion_audit_validation_status": validation_status,
        "material_completion_audit_validation_pass": material_validation_pass,
        "material_completion_audit_conservative_pass_allowed": conservative_pass_allowed,
        "material_completion_audit_text": text,
        "phase_9e_material_completion_audit_complete": complete,
        "stage_9_material_foundation_complete": complete,
    }


def build_material_completion_audit_text(
        status,
        complete,
        phase_status,
        missing_phases,
        interpolation_status,
        provenance_status,
        ranking_status,
        validation_status,
        material_validation_pass,
        conservative_pass_allowed,
        completion_blockers,
):
    lines = [
        "LEAF REGEN PHASE 9E MATERIAL COMPLETION AUDIT",
        "==============================================",
        "",
        f"Status: {status}",
        f"Material foundation complete: {complete}",
        f"Material validation pass: {material_validation_pass}",
        f"Conservative pass allowed: {conservative_pass_allowed}",
        "",
        "Owned By:",
        "- material_completion_audit.py",
        "",
        "Scope:",
        "- Audits material interpolation ownership.",
        "- Audits material provenance ownership.",
        "- Audits material source ranking ownership.",
        "- Audits material validation ownership.",
        "- Does not validate coatings.",
        "- Does not replace solver constants.",
        "",
        "Phase Status:",
    ]

    for key, value in phase_status.items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        f"Interpolation status: {interpolation_status}",
        f"Provenance status: {provenance_status}",
        f"Source ranking status: {ranking_status}",
        f"Material validation status: {validation_status}",
        "",
        "Missing Phases:",
    ])

    if missing_phases:
        for phase in missing_phases:
            lines.append(f"- {phase}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Completion Blockers:")

    if completion_blockers:
        for blocker in completion_blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Next Required Action:")
    lines.append(
        "- After Phase 9E is verified, build Phase 9F coating source/provenance ownership."
    )

    return "\n".join(lines)