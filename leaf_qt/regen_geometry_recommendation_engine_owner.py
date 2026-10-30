"""
PHASE 11A.4
Regen Geometry Recommendation Engine V1

Purpose:
    Generate structured regen geometry recommendations from validation and
    failure-explanation results.

Rules:
    - Recommendation only.
    - Does not modify solver values.
    - Does not apply recommendations.
    - Produces safe structured actions for later Apply Recommended Geometry.
"""


def attach_regen_geometry_recommendation_engine_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_regen_geometry_recommendation_engine(results)
    results.update(audit)
    return results


def build_regen_geometry_recommendation_engine(results):
    results = results if isinstance(results, dict) else {}

    validation_complete = bool(
        results.get("phase_11a2_regen_geometry_constraint_validation_owner_complete")
    )

    explanation_complete = bool(
        results.get("phase_11a3_regen_geometry_failure_explanation_owner_complete")
    )

    validation_results = results.get(
        "phase_11a2_regen_geometry_constraint_validation_owner_results",
        [],
    )

    explanations = results.get(
        "phase_11a3_regen_geometry_failure_explanation_owner_explanations",
        [],
    )

    if not isinstance(validation_results, list):
        validation_results = []

    if not isinstance(explanations, list):
        explanations = []

    recommendations = []

    explanation_by_id = {
        item.get("constraint_id"): item
        for item in explanations
        if isinstance(item, dict)
    }

    for item in validation_results:
        if not isinstance(item, dict):
            continue

        state = item.get("validation_state")

        if state not in ("FAIL", "WARN"):
            continue

        constraint_id = item.get("constraint_id")
        explanation = explanation_by_id.get(constraint_id, {})

        recommendations.extend(
            _recommendations_for_constraint(item, explanation)
        )

    recommendations = _deduplicate_recommendations(recommendations)

    auto_apply_ready = [
        item for item in recommendations
        if item.get("auto_apply_candidate") is True
    ]

    manual_review_required = [
        item for item in recommendations
        if item.get("auto_apply_candidate") is not True
    ]

    if recommendations:
        engineering_status = "WARN_REGEN_GEOMETRY_RECOMMENDATION_ENGINE"
    else:
        engineering_status = "PASS_REGEN_GEOMETRY_RECOMMENDATION_ENGINE"

    owner_status = "PASS_PHASE_11A4_REGEN_GEOMETRY_RECOMMENDATION_ENGINE_OWNER"

    text = build_regen_geometry_recommendation_engine_text(
        owner_status=owner_status,
        engineering_status=engineering_status,
        validation_complete=validation_complete,
        explanation_complete=explanation_complete,
        recommendations=recommendations,
        auto_apply_ready=auto_apply_ready,
        manual_review_required=manual_review_required,
    )

    return {
        "phase_11a4_regen_geometry_recommendation_engine_owner_complete": True,
        "phase_11a4_regen_geometry_recommendation_engine_owner_status": owner_status,
        "phase_11a4_regen_geometry_recommendation_engine_owner_validation_complete": validation_complete,
        "phase_11a4_regen_geometry_recommendation_engine_owner_explanation_complete": explanation_complete,
        "phase_11a4_regen_geometry_recommendation_engine_owner_recommendations": recommendations,
        "phase_11a4_regen_geometry_recommendation_engine_owner_recommendation_count": len(recommendations),
        "phase_11a4_regen_geometry_recommendation_engine_owner_auto_apply_candidate_count": len(auto_apply_ready),
        "phase_11a4_regen_geometry_recommendation_engine_owner_manual_review_count": len(manual_review_required),
        "phase_11a4_regen_geometry_recommendation_engine_owner_engineering_status": engineering_status,
        "phase_11a4_regen_geometry_recommendation_engine_owner_text": text,
        "stage_11a_regen_geometry_recommendation_engine_complete": True,
        "stage_11a_regen_geometry_recommendation_engine_status": owner_status,
        "stage_11a_regen_geometry_recommendation_engineering_status": engineering_status,
    }


