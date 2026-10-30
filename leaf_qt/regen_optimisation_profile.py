"""
LEAF Regen Optimisation Profile Foundation
==========================================

REGEN PHASE 8A

This module owns the optimisation profile foundation only.

It does NOT:
- generate candidates
- score candidates
- rank candidates
- automatically select geometry
- approve recommendations
- replace validation gates
"""

DEFAULT_REGEN_OPTIMISATION_OBJECTIVES = (
    "minimise_hot_gas_wall_temperature",
    "maintain_coolant_pressure_drop_margin",
    "maintain_channel_fit",
    "maintain_manufacturability_margin",
)

DEFAULT_REGEN_OPTIMISATION_CONSTRAINTS = (
    "stage_u_regen_validation_complete",
    "stage_v_scalability_complete",
    "stage_w_real_engine_benchmarking_complete",
    "regen_geometry_valid",
    "regen_coolant_velocity_minimum",
    "regen_pressure_drop_maximum",
    "material_temperature_margin_positive",
    "source_validation_not_placeholder",
)

CANDIDATE_METADATA_SCHEMA = {
    "candidate_id": "Stable candidate identifier. Not generated in Phase 8A.",
    "source": "manual | generated | imported. Generation starts after Phase 8A.",
    "geometry_inputs": "Channel count, width, height, rib width, wall thickness, coating state.",
    "validation_snapshot": "Validation evidence copied from the evaluated design.",
    "objective_snapshot": "Objective values copied from the evaluated design.",
    "selection_allowed": "False in Phase 8A. Later phases may unlock this through gates.",
}


def attach_regen_optimisation_profile(results):
    if not isinstance(results, dict):
        return results

    profile = build_regen_optimisation_profile(results)
    results.update(profile)
    return results


def build_regen_optimisation_profile(results):
    results = results if isinstance(results, dict) else {}

    enabled = _bool_value(
        results.get("regen_optimisation_enabled"),
        default=False,
    )

    intent = _normalise_text(
        results.get("regen_optimisation_intent"),
        default="DEFINE_PROFILE_ONLY",
    )

    objectives = _normalise_sequence(
        results.get("regen_optimisation_requested_objectives"),
        DEFAULT_REGEN_OPTIMISATION_OBJECTIVES,
    )

    constraints = _normalise_sequence(
        results.get("regen_optimisation_requested_constraints"),
        DEFAULT_REGEN_OPTIMISATION_CONSTRAINTS,
    )

    upstream_status = build_upstream_status_snapshot(results)
    blocking_reasons = build_phase_8a_blocking_reasons(results, enabled)

    profile_complete = bool(objectives and constraints and CANDIDATE_METADATA_SCHEMA)

    status = (
        "PASS_REGEN_OPTIMISATION_PROFILE"
        if profile_complete
        else "FAIL_REGEN_OPTIMISATION_PROFILE"
    )

    candidate_generation_allowed = False
    candidate_scoring_allowed = False
    automatic_selection_allowed = False

    text = build_regen_optimisation_profile_text(
        status=status,
        profile_complete=profile_complete,
        enabled=enabled,
        intent=intent,
        objectives=objectives,
        constraints=constraints,
        upstream_status=upstream_status,
        blocking_reasons=blocking_reasons,
        candidate_generation_allowed=candidate_generation_allowed,
        candidate_scoring_allowed=candidate_scoring_allowed,
        automatic_selection_allowed=automatic_selection_allowed,
    )

    return {
        "regen_optimisation_profile_status": status,
        "regen_optimisation_profile_complete": profile_complete,
        "regen_optimisation_profile_enabled": enabled,
        "regen_optimisation_profile_intent": intent,
        "regen_optimisation_profile_objectives": objectives,
        "regen_optimisation_profile_constraints": constraints,
        "regen_optimisation_profile_candidate_metadata_schema": dict(CANDIDATE_METADATA_SCHEMA),
        "regen_optimisation_profile_upstream_status": upstream_status,
        "regen_optimisation_profile_blocking_reasons": blocking_reasons,
        "regen_optimisation_profile_candidate_generation_allowed": candidate_generation_allowed,
        "regen_optimisation_profile_candidate_scoring_allowed": candidate_scoring_allowed,
        "regen_optimisation_profile_automatic_selection_allowed": automatic_selection_allowed,
        "regen_optimisation_profile_text": text,
        "phase_8a_regen_optimisation_profile_complete": profile_complete,
    }


