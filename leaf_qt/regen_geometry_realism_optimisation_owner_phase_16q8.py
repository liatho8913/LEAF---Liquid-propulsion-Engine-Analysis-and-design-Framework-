from __future__ import annotations

from typing import Any


TARGET_COVERAGE = 0.78
MIN_REASONABLE_COVERAGE = 0.60
MAX_REASONABLE_COVERAGE = 0.90

TARGET_ASPECT_RATIO = 2.0
MIN_REASONABLE_ASPECT_RATIO = 1.0
MAX_REASONABLE_ASPECT_RATIO = 3.5

MIN_REASONABLE_CHANNEL_COUNT = 40
MAX_REASONABLE_CHANNEL_COUNT = 160

TARGET_EFFECTIVE_RIB_FACTOR = 1.25
MAX_EFFECTIVE_RIB_FACTOR = 3.0


def _num(value: Any, default=None):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def evaluate_geometry_realism(geometry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(geometry, dict):
        geometry = {}

    width = _num(geometry.get("coolant_channel_width", geometry.get("channel_width")), None)
    height = _num(geometry.get("coolant_channel_height", geometry.get("channel_height")), None)
    rib = _num(geometry.get("rib_width", geometry.get("requested_rib_width")), None)
    effective_rib = _num(geometry.get("effective_rib_width"), None)
    coverage = _num(geometry.get("cooling_coverage"), None)
    count = _num(geometry.get("number_of_coolant_channels", geometry.get("channel_count")), None)

    blockers = []
    warnings = []
    penalties = {}

    aspect = None
    if width and height:
        aspect = height / width
    else:
        blockers.append("Missing channel width/height for realism evaluation.")

    if count is None:
        blockers.append("Missing channel count.")
    elif count < MIN_REASONABLE_CHANNEL_COUNT:
        warnings.append(f"Channel count is low for a regen layout: {count:g}.")
        penalties["channel_count_low"] = (MIN_REASONABLE_CHANNEL_COUNT - count) / MIN_REASONABLE_CHANNEL_COUNT
    elif count > MAX_REASONABLE_CHANNEL_COUNT:
        warnings.append(f"Channel count is high for current realism envelope: {count:g}.")
        penalties["channel_count_high"] = (count - MAX_REASONABLE_CHANNEL_COUNT) / MAX_REASONABLE_CHANNEL_COUNT
    else:
        penalties["channel_count"] = 0.0

    if coverage is None:
        blockers.append("Missing cooling coverage.")
    elif coverage < MIN_REASONABLE_COVERAGE:
        warnings.append(f"Cooling coverage is low; ribs dominate circumference: {coverage:.3f}.")
        penalties["coverage_low"] = (MIN_REASONABLE_COVERAGE - coverage) / MIN_REASONABLE_COVERAGE
    elif coverage > MAX_REASONABLE_COVERAGE:
        blockers.append(f"Cooling coverage is too high for structural margin: {coverage:.3f}.")
        penalties["coverage_high"] = (coverage - MAX_REASONABLE_COVERAGE) / MAX_REASONABLE_COVERAGE
    else:
        penalties["coverage_target_error"] = abs(coverage - TARGET_COVERAGE) / TARGET_COVERAGE

    if aspect is not None:
        if aspect < MIN_REASONABLE_ASPECT_RATIO:
            warnings.append(f"Aspect ratio is low: {aspect:.3f}.")
            penalties["aspect_low"] = (MIN_REASONABLE_ASPECT_RATIO - aspect) / MIN_REASONABLE_ASPECT_RATIO
        elif aspect > MAX_REASONABLE_ASPECT_RATIO:
            warnings.append(f"Aspect ratio is high: {aspect:.3f}.")
            penalties["aspect_high"] = (aspect - MAX_REASONABLE_ASPECT_RATIO) / MAX_REASONABLE_ASPECT_RATIO
        else:
            penalties["aspect_target_error"] = abs(aspect - TARGET_ASPECT_RATIO) / TARGET_ASPECT_RATIO

    if rib is None or effective_rib is None:
        blockers.append("Missing requested/effective rib width.")
    elif rib > 0:
        rib_factor = effective_rib / rib
        penalties["effective_rib_factor_error"] = abs(rib_factor - TARGET_EFFECTIVE_RIB_FACTOR) / TARGET_EFFECTIVE_RIB_FACTOR
        if rib_factor > MAX_EFFECTIVE_RIB_FACTOR:
            warnings.append(f"Effective rib width is excessively larger than requested rib: factor={rib_factor:.3f}.")
            penalties["effective_rib_excess"] = (rib_factor - MAX_EFFECTIVE_RIB_FACTOR) / MAX_EFFECTIVE_RIB_FACTOR
    else:
        blockers.append("Requested rib width is non-positive.")

    score = 100.0
    for value in penalties.values():
        score -= min(50.0, max(0.0, float(value)) * 35.0)

    score -= len(warnings) * 5.0
    score -= len(blockers) * 100.0
    score = max(0.0, min(100.0, score))

    passed = len(blockers) == 0 and score >= 65.0

    return {
        "status": (
            "PASS_REGEN_GEOMETRY_REALISM_OPTIMISATION_OWNER_PHASE_16Q8"
            if passed
            else "FAIL_REGEN_GEOMETRY_REALISM_OPTIMISATION_OWNER_PHASE_16Q8"
        ),
        "passed": passed,
        "score": score,
        "warnings": warnings,
        "blockers": blockers,
        "penalties": penalties,
        "aspect_ratio": aspect,
        "channel_count": count,
        "coverage": coverage,
        "effective_rib_width": effective_rib,
    }


def attach_geometry_realism(results: dict[str, Any], geometry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        return results

    verdict = evaluate_geometry_realism(geometry)

    results["phase_16q8_geometry_realism_status"] = verdict["status"]
    results["phase_16q8_geometry_realism_pass"] = verdict["passed"]
    results["phase_16q8_geometry_realism_score"] = verdict["score"]
    results["phase_16q8_geometry_realism_warnings"] = verdict["warnings"]
    results["phase_16q8_geometry_realism_blockers"] = verdict["blockers"]

    if not verdict["passed"]:
        results["regen_geometry_status"] = "FAIL"
        results["geometry_status"] = "FAIL"
        results["final_regen_design_verdict"] = "FAIL_REGEN_GEOMETRY_REALISM_OPTIMISATION"

    return results
