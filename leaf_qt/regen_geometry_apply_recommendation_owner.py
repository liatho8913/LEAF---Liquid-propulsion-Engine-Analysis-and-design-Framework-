"""
PHASE 11A.5
Apply Recommended Geometry Owner

Purpose:
    Convert regen geometry recommendations into safe candidate modifications.

Rules:
    - Does not silently overwrite original solver inputs.
    - Produces candidate geometry values under phase_11a5_* keys.
    - Applies only conservative, bounded candidate changes.
    - Records before/after deltas and improvement evidence.
    - Later UI stages may expose an explicit "Apply Candidate" button.
"""


def attach_regen_geometry_apply_recommendation_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_regen_geometry_apply_recommendation(results)
    results.update(audit)
    return results


def build_regen_geometry_apply_recommendation(results):
    results = results if isinstance(results, dict) else {}

    recommendation_complete = bool(
        results.get("phase_11a4_regen_geometry_recommendation_engine_owner_complete")
    )

    recommendations = results.get(
        "phase_11a4_regen_geometry_recommendation_engine_owner_recommendations",
        [],
    )

    if not isinstance(recommendations, list):
        recommendations = []

    baseline_geometry = _extract_geometry(results)
    candidate_geometry = dict(baseline_geometry)

    applied_actions = []
    skipped_actions = []

    for recommendation in recommendations:
        if not isinstance(recommendation, dict):
            continue

        action_result = _apply_recommendation_candidate(
            recommendation=recommendation,
            baseline=baseline_geometry,
            candidate=candidate_geometry,
        )

        if action_result["applied"]:
            applied_actions.append(action_result)
        else:
            skipped_actions.append(action_result)

    before_metrics = _geometry_metrics(baseline_geometry)
    after_metrics = _geometry_metrics(candidate_geometry)

    improvement = _compare_geometry_metrics(before_metrics, after_metrics)

    engineering_status = "PASS_REGEN_GEOMETRY_APPLY_RECOMMENDATION"

    if applied_actions:
        engineering_status = "WARN_REGEN_GEOMETRY_APPLY_RECOMMENDATION_CANDIDATE_CREATED"

    owner_status = "PASS_PHASE_11A5_REGEN_GEOMETRY_APPLY_RECOMMENDATION_OWNER"

    text = build_regen_geometry_apply_recommendation_text(
        owner_status=owner_status,
        engineering_status=engineering_status,
        recommendation_complete=recommendation_complete,
        baseline_geometry=baseline_geometry,
        candidate_geometry=candidate_geometry,
        before_metrics=before_metrics,
        after_metrics=after_metrics,
        improvement=improvement,
        applied_actions=applied_actions,
        skipped_actions=skipped_actions,
    )

    return {
        "phase_11a5_regen_geometry_apply_recommendation_owner_complete": True,
        "phase_11a5_regen_geometry_apply_recommendation_owner_status": owner_status,
        "phase_11a5_regen_geometry_apply_recommendation_owner_recommendation_complete": recommendation_complete,
        "phase_11a5_regen_geometry_apply_recommendation_owner_baseline_geometry": baseline_geometry,
        "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry": candidate_geometry,
        "phase_11a5_regen_geometry_apply_recommendation_owner_before_metrics": before_metrics,
        "phase_11a5_regen_geometry_apply_recommendation_owner_after_metrics": after_metrics,
        "phase_11a5_regen_geometry_apply_recommendation_owner_improvement": improvement,
        "phase_11a5_regen_geometry_apply_recommendation_owner_applied_actions": applied_actions,
        "phase_11a5_regen_geometry_apply_recommendation_owner_skipped_actions": skipped_actions,
        "phase_11a5_regen_geometry_apply_recommendation_owner_applied_count": len(applied_actions),
        "phase_11a5_regen_geometry_apply_recommendation_owner_skipped_count": len(skipped_actions),
        "phase_11a5_regen_geometry_apply_recommendation_owner_engineering_status": engineering_status,
        "phase_11a5_regen_geometry_apply_recommendation_owner_text": text,
        "stage_11a_regen_geometry_apply_recommendation_complete": True,
        "stage_11a_regen_geometry_apply_recommendation_status": owner_status,
        "stage_11a_regen_geometry_apply_recommendation_engineering_status": engineering_status,
    }


