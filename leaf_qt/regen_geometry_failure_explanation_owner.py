"""
PHASE 11A.3
Regen Geometry Failure Explanation Owner

Purpose:
    Convert regen geometry validation WARN/FAIL results into clear engineering
    explanations.

Rules:
    - Explanation only.
    - Does not optimise geometry.
    - Does not overwrite solver values.
    - Does not apply recommendations.
    - Produces structured explanations for later recommendation and UI/report stages.
"""


def attach_regen_geometry_failure_explanation_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_regen_geometry_failure_explanation(results)
    results.update(audit)
    return results


def build_regen_geometry_failure_explanation(results):
    results = results if isinstance(results, dict) else {}

    validation_complete = bool(
        results.get("phase_11a2_regen_geometry_constraint_validation_owner_complete")
    )

    validation_results = results.get(
        "phase_11a2_regen_geometry_constraint_validation_owner_results",
        [],
    )

    if not isinstance(validation_results, list):
        validation_results = []

    explanations = []

    for item in validation_results:
        if not isinstance(item, dict):
            continue

        state = item.get("validation_state")

        if state in ("FAIL", "WARN"):
            explanations.append(_build_explanation(item))

    fail_explanations = [
        item for item in explanations
        if item["validation_state"] == "FAIL"
    ]

    warning_explanations = [
        item for item in explanations
        if item["validation_state"] == "WARN"
    ]

    if fail_explanations:
        engineering_status = "FAIL_REGEN_GEOMETRY_FAILURE_EXPLANATION"
    elif warning_explanations:
        engineering_status = "WARN_REGEN_GEOMETRY_FAILURE_EXPLANATION"
    else:
        engineering_status = "PASS_REGEN_GEOMETRY_FAILURE_EXPLANATION"

    owner_status = "PASS_PHASE_11A3_REGEN_GEOMETRY_FAILURE_EXPLANATION_OWNER"

    text = build_regen_geometry_failure_explanation_text(
        owner_status=owner_status,
        engineering_status=engineering_status,
        validation_complete=validation_complete,
        explanations=explanations,
        fail_count=len(fail_explanations),
        warning_count=len(warning_explanations),
    )

    return {
        "phase_11a3_regen_geometry_failure_explanation_owner_complete": True,
        "phase_11a3_regen_geometry_failure_explanation_owner_status": owner_status,
        "phase_11a3_regen_geometry_failure_explanation_owner_validation_complete": validation_complete,
        "phase_11a3_regen_geometry_failure_explanation_owner_explanations": explanations,
        "phase_11a3_regen_geometry_failure_explanation_owner_fail_count": len(fail_explanations),
        "phase_11a3_regen_geometry_failure_explanation_owner_warning_count": len(warning_explanations),
        "phase_11a3_regen_geometry_failure_explanation_owner_engineering_status": engineering_status,
        "phase_11a3_regen_geometry_failure_explanation_owner_text": text,
        "stage_11a_regen_geometry_failure_explanation_complete": True,
        "stage_11a_regen_geometry_failure_explanation_status": owner_status,
        "stage_11a_regen_geometry_failure_explanation_engineering_status": engineering_status,
    }


def _build_explanation(item):
    constraint_id = item.get("constraint_id")
    label = item.get("label", constraint_id)
    category = item.get("category", "UNKNOWN")
    value = item.get("value")
    unit = item.get("unit", "")
    validation_state = item.get("validation_state")
    reason = item.get("reason", "")
    severity = item.get("severity", "UNKNOWN")

    template = _template_for_constraint(constraint_id)

    return {
        "constraint_id": constraint_id,
        "label": label,
        "category": category,
        "value": value,
        "unit": unit,
        "validation_state": validation_state,
        "severity": severity,
        "reason": reason,
        "failure_mode": template["failure_mode"],
        "engineering_meaning": template["engineering_meaning"],
        "likely_causes": template["likely_causes"],
        "engineering_consequences": template["engineering_consequences"],
        "future_recommendation_targets": template["future_recommendation_targets"],
        "explanation": _compose_explanation(
            label=label,
            value=value,
            unit=unit,
            validation_state=validation_state,
            reason=reason,
            template=template,
        ),
    }


