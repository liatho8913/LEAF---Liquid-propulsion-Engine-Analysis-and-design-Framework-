"""
LEAF Regen Optimisation Candidate Generator Foundation
======================================================

REGEN PHASE 8B

This module owns reproducible regen optimisation candidate generation.

It deliberately does NOT:
- score candidates
- rank candidates
- select the best candidate
- apply geometry automatically
- approve recommendations
- bypass validation gates
"""
from leaf_qt.status_presentation import status_severity

DEFAULT_CHANNEL_COUNT_OFFSETS = (-8, 0, 8)
DEFAULT_WIDTH_MULTIPLIERS = (0.85, 1.0, 1.15)
DEFAULT_HEIGHT_MULTIPLIERS = (0.85, 1.0, 1.15)
DEFAULT_RIB_MULTIPLIERS = (0.85, 1.0, 1.15)
DEFAULT_WALL_MULTIPLIERS = (1.0,)

DEFAULT_BASE_GEOMETRY = {
    "coolant_channel_count": 80,
    "coolant_channel_width": 0.0015,
    "coolant_channel_height": 0.0020,
    "coolant_rib_width": 0.0010,
    "regen_wall_thickness": 0.0010,
}


def attach_regen_optimisation_candidate_generator(results):
    if not isinstance(results, dict):
        return results

    generated = build_regen_optimisation_candidate_generator(results)
    results.update(generated)
    return results


def build_regen_optimisation_candidate_generator(results):
    results = results if isinstance(results, dict) else {}

    enabled = _bool_value(
        results.get("regen_optimisation_candidate_generation_enabled"),
        default=False,
    )

    phase_8a_complete = bool(
        results.get("phase_8a_regen_optimisation_profile_complete", False)
    )

    base_geometry = _build_base_geometry(results)
    generation_ranges = _build_generation_ranges(results)

    blocking_reasons = _build_phase_8b_blocking_reasons(
        enabled=enabled,
        phase_8a_complete=phase_8a_complete,
        results=results,
    )

    candidate_generation_allowed = enabled and phase_8a_complete and not blocking_reasons

    candidates = []

    if candidate_generation_allowed:
        candidates = _generate_candidates(
            base_geometry=base_geometry,
            generation_ranges=generation_ranges,
        )

    status = (
        "PASS_REGEN_OPTIMISATION_CANDIDATE_GENERATOR"
        if _generator_structure_complete(base_geometry, generation_ranges)
        else "FAIL_REGEN_OPTIMISATION_CANDIDATE_GENERATOR"
    )

    text = build_regen_optimisation_candidate_generator_text(
        status=status,
        enabled=enabled,
        phase_8a_complete=phase_8a_complete,
        candidate_generation_allowed=candidate_generation_allowed,
        base_geometry=base_geometry,
        generation_ranges=generation_ranges,
        candidates=candidates,
        blocking_reasons=blocking_reasons,
    )

    return {
        "regen_optimisation_candidate_generator_status": status,
        "regen_optimisation_candidate_generator_complete": status_severity(status) == "PASS",
        "regen_optimisation_candidate_generator_enabled": enabled,
        "regen_optimisation_candidate_generator_phase_8a_complete": phase_8a_complete,
        "regen_optimisation_candidate_generator_generation_allowed": candidate_generation_allowed,
        "regen_optimisation_candidate_generator_base_geometry": base_geometry,
        "regen_optimisation_candidate_generator_ranges": generation_ranges,
        "regen_optimisation_candidate_generator_candidates": candidates,
        "regen_optimisation_candidate_generator_candidate_count": len(candidates),
        "regen_optimisation_candidate_generator_blocking_reasons": blocking_reasons,
        "regen_optimisation_candidate_generator_scoring_allowed": False,
        "regen_optimisation_candidate_generator_automatic_selection_allowed": False,
        "regen_optimisation_candidate_generator_text": text,
        "phase_8b_regen_optimisation_candidate_generator_complete": status_severity(status) == "PASS",
    }


