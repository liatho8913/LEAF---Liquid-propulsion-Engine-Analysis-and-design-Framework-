from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


PHASE = "16T.1"
PASS_STATUS = "PASS_REGEN_CALCULATOR_DATA_AUTHORITY_AUDIT_PHASE_16T1"
WARN_STATUS = "WARN_REGEN_CALCULATOR_DATA_AUTHORITY_AUDIT_PHASE_16T1"
FAIL_STATUS = "FAIL_REGEN_CALCULATOR_DATA_AUTHORITY_AUDIT_PHASE_16T1"

SOURCE_SOLVER = "solver"
SOURCE_GEOMETRY = "geometry"
SOURCE_FALLBACK = "fallback"
SOURCE_PLACEHOLDER = "placeholder"
SOURCE_UNAVAILABLE = "unavailable"

BLOCKING_SOURCES = {SOURCE_PLACEHOLDER, SOURCE_UNAVAILABLE}
CAUTION_SOURCES = {SOURCE_FALLBACK}


@dataclass(frozen=True)
class RegenOutputAuthoritySpec:
    key: str
    label: str
    unit: str
    required_for_signoff: bool
    preferred_source: str
    aliases: tuple[str, ...] = ()
    allowed_fallback: bool = False
    notes: str = ""


REGEN_CALCULATOR_AUTHORITY_REGISTRY: tuple[RegenOutputAuthoritySpec, ...] = (
    RegenOutputAuthoritySpec("mach", "Local Mach number", "-", True, SOURCE_SOLVER, ("viewer_station_mach", "Mach", "M")),
    RegenOutputAuthoritySpec("static_pressure", "Static pressure", "Pa", True, SOURCE_SOLVER, ("viewer_station_static_pressure", "pressure", "p")),
    RegenOutputAuthoritySpec("static_temperature", "Static temperature", "K", True, SOURCE_SOLVER, ("viewer_station_static_temperature", "temperature", "T")),
    RegenOutputAuthoritySpec("adiabatic_wall_temperature", "Adiabatic wall temperature", "K", True, SOURCE_SOLVER, ("viewer_station_adiabatic_wall_temperature", "Taw")),
    RegenOutputAuthoritySpec("heat_flux", "Heat flux", "W/m^2", True, SOURCE_SOLVER, ("viewer_station_heat_flux", "q_dot", "q_flux", "heat_flux_w_m2")),
    RegenOutputAuthoritySpec("hot_gas_side_wall_temperature", "Gas-side wall temperature", "K", True, SOURCE_SOLVER, ("viewer_station_hot_wall_temperature", "Twg", "wall_temperature_gas_side")),
    RegenOutputAuthoritySpec("coolant_side_wall_temperature", "Coolant-side wall temperature", "K", True, SOURCE_SOLVER, ("viewer_station_coolant_wall_temperature", "Twc", "wall_temperature_coolant_side")),
    RegenOutputAuthoritySpec("coolant_inlet_temperature", "Coolant inlet temperature", "K", True, SOURCE_SOLVER, ("viewer_station_coolant_in", "coolant_in", "T_coolant_in")),
    RegenOutputAuthoritySpec("coolant_outlet_temperature", "Coolant outlet temperature", "K", True, SOURCE_SOLVER, ("viewer_station_coolant_out", "coolant_out", "T_coolant_out")),
    RegenOutputAuthoritySpec("coolant_velocity", "Coolant velocity", "m/s", True, SOURCE_SOLVER, ("viewer_station_coolant_velocity",)),
    RegenOutputAuthoritySpec("coolant_reynolds_number", "Coolant Reynolds number", "-", True, SOURCE_SOLVER, ("viewer_station_reynolds_number", "reynolds_number", "Re_coolant")),
    RegenOutputAuthoritySpec("coolant_pressure_drop", "Coolant pressure drop", "Pa", True, SOURCE_SOLVER, ("viewer_station_pressure_drop_total", "pressure_drop_total", "delta_p_coolant")),
    RegenOutputAuthoritySpec("gas_radius", "Local gas radius", "m", True, SOURCE_GEOMETRY, ("viewer_station_gas_radius", "radius", "local_gas_radius")),
    RegenOutputAuthoritySpec("coolant_channel_width", "Coolant channel width", "m", True, SOURCE_GEOMETRY, ("viewer_station_coolant_channel_width", "channel_width", "viewer_station_channel_width")),
    RegenOutputAuthoritySpec("coolant_channel_height", "Coolant channel height", "m", True, SOURCE_GEOMETRY, ("viewer_station_coolant_channel_height", "channel_height", "viewer_station_channel_height")),
    RegenOutputAuthoritySpec("rib_width", "Rib width", "m", True, SOURCE_GEOMETRY, ("viewer_station_rib_width", "requested_rib_width", "effective_rib_width")),
    RegenOutputAuthoritySpec("number_of_coolant_channels", "Number of coolant channels", "count", True, SOURCE_GEOMETRY, ("viewer_station_number_of_coolant_channels", "channel_count", "n_channels")),
    RegenOutputAuthoritySpec("cooling_coverage", "Cooling coverage", "fraction", True, SOURCE_GEOMETRY, ("viewer_station_cooling_coverage",)),
    RegenOutputAuthoritySpec("channel_fit_ratio", "Channel fit ratio", "-", True, SOURCE_GEOMETRY, ("viewer_station_channel_fit_ratio",)),
    RegenOutputAuthoritySpec("manufacturability_status", "Manufacturability status", "status", True, SOURCE_SOLVER, ("phase_16q3_manufacturability_status", "regen_manufacturability_status")),
    RegenOutputAuthoritySpec("engineering_realism_score", "Engineering realism score", "0-100", False, SOURCE_SOLVER, ("realism_score", "phase_16q8_realism_score"), True),
)


