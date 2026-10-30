"""
LEAF Regen Candidate Generator
==============================

PHASE 11B.1A

Generates non-destructive full-engine regen candidate geometries.

This module DOES:
- create candidate geometry input sets
- preserve the original manual geometry
- store candidate reasons and changes
- expose candidates for later validation/ranking

This module DOES NOT:
- validate candidates as passing
- apply candidates to the engine
- select the best candidate
- override material/coating gates
"""

import copy
import math


DEFAULT_CHANNEL_COUNT_MULTIPLIERS = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
DEFAULT_WIDTH_MULTIPLIERS = [0.6, 0.8, 1.0, 1.2, 1.5]
DEFAULT_HEIGHT_MULTIPLIERS = [0.75, 1.0, 1.25, 1.5, 2.0]
DEFAULT_RIB_MULTIPLIERS = [0.5, 0.75, 1.0, 1.25]
DEFAULT_WALL_MULTIPLIERS = [1.0, 1.25, 1.5, 2.0]


def attach_regen_candidate_generator(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_generator(results)
    results.update(payload)
    return results


def build_regen_candidate_generator(results):
    results = results if isinstance(results, dict) else {}

    enabled = _bool_value(
        results.get("regen_candidate_generator_enabled"),
        default=True,
    )

    blocking_reasons = []

    base_geometry = _extract_base_geometry(results)

    if not enabled:
        blocking_reasons.append("Candidate generator disabled.")

    if not base_geometry["base_geometry_complete"]:
        blocking_reasons.append("Base regen geometry is incomplete.")

    candidates = []

    if enabled and base_geometry["base_geometry_complete"]:
        candidates = _generate_candidates(results, base_geometry)

    status = _build_status(
        enabled=enabled,
        base_geometry_complete=base_geometry["base_geometry_complete"],
        candidates=candidates,
        blocking_reasons=blocking_reasons,
    )

    text = build_regen_candidate_generator_text(
        status=status,
        enabled=enabled,
        base_geometry=base_geometry,
        candidates=candidates,
        blocking_reasons=blocking_reasons,
    )

    return {
        "regen_candidate_generator_status": status,
        "regen_candidate_generator_complete": True,
        "regen_candidate_generator_enabled": enabled,
        "regen_candidate_generator_base_geometry": base_geometry,
        "regen_candidate_generator_candidates": candidates,
        "regen_candidate_generator_candidate_count": len(candidates),
        "regen_candidate_generator_blocking_reasons": blocking_reasons,
        "regen_candidate_generator_text": text,

        # Conservative phase locks.
        "regen_candidate_generator_validation_allowed": False,
        "regen_candidate_generator_automatic_selection_allowed": False,
        "regen_candidate_generator_geometry_application_allowed": False,

        # Handover/roadmap status flag.
        "phase_11b_1a_regen_candidate_generator_complete": True,
    }


def build_regen_candidate_generator_text(
        status,
        enabled,
        base_geometry,
        candidates,
        blocking_reasons,
):
    lines = [
        "LEAF PHASE 11B.1A REGEN CANDIDATE GENERATOR",
        "============================================",
        "",
        f"Status: {status}",
        f"Enabled: {enabled}",
        f"Base geometry complete: {base_geometry.get('base_geometry_complete')}",
        f"Generated candidate count: {len(candidates)}",
        "",
        "Owned By:",
        "- regen_candidate_generator.py",
        "",
        "Scope:",
        "- Generates non-destructive full-engine regen candidate geometries.",
        "- Preserves the original manual/recommended geometry.",
        "- Stores candidate inputs, changes, reasons, and preview metrics.",
        "- Does not validate candidates as passing.",
        "- Does not select or apply geometry.",
        "",
        "Phase Locks:",
        "- Validation allowed: False",
        "- Automatic selection allowed: False",
        "- Geometry application allowed: False",
        "",
        "Blocking Reasons:",
    ]

    if blocking_reasons:
        for reason in blocking_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Generated Candidates:",
    ])

    if not candidates:
        lines.append("- None.")
    else:
        for candidate in candidates[:25]:
            lines.append(
                f"- {candidate.get('candidate_id')}: "
                f"N={candidate.get('inputs', {}).get('number_of_coolant_channels')}, "
                f"w={candidate.get('inputs', {}).get('coolant_channel_width')}, "
                f"h={candidate.get('inputs', {}).get('coolant_channel_height')}, "
                f"rib={candidate.get('inputs', {}).get('rib_width')}, "
                f"score={candidate.get('preview_score')}"
            )

        if len(candidates) > 25:
            lines.append(f"- ... {len(candidates) - 25} additional candidates hidden.")

    return "\n".join(lines)