def _extract_geometry(results):
    return {
        "channel_count": _first_number(results, [
            "number_of_coolant_channels",
            "coolant_channel_count",
            "regen_channel_count",
            "channel_count",
            "Nch",
        ]),
        "number_of_coolant_channels": _first_number(results, [
            "number_of_coolant_channels",
            "coolant_channel_count",
            "regen_channel_count",
            "channel_count",
            "Nch",
        ]),
        "channel_width": _first_number(results, [
            "coolant_channel_width",
            "regen_channel_width",
            "channel_width",
        ]),
        "coolant_channel_width": _first_number(results, [
            "coolant_channel_width",
            "regen_channel_width",
            "channel_width",
        ]),
        "channel_height": _first_number(results, [
            "coolant_channel_height",
            "regen_channel_height",
            "channel_height",
        ]),
        "coolant_channel_height": _first_number(results, [
            "coolant_channel_height",
            "regen_channel_height",
            "channel_height",
        ]),
        "rib_width": _first_number(results, [
            "rib_width",
            "regen_rib_width",
            "coolant_rib_width",
        ]),
        "hot_gas_wall_thickness": _first_number(results, [
            "hot_gas_wall_thickness",
            "regen_wall_thickness",
            "wall_thickness",
        ]),
        "fit_ratio": _first_number(results, [
            "channel_fit_ratio",
            "regen_channel_fit_ratio",
        ]),
        "effective_rib_width": _first_number(results, [
            "effective_rib_width",
            "regen_effective_rib_width",
        ]),
        "coolant_velocity": _first_number(results, [
            "coolant_velocity_preview",
            "regen_coolant_velocity_preview",
            "regen_coolant_velocity",
            "coolant_velocity",
        ]),
        "reynolds_number": _first_number(results, [
            "coolant_reynolds_preview",
            "regen_coolant_reynolds_preview",
            "regen_reynolds_number",
            "coolant_reynolds_number",
            "reynolds_number",
        ]),
        "pressure_drop": _first_number(results, [
            "regen_pressure_drop",
            "coolant_pressure_drop",
            "pressure_drop",
        ]),
        "hot_wall_temperature": _first_number(results, [
            "hot_gas_side_wall_temperature",
            "wall_temperature_hot_gas",
            "Twg",
        ]),
    }


def _apply_recommendation_candidate(recommendation, baseline, candidate):
    recommendation_id = recommendation.get("recommendation_id")
    source_constraint = recommendation.get("source_constraint")
    target_variables = recommendation.get("target_variables", [])

    if not isinstance(target_variables, list):
        target_variables = []

    if recommendation_id in (
        "correct_coolant_velocity",
        "increase_reynolds_number_margin",
    ):
        return _apply_velocity_improvement(
            recommendation=recommendation,
            baseline=baseline,
            candidate=candidate,
        )

    if recommendation_id in (
        "reduce_channel_pitch_demand",
        "increase_available_pitch_margin",
        "restore_effective_rib_width",
    ):
        return _apply_fit_improvement(
            recommendation=recommendation,
            baseline=baseline,
            candidate=candidate,
        )

    if recommendation_id == "reduce_hot_wall_temperature":
        return _apply_hot_wall_temperature_improvement(
            recommendation=recommendation,
            baseline=baseline,
            candidate=candidate,
        )

    return {
        "applied": False,
        "recommendation_id": recommendation_id,
        "source_constraint": source_constraint,
        "reason": "No safe bounded candidate rule exists for this recommendation yet.",
        "target_variables": target_variables,
    }


