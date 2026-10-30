"""
PHASE 11A.1
Regen Geometry Constraint Discovery Audit Owner

Purpose:
    Discover and report the active regenerative-cooling geometry constraints
    currently available in solver results.

Rules:
    - Audit/discovery only.
    - Does not overwrite solver physics.
    - Does not optimise geometry.
    - Does not declare final geometry valid/invalid.
    - Produces structured constraint discovery data for later validation,
      failure explanation, and recommendation stages.
"""


def attach_regen_geometry_constraint_discovery_audit_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_regen_geometry_constraint_discovery_audit(results)
    results.update(audit)
    return results


def build_regen_geometry_constraint_discovery_audit(results):
    # Work on an audit-local copy so derived discovery values do not
    # mutate the canonical solved result state.
    results = dict(results) if isinstance(results, dict) else {}

    channel_height = results.get("coolant_channel_height")
    channel_width = results.get("coolant_channel_width")

    if (
        results.get("channel_aspect_ratio") is None
        and isinstance(channel_height, (int, float))
        and not isinstance(channel_height, bool)
        and isinstance(channel_width, (int, float))
        and not isinstance(channel_width, bool)
        and channel_width != 0
    ):
        results["channel_aspect_ratio"] = channel_height / channel_width

    constraints = []

    _add_constraint(
        constraints,
        results,
        constraint_id="channel_count",
        label="Channel count",
        keys=["number_of_coolant_channels", "coolant_channel_count", "regen_channel_count", "channel_count", "Nch"],
        category="GEOMETRY",
        role="Number of parallel coolant channels.",
        unit="count",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="channel_width",
        label="Channel width",
        keys=["coolant_channel_width", "regen_channel_width", "channel_width"],
        category="GEOMETRY",
        role="Coolant channel circumferential width.",
        unit="m",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="channel_height",
        label="Channel height",
        keys=["coolant_channel_height", "regen_channel_height", "channel_height"],
        category="GEOMETRY",
        role="Coolant channel radial height.",
        unit="m",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="rib_width",
        label="Rib width",
        keys=["rib_width", "regen_rib_width", "coolant_rib_width"],
        category="GEOMETRY",
        role="Solid web/rib thickness between adjacent coolant channels.",
        unit="m",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="requested_pitch",
        label="Requested channel pitch",
        keys=["requested_channel_pitch", "coolant_channel_pitch", "channel_pitch"],
        category="GEOMETRY_FIT",
        role="Requested circumferential pitch per channel.",
        unit="m",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="available_pitch",
        label="Available circumferential pitch",
        keys=["circumferential_channel_pitch", "available_circumferential_pitch", "available_channel_pitch"],
        category="GEOMETRY_FIT",
        role="Available pitch from local circumference divided by channel count.",
        unit="m",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="channel_fit_ratio",
        label="Channel fit ratio",
        keys=["channel_fit_ratio", "regen_channel_fit_ratio"],
        category="GEOMETRY_FIT",
        role="Ratio showing whether requested channel pitch fits available circumference.",
        unit="ratio",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="effective_rib_width",
        label="Effective rib width",
        keys=["effective_rib_width", "regen_effective_rib_width"],
        category="GEOMETRY_FIT",
        role="Rib width remaining after fitting channels around circumference.",
        unit="m",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="inner_wall_thickness",
        label="Inner wall thickness",
        keys=["hot_gas_wall_thickness", "inner_wall_thickness", "regen_wall_thickness", "wall_thickness"],
        category="STRUCTURAL",
        role="Hot-gas-side wall thickness between chamber/nozzle gas and coolant.",
        unit="m",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="outer_wall_thickness",
        label="Outer wall thickness",
        keys=["outer_jacket_thickness", "outer_wall_thickness", "regen_outer_wall_thickness"],
        category="STRUCTURAL",
        role="Outer jacket/wall thickness outside coolant channels.",
        unit="m",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="channel_aspect_ratio",
        label="Channel aspect ratio",
        keys=["channel_aspect_ratio", "regen_channel_aspect_ratio"],
        category="MANUFACTURING",
        role="Channel height-to-width or width-to-height proportion used for manufacturability screening.",
        unit="ratio",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="coolant_velocity",
        label="Coolant velocity",
        keys=["regen_coolant_velocity", "coolant_velocity"],
        category="HYDRAULIC",
        role="Mean coolant velocity through the channels.",
        unit="m/s",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="reynolds_number",
        label="Coolant Reynolds number",
        keys=["regen_reynolds_number", "coolant_reynolds_number", "reynolds_number"],
        category="HYDRAULIC",
        role="Coolant flow regime indicator.",
        unit="dimensionless",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="pressure_drop",
        label="Coolant pressure drop",
        keys=["regen_pressure_drop", "coolant_pressure_drop", "pressure_drop"],
        category="HYDRAULIC",
        role="Coolant-side pressure loss through the cooling path.",
        unit="Pa",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="coolant_temperature_rise",
        label="Coolant temperature rise",
        keys=["coolant_temperature_rise", "regen_coolant_temperature_rise"],
        category="THERMAL",
        role="Bulk coolant temperature increase across the cooling path.",
        unit="K",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="heat_flux",
        label="Heat flux",
        keys=["regen_heat_flux", "heat_flux", "hot_gas_heat_flux"],
        category="THERMAL",
        role="Heat flux entering the wall/cooling system.",
        unit="W/m^2",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="hot_wall_temperature",
        label="Hot-gas-side wall temperature",
        keys=["hot_gas_side_wall_temperature", "wall_temperature_hot_gas", "Twg"],
        category="THERMAL",
        role="Wall temperature at the hot-gas-facing surface.",
        unit="K",
    )

    _add_constraint(
        constraints,
        results,
        constraint_id="coolant_wall_temperature",
        label="Coolant-side wall temperature",
        keys=["coolant_side_wall_temperature", "wall_temperature_coolant_side", "Twc"],
        category="THERMAL",
        role="Wall temperature at the coolant-side surface.",
        unit="K",
    )

    discovered = [item for item in constraints if item["available"]]
    missing = [item for item in constraints if not item["available"]]

    categories = {}
    for item in constraints:
        category = item["category"]
        if category not in categories:
            categories[category] = {
                "total": 0,
                "available": 0,
                "missing": 0,
            }

        categories[category]["total"] += 1

        if item["available"]:
            categories[category]["available"] += 1
        else:
            categories[category]["missing"] += 1

    status = "PASS_PHASE_11A1_REGEN_GEOMETRY_CONSTRAINT_DISCOVERY_AUDIT_OWNER"

    text = build_regen_geometry_constraint_discovery_audit_text(
        status=status,
        constraints=constraints,
        discovered=discovered,
        missing=missing,
        categories=categories,
    )

    return {
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_complete": True,
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_status": status,
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_constraints": constraints,
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_discovered_count": len(discovered),
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_missing_count": len(missing),
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_categories": categories,
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_text": text,
        "stage_11a_regen_geometry_constraint_discovery_complete": True,
        "stage_11a_regen_geometry_constraint_discovery_status": status,
    }