def _template_for_constraint(constraint_id):
    templates = {
        "channel_count": {
            "failure_mode": "CHANNEL_COUNT_OUT_OF_GUIDANCE",
            "engineering_meaning": (
                "The number of coolant channels may not provide a practical balance "
                "between cooling distribution, manufacturability, and pressure drop."
            ),
            "likely_causes": [
                "Manual channel count is too low or too high.",
                "Geometry scaling has not adjusted channel count to chamber/nozzle circumference.",
                "A previous recommendation was not applied.",
            ],
            "engineering_consequences": [
                "Uneven cooling distribution.",
                "Manufacturing difficulty.",
                "Poor channel pitch fit.",
            ],
            "future_recommendation_targets": [
                "channel_count",
                "channel_width",
                "rib_width",
            ],
        },
        "channel_width": {
            "failure_mode": "CHANNEL_WIDTH_OUT_OF_GUIDANCE",
            "engineering_meaning": (
                "The coolant channel width may be too small to manufacture or too large "
                "to fit around the circumference with the selected rib width."
            ),
            "likely_causes": [
                "Requested width is outside practical manufacturing range.",
                "Channel count and circumference were not solved together.",
                "Rib width requirement leaves insufficient circumferential space.",
            ],
            "engineering_consequences": [
                "Collapsed ribs.",
                "Poor manufacturability.",
                "Incorrect coolant flow area.",
            ],
            "future_recommendation_targets": [
                "channel_width",
                "channel_count",
                "rib_width",
            ],
        },
        "channel_height": {
            "failure_mode": "CHANNEL_HEIGHT_OUT_OF_GUIDANCE",
            "engineering_meaning": (
                "The coolant channel height may create poor aspect ratio, excessive wall/jacket size, "
                "or insufficient coolant flow area."
            ),
            "likely_causes": [
                "Manual channel height is too small or too large.",
                "Coolant velocity target has not been linked to channel area.",
                "Thermal requirement was not balanced against pressure drop.",
            ],
            "engineering_consequences": [
                "High pressure drop.",
                "Low coolant velocity.",
                "Manufacturing difficulty.",
            ],
            "future_recommendation_targets": [
                "channel_height",
                "channel_width",
                "coolant_velocity",
                "pressure_drop",
            ],
        },
        "rib_width": {
            "failure_mode": "RIB_WIDTH_OUT_OF_GUIDANCE",
            "engineering_meaning": (
                "The rib/web between coolant channels may be too small for manufacturing or too large "
                "to allow the requested channels to fit."
            ),
            "likely_causes": [
                "Requested rib width conflicts with channel width and channel count.",
                "Available circumferential pitch is too small.",
                "Manufacturing minimum rib width has not been enforced.",
            ],
            "engineering_consequences": [
                "Collapsed effective ribs.",
                "Weak channel walls.",
                "Geometry cannot be manufactured as requested.",
            ],
            "future_recommendation_targets": [
                "rib_width",
                "channel_width",
                "channel_count",
            ],
        },
        "channel_fit_ratio": {
            "failure_mode": "CHANNEL_PITCH_DOES_NOT_FIT",
            "engineering_meaning": (
                "The requested channel pitch is too close to or exceeds the available circumferential pitch."
            ),
            "likely_causes": [
                "Too many channels for the local radius.",
                "Channel width plus rib width is too large.",
                "Geometry was sized at one station but applied to another smaller circumference.",
            ],
            "engineering_consequences": [
                "Effective rib width collapses.",
                "Requested geometry cannot be wrapped around the chamber/nozzle.",
                "Manufacturing validity should be blocked.",
            ],
            "future_recommendation_targets": [
                "channel_count",
                "channel_width",
                "rib_width",
                "available_pitch",
            ],
        },
        "effective_rib_width": {
            "failure_mode": "EFFECTIVE_RIB_WIDTH_TOO_SMALL",
            "engineering_meaning": (
                "The actual fitted rib width is below the intended or manufacturable rib width."
            ),
            "likely_causes": [
                "Requested pitch exceeds available pitch.",
                "Channel count is too high.",
                "Channel width is too large for circumference.",
            ],
            "engineering_consequences": [
                "Weak ribs.",
                "Poor manufacturability.",
                "Possible leakage or wall failure risk.",
            ],
            "future_recommendation_targets": [
                "channel_count",
                "channel_width",
                "rib_width",
            ],
        },
        "channel_aspect_ratio": {
            "failure_mode": "CHANNEL_ASPECT_RATIO_OUT_OF_GUIDANCE",
            "engineering_meaning": (
                "The channel shape may be difficult to manufacture or hydraulically inefficient."
            ),
            "likely_causes": [
                "Channel height and width were not solved together.",
                "Thermal area target conflicts with manufacturability.",
            ],
            "engineering_consequences": [
                "Poor heat-transfer performance.",
                "Manufacturing difficulty.",
                "Unexpected pressure drop.",
            ],
            "future_recommendation_targets": [
                "channel_width",
                "channel_height",
            ],
        },
        "coolant_velocity": {
            "failure_mode": "COOLANT_VELOCITY_OUT_OF_GUIDANCE",
            "engineering_meaning": (
                "Coolant velocity may be too low for strong heat transfer or too high for practical pressure drop."
            ),
            "likely_causes": [
                "Coolant flow area is too large or too small.",
                "Coolant mass flow is not balanced with channel count and channel area.",
                "Channel dimensions were selected independently of hydraulic targets.",
            ],
            "engineering_consequences": [
                "Weak coolant heat transfer if velocity is too low.",
                "Excessive pressure drop if velocity is too high.",
                "Thermal margin may be misleading.",
            ],
            "future_recommendation_targets": [
                "channel_width",
                "channel_height",
                "channel_count",
                "coolant_mass_flow",
            ],
        },
        "reynolds_number": {
            "failure_mode": "COOLANT_REYNOLDS_OUT_OF_GUIDANCE",
            "engineering_meaning": (
                "The coolant flow regime may not provide the intended convective heat-transfer performance."
            ),
            "likely_causes": [
                "Coolant velocity is too low.",
                "Hydraulic diameter is too small or viscosity is high.",
                "Channel geometry does not promote turbulent cooling.",
            ],
            "engineering_consequences": [
                "Laminar or transitional cooling may reduce heat-transfer coefficient.",
                "Wall temperatures may be under-protected.",
                "Regen pass/fail should remain conservative.",
            ],
            "future_recommendation_targets": [
                "channel_width",
                "channel_height",
                "coolant_velocity",
                "hydraulic_diameter",
            ],
        },
        "pressure_drop": {
            "failure_mode": "PRESSURE_DROP_OUT_OF_GUIDANCE",
            "engineering_meaning": (
                "Coolant pressure loss may be too high for the feed system or too low to indicate an active hydraulic model."
            ),
            "likely_causes": [
                "Channels are too narrow.",
                "Coolant velocity is too high.",
                "Cooling path length is too long.",
                "Hydraulic model may be inactive if pressure drop is zero.",
            ],
            "engineering_consequences": [
                "Pump/feed pressure requirement may be excessive.",
                "Coolant flow may be unrealistic.",
                "Engine cycle integration may fail.",
            ],
            "future_recommendation_targets": [
                "channel_width",
                "channel_height",
                "channel_count",
                "coolant_velocity",
            ],
        },
        "heat_flux": {
            "failure_mode": "HEAT_FLUX_OUT_OF_GUIDANCE",
            "engineering_meaning": (
                "The wall heat load is unusually high or invalid and should be reviewed before geometry optimisation."
            ),
            "likely_causes": [
                "Hot-gas coefficient is high.",
                "Wall temperature chain may be under-protected.",
                "Material/coating margins may be insufficient.",
            ],
            "engineering_consequences": [
                "Wall overheating.",
                "Large coolant temperature rise.",
                "Cooling channel geometry may need stronger thermal performance.",
            ],
            "future_recommendation_targets": [
                "wall_thickness",
                "channel_height",
                "coolant_velocity",
                "coating",
            ],
        },
        "hot_wall_temperature": {
            "failure_mode": "HOT_WALL_TEMPERATURE_OUT_OF_GUIDANCE",
            "engineering_meaning": (
                "Hot-gas-side wall temperature may exceed material or coating capability."
            ),
            "likely_causes": [
                "Heat flux is too high.",
                "Coolant-side heat transfer is too weak.",
                "Wall/coating resistance stack is insufficient.",
                "Material temperature limit is exceeded.",
            ],
            "engineering_consequences": [
                "Material failure risk.",
                "Coating failure risk.",
                "Design must not be signed off without correction.",
            ],
            "future_recommendation_targets": [
                "coolant_velocity",
                "channel_height",
                "channel_width",
                "wall_thickness",
                "coating",
            ],
        },
        "coolant_wall_temperature": {
            "failure_mode": "COOLANT_SIDE_WALL_TEMPERATURE_OUT_OF_GUIDANCE",
            "engineering_meaning": (
                "Coolant-side wall temperature may indicate insufficient coolant heat transfer or excessive wall loading."
            ),
            "likely_causes": [
                "Coolant velocity is too low.",
                "Coolant heat-transfer coefficient is weak.",
                "Thermal load is too high.",
            ],
            "engineering_consequences": [
                "Wall thermal margin may be poor.",
                "Coolant coking/decomposition risk may rise depending on coolant.",
            ],
            "future_recommendation_targets": [
                "coolant_velocity",
                "channel_width",
                "channel_height",
                "coolant_mass_flow",
            ],
        },
    }

    return templates.get(
        constraint_id,
        {
            "failure_mode": "GENERIC_REGEN_GEOMETRY_CONSTRAINT_REVIEW",
            "engineering_meaning": (
                "The constraint requires engineering review before automated recommendation."
            ),
            "likely_causes": [
                "Constraint is outside a broad validation rule.",
                "A specialised explanation template has not yet been added.",
            ],
            "engineering_consequences": [
                "Design confidence is reduced until reviewed.",
            ],
            "future_recommendation_targets": [
                constraint_id,
            ],
        },
    )