PLACEHOLDER_TOKENS = ("placeholder", "stub", "todo", "not implemented", "dummy")
FALLBACK_TOKENS = ("fallback", "schematic", "estimated", "derived_viewer", "viewer_derived")
UNAVAILABLE_TOKENS = ("unavailable", "unknown", "n/a", "na", "none", "null", "")
SOLVER_TOKENS = ("solver", "regen_solver", "axial_solver", "directed_solver", "cea", "bartz")
GEOMETRY_TOKENS = ("geometry", "manual", "automatic", "station_geometry", "nozzle_profile")


def _normalise_token(value: Any) -> str:
    return str(value).strip().lower().replace("-", "_")


def _is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and _normalise_token(value) in UNAVAILABLE_TOKENS:
        return True
    return False


def _first_present(container: dict[str, Any], keys: Iterable[str]) -> tuple[str | None, Any]:
    for key in keys:
        if key in container and not _is_missing_value(container.get(key)):
            return key, container.get(key)
    return None, None


def _get_nested_source(results: dict[str, Any], used_key: str | None) -> Any:
    if not used_key:
        return None
    for key in (
        f"{used_key}_source",
        f"{used_key}_authority",
        f"{used_key}_source_classification",
        f"{used_key}_authority_classification",
    ):
        if key in results and not _is_missing_value(results.get(key)):
            return results.get(key)
    return None


def _classify_source(raw_source: Any, preferred_source: str, used_key: str | None, value: Any) -> str:
    if used_key is None or _is_missing_value(value):
        return SOURCE_UNAVAILABLE

    source_text = _normalise_token(raw_source) if raw_source is not None else ""
    value_text = _normalise_token(value) if isinstance(value, str) else ""
    key_text = _normalise_token(used_key)
    combined = " ".join((source_text, value_text, key_text))

    if any(token in combined for token in PLACEHOLDER_TOKENS):
        return SOURCE_PLACEHOLDER
    if any(token in combined for token in FALLBACK_TOKENS):
        return SOURCE_FALLBACK
    if source_text:
        if any(token in source_text for token in SOLVER_TOKENS):
            return SOURCE_SOLVER
        if any(token in source_text for token in GEOMETRY_TOKENS):
            return SOURCE_GEOMETRY
        if any(token in source_text for token in UNAVAILABLE_TOKENS):
            return SOURCE_UNAVAILABLE

    return preferred_source