def build_upstream_status_snapshot(results):
    results = results if isinstance(results, dict) else {}

    return {
        "stage_u_regen_validation_complete": bool(
            results.get("stage_u_regen_validation_complete", False)
        ),
        "stage_v_scalability_complete": bool(
            results.get("stage_v_scalability_complete")
            or results.get("stage_v_complete")
            or False
        ),
        "stage_w_real_engine_benchmarking_complete": bool(
            results.get("stage_w_real_engine_benchmarking_complete")
            or results.get("stage_w_complete")
            or False
        ),
        "regen_validation_master_gate_status": results.get(
            "regen_validation_master_gate_status",
            "UNKNOWN",
        ),
        "regen_scalability_master_gate_status": results.get(
            "regen_scalability_master_gate_status",
            "UNKNOWN",
        ),
        "real_engine_benchmark_master_gate_status": results.get(
            "real_engine_benchmark_master_gate_status",
            "UNKNOWN",
        ),
    }


def build_phase_8a_blocking_reasons(results, enabled):
    results = results if isinstance(results, dict) else {}

    blocking = []

    if enabled:
        blocking.append(
            "Automatic optimisation is not permitted in Phase 8A; this phase only defines the optimisation profile."
        )

    if results.get("regen_optimisation_candidate_generation_requested"):
        blocking.append(
            "Candidate generation was requested, but this belongs to Phase 8B."
        )

    if results.get("regen_optimisation_scoring_requested"):
        blocking.append(
            "Candidate scoring was requested, but this belongs to Phase 8C."
        )

    if results.get("regen_optimisation_auto_select_requested"):
        blocking.append(
            "Automatic geometry selection was requested, but this is blocked until later optimisation gates exist."
        )

    return blocking


def build_regen_optimisation_profile_text(
        status,
        profile_complete,
        enabled,
        intent,
        objectives,
        constraints,
        upstream_status,
        blocking_reasons,
        candidate_generation_allowed,
        candidate_scoring_allowed,
        automatic_selection_allowed,
):
    lines = [
        "LEAF REGEN PHASE 8A OPTIMISATION PROFILE FOUNDATION",
        "======================================================",
        "",
        f"Status: {status}",
        f"Profile complete: {profile_complete}",
        f"Optimisation enabled: {enabled}",
        f"Intent: {intent}",
        "",
        "Owned By:",
        "- regen_optimisation_profile.py",
        "",
        "Scope:",
        "- Owns optimisation intent/profile metadata.",
        "- Owns objective declarations.",
        "- Owns constraint declarations.",
        "- Owns candidate metadata schema declaration.",
        "- Does not generate candidates.",
        "- Does not score candidates.",
        "- Does not rank candidates.",
        "- Does not automatically select geometry.",
        "- Does not approve recommendations.",
        "",
        "Phase Locks:",
        f"- Candidate generation allowed: {candidate_generation_allowed}",
        f"- Candidate scoring allowed: {candidate_scoring_allowed}",
        f"- Automatic selection allowed: {automatic_selection_allowed}",
        "",
        "Objectives:",
    ]

    if objectives:
        for objective in objectives:
            lines.append(f"- {objective}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Constraints:")

    if constraints:
        for constraint in constraints:
            lines.append(f"- {constraint}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Candidate Metadata Schema:")

    for key, description in CANDIDATE_METADATA_SCHEMA.items():
        lines.append(f"- {key}: {description}")

    lines.append("")
    lines.append("Upstream Status Snapshot:")

    for key, value in upstream_status.items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("Blocking Reasons:")

    if blocking_reasons:
        for item in blocking_reasons:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Next Required Action:")
    lines.append(
        "- After Phase 8A is verified, build Phase 8B candidate generation without enabling automatic selection."
    )

    return "\n".join(lines)


def _bool_value(value, default=False):
    if value is None:
        return bool(default)

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value_l = value.strip().lower()

        if value_l in {"true", "1", "yes", "y", "enabled", "on"}:
            return True

        if value_l in {"false", "0", "no", "n", "disabled", "off"}:
            return False

    return bool(value)


def _normalise_text(value, default=""):
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _normalise_sequence(value, default):
    if value is None:
        return list(default)

    if isinstance(value, str):
        cleaned = [
            part.strip()
            for part in value.split(",")
            if part.strip()
        ]
        return cleaned or list(default)

    if isinstance(value, (list, tuple, set)):
        cleaned = [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]
        return cleaned or list(default)

    return list(default)