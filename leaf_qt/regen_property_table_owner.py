def attach_regen_property_table_owner(results):
    if not isinstance(results, dict):
        return results

    audit = audit_property_tables(results)
    results.update(audit)
    return results


def audit_property_tables(results):
    wall_temp = _value(results, "hot_gas_side_wall_temperature", None)

    material_status = _table_status(
        label="Material",
        table_status=_value(results, "material_temperature_table_status", "UNKNOWN"),
        interpolation_status=_value(results, "material_property_interpolation_status", "UNKNOWN"),
        temperature=wall_temp,
        min_temp=_value(results, "material_table_min_temperature", None),
        max_temp=_value(results, "material_table_max_temperature", None),
        required=True,
    )

    coating_name = str(_value(results, "coating_name", "NONE")).strip().upper()
    coating_mode = str(
        _value(
            results,
            "coating_source_validation_mode",
            _value(results, "regen_source_validation_coating_mode", "NONE"),
        )
    ).strip().upper()

    coating_required = (
        coating_name not in {"", "NONE", "N/A", "NO COATING"}
        and coating_mode not in {"", "NONE", "N/A"}
    )

    coating_status = _table_status(
        label="Coating",
        table_status=_value(results, "coating_temperature_table_status", "UNKNOWN"),
        interpolation_status=_value(results, "coating_property_interpolation_status", "UNKNOWN"),
        temperature=wall_temp,
        min_temp=_value(results, "coating_table_min_temperature", None),
        max_temp=_value(results, "coating_table_max_temperature", None),
        required=coating_required,
    )

    blocking = material_status["blocking"] + coating_status["blocking"]
    warnings = material_status["warnings"] + coating_status["warnings"]

    if blocking:
        status = "FAIL_PROPERTY_TABLE_BLOCKED"
    elif warnings:
        status = "WARN_PROPERTY_TABLE_LIMITED"
    else:
        status = "PASS_PROPERTY_TABLE_OWNER"

    text = build_property_table_report(
        status,
        wall_temp,
        material_status,
        coating_status,
        blocking,
        warnings,
    )

    return {
        "regen_property_table_owner_status": status,
        "regen_property_table_owner_wall_temperature": wall_temp,
        "regen_property_table_owner_blocking_reasons": blocking,
        "regen_property_table_owner_warning_reasons": warnings,
        "regen_property_table_owner_text": text,
        "regen_property_table_owner_pass_allowed": status == "PASS_PROPERTY_TABLE_OWNER",
        "regen_property_table_owner_coating_required": coating_required,
    }


def _table_status(
    label,
    table_status,
    interpolation_status,
    temperature,
    min_temp,
    max_temp,
    required=True,
):
    blocking = []
    warnings = []

    if not required:
        return {
            "label": label,
            "required": False,
            "table_status": "NOT_APPLICABLE",
            "interpolation_status": "NOT_APPLICABLE",
            "min_temperature": None,
            "max_temperature": None,
            "blocking": [],
            "warnings": [],
        }

    table_status_l = str(table_status).upper()
    interpolation_status_l = str(interpolation_status).upper()

    if table_status_l in {"UNKNOWN", "MISSING", "PLACEHOLDER", "NONE", "N/A", ""}:
        blocking.append(
            f"{label} temperature-dependent property table is missing or placeholder."
        )

    if interpolation_status_l in {"UNKNOWN", "FAILED", "OUT_OF_RANGE", "NONE", "N/A", ""}:
        warnings.append(
            f"{label} property interpolation status is {interpolation_status}."
        )

    try:
        t = float(temperature)
        t_min = float(min_temp)
        t_max = float(max_temp)

        if t < t_min or t > t_max:
            blocking.append(
                f"{label} wall temperature {t} K is outside property table range {t_min}–{t_max} K."
            )
    except Exception:
        warnings.append(f"{label} table range could not be fully checked.")

    return {
        "label": label,
        "required": True,
        "table_status": table_status,
        "interpolation_status": interpolation_status,
        "min_temperature": min_temp,
        "max_temperature": max_temp,
        "blocking": blocking,
        "warnings": warnings,
    }


def build_property_table_report(status, wall_temp, material_status, coating_status, blocking, warnings):
    lines = [
        "LEAF REGEN PROPERTY TABLE OWNERSHIP REPORT",
        "==========================================",
        "",
        f"Status: {status}",
        f"Wall temperature checked: {wall_temp}",
        "",
        "Material Table:",
        f"- Required: {material_status['required']}",
        f"- Table status: {material_status['table_status']}",
        f"- Interpolation status: {material_status['interpolation_status']}",
        f"- Temperature range: {material_status['min_temperature']} to {material_status['max_temperature']} K",
        "",
        "Coating Table:",
        f"- Required: {coating_status['required']}",
        f"- Table status: {coating_status['table_status']}",
        f"- Interpolation status: {coating_status['interpolation_status']}",
        f"- Temperature range: {coating_status['min_temperature']} to {coating_status['max_temperature']} K",
        "",
        "Blocking Reasons:",
    ]

    lines.extend([f"- {r}" for r in blocking] or ["- None."])

    lines.append("")
    lines.append("Warnings:")
    lines.extend([f"- {r}" for r in warnings] or ["- None."])

    lines.append("")
    lines.append("Rule:")
    lines.append("- Missing, placeholder, or out-of-range required property tables block final regen validation PASS.")
    lines.append("- Coating property tables are required only when a coating is actually selected.")

    return "\n".join(lines)


def _value(results, key, default=None):
    value = results.get(key, default)
    return default if value in (None, "") else value