def build_regen_optimisation_candidate_generator_text(
        status,
        enabled,
        phase_8a_complete,
        candidate_generation_allowed,
        base_geometry,
        generation_ranges,
        candidates,
        blocking_reasons,
):
    lines = [
        "LEAF REGEN PHASE 8B OPTIMISATION CANDIDATE GENERATOR FOUNDATION",
        "=================================================================",
        "",
        f"Status: {status}",
        f"Candidate generation enabled: {enabled}",
        f"Phase 8A complete: {phase_8a_complete}",
        f"Candidate generation allowed: {candidate_generation_allowed}",
        "",
        "Owned By:",
        "- regen_optimisation_candidate_generator.py",
        "",
        "Scope:",
        "- Owns deterministic candidate generation.",
        "- Owns generation ranges.",
        "- Owns generated candidate metadata.",
        "- Does not score candidates.",
        "- Does not rank candidates.",
        "- Does not automatically select geometry.",
        "- Does not approve recommendations.",
        "",
        "Phase Locks:",
        "- Candidate scoring allowed: False",
        "- Automatic selection allowed: False",
        "",
        "Base Geometry:",
    ]

    for key, value in base_geometry.items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("Generation Ranges:")

    for key, value in generation_ranges.items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append(f"Generated candidate count: {len(candidates)}")

    if candidates:
        lines.append("")
        lines.append("Generated Candidates:")
        for candidate in candidates:
            lines.append(
                "- "
                f"{candidate['candidate_id']}: "
                f"N={candidate['coolant_channel_count']}, "
                f"w={candidate['coolant_channel_width']}, "
                f"h={candidate['coolant_channel_height']}, "
                f"rib={candidate['coolant_rib_width']}, "
                f"wall={candidate['regen_wall_thickness']}"
            )

    lines.append("")
    lines.append("Blocking Reasons:")

    if blocking_reasons:
        for reason in blocking_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Next Required Action:")
    lines.append(
        "- After Phase 8B is verified, build Phase 8C candidate scoring without enabling automatic selection."
    )

    return "\n".join(lines)


def _build_base_geometry(results):
    return {
        "coolant_channel_count": _int_value(
            results.get("coolant_channel_count"),
            DEFAULT_BASE_GEOMETRY["coolant_channel_count"],
        ),
        "coolant_channel_width": _float_value(
            results.get("coolant_channel_width"),
            DEFAULT_BASE_GEOMETRY["coolant_channel_width"],
        ),
        "coolant_channel_height": _float_value(
            results.get("coolant_channel_height"),
            DEFAULT_BASE_GEOMETRY["coolant_channel_height"],
        ),
        "coolant_rib_width": _float_value(
            results.get("coolant_rib_width"),
            DEFAULT_BASE_GEOMETRY["coolant_rib_width"],
        ),
        "regen_wall_thickness": _float_value(
            results.get("regen_wall_thickness"),
            DEFAULT_BASE_GEOMETRY["regen_wall_thickness"],
        ),
    }


def _build_generation_ranges(results):
    return {
        "channel_count_offsets": _normalise_numeric_sequence(
            results.get("regen_optimisation_channel_count_offsets"),
            DEFAULT_CHANNEL_COUNT_OFFSETS,
            cast=int,
        ),
        "width_multipliers": _normalise_numeric_sequence(
            results.get("regen_optimisation_width_multipliers"),
            DEFAULT_WIDTH_MULTIPLIERS,
            cast=float,
        ),
        "height_multipliers": _normalise_numeric_sequence(
            results.get("regen_optimisation_height_multipliers"),
            DEFAULT_HEIGHT_MULTIPLIERS,
            cast=float,
        ),
        "rib_multipliers": _normalise_numeric_sequence(
            results.get("regen_optimisation_rib_multipliers"),
            DEFAULT_RIB_MULTIPLIERS,
            cast=float,
        ),
        "wall_multipliers": _normalise_numeric_sequence(
            results.get("regen_optimisation_wall_multipliers"),
            DEFAULT_WALL_MULTIPLIERS,
            cast=float,
        ),
    }


