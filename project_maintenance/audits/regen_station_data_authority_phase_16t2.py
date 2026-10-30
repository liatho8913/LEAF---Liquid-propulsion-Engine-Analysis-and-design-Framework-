from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PHASE = "16T.2"

PASS_STATUS = "PASS_REGEN_STATION_DATA_AUTHORITY_PHASE_16T2"
WARN_STATUS = "WARN_REGEN_STATION_DATA_AUTHORITY_PHASE_16T2"
FAIL_STATUS = "FAIL_REGEN_STATION_DATA_AUTHORITY_PHASE_16T2"

AUTH_SOLVER = "solver_authoritative"
AUTH_GEOMETRY = "geometry_authoritative"
AUTH_FALLBACK = "fallback"
AUTH_SCHEMATIC = "schematic"
AUTH_PLACEHOLDER = "placeholder"
AUTH_UNAVAILABLE = "unavailable"
AUTH_MIXED = "mixed"

REQUIRED_STATION_KEYS = (
    "mach",
    "static_pressure",
    "static_temperature",
    "adiabatic_wall_temperature",
    "heat_flux",
    "hot_gas_side_wall_temperature",
    "coolant_side_wall_temperature",
    "coolant_inlet_temperature",
    "coolant_outlet_temperature",
    "coolant_velocity",
    "coolant_reynolds_number",
    "coolant_pressure_drop",
    "gas_radius",
)

STATION_ROW_COLLECTION_KEYS = (
    "regen_station_rows",
    "regen_axial_station_rows",
    "axial_station_rows",
    "full_engine_regen_station_rows",
    "station_rows",
    "stations",
)


@dataclass(frozen=True)
class StationAuthorityResult:
    status: str
    passed: bool
    station_row_count: int
    authoritative_row_count: int
    fallback_row_count: int
    schematic_row_count: int
    placeholder_row_count: int
    unavailable_row_count: int
    mixed_row_count: int
    blockers: list[str]
    warnings: list[str]
    rows: list[dict[str, Any]]


def _normalise(value: Any) -> str:
    return str(value).strip().lower().replace("-", "_")


def _missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and _normalise(value) in {"", "none", "null", "n/a", "na", "unavailable", "unknown"}:
        return True
    return False


def extract_station_rows(results: dict[str, Any]) -> tuple[str | None, list[dict[str, Any]]]:
    if not isinstance(results, dict):
        return None, []

    for key in STATION_ROW_COLLECTION_KEYS:
        rows = results.get(key)
        if isinstance(rows, list):
            return key, [row for row in rows if isinstance(row, dict)]

    return None, []


def _row_source_text(row: dict[str, Any]) -> str:
    parts = []

    for key in (
        "source",
        "authority",
        "source_classification",
        "authority_classification",
        "station_source",
        "station_authority",
        "data_origin",
        "profile_radius_source",
    ):
        if key in row and not _missing(row.get(key)):
            parts.append(_normalise(row.get(key)))

    for key, value in row.items():
        key_text = _normalise(key)
        if key_text.endswith("_source") or key_text.endswith("_authority"):
            parts.append(_normalise(value))

    return " ".join(parts)


def classify_station_row(row: dict[str, Any]) -> str:
    if not isinstance(row, dict) or not row:
        return AUTH_UNAVAILABLE

    source_text = _row_source_text(row)

    if any(token in source_text for token in ("placeholder", "stub", "todo", "dummy", "not_implemented")):
        return AUTH_PLACEHOLDER

    if any(token in source_text for token in ("schematic", "illustrative", "visual_only")):
        return AUTH_SCHEMATIC

    if any(token in source_text for token in ("fallback", "viewer_derived", "estimated", "derived_viewer")):
        return AUTH_FALLBACK

    if any(token in source_text for token in ("solver", "regen_solver", "axial_solver", "directed_solver", "bartz")):
        return AUTH_SOLVER

    if any(token in source_text for token in ("geometry", "manual", "automatic", "station_geometry", "nozzle_profile")):
        return AUTH_GEOMETRY

    present_required = [key for key in REQUIRED_STATION_KEYS if not _missing(row.get(key))]
    if len(present_required) >= 9:
        return AUTH_MIXED

    if present_required:
        return AUTH_FALLBACK

    return AUTH_UNAVAILABLE


def _missing_required_keys(row: dict[str, Any]) -> list[str]:
    return [key for key in REQUIRED_STATION_KEYS if _missing(row.get(key))]


