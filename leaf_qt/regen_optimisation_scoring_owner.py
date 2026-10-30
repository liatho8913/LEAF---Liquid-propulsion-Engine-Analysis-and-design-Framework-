from leaf_qt.status_presentation import status_severity

try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:


    class LegacyCompatibilityProducer:
        """
        Phase 16U shared presentation compatibility fallback.

        This local fallback is only used when leaf_qt.status_presentation
        cannot be imported. Normal production execution should use the shared
        status_presentation implementation.
        """

        @staticmethod
        def marker_from_bool(value, pass_marker="PASS", fail_marker="FAIL"):
            return pass_marker if bool(value) else fail_marker

        @staticmethod
        def marker_from_status(value):
            severity = status_severity(value)
            if severity == "FAIL":
                return "FAIL"
            if severity == "WARN":
                return "WARN"
            if severity == "PASS":
                return "PASS"
            return "UNKNOWN"

        @staticmethod
        def status_severity(value):
            return status_severity(value)

def _leaf_16u71_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u71_is_fail_like(text) or _leaf_16u71_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u71_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u71_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u71_is_fail_like(value):
    return _leaf_16u71_status_severity(value) == "FAIL"


def _leaf_16u71_is_warn_like(value):
    return _leaf_16u71_status_severity(value) == "WARN"


def _leaf_16u71_is_pass_like(value):
    return _leaf_16u71_status_severity(value) == "PASS"


"""
LEAF Regen Optimisation Scoring Owner
=====================================

REGEN PHASE 8C

Owns scoring of generated regen optimisation candidates.

This module does NOT:
- select the best candidate automatically
- apply geometry
- approve recommendations
- replace validation gates
"""

DEFAULT_SCORE_WEIGHTS = {
    "thermal": 0.35,
    "hydraulic": 0.25,
    "geometry_fit": 0.25,
    "manufacturability": 0.15,
}


def attach_regen_optimisation_scoring_owner(results):
    if not isinstance(results, dict):
        return results

    scoring = build_regen_optimisation_scoring_owner(results)
    results.update(scoring)
    return results


def build_regen_optimisation_scoring_owner(results):
    results = results if isinstance(results, dict) else {}

    phase_8b_complete = bool(
        results.get("phase_8b_regen_optimisation_candidate_generator_complete", False)
    )

    candidates = results.get("regen_optimisation_candidate_generator_candidates", [])
    if not isinstance(candidates, list):
        candidates = []

    scoring_enabled = _bool_value(
        results.get("regen_optimisation_scoring_enabled"),
        default=False,
    )

    weights = _normalise_weights(
        results.get("regen_optimisation_score_weights"),
        DEFAULT_SCORE_WEIGHTS,
    )

    blocking_reasons = _build_scoring_blocking_reasons(
        scoring_enabled=scoring_enabled,
        phase_8b_complete=phase_8b_complete,
        candidates=candidates,
        results=results,
    )

    scoring_allowed = (
        scoring_enabled
        and phase_8b_complete
        and bool(candidates)
        and not blocking_reasons
    )

    scored_candidates = []

    if scoring_allowed:
        scored_candidates = [
            _score_candidate(candidate, weights)
            for candidate in candidates
            if isinstance(candidate, dict)
        ]

    status = (
        "PASS_REGEN_OPTIMISATION_SCORING_OWNER"
        if _scoring_structure_complete(weights)
        else "FAIL_REGEN_OPTIMISATION_SCORING_OWNER"
    )

    text = build_regen_optimisation_scoring_text(
        status=status,
        scoring_enabled=scoring_enabled,
        phase_8b_complete=phase_8b_complete,
        scoring_allowed=scoring_allowed,
        weights=weights,
        candidates=candidates,
        scored_candidates=scored_candidates,
        blocking_reasons=blocking_reasons,
    )

    return {
        "regen_optimisation_scoring_owner_status": status,
        "regen_optimisation_scoring_owner_complete": _leaf_16u71_is_pass_like(status),
        "regen_optimisation_scoring_enabled": scoring_enabled,
        "regen_optimisation_scoring_phase_8b_complete": phase_8b_complete,
        "regen_optimisation_scoring_allowed": scoring_allowed,
        "regen_optimisation_score_weights": weights,
        "regen_optimisation_scored_candidates": scored_candidates,
        "regen_optimisation_scored_candidate_count": len(scored_candidates),
        "regen_optimisation_scoring_blocking_reasons": blocking_reasons,
        "regen_optimisation_scoring_automatic_selection_allowed": False,
        "regen_optimisation_scoring_geometry_application_allowed": False,
        "regen_optimisation_scoring_recommendation_approval_allowed": False,
        "regen_optimisation_scoring_text": text,
        "phase_8c_regen_optimisation_scoring_owner_complete": _leaf_16u71_is_pass_like(status),
    }