def _build_phase_8b_blocking_reasons(enabled, phase_8a_complete, results):
    blocking = []

    if not enabled:
        blocking.append(
            "Candidate generation is disabled by default. Enable it with regen_optimisation_candidate_generation_enabled=True."
        )

    if not phase_8a_complete:
        blocking.append(
            "Phase 8A optimisation profile foundation is not complete, so Phase 8B generation is blocked."
        )

    if results.get("regen_optimisation_scoring_requested"):
        blocking.append(
            "Candidate scoring was requested, but this belongs to Phase 8C."
        )

    if results.get("regen_optimisation_auto_select_requested"):
        blocking.append(
            "Automatic geometry selection was requested, but this remains blocked until later optimisation gates exist."
        )

    return blocking


def _generate_candidates(base_geometry, generation_ranges):
    candidates = []
    seen = set()

    channel_count_base = base_geometry["coolant_channel_count"]
    width_base = base_geometry["coolant_channel_width"]
    height_base = base_geometry["coolant_channel_height"]
    rib_base = base_geometry["coolant_rib_width"]
    wall_base = base_geometry["regen_wall_thickness"]

    for channel_offset in generation_ranges["channel_count_offsets"]:
        channel_count = max(1, int(channel_count_base + channel_offset))

        for width_multiplier in generation_ranges["width_multipliers"]:
            width = _round_geometry(width_base * width_multiplier)

            for height_multiplier in generation_ranges["height_multipliers"]:
                height = _round_geometry(height_base * height_multiplier)

                for rib_multiplier in generation_ranges["rib_multipliers"]:
                    rib = _round_geometry(rib_base * rib_multiplier)

                    for wall_multiplier in generation_ranges["wall_multipliers"]:
                        wall = _round_geometry(wall_base * wall_multiplier)

                        key = (
                            channel_count,
                            width,
                            height,
                            rib,
                            wall,
                        )

                        if key in seen:
                            continue

                        seen.add(key)

                        candidate_index = len(candidates) + 1

                        candidates.append({
                            "candidate_id": _candidate_id(candidate_index),
                            "source": "generated_phase_8b",
                            "coolant_channel_count": channel_count,
                            "coolant_channel_width": width,
                            "coolant_channel_height": height,
                            "coolant_rib_width": rib,
                            "regen_wall_thickness": wall,
                            "scoring_allowed": False,
                            "automatic_selection_allowed": False,
                            "selection_allowed": False,
                        })

    return candidates


def _generator_structure_complete(base_geometry, generation_ranges):
    if not isinstance(base_geometry, dict):
        return False

    if not isinstance(generation_ranges, dict):
        return False

    required_base = {
        "coolant_channel_count",
        "coolant_channel_width",
        "coolant_channel_height",
        "coolant_rib_width",
        "regen_wall_thickness",
    }

    required_ranges = {
        "channel_count_offsets",
        "width_multipliers",
        "height_multipliers",
        "rib_multipliers",
        "wall_multipliers",
    }

    return required_base.issubset(base_geometry) and required_ranges.issubset(generation_ranges)


def _candidate_id(index):
    return f"REGEN-OPT-8B-{index:04d}"


def _round_geometry(value):
    return round(float(value), 9)


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


def _float_value(value, default):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return float(default)

    if value <= 0:
        return float(default)

    return value


def _int_value(value, default):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return int(default)

    if value <= 0:
        return int(default)

    return value


def _normalise_numeric_sequence(value, default, cast=float):
    if value is None:
        return list(default)

    if isinstance(value, str):
        raw_items = [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]
    elif isinstance(value, (list, tuple, set)):
        raw_items = list(value)
    else:
        return list(default)

    cleaned = []

    for item in raw_items:
        try:
            cleaned.append(cast(item))
        except (TypeError, ValueError):
            continue

    return cleaned or list(default)