def _station_rows(results: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("regen_station_rows", "regen_axial_station_rows", "axial_station_rows", "full_engine_regen_station_rows", "station_rows", "stations"):
        rows = results.get(key)
        if isinstance(rows, list) and rows:
            return [row for row in rows if isinstance(row, dict)]
    return []


def _station_value_and_source(rows: list[dict[str, Any]], spec: RegenOutputAuthoritySpec) -> tuple[str | None, Any, Any]:
    if not rows:
        return None, None, None

    for row in rows:
        used_key, value = _first_present(row, (spec.key, *spec.aliases))
        if used_key is not None:
            return used_key, value, _get_nested_source(row, used_key) or row.get("source") or row.get("authority")
    return None, None, None


def resolve_output_authority(results: dict[str, Any], spec: RegenOutputAuthoritySpec) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    used_key, value = _first_present(results, (spec.key, *spec.aliases))
    raw_source = _get_nested_source(results, used_key)

    if used_key is None:
        used_key, value, raw_source = _station_value_and_source(_station_rows(results), spec)

    source_classification = _classify_source(raw_source, spec.preferred_source, used_key, value)

    blocking = bool(spec.required_for_signoff and source_classification in BLOCKING_SOURCES)
    caution = bool(source_classification in CAUTION_SOURCES and not spec.allowed_fallback)

    return {
        "key": spec.key,
        "label": spec.label,
        "unit": spec.unit,
        "required_for_signoff": spec.required_for_signoff,
        "preferred_source": spec.preferred_source,
        "used_key": used_key,
        "value": value,
        "raw_source": raw_source,
        "source_classification": source_classification,
        "blocking": blocking,
        "caution": caution,
        "allowed_fallback": spec.allowed_fallback,
        "notes": spec.notes,
    }


def build_regen_calculator_data_authority_audit(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    outputs = [resolve_output_authority(results, spec) for spec in REGEN_CALCULATOR_AUTHORITY_REGISTRY]

    blockers = []
    warnings = []

    for output in outputs:
        if output["blocking"]:
            blockers.append(f"{output['key']} is required for regen sign-off but is {output['source_classification']}.")
        if output["caution"]:
            warnings.append(f"{output['key']} is fallback-derived and must be labelled in calculator/report outputs.")

    classified_counts = {
        SOURCE_SOLVER: 0,
        SOURCE_GEOMETRY: 0,
        SOURCE_FALLBACK: 0,
        SOURCE_PLACEHOLDER: 0,
        SOURCE_UNAVAILABLE: 0,
    }

    for output in outputs:
        classified_counts[output["source_classification"]] = classified_counts.get(output["source_classification"], 0) + 1

    required_outputs = [o for o in outputs if o["required_for_signoff"]]
    authoritative_required = [o for o in required_outputs if o["source_classification"] in {SOURCE_SOLVER, SOURCE_GEOMETRY}]

    if blockers:
        status = FAIL_STATUS
        passed = False
    elif warnings:
        status = WARN_STATUS
        passed = True
    else:
        status = PASS_STATUS
        passed = True

    return {
        "phase": PHASE,
        "status": status,
        "passed": passed,
        "output_count": len(outputs),
        "required_output_count": len(required_outputs),
        "authoritative_required_count": len(authoritative_required),
        "classified_counts": classified_counts,
        "outputs": outputs,
        "blockers": blockers,
        "warnings": warnings,
        "station_row_count": len(_station_rows(results)),
        "summary": f"{len(authoritative_required)}/{len(required_outputs)} required regen calculator outputs resolved to solver/geometry authority.",
    }


def attach_regen_calculator_data_authority_audit(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    audit = build_regen_calculator_data_authority_audit(results)
    results["phase_16t1_regen_calculator_data_authority_status"] = audit["status"]
    results["phase_16t1_regen_calculator_data_authority_pass"] = audit["passed"]
    results["phase_16t1_regen_calculator_data_authority_summary"] = audit["summary"]
    results["phase_16t1_regen_calculator_data_authority_blockers"] = audit["blockers"]
    results["phase_16t1_regen_calculator_data_authority_warnings"] = audit["warnings"]
    results["phase_16t1_regen_calculator_data_authority_counts"] = audit["classified_counts"]
    results["phase_16t1_regen_calculator_data_authority_outputs"] = audit["outputs"]
    results["phase_16t1_regen_calculator_data_authority_audit"] = audit
    return results


def build_regen_calculator_data_authority_report(results: dict[str, Any]) -> str:
    audit = build_regen_calculator_data_authority_audit(results)

    lines = [
        "REGEN CALCULATOR DATA AUTHORITY AUDIT",
        "======================================",
        f"Phase: {audit['phase']}",
        f"Status: {audit['status']}",
        f"Passed: {audit['passed']}",
        f"Summary: {audit['summary']}",
        f"Station rows detected: {audit['station_row_count']}",
        "",
        "CLASSIFIED SOURCE COUNTS",
        "------------------------",
    ]

    for source, count in audit["classified_counts"].items():
        lines.append(f"{source}: {count}")

    lines.extend(["", "OUTPUT AUTHORITY TABLE", "----------------------"])

    for output in audit["outputs"]:
        value = output["value"] if output["value"] is not None else "UNAVAILABLE"
        lines.append(
            f"{output['key']} [{output['unit']}]: {value} | "
            f"source={output['source_classification']} | "
            f"used_key={output['used_key']} | "
            f"required={output['required_for_signoff']}"
        )

    if audit["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in audit["warnings"])

    if audit["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in audit["blockers"])

    return "\n".join(lines)