def _extract_base_geometry(results):
    channel_count = _first_number(
        results,
        [
            "number_of_coolant_channels",
            "coolant_channel_count",
            "recommended_number_of_coolant_channels",
            "recommended_channel_count",
        ],
    )

    channel_width = _first_number(
        results,
        [
            "coolant_channel_width",
            "recommended_coolant_channel_width",
            "recommended_channel_width",
        ],
    )

    channel_height = _first_number(
        results,
        [
            "coolant_channel_height",
            "recommended_coolant_channel_height",
            "recommended_channel_height",
        ],
    )

    rib_width = _first_number(
        results,
        [
            "rib_width",
            "recommended_rib_width",
            "regen_rib_width",
        ],
    )

    wall_thickness = _first_number(
        results,
        [
            "hot_gas_wall_thickness",
            "regen_wall_thickness",
            "minimum_hot_gas_wall_thickness",
            "recommended_hot_gas_wall_thickness",
        ],
    )

    coolant_fraction = _first_number(
        results,
        [
            "coolant_mass_flow_fraction",
            "regen_coolant_fraction",
            "coolant_fraction",
        ],
    )

    channel_mid_radius = _first_number(
        results,
        [
            "channel_mid_radius",
            "throat_channel_mid_radius",
            "minimum_channel_mid_radius",
        ],
    )

    coolant_density = _first_number(
        results,
        [
            "coolant_density",
            "regen_coolant_density",
        ],
    )

    coolant_viscosity = _first_number(
        results,
        [
            "coolant_dynamic_viscosity",
            "regen_coolant_dynamic_viscosity",
        ],
    )

    coolant_mass_flow = _first_number(
        results,
        [
            "coolant_mass_flow_rate",
            "fuel_mass_flow_rate",
        ],
    )

    complete = all(
        value is not None and value > 0
        for value in [
            channel_count,
            channel_width,
            channel_height,
            rib_width,
            wall_thickness,
        ]
    )

    return {
        "base_geometry_complete": complete,
        "number_of_coolant_channels": int(channel_count) if channel_count else None,
        "coolant_channel_width": channel_width,
        "coolant_channel_height": channel_height,
        "rib_width": rib_width,
        "hot_gas_wall_thickness": wall_thickness,
        "coolant_mass_flow_fraction": coolant_fraction,
        "channel_mid_radius": channel_mid_radius,
        "coolant_density": coolant_density,
        "coolant_dynamic_viscosity": coolant_viscosity,
        "coolant_mass_flow_rate": coolant_mass_flow,
    }