def _apply_velocity_improvement(recommendation, baseline, candidate):
    velocity = baseline.get("coolant_velocity")
    width = candidate.get("channel_width")
    height = candidate.get("channel_height")

    if velocity is None:
        return _skip(recommendation, "Missing coolant velocity.")

    if width is None:
        width = _first_non_none(
            baseline,
            [
                "coolant_channel_width",
                "channel_width",
                "regen_channel_width",
            ],
        )

    if height is None:
        height = _first_non_none(
            baseline,
            [
                "coolant_channel_height",
                "channel_height",
                "regen_channel_height",
            ],
        )

    if width is None or height is None:
        width = 0.0015
        height = 0.0020
        candidate["candidate_geometry_used_default_dimensions"] = True
    else:
        candidate["candidate_geometry_used_default_dimensions"] = False

    if velocity < 1.0:
        scale = 0.85
        candidate["channel_width"] = _bounded(width * scale, width * 0.5, width)
        candidate["channel_height"] = _bounded(height * scale, height * 0.5, height)
        candidate["candidate_intent"] = "increase_coolant_velocity"

        return _applied(
            recommendation,
            "Reduced candidate channel width/height by 15% to increase velocity.",
            ["channel_width", "channel_height"],
        )

    if velocity > 120.0:
        scale = 1.15
        candidate["channel_width"] = _bounded(width * scale, width, width * 2.0)
        candidate["channel_height"] = _bounded(height * scale, height, height * 2.0)
        candidate["candidate_intent"] = "decrease_coolant_velocity"

        return _applied(
            recommendation,
            "Increased candidate channel width/height by 15% to reduce velocity.",
            ["channel_width", "channel_height"],
        )

    return _skip(recommendation, "Velocity is not outside apply threshold.")


def _apply_fit_improvement(recommendation, baseline, candidate):
    fit_ratio = baseline.get("fit_ratio")
    count = candidate.get("channel_count")
    width = candidate.get("channel_width")
    rib = candidate.get("rib_width")

    if fit_ratio is None:
        return _skip(recommendation, "Missing fit ratio.")

    changed = []

    if count is not None and fit_ratio > 1.0:
        new_count = max(1, int(round(count / fit_ratio * 0.95)))
        if new_count < count:
            candidate["channel_count"] = new_count
            changed.append("channel_count")

    if width is not None and fit_ratio > 0.95:
        candidate["channel_width"] = width * 0.9
        changed.append("channel_width")

    if rib is not None and fit_ratio > 0.95:
        candidate["rib_width"] = rib * 0.9
        changed.append("rib_width")

    if changed:
        candidate["candidate_intent"] = "improve_circumferential_fit"
        return _applied(
            recommendation,
            "Created conservative candidate to reduce pitch demand and improve fit ratio.",
            changed,
        )

    return _skip(recommendation, "Fit ratio does not require candidate modification.")


def _apply_hot_wall_temperature_improvement(recommendation, baseline, candidate):
    hot_wall = baseline.get("hot_wall_temperature")
    width = candidate.get("channel_width")
    height = candidate.get("channel_height")

    if hot_wall is None or width is None or height is None:
        return _skip(recommendation, "Missing hot wall temperature, width, or height.")

    if hot_wall <= 1600.0:
        return _skip(recommendation, "Hot wall temperature is not above apply threshold.")

    candidate["channel_width"] = width * 0.9
    candidate["channel_height"] = height * 0.9
    candidate["candidate_intent"] = "increase_cooling_strength_for_hot_wall"

    return _applied(
        recommendation,
        "Reduced channel dimensions by 10% as a candidate to increase coolant velocity and cooling strength.",
        ["channel_width", "channel_height"],
    )


def _geometry_metrics(geometry):
    width = geometry.get("channel_width")
    height = geometry.get("channel_height")
    count = geometry.get("channel_count")
    rib = geometry.get("rib_width")

    channel_area = None
    total_channel_area = None
    requested_pitch = None

    if width is not None and height is not None:
        channel_area = width * height

    if channel_area is not None and count is not None:
        total_channel_area = channel_area * count

    if width is not None and rib is not None:
        requested_pitch = width + rib

    return {
        "channel_area": channel_area,
        "total_channel_area": total_channel_area,
        "requested_pitch": requested_pitch,
        "channel_count": count,
        "channel_width": width,
        "channel_height": height,
        "rib_width": rib,
        "fit_ratio": geometry.get("fit_ratio"),
        "effective_rib_width": geometry.get("effective_rib_width"),
        "coolant_velocity": geometry.get("coolant_velocity"),
        "reynolds_number": geometry.get("reynolds_number"),
        "pressure_drop": geometry.get("pressure_drop"),
        "hot_wall_temperature": geometry.get("hot_wall_temperature"),
    }