def _recommendations_for_constraint(validation, explanation):
    constraint_id = validation.get("constraint_id")
    state = validation.get("validation_state")
    value = validation.get("value")
    severity = validation.get("severity", "UNKNOWN")
    reason = validation.get("reason", "")

    builders = {
        "channel_fit_ratio": _recommend_channel_fit_ratio,
        "effective_rib_width": _recommend_effective_rib_width,
        "channel_width": _recommend_channel_width,
        "channel_height": _recommend_channel_height,
        "rib_width": _recommend_rib_width,
        "channel_count": _recommend_channel_count,
        "channel_aspect_ratio": _recommend_channel_aspect_ratio,
        "coolant_velocity": _recommend_coolant_velocity,
        "reynolds_number": _recommend_reynolds_number,
        "pressure_drop": _recommend_pressure_drop,
        "heat_flux": _recommend_heat_flux,
        "hot_wall_temperature": _recommend_hot_wall_temperature,
        "coolant_wall_temperature": _recommend_coolant_wall_temperature,
        "inner_wall_thickness": _recommend_wall_thickness,
        "outer_wall_thickness": _recommend_wall_thickness,
        "coolant_temperature_rise": _recommend_coolant_temperature_rise,
    }

    builder = builders.get(constraint_id)

    if builder is None:
        return [
            _make_recommendation(
                recommendation_id=f"review_{constraint_id}",
                source_constraint=constraint_id,
                source_state=state,
                priority=_priority_from_state(state),
                action_type="MANUAL_REVIEW",
                title=f"Review {constraint_id}",
                rationale=(
                    f"{constraint_id} produced {state}. "
                    f"Reason: {reason}"
                ),
                target_variables=[constraint_id],
                proposed_direction="review",
                expected_benefit="Improves confidence before automated geometry changes.",
                auto_apply_candidate=False,
                evidence={
                    "value": value,
                    "severity": severity,
                    "explanation": explanation.get("explanation"),
                },
            )
        ]

    return builder(validation, explanation)


def _recommend_channel_fit_ratio(validation, explanation):
    value = _float(validation.get("value"))

    recs = [
        _make_recommendation(
            recommendation_id="reduce_channel_pitch_demand",
            source_constraint="channel_fit_ratio",
            source_state=validation.get("validation_state"),
            priority="HIGH",
            action_type="GEOMETRY_FIT",
            title="Reduce requested circumferential pitch demand",
            rationale=(
                "The requested channel width plus rib width is too close to, "
                "or exceeds, the available circumferential pitch."
            ),
            target_variables=["channel_width", "rib_width", "channel_count"],
            proposed_direction="decrease channel width/rib width or decrease channel count",
            expected_benefit=(
                "Restores fit ratio below 1.0 and prevents effective rib collapse."
            ),
            auto_apply_candidate=False,
            evidence={
                "channel_fit_ratio": value,
                "explanation": explanation.get("explanation"),
            },
        ),
        _make_recommendation(
            recommendation_id="increase_available_pitch_margin",
            source_constraint="channel_fit_ratio",
            source_state=validation.get("validation_state"),
            priority="HIGH",
            action_type="GEOMETRY_FIT",
            title="Increase available pitch margin",
            rationale=(
                "The circumference available per channel is insufficient for the requested pitch."
            ),
            target_variables=["channel_count"],
            proposed_direction="reduce channel count at constrained stations",
            expected_benefit=(
                "Increases available pitch per channel and improves manufacturability margin."
            ),
            auto_apply_candidate=False,
            evidence={
                "channel_fit_ratio": value,
                "explanation": explanation.get("explanation"),
            },
        ),
    ]

    return recs