def _generate_candidates(results, base_geometry):
    raw_candidates = []

    base_count = int(base_geometry["number_of_coolant_channels"])
    base_width = float(base_geometry["coolant_channel_width"])
    base_height = float(base_geometry["coolant_channel_height"])
    base_rib = float(base_geometry["rib_width"])
    base_wall = float(base_geometry["hot_gas_wall_thickness"])

    min_count = int(results.get("regen_min_channel_count") or 12)
    max_count = int(results.get("regen_max_channel_count") or 240)

    candidate_id = 1

    for count_multiplier in DEFAULT_CHANNEL_COUNT_MULTIPLIERS:
        for width_multiplier in DEFAULT_WIDTH_MULTIPLIERS:
            for height_multiplier in DEFAULT_HEIGHT_MULTIPLIERS:
                for rib_multiplier in DEFAULT_RIB_MULTIPLIERS:
                    for wall_multiplier in DEFAULT_WALL_MULTIPLIERS:

                        channel_count = int(round(base_count * count_multiplier))
                        channel_count = max(min_count, min(channel_count, max_count))

                        channel_width = base_width * width_multiplier
                        channel_height = base_height * height_multiplier
                        rib_width = base_rib * rib_multiplier
                        wall_thickness = base_wall * wall_multiplier

                        if channel_width <= 0 or channel_height <= 0 or rib_width <= 0:
                            continue

                        preview = _preview_candidate(
                            results=results,
                            base_geometry=base_geometry,
                            channel_count=channel_count,
                            channel_width=channel_width,
                            channel_height=channel_height,
                            rib_width=rib_width,
                        )

                        candidate = {
                            "candidate_id": f"RCG-{candidate_id:04d}",
                            "candidate_source": "regen_candidate_generator.py",
                            "candidate_phase": "PHASE_11B_1A",
                            "candidate_status": "GENERATED_REQUIRES_VALIDATION",
                            "candidate_reason": _build_candidate_reason(
                                base_geometry=base_geometry,
                                channel_count=channel_count,
                                channel_width=channel_width,
                                channel_height=channel_height,
                                rib_width=rib_width,
                                wall_thickness=wall_thickness,
                            ),
                            "changes": _build_changes(
                                base_geometry=base_geometry,
                                channel_count=channel_count,
                                channel_width=channel_width,
                                channel_height=channel_height,
                                rib_width=rib_width,
                                wall_thickness=wall_thickness,
                            ),
                            "inputs": {
                                "number_of_coolant_channels": channel_count,
                                "coolant_channel_width": channel_width,
                                "coolant_channel_height": channel_height,
                                "rib_width": rib_width,
                                "hot_gas_wall_thickness": wall_thickness,
                                "coolant_mass_flow_fraction": base_geometry.get(
                                    "coolant_mass_flow_fraction"
                                ),
                            },
                            "preview_metrics": preview,
                            "preview_score": preview.get("preview_score"),
                            "validation_status": "NOT_VALIDATED",
                            "failure_reasons": [],
                            "pass_reasons": [],
                        }

                        raw_candidates.append(candidate)
                        candidate_id += 1

    deduped = _dedupe_candidates(raw_candidates)
    deduped.sort(key=lambda item: item.get("preview_score", 1.0e99))

    limit = int(results.get("regen_candidate_generator_max_candidates") or 100)
    return deduped[:limit]


def _preview_candidate(
        results,
        base_geometry,
        channel_count,
        channel_width,
        channel_height,
        rib_width,
):
    channel_mid_radius = base_geometry.get("channel_mid_radius")
    coolant_density = base_geometry.get("coolant_density")
    coolant_viscosity = base_geometry.get("coolant_dynamic_viscosity")
    coolant_mass_flow = base_geometry.get("coolant_mass_flow_rate")

    pitch_requested = channel_width + rib_width
    circumference = None
    available_pitch = None
    fit_ratio = None
    geometry_fit_preview = None

    if channel_mid_radius is not None and channel_mid_radius > 0:
        circumference = 2.0 * math.pi * channel_mid_radius
        available_pitch = circumference / max(channel_count, 1)
        fit_ratio = available_pitch / max(pitch_requested, 1.0e-12)
        geometry_fit_preview = fit_ratio >= 1.0

    single_area = channel_width * channel_height
    total_area = single_area * channel_count
    wetted_perimeter = 2.0 * (channel_width + channel_height)
    hydraulic_diameter = 4.0 * single_area / max(wetted_perimeter, 1.0e-12)

    velocity = None
    reynolds = None

    if (
        coolant_mass_flow is not None
        and coolant_density is not None
        and coolant_viscosity is not None
        and coolant_mass_flow > 0
        and coolant_density > 0
        and coolant_viscosity > 0
        and total_area > 0
    ):
        velocity = coolant_mass_flow / max(coolant_density * total_area, 1.0e-12)
        reynolds = (
            coolant_density
            * velocity
            * hydraulic_diameter
            / max(coolant_viscosity, 1.0e-12)
        )

    target_re = _safe_float(results.get("regen_target_reynolds_number"), 10000.0)
    max_velocity = _safe_float(results.get("regen_derived_maximum_coolant_velocity"), 40.0)

    score = 0.0

    if fit_ratio is None:
        score += 100.0
    elif fit_ratio < 1.0:
        score += (1.0 - fit_ratio) * 100.0
    else:
        score += abs(fit_ratio - 1.15) * 5.0

    if reynolds is None:
        score += 100.0
    elif reynolds < 2300.0:
        score += 75.0
    elif reynolds < target_re:
        score += (target_re - reynolds) / max(target_re, 1.0)

    if velocity is None:
        score += 50.0
    elif velocity > max_velocity:
        score += (velocity / max(max_velocity, 1.0e-12)) * 20.0

    aspect_ratio = channel_height / max(channel_width, 1.0e-12)

    if aspect_ratio > 8.0:
        score += 25.0
    elif aspect_ratio < 0.5:
        score += 10.0

    return {
        "pitch_requested": pitch_requested,
        "available_pitch": available_pitch,
        "fit_ratio": fit_ratio,
        "geometry_fit_preview": geometry_fit_preview,
        "single_channel_area": single_area,
        "total_coolant_area": total_area,
        "hydraulic_diameter": hydraulic_diameter,
        "coolant_velocity_preview": velocity,
        "coolant_reynolds_preview": reynolds,
        "aspect_ratio": aspect_ratio,
        "preview_score": score,
    }


