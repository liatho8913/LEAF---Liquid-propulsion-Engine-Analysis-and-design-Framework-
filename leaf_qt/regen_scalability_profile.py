"""
LEAF Regen Scalability Profile
==============================

Stage V.0 owner for regen scalability metadata and engine scale classification.

This module owns metadata only.
It does not validate scalability.
It does not benchmark real engines.
It does not optimise geometry.
"""


ENGINE_SCALE_CLASSES = {
    "MICRO_ENGINE": {
        "description": "Very small experimental or educational engine.",
        "thrust_min_n": 0.0,
        "thrust_max_n": 100.0,
    },
    "SMALL_ENGINE": {
        "description": "Small lab, demonstrator, or upper-stage-class engine.",
        "thrust_min_n": 100.0,
        "thrust_max_n": 10_000.0,
    },
    "MEDIUM_ENGINE": {
        "description": "Medium thrust engine or sizeable upper-stage engine.",
        "thrust_min_n": 10_000.0,
        "thrust_max_n": 250_000.0,
    },
    "LARGE_ENGINE": {
        "description": "Large booster or main propulsion engine.",
        "thrust_min_n": 250_000.0,
        "thrust_max_n": 1_500_000.0,
    },
    "VERY_LARGE_ENGINE": {
        "description": "Very large booster-class engine.",
        "thrust_min_n": 1_500_000.0,
        "thrust_max_n": None,
    },
}


def attach_regen_scalability_profile(results):
    if not isinstance(results, dict):
        return results

    profile = build_regen_scalability_profile(results)
    results.update(profile)
    return results


def build_regen_scalability_profile(results):
    results = results if isinstance(results, dict) else {}

    scale_class = classify_engine_scale(results)
    scale_metadata = ENGINE_SCALE_CLASSES.get(scale_class, {})

    return {
        "regen_scalability_profile_status": "PASS_REGEN_SCALABILITY_PROFILE",
        "regen_scalability_profile_scale_class": scale_class,
        "regen_scalability_profile_scale_metadata": scale_metadata,
        "regen_scalability_profile_text": build_regen_scalability_profile_text(
            scale_class,
            scale_metadata,
            results,
        ),
        "stage_v0_regen_scalability_profile_complete": True,
    }


def classify_engine_scale(results):
    results = results if isinstance(results, dict) else {}

    thrust = _number(
        results.get("thrust")
        or results.get("thrust_n")
        or results.get("engine_thrust")
        or results.get("engine_thrust_n")
    )

    if thrust is None:
        return classify_engine_scale_from_mass_flow(results)

    for scale_class, metadata in ENGINE_SCALE_CLASSES.items():
        thrust_min = metadata["thrust_min_n"]
        thrust_max = metadata["thrust_max_n"]

        if thrust_max is None:
            if thrust >= thrust_min:
                return scale_class
        elif thrust_min <= thrust < thrust_max:
            return scale_class

    return "UNKNOWN_ENGINE_SCALE"


def classify_engine_scale_from_mass_flow(results):
    mass_flow = _number(
        results.get("mass_flow_rate")
        or results.get("mdot")
        or results.get("m_dot")
        or results.get("mass_flow")
    )

    if mass_flow is None:
        return "UNKNOWN_ENGINE_SCALE"

    if mass_flow < 0.1:
        return "MICRO_ENGINE"

    if mass_flow < 5:
        return "SMALL_ENGINE"

    if mass_flow < 100:
        return "MEDIUM_ENGINE"

    if mass_flow < 800:
        return "LARGE_ENGINE"

    return "VERY_LARGE_ENGINE"


def build_regen_scalability_profile_text(scale_class, scale_metadata, results):
    lines = [
        "LEAF STAGE V.0 REGEN SCALABILITY PROFILE",
        "=========================================",
        "",
        "Status: PASS_REGEN_SCALABILITY_PROFILE",
        f"Engine scale class: {scale_class}",
        "",
        "Owned By:",
        "- regen_scalability_profile.py",
        "",
        "Scope:",
        "- Owns engine scale metadata.",
        "- Owns scale classification.",
        "- Does not approve or reject scalability.",
        "",
        "Scale Metadata:",
    ]

    for key, value in scale_metadata.items():
        lines.append(f"- {key}: {value}")

    return "\n".join(lines)


def _number(value):
    try:
        return float(value)
    except Exception:
        return None