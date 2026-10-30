"""
LEAF Regen Candidate Ranker
===========================

PHASE 11B.1C

Ranks validated regen candidates.

This module DOES:
- accept validated candidates
- ignore failed candidates
- score passing candidates
- assign candidate ranks
- expose the best ranked candidate

This module DOES NOT:
- apply candidate geometry
- overwrite manual geometry
- permanently select a design
"""

import math


def attach_regen_candidate_ranker(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_ranker(results)
    results.update(payload)
    return results


def build_regen_candidate_ranker(results):
    candidates = results.get("regen_candidate_validator_validated_candidates") or []

    passing = [
        candidate
        for candidate in candidates
        if candidate.get("validation_status") == "PASS_CANDIDATE_VALIDATION"
    ]

    ranked = []

    for candidate in passing:
        ranked.append(score_candidate(candidate, results))

    ranked.sort(key=lambda item: item.get("candidate_rank_score", 1.0e99))

    for index, candidate in enumerate(ranked, start=1):
        candidate["candidate_rank"] = index
        candidate["candidate_ranking_status"] = "RANKED_PASSING_CANDIDATE"

    best = ranked[0] if ranked else None

    if not candidates:
        status = "FAIL_NO_VALIDATED_CANDIDATES_TO_RANK"
    elif not passing:
        status = "FAIL_NO_PASSING_CANDIDATES_TO_RANK"
    elif best:
        status = "PASS_CANDIDATES_RANKED"
    else:
        status = "FAIL_CANDIDATE_RANKING_UNKNOWN"

    text = build_regen_candidate_ranker_text(
        status=status,
        ranked=ranked,
        best=best,
        passing_count=len(passing),
        total_count=len(candidates),
    )

    return {
        "regen_candidate_ranker_complete": True,
        "phase_11b_1c_regen_candidate_ranker_complete": True,
        "regen_candidate_ranker_status": status,
        "regen_candidate_ranker_total_validated_count": len(candidates),
        "regen_candidate_ranker_passing_count": len(passing),
        "regen_candidate_ranker_ranked_count": len(ranked),
        "regen_candidate_ranker_ranked_candidates": ranked,
        "regen_candidate_ranker_best_candidate": best,
        "regen_candidate_ranker_best_candidate_id": (
            best.get("candidate_id") if best else None
        ),
        "regen_candidate_ranker_text": text,

        # Still locked until selector/application owners exist.
        "regen_candidate_best_selection_allowed": bool(best),
        "regen_candidate_automatic_selection_allowed": False,
        "regen_candidate_geometry_application_allowed": False,
    }


def score_candidate(candidate, results):
    candidate = dict(candidate)

    metrics = candidate.get("validation_metrics") or {}
    preview = candidate.get("preview_metrics") or {}
    inputs = candidate.get("inputs") or {}

    score_parts = {}

    score_parts["geometry_fit_score"] = _geometry_fit_score(metrics, preview)
    score_parts["reynolds_score"] = _reynolds_score(metrics, preview, results)
    score_parts["velocity_score"] = _velocity_score(metrics, preview, results)
    score_parts["aspect_ratio_score"] = _aspect_ratio_score(metrics, preview, results)
    score_parts["wall_thickness_score"] = _wall_thickness_score(inputs, results)
    score_parts["manufacturability_score"] = _manufacturability_score(inputs, preview)
    score_parts["mass_penalty_score"] = _mass_penalty_score(inputs, results)

    total = sum(score_parts.values())

    candidate["candidate_rank_score"] = total
    candidate["candidate_rank_score_parts"] = score_parts
    candidate["candidate_ranking_reason"] = build_candidate_ranking_reason(
        candidate,
        score_parts,
        total,
    )

    return candidate


def build_candidate_ranking_reason(candidate, score_parts, total):
    best_terms = sorted(score_parts.items(), key=lambda item: item[1])

    lines = [
        f"Candidate {candidate.get('candidate_id')} ranked with total score {total:.3f}.",
        "Lower score is better.",
        "Dominant score contributors:",
    ]

    for key, value in sorted(score_parts.items(), key=lambda item: item[1], reverse=True)[:3]:
        lines.append(f"- {key}: {value:.3f}")

    lines.append("Strongest areas:")

    for key, value in best_terms[:3]:
        lines.append(f"- {key}: {value:.3f}")

    return "\n".join(lines)


def _geometry_fit_score(metrics, preview):
    fit_ratio = _num(metrics.get("fit_ratio") or preview.get("fit_ratio"))

    if fit_ratio is None:
        return 100.0

    # Ideal fit is slightly above 1.0 so the geometry fits without huge unused pitch.
    ideal = 1.15
    return abs(fit_ratio - ideal) * 25.0


def _reynolds_score(metrics, preview, results):
    reynolds = _num(
        metrics.get("coolant_reynolds_preview")
        or preview.get("coolant_reynolds_preview")
    )
    target = _num(results.get("regen_target_reynolds_number"), 10000.0)

    if reynolds is None:
        return 100.0

    if reynolds < target:
        return ((target - reynolds) / max(target, 1.0)) * 50.0

    # Avoid excessively high Reynolds by mildly penalising huge overshoot.
    overshoot = max(0.0, reynolds - target)
    return min(20.0, overshoot / max(target, 1.0) * 5.0)


def _velocity_score(metrics, preview, results):
    velocity = _num(
        metrics.get("coolant_velocity_preview")
        or preview.get("coolant_velocity_preview")
    )
    min_velocity = _num(results.get("regen_derived_minimum_coolant_velocity"), 2.0)
    max_velocity = _num(results.get("regen_derived_maximum_coolant_velocity"), 40.0)

    if velocity is None:
        return 100.0

    ideal = (min_velocity + max_velocity) / 2.0
    span = max(max_velocity - min_velocity, 1.0e-9)

    return abs(velocity - ideal) / span * 30.0


def _aspect_ratio_score(metrics, preview, results):
    aspect_ratio = _num(metrics.get("aspect_ratio") or preview.get("aspect_ratio"))
    min_ar = _num(results.get("regen_min_channel_aspect_ratio"), 0.5)
    max_ar = _num(results.get("regen_max_channel_aspect_ratio"), 8.0)

    if aspect_ratio is None:
        return 100.0

    ideal = 2.0

    if aspect_ratio < min_ar:
        return 50.0 + (min_ar - aspect_ratio) * 25.0

    if aspect_ratio > max_ar:
        return 50.0 + (aspect_ratio - max_ar) * 25.0

    return abs(aspect_ratio - ideal) * 5.0


def _wall_thickness_score(inputs, results):
    wall = _num(inputs.get("hot_gas_wall_thickness"))
    min_wall = _num(results.get("minimum_hot_gas_wall_thickness"), 0.00075)
    max_wall = _num(results.get("maximum_hot_gas_wall_thickness"), 0.006)

    if wall is None:
        return 100.0

    # Prefer modestly above minimum: enough strength margin without killing heat transfer.
    ideal = min_wall * 1.5

    if wall < min_wall:
        return 100.0

    if wall > max_wall:
        return 100.0

    return abs(wall - ideal) / max(ideal, 1.0e-9) * 20.0


def _manufacturability_score(inputs, preview):
    width = _num(inputs.get("coolant_channel_width"))
    height = _num(inputs.get("coolant_channel_height"))
    rib = _num(inputs.get("rib_width"))
    channel_count = _num(inputs.get("number_of_coolant_channels"))

    score = 0.0

    # Extremely tiny features are harder to manufacture.
    if width is not None and width < 0.0005:
        score += 30.0

    if height is not None and height < 0.0005:
        score += 20.0

    if rib is not None and rib < 0.0004:
        score += 30.0

    if channel_count is not None and channel_count > 180:
        score += 15.0

    if channel_count is not None and channel_count < 24:
        score += 15.0

    aspect_ratio = _num(preview.get("aspect_ratio"))

    if aspect_ratio is not None and aspect_ratio > 6.0:
        score += 15.0

    return score


def _mass_penalty_score(inputs, results):
    wall = _num(inputs.get("hot_gas_wall_thickness"))
    base_wall = _num(
        results.get("hot_gas_wall_thickness")
        or results.get("regen_wall_thickness")
        or results.get("minimum_hot_gas_wall_thickness")
    )

    if wall is None or base_wall is None or base_wall <= 0:
        return 0.0

    if wall <= base_wall:
        return 0.0

    return ((wall - base_wall) / base_wall) * 10.0


def build_regen_candidate_ranker_text(
        status,
        ranked,
        best,
        passing_count,
        total_count,
):
    lines = [
        "LEAF PHASE 11B.1C REGEN CANDIDATE RANKER",
        "========================================",
        "",
        f"Status: {status}",
        f"Total validated candidates: {total_count}",
        f"Passing candidates: {passing_count}",
        f"Ranked candidates: {len(ranked)}",
        f"Best candidate ID: {best.get('candidate_id') if best else None}",
        "",
        "Scope:",
        "- Ranks only candidates that passed validation.",
        "- Failed candidates are ignored.",
        "- Does not apply geometry.",
        "- Does not overwrite manual design inputs.",
        "",
        "Ranking Metrics:",
        "- Geometry fit margin",
        "- Reynolds margin",
        "- Coolant velocity margin",
        "- Channel aspect ratio",
        "- Wall thickness",
        "- Manufacturability",
        "- Mass penalty",
        "",
        "Ranked Candidates:",
    ]

    if not ranked:
        lines.append("- None.")
    else:
        for candidate in ranked[:25]:
            lines.append(
                f"- Rank {candidate.get('candidate_rank')}: "
                f"{candidate.get('candidate_id')} "
                f"score={candidate.get('candidate_rank_score'):.3f}"
            )

        if len(ranked) > 25:
            lines.append(f"- ... {len(ranked) - 25} additional ranked candidates hidden.")

    return "\n".join(lines)


def _num(value, default=None):
    try:
        if value is None:
            return default
        if isinstance(value, float) and math.isnan(value):
            return default
        return float(value)
    except Exception:
        return default