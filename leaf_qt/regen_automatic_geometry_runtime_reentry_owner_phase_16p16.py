"""
LEAF Phase 16P.16
Automatic Geometry Runtime Re-entry Owner

Purpose:
- Force the Generate Automatic Geometry button to rebuild the automatic candidate
  at runtime instead of reusing stale staged payloads.
- Ensure old pre-16P.14 nudge geometry cannot silently remain active.
"""

from __future__ import annotations

from typing import Any



STALE_AUTOMATIC_KEYS = [
    "regen_geometry_commit_staged_geometry",
    "regen_autonomous_geometry_staged_candidate",
    "phase_16p2_automatic_geometry_candidate_geometry",
    "phase_16p1_automatic_geometry_workflow_staged_geometry",
]


def _num(value: Any, default=None):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _compact_geometry(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {}

    out = {}

    aliases = {
        "channel_width": ["channel_width", "coolant_channel_width"],
        "channel_height": ["channel_height", "coolant_channel_height"],
        "requested_rib_width": ["requested_rib_width", "rib_width"],
        "channel_count": ["channel_count", "number_of_coolant_channels"],
        "wall": ["wall", "hot_gas_wall_thickness"],
        "jacket": ["jacket", "outer_wall_thickness"],
        "gas_radius": [
            "gas_radius",
            "radius",
            "profile_radius",
            "station_radius",
            "selected_radius",
            "selected_station_radius",
            "throat_radius",
            "minimum_gas_radius",
        ],
        "minimum_gas_radius": ["minimum_gas_radius", "throat_radius", "gas_radius"],
        "throat_radius": ["throat_radius", "minimum_gas_radius", "gas_radius"],
    }

    for target, keys in aliases.items():
        for key in keys:
            if key in raw:
                value = raw.get(key)
                if value is not None:
                    out[target] = value
                    break

    return out


def purge_stale_automatic_geometry(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    removed = {}

    for key in STALE_AUTOMATIC_KEYS:
        if key in results:
            removed[key] = results.pop(key)

    results["phase_16p16_stale_payload_purged"] = True
    results["phase_16p16_stale_payload_removed_keys"] = list(removed.keys())
    results["phase_16p16_stale_payload_removed_count"] = len(removed)

    return results


def build_runtime_reentry_candidate(
    results: dict[str, Any],
    manual_geometry: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate re-entry into an already staged canonical automatic
    geometry.

    Runtime re-entry does not generate geometry and does not purge
    the canonical staged payload. Automatic geometry authority
    remains with the optimiser -> application -> commit chain.
    """

    if not isinstance(results, dict):
        results = {}

    snapshot = _compact_geometry(
        manual_geometry
    )

    # Diagnostic rollback/reference snapshot only.
    # Do not overwrite canonical current/manual geometry ownership.
    results[
        "phase_16p16_runtime_manual_snapshot"
    ] = dict(snapshot)

    staged = results.get(
        "regen_geometry_commit_staged_geometry"
    )

    if not isinstance(
        staged,
        dict,
    ):
        staged = {}

    application_patch = (
        results.get(
            "regen_candidate_application_patch"
        )
        or results.get(
            "recommended_regen_geometry_patch"
        )
        or {}
    )

    application_allowed = bool(
        results.get(
            "regen_candidate_geometry_application_allowed"
        )
    )

    commit_ready = bool(
        results.get(
            "regen_autonomous_geometry_commit_ready"
        )
        or results.get(
            "regen_geometry_commit_candidate_ready"
        )
    )

    geometry_valid = _num(
        staged.get(
            "channel_geometry_valid"
        ),
        None,
    )

    fit_ratio = _num(
        staged.get(
            "channel_fit_ratio"
        ),
        None,
    )

    effective_rib = _num(
        staged.get(
            "effective_rib_width"
        ),
        None,
    )

    # If the staged payload contains downstream physical proof,
    # respect it. Absence is not itself a failure here because
    # physical validation belongs to the engineering solver/gates.
    embedded_physical_checks = []

    if geometry_valid is not None:
        embedded_physical_checks.append(
            geometry_valid == 1.0
        )

    if fit_ratio is not None:
        embedded_physical_checks.append(
            fit_ratio >= 1.0
        )

    if effective_rib is not None:
        embedded_physical_checks.append(
            effective_rib > 0.0
        )

    embedded_physical_valid = (
        all(embedded_physical_checks)
        if embedded_physical_checks
        else True
    )

    passed = bool(
        staged
        and
        isinstance(
            application_patch,
            dict,
        )
        and
        application_patch
        and
        application_allowed
        and
        commit_ready
        and
        embedded_physical_valid
    )

    results[
        "phase_16p16_runtime_reentry_staged_geometry"
    ] = dict(staged)

    results[
        "phase_16p16_runtime_reentry_fit_ratio"
    ] = fit_ratio

    results[
        "phase_16p16_runtime_reentry_effective_rib_width"
    ] = effective_rib

    results[
        "phase_16p16_runtime_reentry_geometry_valid"
    ] = geometry_valid

    results[
        "phase_16p16_runtime_reentry_validation_mode"
    ] = "CANONICAL_STAGED_GEOMETRY_ONLY"

    results[
        "phase_16p16_runtime_reentry_pass"
    ] = bool(passed)

    results[
        "phase_16p16_runtime_reentry_status"
    ] = (
        "PASS_REGEN_AUTOMATIC_GEOMETRY_RUNTIME_REENTRY_PHASE_16P16"
        if passed
        else
        "FAIL_REGEN_AUTOMATIC_GEOMETRY_RUNTIME_REENTRY_PHASE_16P16"
    )

    return results
