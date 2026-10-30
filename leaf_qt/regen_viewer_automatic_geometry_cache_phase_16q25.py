from __future__ import annotations

import hashlib
import json
from typing import Any


GEOMETRY_INPUT_KEYS = (
    # Calculation / propellant mode.
    "calculation_mode",
    "fuel",
    "oxidizer",
    "selected_coolant_name",
    "coolant",
    "fuel_temp_k",
    "fuel_temperature_k",
    "oxidizer_temp_k",
    "oxidizer_temperature_k",
    "mixture_ratio",

    # Primary operating state.
    "mass_flow_rate",
    "chamber_pressure",
    "chamber_temperature",
    "characteristic_length",
    "ambient_pressure",

    # Manual thermodynamic authority when Manual mode is used.
    "Gamma",
    "R",
    "specific_heat_cp",
    "specific_heat_cv",

    # Chamber / engine geometry affecting the regen solution.
    "chamber_contraction_ratio",
    "chamber_converging_half_angle_deg",
    "gas_radius",
    "throat_radius",
    "exit_radius",
    "minimum_gas_radius",

    # Regen geometry / flow design inputs.
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
    "outer_wall_thickness",
    "outer_jacket_thickness",
    "coolant_flow_fraction",

    # Material stack.
    "hot_gas_liner",
    "outer_jacket",
    "rib_channel",
    "selected_material",
    "selected_material_name",
    "selected_coating_material",
    "selected_bond_coat",

    # Optional advanced overrides that can alter viability
    # or the resulting regen geometry.
    "wall_safety_factor",
    "wall_joint_efficiency",
    "minimum_wall_thickness",
    "corrosion_allowance",
    "coating_thickness",
    "selected_length",
    "coolant_side_wall_temperature",
    "selected_station_length",
)


AUTOMATIC_GEOMETRY_KEYS = (
    "regen_geometry_commit_staged_geometry",
)


def _clean_value(value: Any):
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, dict):
        return {str(k): _clean_value(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [_clean_value(v) for v in value]
    return value


def build_geometry_input_signature(results: dict[str, Any]) -> str:
    if not isinstance(results, dict):
        results = {}

    payload = {}

    for key in GEOMETRY_INPUT_KEYS:
        value = results.get(key)
        if value not in (None, "", "N/A"):
            payload[key] = _clean_value(value)

    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def find_current_automatic_geometry(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return {}

    for key in AUTOMATIC_GEOMETRY_KEYS:
        value = results.get(key)
        if isinstance(value, dict) and value:
            return dict(value)

    return {}


def store_automatic_geometry_cache(results: dict[str, Any]) -> dict[str, Any]:
    """
    Store only canonical automatic geometry produced by the
    optimiser -> recommendation -> application -> commit chain.

    The cache is storage/recovery infrastructure. It is not a
    geometry-generation owner.
    """

    if not isinstance(results, dict):
        return results

    geometry = find_current_automatic_geometry(
        results
    )

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

    candidate_id = (
        application_patch.get(
            "candidate_id"
        )
        if isinstance(
            application_patch,
            dict,
        )
        else None
    )

    canonical_provenance = bool(
        geometry
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
        candidate_id
    )

    if not canonical_provenance:
        results[
            "phase_16q25_auto_geometry_cache_status"
        ] = (
            "WARN_REGEN_VIEWER_AUTOMATIC_GEOMETRY_"
            "CACHE_NONCANONICAL_SOURCE_PHASE_16Q25"
        )

        results[
            "phase_16q25_auto_geometry_cache_available"
        ] = False

        results.pop(
            "phase_16q25_auto_geometry_cache",
            None,
        )

        return results

    signature = build_geometry_input_signature(
        results
    )

    results[
        "phase_16q25_auto_geometry_cache"
    ] = {
        "signature":
            signature,

        "geometry":
            dict(geometry),

        "source":
            "canonical_regen_commit",

        "candidate_id":
            candidate_id,

        "provenance":
            "CANDIDATE_APPLICATION_TO_AUTONOMOUS_COMMIT",

        "application_patch_source":
            application_patch.get(
                "source"
            ),
    }

    results[
        "phase_16q25_auto_geometry_cache_status"
    ] = (
        "PASS_REGEN_VIEWER_AUTOMATIC_GEOMETRY_"
        "CACHE_STORED_PHASE_16Q25"
    )

    results[
        "phase_16q25_auto_geometry_cache_available"
    ] = True

    return results


def automatic_geometry_cache_valid(results: dict[str, Any]) -> bool:
    """
    Return True only for a canonical optimiser/commit cache entry
    whose complete current-input signature still matches.
    """

    if not isinstance(results, dict):
        return False

    cache = results.get(
        "phase_16q25_auto_geometry_cache"
    )

    if not isinstance(
        cache,
        dict,
    ):
        return False

    if (
        cache.get("source")
        != "canonical_regen_commit"
    ):
        return False

    if (
        cache.get("provenance")
        !=
        "CANDIDATE_APPLICATION_TO_AUTONOMOUS_COMMIT"
    ):
        return False

    if not cache.get(
        "candidate_id"
    ):
        return False

    geometry = cache.get(
        "geometry"
    )

    if not isinstance(
        geometry,
        dict,
    ) or not geometry:
        return False

    cached_signature = cache.get(
        "signature"
    )

    current_signature = (
        build_geometry_input_signature(
            results
        )
    )

    return bool(
        cached_signature
        and
        cached_signature
        == current_signature
    )


def apply_cached_automatic_geometry(results: dict[str, Any]) -> dict[str, Any]:
    """
    Restore a previously canonical automatic geometry.

    This function does not generate geometry. It can only restore
    a cache entry that still proves canonical commit provenance and
    matches the current optimisation-driving input signature.
    """

    if not isinstance(results, dict):
        return results

    if not automatic_geometry_cache_valid(
        results
    ):
        results[
            "phase_16q25_auto_geometry_cache_apply_status"
        ] = (
            "MISS_REGEN_VIEWER_AUTOMATIC_GEOMETRY_"
            "CACHE_PHASE_16Q25"
        )

        results[
            "phase_16q25_auto_geometry_cache_used"
        ] = False

        return results

    cache = results[
        "phase_16q25_auto_geometry_cache"
    ]

    geometry = dict(
        cache["geometry"]
    )

    candidate_id = cache.get(
        "candidate_id"
    )

    results[
        "regen_geometry_commit_staged_geometry"
    ] = dict(geometry)

    results[
        "regen_ui_applied_geometry"
    ] = dict(geometry)

    results[
        "regen_autonomous_geometry_staged_candidate"
    ] = {
        "ready":
            True,

        "decision":
            "RESTORE_CANONICAL_CACHED_AUTOMATIC_GEOMETRY",

        "candidate_id":
            candidate_id,

        "staged_geometry":
            dict(geometry),

        "requires_user_acceptance":
            False,

        "committed":
            True,

        "source":
            "canonical_regen_commit_cache",
    }

    for key, value in geometry.items():
        if key not in (
            "source",
            "data_origin",
        ):
            results[key] = value

    results[
        "viewer_actual_geometry_source"
    ] = "automatic"

    results[
        "viewer_geometry_source"
    ] = "automatic"

    results[
        "geometry_display_mode"
    ] = "automatic"

    results[
        "phase_16q25_auto_geometry_cache_apply_status"
    ] = (
        "PASS_REGEN_VIEWER_AUTOMATIC_GEOMETRY_"
        "CACHE_APPLIED_PHASE_16Q25"
    )

    results[
        "phase_16q25_auto_geometry_cache_used"
    ] = True

    return results