def _add_constraint(
        constraints,
        results,
        constraint_id,
        label,
        keys,
        category,
        role,
        unit,
):
    value, source_key = _first_available_value(results, keys)

    constraints.append(
        {
            "constraint_id": constraint_id,
            "label": label,
            "category": category,
            "role": role,
            "unit": unit,
            "available": value is not None,
            "value": value,
            "source_key": source_key,
            "candidate_keys": list(keys),
        }
    )


def _first_available_value(results, keys):
    for key in keys:
        if key in results:
            value = results.get(key)
            if value is not None:
                return value, key

    return None, None


def build_regen_geometry_constraint_discovery_audit_text(
        status,
        constraints,
        discovered,
        missing,
        categories,
):
    lines = []
    lines.append("PHASE 11A.1 — REGEN GEOMETRY CONSTRAINT DISCOVERY AUDIT")
    lines.append("=======================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append("")
    lines.append("Purpose:")
    lines.append("- Discover which regen geometry, hydraulic, thermal, structural, and manufacturing constraints are available.")
    lines.append("- This stage does not validate, optimise, or overwrite geometry.")
    lines.append("")
    lines.append("Summary:")
    lines.append(f"- Total tracked constraints: {len(constraints)}")
    lines.append(f"- Discovered constraints: {len(discovered)}")
    lines.append(f"- Missing constraints: {len(missing)}")
    lines.append("")
    lines.append("Categories:")

    for category, counts in sorted(categories.items()):
        lines.append(
            f"- {category}: "
            f"available={counts['available']}; "
            f"missing={counts['missing']}; "
            f"total={counts['total']}"
        )

    lines.append("")
    lines.append("Discovered Constraints:")

    if discovered:
        for item in discovered:
            lines.append(
                f"- {item['label']} "
                f"({item['constraint_id']}): "
                f"value={item['value']} {item['unit']}; "
                f"source={item['source_key']}; "
                f"category={item['category']}"
            )
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Missing Constraints:")

    if missing:
        for item in missing:
            lines.append(
                f"- {item['label']} "
                f"({item['constraint_id']}): "
                f"candidate_keys={item['candidate_keys']}; "
                f"category={item['category']}"
            )
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Conclusion:")
    lines.append(
        "PASS means geometry constraints have been discovered and structured for "
        "future validation, explanation, and recommendation stages."
    )

    return "\n".join(lines)