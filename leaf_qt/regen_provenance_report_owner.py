def attach_regen_provenance_report(results):
    if not isinstance(results, dict):
        return results

    report = build_regen_provenance_report(results)

    results["regen_provenance_report_status"] = _status(results)
    results["regen_provenance_report_text"] = report
    results["regen_provenance_material_name"] = _value(results, "material_name", "UNKNOWN")
    results["regen_provenance_coating_name"] = _value(results, "coating_name", "NONE")
    results["regen_provenance_material_mode"] = _value(
        results,
        "regen_source_validation_material_mode",
        _value(results, "material_source_validation_mode", "UNKNOWN"),
    )
    results["regen_provenance_coating_mode"] = _value(
        results,
        "regen_source_validation_coating_mode",
        _value(results, "coating_source_validation_mode", "NONE"),
    )
    results["regen_provenance_material_score"] = _value(
        results,
        "regen_source_validation_material_score",
        0,
    )
    results["regen_provenance_coating_score"] = _value(
        results,
        "regen_source_validation_coating_score",
        0,
    )

    return results


def build_regen_provenance_report(results):
    material_name = _value(results, "material_name", "UNKNOWN")
    coating_name = _value(results, "coating_name", "NONE")

    material_mode = _value(
        results,
        "regen_source_validation_material_mode",
        _value(results, "material_source_validation_mode", "UNKNOWN"),
    )

    coating_mode = _value(
        results,
        "regen_source_validation_coating_mode",
        _value(results, "coating_source_validation_mode", "NONE"),
    )

    material_score = _value(results, "regen_source_validation_material_score", 0)
    coating_score = _value(results, "regen_source_validation_coating_score", 0)

    material_placeholder = _value(results, "material_source_is_placeholder", False)
    coating_placeholder = _value(results, "coating_source_is_placeholder", False)

    temperature_table_status = _value(
        results,
        "material_temperature_table_status",
        "UNKNOWN",
    )

    coating_temperature_table_status = _value(
        results,
        "coating_temperature_table_status",
        "UNKNOWN",
    )

    interpolation_status = _value(
        results,
        "material_property_interpolation_status",
        "UNKNOWN",
    )

    coating_interpolation_status = _value(
        results,
        "coating_property_interpolation_status",
        "UNKNOWN",
    )

    pass_allowed = _value(results, "regen_source_validation_pass_allowed", False)

    lines = [
        "LEAF REGEN MATERIAL AND COATING PROVENANCE REPORT",
        "=================================================",
        "",
        f"Status: {_status(results)}",
        f"Regen PASS allowed: {pass_allowed}",
        "",
        "Material:",
        f"- Name: {material_name}",
        f"- Source validation mode: {material_mode}",
        f"- Source score: {material_score}",
        f"- Placeholder: {material_placeholder}",
        f"- Temperature table status: {temperature_table_status}",
        f"- Interpolation status: {interpolation_status}",
        "",
        "Coating:",
        f"- Name: {coating_name}",
        f"- Source validation mode: {coating_mode}",
        f"- Source score: {coating_score}",
        f"- Placeholder: {coating_placeholder}",
        f"- Temperature table status: {coating_temperature_table_status}",
        f"- Interpolation status: {coating_interpolation_status}",
        "",
        "Source Validation Gate:",
        f"- Gate status: {_value(results, 'regen_source_validation_gate_status', 'N/A')}",
        f"- Conservative gate: {_value(results, 'regen_conservative_validation_gate_status', 'N/A')}",
        f"- Gate reason: {_value(results, 'regen_conservative_validation_gate_reason', 'N/A')}",
        "",
        "Rule:",
        "- Placeholder or insufficient source data cannot produce final PASS.",
        "- Partial source data may support review but cannot produce final sourced validation PASS.",
        "- Final PASS requires sourced validation mode and acceptable source confidence.",
    ]

    return "\n".join(lines)


def _status(results):
    if not _value(results, "regen_source_validation_pass_allowed", False):
        return "PROVENANCE_BLOCKS_FINAL_PASS"

    return "PROVENANCE_SUPPORTS_SOURCED_VALIDATION"


def _value(results, key, default=None):
    value = results.get(key, default)

    if value in (None, ""):
        return default

    return value