def build_regen_station_data_authority_audit(results: dict[str, Any]) -> dict[str, Any]:
    collection_key, station_rows = extract_station_rows(results)

    analysed_rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    warnings: list[str] = []

    counts = {
        AUTH_SOLVER: 0,
        AUTH_GEOMETRY: 0,
        AUTH_FALLBACK: 0,
        AUTH_SCHEMATIC: 0,
        AUTH_PLACEHOLDER: 0,
        AUTH_UNAVAILABLE: 0,
        AUTH_MIXED: 0,
    }

    if not station_rows:
        blockers.append("No regen station rows were found.")
        return {
            "phase": PHASE,
            "status": FAIL_STATUS,
            "passed": False,
            "collection_key": collection_key,
            "station_row_count": 0,
            "authoritative_row_count": 0,
            "classified_counts": counts,
            "rows": [],
            "blockers": blockers,
            "warnings": warnings,
            "summary": "0 station rows available for regen calculator authority.",
        }

    for index, row in enumerate(station_rows):
        authority = classify_station_row(row)
        missing_keys = _missing_required_keys(row)
        counts[authority] = counts.get(authority, 0) + 1

        row_report = {
            "index": index,
            "authority": authority,
            "missing_required_keys": missing_keys,
            "required_key_count": len(REQUIRED_STATION_KEYS),
            "present_required_key_count": len(REQUIRED_STATION_KEYS) - len(missing_keys),
            "source_text": _row_source_text(row),
        }
        analysed_rows.append(row_report)

        if authority in {AUTH_PLACEHOLDER, AUTH_UNAVAILABLE}:
            blockers.append(f"Station row {index} is {authority}.")

        if authority in {AUTH_FALLBACK, AUTH_SCHEMATIC, AUTH_MIXED}:
            warnings.append(f"Station row {index} is {authority}; final reports must label it clearly.")

        if authority in {AUTH_SOLVER, AUTH_MIXED} and missing_keys:
            warnings.append(f"Station row {index} is missing required values: {', '.join(missing_keys)}.")

    authoritative_row_count = counts[AUTH_SOLVER] + counts[AUTH_GEOMETRY]

    if authoritative_row_count == 0:
        blockers.append("No solver-authoritative or geometry-authoritative station rows were found.")

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
        "collection_key": collection_key,
        "station_row_count": len(station_rows),
        "authoritative_row_count": authoritative_row_count,
        "classified_counts": counts,
        "rows": analysed_rows,
        "blockers": blockers,
        "warnings": warnings,
        "summary": f"{authoritative_row_count}/{len(station_rows)} station rows are solver/geometry authoritative.",
    }


def attach_regen_station_data_authority_audit(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    audit = build_regen_station_data_authority_audit(results)

    results["phase_16t2_regen_station_data_authority_status"] = audit["status"]
    results["phase_16t2_regen_station_data_authority_pass"] = audit["passed"]
    results["phase_16t2_regen_station_data_authority_summary"] = audit["summary"]
    results["phase_16t2_regen_station_data_authority_counts"] = audit["classified_counts"]
    results["phase_16t2_regen_station_data_authority_rows"] = audit["rows"]
    results["phase_16t2_regen_station_data_authority_blockers"] = audit["blockers"]
    results["phase_16t2_regen_station_data_authority_warnings"] = audit["warnings"]
    results["phase_16t2_regen_station_data_authority_audit"] = audit

    return results


def build_regen_station_data_authority_report(results: dict[str, Any]) -> str:
    audit = build_regen_station_data_authority_audit(results)

    lines = [
        "REGEN STATION DATA AUTHORITY AUDIT",
        "==================================",
        f"Phase: {audit['phase']}",
        f"Status: {audit['status']}",
        f"Passed: {audit['passed']}",
        f"Collection key: {audit['collection_key']}",
        f"Summary: {audit['summary']}",
        "",
        "CLASSIFIED ROW COUNTS",
        "---------------------",
    ]

    for key, value in audit["classified_counts"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "STATION ROWS", "------------"])

    for row in audit["rows"]:
        missing = ", ".join(row["missing_required_keys"]) if row["missing_required_keys"] else "none"
        lines.append(
            f"row {row['index']}: authority={row['authority']} | "
            f"present_required={row['present_required_key_count']}/{row['required_key_count']} | "
            f"missing={missing}"
        )

    if audit["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in audit["warnings"])

    if audit["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in audit["blockers"])

    return "\n".join(lines)
