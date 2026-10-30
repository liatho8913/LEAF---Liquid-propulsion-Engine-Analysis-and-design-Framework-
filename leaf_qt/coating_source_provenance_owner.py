"""
LEAF Coating Source / Provenance Owner
======================================

REGEN PHASE 9F

Owns coating source and provenance metadata.

This module does NOT:
- validate coating performance
- rank coating sources
- approve coating use
- replace regen thermal solver coating logic
"""

DEFAULT_COATING_SOURCE_RECORDS = {
    "None": {
        "coating": "None",
        "mode": "NO_COATING_MODE",
        "source_quality": "NO_COATING_SELECTED",
        "sources": [],
    },
    "Generic TBC": {
        "coating": "Generic TBC",
        "mode": "PLACEHOLDER_MODE",
        "source_quality": "ENGINEERING_PLACEHOLDER_PENDING_FULL_SOURCE_TABLE",
        "sources": [
            {
                "source_id": "GENERIC_TBC_PLACEHOLDER_001",
                "source_type": "engineering_placeholder",
                "title": "Placeholder generic thermal barrier coating record",
                "citation": "Internal placeholder pending sourced coating database.",
                "confidence": 0.20,
                "properties_covered": [
                    "thermal_conductivity",
                    "max_service_temperature",
                    "bond_compatibility",
                    "thickness_range",
                ],
                "is_placeholder": True,
            }
        ],
    },
}


def attach_coating_source_provenance_owner(results):
    if not isinstance(results, dict):
        return results

    provenance = build_coating_source_provenance_owner(results)
    results.update(provenance)
    return results


def build_coating_source_provenance_owner(results):
    results = results if isinstance(results, dict) else {}

    coating_name = _normalise_text(
        results.get("selected_coating")
        or results.get("coating")
        or results.get("regen_coating")
        or results.get("coating_name"),
        default="None",
    )

    records = results.get("coating_source_records")
    if not isinstance(records, dict):
        records = DEFAULT_COATING_SOURCE_RECORDS

    record = records.get(coating_name)

    blockers = []
    warnings = []

    if not isinstance(record, dict):
        blockers.append(f"No coating source/provenance record exists for {coating_name}.")
        mode = "MISSING_COATING_SOURCE_MODE"
        source_quality = "NO_SOURCE"
        sources = []
    else:
        mode = _normalise_text(record.get("mode"), default="UNKNOWN_MODE")
        source_quality = _normalise_text(
            record.get("source_quality"),
            default="UNKNOWN_SOURCE_QUALITY",
        )
        sources = record.get("sources", [])

        if not isinstance(sources, list):
            blockers.append(f"Coating source record for {coating_name} has invalid sources list.")
            sources = []

    normalised_sources = [_normalise_source(source) for source in sources]
    normalised_sources = [source for source in normalised_sources if source is not None]

    no_coating_selected = coating_name.lower() in {"none", "no coating", "uncoated"}

    if not normalised_sources and not no_coating_selected:
        blockers.append(f"No usable coating source entries exist for {coating_name}.")

    placeholder_count = sum(1 for source in normalised_sources if source["is_placeholder"])
    source_count = len(normalised_sources)

    confidence_values = [
        source["confidence"]
        for source in normalised_sources
        if source["confidence"] is not None
    ]

    average_confidence = (
        round(sum(confidence_values) / len(confidence_values), 6)
        if confidence_values
        else 0.0
    )

    properties_covered = sorted({
        prop
        for source in normalised_sources
        for prop in source.get("properties_covered", [])
    })

    if placeholder_count > 0:
        warnings.append(
            f"{placeholder_count} placeholder coating source(s) are present; conservative coating validation pass remains blocked."
        )

    if no_coating_selected:
        warnings.append(
            "No coating is selected; coating provenance is treated as structurally complete but not as coating validation."
        )

    if mode not in {"SOURCED_VALIDATION_MODE", "NO_COATING_MODE"}:
        warnings.append(
            f"Coating is not in SOURCED_VALIDATION_MODE; current mode is {mode}."
        )

    conservative_pass_allowed = (
        no_coating_selected
        or (
            not blockers
            and source_count > 0
            and placeholder_count == 0
            and mode == "SOURCED_VALIDATION_MODE"
            and source_quality == "FULLY_SOURCED"
            and average_confidence >= 0.75
        )
    )

    complete = not blockers

    status = (
        "PASS_COATING_SOURCE_PROVENANCE_OWNER"
        if complete
        else "FAIL_COATING_SOURCE_PROVENANCE_OWNER"
    )

    text = build_coating_source_provenance_text(
        status=status,
        coating_name=coating_name,
        mode=mode,
        source_quality=source_quality,
        source_count=source_count,
        placeholder_count=placeholder_count,
        average_confidence=average_confidence,
        properties_covered=properties_covered,
        sources=normalised_sources,
        blockers=blockers,
        warnings=warnings,
        conservative_pass_allowed=conservative_pass_allowed,
        no_coating_selected=no_coating_selected,
    )

    return {
        "coating_source_provenance_owner_status": status,
        "coating_source_provenance_owner_complete": complete,
        "coating_source_provenance_coating": coating_name,
        "coating_source_provenance_mode": mode,
        "coating_source_provenance_source_quality": source_quality,
        "coating_source_provenance_sources": normalised_sources,
        "coating_source_provenance_source_count": source_count,
        "coating_source_provenance_placeholder_count": placeholder_count,
        "coating_source_provenance_average_confidence": average_confidence,
        "coating_source_provenance_properties_covered": properties_covered,
        "coating_source_provenance_blockers": blockers,
        "coating_source_provenance_warnings": warnings,
        "coating_source_provenance_no_coating_selected": no_coating_selected,
        "coating_source_provenance_conservative_pass_allowed": conservative_pass_allowed,
        "coating_source_provenance_text": text,
        "phase_9f_coating_source_provenance_owner_complete": complete,
    }