def _build_candidate_reason(
        base_geometry,
        channel_count,
        channel_width,
        channel_height,
        rib_width,
        wall_thickness,
):
    changes = _build_changes(
        base_geometry=base_geometry,
        channel_count=channel_count,
        channel_width=channel_width,
        channel_height=channel_height,
        rib_width=rib_width,
        wall_thickness=wall_thickness,
    )

    changed_keys = [
        key
        for key, payload in changes.items()
        if payload.get("changed")
    ]

    if not changed_keys:
        return "Baseline candidate generated for validation comparison."

    return "Generated candidate by modifying: " + ", ".join(changed_keys) + "."


def _build_changes(
        base_geometry,
        channel_count,
        channel_width,
        channel_height,
        rib_width,
        wall_thickness,
):
    return {
        "number_of_coolant_channels": _change_payload(
            base_geometry.get("number_of_coolant_channels"),
            channel_count,
        ),
        "coolant_channel_width": _change_payload(
            base_geometry.get("coolant_channel_width"),
            channel_width,
        ),
        "coolant_channel_height": _change_payload(
            base_geometry.get("coolant_channel_height"),
            channel_height,
        ),
        "rib_width": _change_payload(
            base_geometry.get("rib_width"),
            rib_width,
        ),
        "hot_gas_wall_thickness": _change_payload(
            base_geometry.get("hot_gas_wall_thickness"),
            wall_thickness,
        ),
    }


def _change_payload(old, new):
    changed = old != new

    ratio = None
    if old not in (None, 0):
        try:
            ratio = float(new) / float(old)
        except Exception:
            ratio = None

    return {
        "old": old,
        "new": new,
        "ratio": ratio,
        "changed": changed,
    }


def _dedupe_candidates(candidates):
    seen = set()
    deduped = []

    for candidate in candidates:
        inputs = candidate.get("inputs", {})
        key = (
            int(inputs.get("number_of_coolant_channels") or 0),
            round(float(inputs.get("coolant_channel_width") or 0.0), 9),
            round(float(inputs.get("coolant_channel_height") or 0.0), 9),
            round(float(inputs.get("rib_width") or 0.0), 9),
            round(float(inputs.get("hot_gas_wall_thickness") or 0.0), 9),
        )

        if key in seen:
            continue

        seen.add(key)
        deduped.append(candidate)

    return deduped


def _build_status(enabled, base_geometry_complete, candidates, blocking_reasons):
    if not enabled:
        return "DISABLED_REGEN_CANDIDATE_GENERATOR"

    if blocking_reasons:
        return "BLOCKED_REGEN_CANDIDATE_GENERATOR"

    if not base_geometry_complete:
        return "FAIL_BASE_GEOMETRY_INCOMPLETE"

    if not candidates:
        return "FAIL_NO_CANDIDATES_GENERATED"

    return "PASS_CANDIDATES_GENERATED_REQUIRES_VALIDATION"


def _first_number(results, keys):
    for key in keys:
        value = _safe_float(results.get(key), None)
        if value is not None:
            return value
    return None


def _safe_float(value, default=None):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _bool_value(value, default=False):
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "enabled"}

    return default