def _recommend_effective_rib_width(validation, explanation):
    return [
        _make_recommendation(
            recommendation_id="restore_effective_rib_width",
            source_constraint="effective_rib_width",
            source_state=validation.get("validation_state"),
            priority="HIGH",
            action_type="MANUFACTURING_MARGIN",
            title="Restore manufacturable effective rib width",
            rationale=(
                "Effective rib width is too small after the channel layout is fitted "
                "around the circumference."
            ),
            target_variables=["channel_width", "rib_width", "channel_count"],
            proposed_direction="reduce channel count or channel width; enforce minimum rib width",
            expected_benefit=(
                "Improves structural/manufacturing margin between adjacent channels."
            ),
            auto_apply_candidate=False,
            evidence={
                "effective_rib_width": validation.get("value"),
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_channel_width(validation, explanation):
    return [
        _make_recommendation(
            recommendation_id="review_channel_width",
            source_constraint="channel_width",
            source_state=validation.get("validation_state"),
            priority=_priority_from_state(validation.get("validation_state")),
            action_type="GEOMETRY_DIMENSION",
            title="Review coolant channel width",
            rationale=(
                "Channel width controls flow area, pitch demand, velocity, and manufacturability."
            ),
            target_variables=["channel_width", "channel_count", "rib_width", "coolant_velocity"],
            proposed_direction="adjust width with pitch and velocity targets",
            expected_benefit=(
                "Balances channel fit, coolant velocity, and manufacturability."
            ),
            auto_apply_candidate=False,
            evidence={
                "channel_width": validation.get("value"),
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_channel_height(validation, explanation):
    return [
        _make_recommendation(
            recommendation_id="review_channel_height",
            source_constraint="channel_height",
            source_state=validation.get("validation_state"),
            priority=_priority_from_state(validation.get("validation_state")),
            action_type="GEOMETRY_DIMENSION",
            title="Review coolant channel height",
            rationale=(
                "Channel height controls flow area, hydraulic diameter, velocity, "
                "pressure drop, and heat-transfer behaviour."
            ),
            target_variables=["channel_height", "channel_width", "coolant_velocity", "pressure_drop"],
            proposed_direction="adjust height with velocity and pressure-drop targets",
            expected_benefit=(
                "Improves hydraulic balance without immediately changing channel count."
            ),
            auto_apply_candidate=False,
            evidence={
                "channel_height": validation.get("value"),
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_rib_width(validation, explanation):
    return [
        _make_recommendation(
            recommendation_id="review_rib_width",
            source_constraint="rib_width",
            source_state=validation.get("validation_state"),
            priority=_priority_from_state(validation.get("validation_state")),
            action_type="MANUFACTURING_MARGIN",
            title="Review rib width",
            rationale=(
                "Rib width affects structural margin and circumferential fit."
            ),
            target_variables=["rib_width", "channel_width", "channel_count"],
            proposed_direction="enforce minimum rib while preserving fit ratio",
            expected_benefit=(
                "Prevents rib collapse and improves manufacturability confidence."
            ),
            auto_apply_candidate=False,
            evidence={
                "rib_width": validation.get("value"),
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_channel_count(validation, explanation):
    return [
        _make_recommendation(
            recommendation_id="review_channel_count",
            source_constraint="channel_count",
            source_state=validation.get("validation_state"),
            priority=_priority_from_state(validation.get("validation_state")),
            action_type="GEOMETRY_LAYOUT",
            title="Review channel count",
            rationale=(
                "Channel count affects available pitch, flow area per channel, "
                "cooling distribution, pressure drop, and manufacturability."
            ),
            target_variables=["channel_count", "available_pitch", "channel_width", "rib_width"],
            proposed_direction="solve channel count with local circumference and pitch targets",
            expected_benefit=(
                "Improves fit, flow distribution, and manufacturability."
            ),
            auto_apply_candidate=False,
            evidence={
                "channel_count": validation.get("value"),
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_channel_aspect_ratio(validation, explanation):
    return [
        _make_recommendation(
            recommendation_id="rebalance_channel_aspect_ratio",
            source_constraint="channel_aspect_ratio",
            source_state=validation.get("validation_state"),
            priority="MEDIUM",
            action_type="MANUFACTURING_MARGIN",
            title="Rebalance channel aspect ratio",
            rationale=(
                "Channel aspect ratio is outside broad manufacturability guidance."
            ),
            target_variables=["channel_width", "channel_height"],
            proposed_direction="adjust width and height together",
            expected_benefit=(
                "Improves manufacturability and hydraulic predictability."
            ),
            auto_apply_candidate=False,
            evidence={
                "channel_aspect_ratio": validation.get("value"),
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_coolant_velocity(validation, explanation):
    value = _float(validation.get("value"))

    if value is not None and value < 1.0:
        direction = "decrease total coolant flow area or increase coolant mass flow"
        expected = "Raises coolant velocity and improves coolant-side heat transfer."
    elif value is not None and value > 120.0:
        direction = "increase total coolant flow area or reduce coolant mass flow"
        expected = "Reduces pressure drop and high-velocity risk."
    else:
        direction = "review coolant velocity against hydraulic targets"
        expected = "Improves hydraulic and thermal confidence."

    return [
        _make_recommendation(
            recommendation_id="correct_coolant_velocity",
            source_constraint="coolant_velocity",
            source_state=validation.get("validation_state"),
            priority=_priority_from_state(validation.get("validation_state")),
            action_type="HYDRAULIC_BALANCE",
            title="Correct coolant velocity",
            rationale=(
                "Coolant velocity controls heat-transfer coefficient, Reynolds number, "
                "and pressure-drop behaviour."
            ),
            target_variables=["channel_width", "channel_height", "channel_count", "coolant_mass_flow"],
            proposed_direction=direction,
            expected_benefit=expected,
            auto_apply_candidate=False,
            evidence={
                "coolant_velocity": value,
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_reynolds_number(validation, explanation):
    return [
        _make_recommendation(
            recommendation_id="increase_reynolds_number_margin",
            source_constraint="reynolds_number",
            source_state=validation.get("validation_state"),
            priority=_priority_from_state(validation.get("validation_state")),
            action_type="HEAT_TRANSFER_MARGIN",
            title="Increase Reynolds number margin",
            rationale=(
                "Low Reynolds number indicates laminar/transitional coolant flow, "
                "which can weaken coolant-side heat transfer."
            ),
            target_variables=["coolant_velocity", "hydraulic_diameter", "channel_width", "channel_height"],
            proposed_direction="increase coolant velocity or adjust hydraulic diameter",
            expected_benefit=(
                "Improves coolant-side heat-transfer confidence."
            ),
            auto_apply_candidate=False,
            evidence={
                "reynolds_number": validation.get("value"),
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_pressure_drop(validation, explanation):
    value = _float(validation.get("value"))

    if value is not None and value == 0:
        direction = "verify hydraulic pressure-drop model is active"
        expected = "Prevents false hydraulic pass from inactive model."
    elif value is not None and value > 10_000_000:
        direction = "increase flow area, reduce velocity, or shorten/segment flow path"
        expected = "Reduces feed-system pressure burden."
    else:
        direction = "review pressure drop against feed-system limits"
        expected = "Improves engine-cycle compatibility."

    return [
        _make_recommendation(
            recommendation_id="correct_pressure_drop",
            source_constraint="pressure_drop",
            source_state=validation.get("validation_state"),
            priority=_priority_from_state(validation.get("validation_state")),
            action_type="HYDRAULIC_BALANCE",
            title="Correct coolant pressure drop",
            rationale=(
                "Pressure drop affects pump/feed requirements and cooling-path feasibility."
            ),
            target_variables=["channel_width", "channel_height", "channel_count", "coolant_velocity"],
            proposed_direction=direction,
            expected_benefit=expected,
            auto_apply_candidate=False,
            evidence={
                "pressure_drop": value,
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_heat_flux(validation, explanation):
    return [
        _make_recommendation(
            recommendation_id="reduce_or_manage_heat_flux",
            source_constraint="heat_flux",
            source_state=validation.get("validation_state"),
            priority=_priority_from_state(validation.get("validation_state")),
            action_type="THERMAL_MARGIN",
            title="Reduce or manage heat flux",
            rationale=(
                "High heat flux increases wall temperature and coolant heat load."
            ),
            target_variables=["coolant_velocity", "channel_height", "wall_thickness", "coating"],
            proposed_direction="increase cooling strength or improve thermal protection",
            expected_benefit=(
                "Improves wall temperature and coolant thermal margin."
            ),
            auto_apply_candidate=False,
            evidence={
                "heat_flux": validation.get("value"),
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_hot_wall_temperature(validation, explanation):
    return [
        _make_recommendation(
            recommendation_id="reduce_hot_wall_temperature",
            source_constraint="hot_wall_temperature",
            source_state=validation.get("validation_state"),
            priority="HIGH",
            action_type="THERMAL_MARGIN",
            title="Reduce hot-gas-side wall temperature",
            rationale=(
                "Hot wall temperature is a direct material/coating survivability concern."
            ),
            target_variables=["coolant_velocity", "channel_width", "channel_height", "wall_thickness", "coating"],
            proposed_direction="increase coolant-side heat transfer or add/improve coating protection",
            expected_benefit=(
                "Improves material and coating temperature margin."
            ),
            auto_apply_candidate=False,
            evidence={
                "hot_wall_temperature": validation.get("value"),
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_coolant_wall_temperature(validation, explanation):
    return [
        _make_recommendation(
            recommendation_id="review_coolant_wall_temperature",
            source_constraint="coolant_wall_temperature",
            source_state=validation.get("validation_state"),
            priority=_priority_from_state(validation.get("validation_state")),
            action_type="THERMAL_MARGIN",
            title="Review coolant-side wall temperature",
            rationale=(
                "Coolant-side wall temperature indicates coolant heat-transfer effectiveness "
                "and possible coolant degradation risk."
            ),
            target_variables=["coolant_velocity", "channel_width", "channel_height", "coolant_mass_flow"],
            proposed_direction="improve coolant-side heat transfer or reduce thermal load",
            expected_benefit=(
                "Improves coolant-side thermal margin."
            ),
            auto_apply_candidate=False,
            evidence={
                "coolant_wall_temperature": validation.get("value"),
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_wall_thickness(validation, explanation):
    return [
        _make_recommendation(
            recommendation_id="review_wall_thickness",
            source_constraint=validation.get("constraint_id"),
            source_state=validation.get("validation_state"),
            priority=_priority_from_state(validation.get("validation_state")),
            action_type="STRUCTURAL_THERMAL_BALANCE",
            title="Review wall thickness",
            rationale=(
                "Wall thickness affects structural margin and thermal resistance."
            ),
            target_variables=["wall_thickness", "material", "coolant_velocity"],
            proposed_direction="balance structural requirement against thermal resistance",
            expected_benefit=(
                "Improves structural/thermal consistency."
            ),
            auto_apply_candidate=False,
            evidence={
                "wall_thickness": validation.get("value"),
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _recommend_coolant_temperature_rise(validation, explanation):
    return [
        _make_recommendation(
            recommendation_id="review_coolant_temperature_rise",
            source_constraint="coolant_temperature_rise",
            source_state=validation.get("validation_state"),
            priority=_priority_from_state(validation.get("validation_state")),
            action_type="THERMAL_MARGIN",
            title="Review coolant temperature rise",
            rationale=(
                "Large coolant temperature rise can reduce cooling margin and may create coolant decomposition risk."
            ),
            target_variables=["coolant_mass_flow", "coolant_cp", "heat_load"],
            proposed_direction="increase coolant mass flow or reduce absorbed heat load",
            expected_benefit=(
                "Improves coolant thermal margin."
            ),
            auto_apply_candidate=False,
            evidence={
                "coolant_temperature_rise": validation.get("value"),
                "explanation": explanation.get("explanation"),
            },
        )
    ]


def _make_recommendation(
        recommendation_id,
        source_constraint,
        source_state,
        priority,
        action_type,
        title,
        rationale,
        target_variables,
        proposed_direction,
        expected_benefit,
        auto_apply_candidate,
        evidence,
):
    return {
        "recommendation_id": recommendation_id,
        "source_constraint": source_constraint,
        "source_state": source_state,
        "priority": priority,
        "action_type": action_type,
        "title": title,
        "rationale": rationale,
        "target_variables": list(target_variables),
        "proposed_direction": proposed_direction,
        "expected_benefit": expected_benefit,
        "auto_apply_candidate": bool(auto_apply_candidate),
        "evidence": evidence if isinstance(evidence, dict) else {},
    }


def _deduplicate_recommendations(recommendations):
    seen = set()
    deduped = []

    for item in recommendations:
        if not isinstance(item, dict):
            continue

        key = (
            item.get("recommendation_id"),
            item.get("source_constraint"),
            item.get("proposed_direction"),
        )

        if key in seen:
            continue

        seen.add(key)
        deduped.append(item)

    priority_order = {
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 2,
        "INFO": 3,
    }

    deduped.sort(
        key=lambda item: priority_order.get(item.get("priority"), 99)
    )

    return deduped


def _priority_from_state(state):
    if state == "FAIL":
        return "HIGH"
    if state == "WARN":
        return "MEDIUM"
    return "INFO"


def _float(value):
    try:
        if value is None or isinstance(value, bool):
            return None
        return float(value)
    except Exception:
        return None


def build_regen_geometry_recommendation_engine_text(
        owner_status,
        engineering_status,
        validation_complete,
        explanation_complete,
        recommendations,
        auto_apply_ready,
        manual_review_required,
):
    lines = []
    lines.append("PHASE 11A.4 — REGEN GEOMETRY RECOMMENDATION ENGINE V1")
    lines.append("====================================================")
    lines.append("")
    lines.append(f"Owner Status: {owner_status}")
    lines.append(f"Engineering Status: {engineering_status}")
    lines.append(f"Validation Complete: {validation_complete}")
    lines.append(f"Explanation Complete: {explanation_complete}")
    lines.append("")
    lines.append("Purpose:")
    lines.append("- Convert regen geometry WARN/FAIL diagnostics into structured engineering recommendations.")
    lines.append("- This stage does not apply or overwrite geometry.")
    lines.append("")
    lines.append("Summary:")
    lines.append(f"- Recommendations: {len(recommendations)}")
    lines.append(f"- Auto-apply candidates: {len(auto_apply_ready)}")
    lines.append(f"- Manual-review recommendations: {len(manual_review_required)}")
    lines.append("")
    lines.append("Recommendations:")

    if recommendations:
        for item in recommendations:
            lines.append("")
            lines.append(f"- {item['title']} [{item['priority']}]")
            lines.append(f"  ID: {item['recommendation_id']}")
            lines.append(f"  Source Constraint: {item['source_constraint']}")
            lines.append(f"  Action Type: {item['action_type']}")
            lines.append(f"  Rationale: {item['rationale']}")
            lines.append(f"  Target Variables: {item['target_variables']}")
            lines.append(f"  Proposed Direction: {item['proposed_direction']}")
            lines.append(f"  Expected Benefit: {item['expected_benefit']}")
            lines.append(f"  Auto Apply Candidate: {item['auto_apply_candidate']}")
    else:
        lines.append("- No geometry recommendations required.")

    lines.append("")
    lines.append("Conclusion:")
    lines.append(
        "PASS/WARN recommendation data is now available for later apply, output, and UI stages."
    )

    return "\n".join(lines)