def _compose_explanation(label, value, unit, validation_state, reason, template):
    return (
        f"{label} is in state {validation_state}. "
        f"Current value: {value} {unit}. "
        f"Reason: {reason} "
        f"Engineering meaning: {template['engineering_meaning']}"
    )


def build_regen_geometry_failure_explanation_text(
        owner_status,
        engineering_status,
        validation_complete,
        explanations,
        fail_count,
        warning_count,
):
    lines = []
    lines.append("PHASE 11A.3 — REGEN GEOMETRY FAILURE EXPLANATION OWNER")
    lines.append("======================================================")
    lines.append("")
    lines.append(f"Owner Status: {owner_status}")
    lines.append(f"Engineering Status: {engineering_status}")
    lines.append(f"Validation Complete: {validation_complete}")
    lines.append("")
    lines.append("Purpose:")
    lines.append("- Convert regen geometry validation WARN/FAIL states into engineering explanations.")
    lines.append("- This stage does not optimise or apply fixes.")
    lines.append("")
    lines.append("Summary:")
    lines.append(f"- FAIL explanations: {fail_count}")
    lines.append(f"- WARN explanations: {warning_count}")
    lines.append("")
    lines.append("Explanations:")

    if explanations:
        for item in explanations:
            lines.append("")
            lines.append(f"- {item['label']} ({item['constraint_id']})")
            lines.append(f"  State: {item['validation_state']}")
            lines.append(f"  Failure Mode: {item['failure_mode']}")
            lines.append(f"  Value: {item['value']} {item['unit']}")
            lines.append(f"  Reason: {item['reason']}")
            lines.append(f"  Meaning: {item['engineering_meaning']}")
            lines.append("  Likely Causes:")
            for cause in item["likely_causes"]:
                lines.append(f"    - {cause}")
            lines.append("  Consequences:")
            for consequence in item["engineering_consequences"]:
                lines.append(f"    - {consequence}")
            lines.append("  Future Recommendation Targets:")
            for target in item["future_recommendation_targets"]:
                lines.append(f"    - {target}")
    else:
        lines.append("- No WARN/FAIL constraints requiring explanation.")

    lines.append("")
    lines.append("Conclusion:")
    lines.append(
        "PASS/WARN/FAIL explanations are now available for future recommendation, report, and UI stages."
    )

    return "\n".join(lines)