def build_coating_source_provenance_text(
        status,
        coating_name,
        mode,
        source_quality,
        source_count,
        placeholder_count,
        average_confidence,
        properties_covered,
        sources,
        blockers,
        warnings,
        conservative_pass_allowed,
        no_coating_selected,
):
    lines = [
        "LEAF REGEN PHASE 9F COATING SOURCE / PROVENANCE OWNER",
        "======================================================",
        "",
        f"Status: {status}",
        f"Coating: {coating_name}",
        f"No coating selected: {no_coating_selected}",
        f"Validation mode: {mode}",
        f"Source quality: {source_quality}",
        f"Source count: {source_count}",
        f"Placeholder source count: {placeholder_count}",
        f"Average confidence: {average_confidence}",
        f"Conservative pass allowed: {conservative_pass_allowed}",
        "",
        "Owned By:",
        "- coating_source_provenance_owner.py",
        "",
        "Scope:",
        "- Owns coating source metadata.",
        "- Owns coating provenance evidence.",
        "- Owns placeholder coating-source detection.",
        "- Owns coating source confidence summaries.",
        "- Does not validate coating performance.",
        "- Does not approve coating use by itself.",
        "",
        "Properties Covered:",
    ]

    if properties_covered:
        for prop in properties_covered:
            lines.append(f"- {prop}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Sources:")

    if sources:
        for source in sources:
            lines.append("")
            lines.append(f"- Source ID: {source.get('source_id')}")
            lines.append(f"  Type: {source.get('source_type')}")
            lines.append(f"  Title: {source.get('title')}")
            lines.append(f"  Citation: {source.get('citation')}")
            lines.append(f"  Confidence: {source.get('confidence')}")
            lines.append(f"  Placeholder: {source.get('is_placeholder')}")
            lines.append(f"  Properties: {source.get('properties_covered')}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Warnings:")

    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Blockers:")

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Next Required Action:")
    lines.append(
        "- After Phase 9F is verified, build Phase 9G coating validation owner."
    )

    return "\n".join(lines)


def _normalise_source(source):
    if not isinstance(source, dict):
        return None

    source_id = _normalise_text(source.get("source_id"), default="")
    if not source_id:
        return None

    properties = source.get("properties_covered", [])
    if isinstance(properties, str):
        properties = [item.strip() for item in properties.split(",") if item.strip()]
    elif isinstance(properties, (list, tuple, set)):
        properties = [str(item).strip() for item in properties if str(item).strip()]
    else:
        properties = []

    return {
        "source_id": source_id,
        "source_type": _normalise_text(source.get("source_type"), default="UNKNOWN"),
        "title": _normalise_text(source.get("title"), default="UNKNOWN"),
        "citation": _normalise_text(source.get("citation"), default="UNKNOWN"),
        "confidence": _clamp01(_safe_float(source.get("confidence"), default=0.0)),
        "properties_covered": properties,
        "is_placeholder": _bool_value(source.get("is_placeholder"), default=False),
    }


def _normalise_text(value, default=""):
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _clamp01(value):
    return max(0.0, min(1.0, float(value)))


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