def _compare_geometry_metrics(before, after):
    keys = sorted(set(before.keys()) | set(after.keys()))
    deltas = {}

    for key in keys:
        before_value = before.get(key)
        after_value = after.get(key)

        if before_value is None or after_value is None:
            deltas[key] = None
        else:
            deltas[key] = after_value - before_value

    changed_keys = [
        key for key, delta in deltas.items()
        if delta not in (None, 0)
    ]

    return {
        "changed_keys": changed_keys,
        "deltas": deltas,
        "changed_count": len(changed_keys),
    }


def _first_number(results, keys, default=None):
    for key in keys:
        value = results.get(key)
        number = _to_float_or_none(value)

        if number is not None:
            return number

    return default


def _to_float_or_none(value):
    try:
        if value is None or isinstance(value, bool):
            return None
        return float(value)
    except Exception:
        return None


def _bounded(value, lower, upper):
    return max(lower, min(upper, value))

def _first_non_none(mapping, keys):
    if not isinstance(mapping, dict):
        return None

    for key in keys:
        value = mapping.get(key)
        if value is not None:
            return value

    return None

def _applied(recommendation, reason, changed_variables):
    return {
        "applied": True,
        "recommendation_id": recommendation.get("recommendation_id"),
        "source_constraint": recommendation.get("source_constraint"),
        "reason": reason,
        "changed_variables": list(changed_variables),
    }


def _skip(recommendation, reason):
    return {
        "applied": False,
        "recommendation_id": recommendation.get("recommendation_id"),
        "source_constraint": recommendation.get("source_constraint"),
        "reason": reason,
        "target_variables": recommendation.get("target_variables", []),
    }


def build_regen_geometry_apply_recommendation_text(
        owner_status,
        engineering_status,
        recommendation_complete,
        baseline_geometry,
        candidate_geometry,
        before_metrics,
        after_metrics,
        improvement,
        applied_actions,
        skipped_actions,
):
    lines = []
    lines.append("PHASE 11A.5 — APPLY RECOMMENDED GEOMETRY OWNER")
    lines.append("==============================================")
    lines.append("")
    lines.append(f"Owner Status: {owner_status}")
    lines.append(f"Engineering Status: {engineering_status}")
    lines.append(f"Recommendation Complete: {recommendation_complete}")
    lines.append("")
    lines.append("Purpose:")
    lines.append("- Convert recommendations into safe candidate geometry changes.")
    lines.append("- This stage does not silently overwrite original user inputs.")
    lines.append("")
    lines.append("Summary:")
    lines.append(f"- Applied candidate actions: {len(applied_actions)}")
    lines.append(f"- Skipped actions: {len(skipped_actions)}")
    lines.append(f"- Changed metric count: {improvement.get('changed_count')}")
    lines.append("")
    lines.append("Baseline Geometry:")
    for key, value in sorted(baseline_geometry.items()):
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("Candidate Geometry:")
    for key, value in sorted(candidate_geometry.items()):
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("Applied Actions:")
    if applied_actions:
        for item in applied_actions:
            lines.append(
                f"- {item['recommendation_id']}: {item['reason']} "
                f"changed={item.get('changed_variables')}"
            )
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("Skipped Actions:")
    if skipped_actions:
        for item in skipped_actions:
            lines.append(f"- {item['recommendation_id']}: {item['reason']}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("Conclusion:")
    lines.append(
        "Candidate geometry is available for later explicit UI application and output comparison."
    )

    return "\n".join(lines)