def build_regen_optimisation_scoring_text(
        status,
        scoring_enabled,
        phase_8b_complete,
        scoring_allowed,
        weights,
        candidates,
        scored_candidates,
        blocking_reasons,
):
    lines = [
        "LEAF REGEN PHASE 8C OPTIMISATION SCORING OWNER",
        "================================================",
        "",
        f"Status: {status}",
        f"Scoring enabled: {scoring_enabled}",
        f"Phase 8B complete: {phase_8b_complete}",
        f"Scoring allowed: {scoring_allowed}",
        f"Input candidate count: {len(candidates)}",
        f"Scored candidate count: {len(scored_candidates)}",
        "",
        "Owned By:",
        "- regen_optimisation_scoring_owner.py",
        "",
        "Scope:",
        "- Owns candidate scoring evidence.",
        "- Owns weighted objective scores.",
        "- Owns thermal, hydraulic, geometry-fit, and manufacturability sub-scores.",
        "- Does not automatically select geometry.",
        "- Does not apply geometry.",
        "- Does not approve recommendations.",
        "",
        "Phase Locks:",
        "- Automatic selection allowed: False",
        "- Geometry application allowed: False",
        "- Recommendation approval allowed: False",
        "",
        "Score Weights:",
    ]

    for key, value in weights.items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("Blocking Reasons:")

    if blocking_reasons:
        for reason in blocking_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None.")

    if scored_candidates:
        lines.append("")
        lines.append("Scored Candidates:")
        for candidate in scored_candidates:
            lines.append(
                "- "
                f"{candidate.get('candidate_id')}: "
                f"total={candidate.get('total_score')}, "
                f"thermal={candidate.get('thermal_score')}, "
                f"hydraulic={candidate.get('hydraulic_score')}, "
                f"geometry_fit={candidate.get('geometry_fit_score')}, "
                f"manufacturability={candidate.get('manufacturability_score')}"
            )

    lines.append("")
    lines.append("Next Required Action:")
    lines.append(
        "- After Phase 8C is verified, build Phase 8D failure ownership before any recommendation or selection gate."
    )

    return "\n".join(lines)


def _score_candidate(candidate, weights):
    channel_count = _safe_float(candidate.get("coolant_channel_count"), 1.0)
    width = _safe_float(candidate.get("coolant_channel_width"), 0.0015)
    height = _safe_float(candidate.get("coolant_channel_height"), 0.0020)
    rib = _safe_float(candidate.get("coolant_rib_width"), 0.0010)
    wall = _safe_float(candidate.get("regen_wall_thickness"), 0.0010)

    area = max(width * height, 1e-12)
    hydraulic_size = max(width + height, 1e-12)
    pitch = max(width + rib, 1e-12)
    aspect_ratio = height / max(width, 1e-12)

    thermal_score = _clamp01(
        0.55 * _target_score(wall, target=0.0010, tolerance=0.00075)
        + 0.45 * _target_score(area, target=3.0e-6, tolerance=2.0e-6)
    )

    hydraulic_score = _clamp01(
        0.60 * _target_score(hydraulic_size, target=0.0035, tolerance=0.0025)
        + 0.40 * _target_score(channel_count, target=80.0, tolerance=60.0)
    )

    geometry_fit_score = _clamp01(
        0.50 * _target_score(pitch, target=0.0025, tolerance=0.0020)
        + 0.50 * _target_score(channel_count, target=80.0, tolerance=40.0)
    )

    manufacturability_score = _clamp01(
        0.45 * _target_score(width, target=0.0015, tolerance=0.0010)
        + 0.35 * _target_score(rib, target=0.0010, tolerance=0.00075)
        + 0.20 * _target_score(aspect_ratio, target=1.5, tolerance=1.5)
    )

    total_score = _clamp01(
        weights["thermal"] * thermal_score
        + weights["hydraulic"] * hydraulic_score
        + weights["geometry_fit"] * geometry_fit_score
        + weights["manufacturability"] * manufacturability_score
    )

    scored = dict(candidate)
    scored.update({
        "thermal_score": round(thermal_score, 6),
        "hydraulic_score": round(hydraulic_score, 6),
        "geometry_fit_score": round(geometry_fit_score, 6),
        "manufacturability_score": round(manufacturability_score, 6),
        "total_score": round(total_score, 6),
        "score_basis": "phase_8c_structural_scoring_only",
        "automatic_selection_allowed": False,
        "geometry_application_allowed": False,
        "recommendation_approval_allowed": False,
    })

    return scored


def _build_scoring_blocking_reasons(scoring_enabled, phase_8b_complete, candidates, results):
    blocking = []

    if not scoring_enabled:
        blocking.append(
            "Candidate scoring is disabled by default. Enable it with regen_optimisation_scoring_enabled=True."
        )

    if not phase_8b_complete:
        blocking.append(
            "Phase 8B candidate generator foundation is not complete, so Phase 8C scoring is blocked."
        )

    if not candidates:
        blocking.append(
            "No generated candidates are available to score."
        )

    if results.get("regen_optimisation_auto_select_requested"):
        blocking.append(
            "Automatic geometry selection was requested, but Phase 8C only scores candidates."
        )

    if results.get("regen_optimisation_apply_geometry_requested"):
        blocking.append(
            "Automatic geometry application was requested, but this remains blocked until later recommendation gates exist."
        )

    return blocking


def _normalise_weights(value, default):
    weights = dict(default)

    if isinstance(value, dict):
        for key in weights:
            if key in value:
                weights[key] = _safe_float(value[key], weights[key])

    total = sum(weights.values())

    if total <= 0:
        return dict(default)

    return {
        key: round(val / total, 6)
        for key, val in weights.items()
    }


def _scoring_structure_complete(weights):
    required = {
        "thermal",
        "hydraulic",
        "geometry_fit",
        "manufacturability",
    }

    return isinstance(weights, dict) and required.issubset(weights)


def _target_score(value, target, tolerance):
    error = abs(float(value) - float(target))
    tolerance = max(float(tolerance), 1e-12)
    return _clamp01(1.0 - error / tolerance)


def _clamp01(value):
    return max(0.0, min(1.0, float(value)))


def _safe_float(value, default):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return float(default)

    if value <= 0:
        return float(default)

    return value


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
