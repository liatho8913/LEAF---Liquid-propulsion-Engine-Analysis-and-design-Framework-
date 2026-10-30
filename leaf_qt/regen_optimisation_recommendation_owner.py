"""
LEAF Regen Optimisation Recommendation Owner
============================================

REGEN PHASE 8F

Owns recommendation evidence for regen optimisation.

This module can identify a recommended candidate from scored evidence.

It does NOT:
- approve the recommendation
- act as a master gate
- select geometry automatically
- apply geometry automatically
- replace validation gates
"""


def attach_regen_optimisation_recommendation_owner(results):
    if not isinstance(results, dict):
        return results

    recommendation = build_regen_optimisation_recommendation_owner(results)
    results.update(recommendation)
    return results


def build_regen_optimisation_recommendation_owner(results):
    results = results if isinstance(results, dict) else {}

    phase_8e_complete = bool(
        results.get("phase_8e_regen_optimisation_report_owner_complete", False)
    )

    recommendation_enabled = _bool_value(
        results.get("regen_optimisation_recommendation_enabled"),
        default=False,
    )

    scored_candidates = results.get("regen_optimisation_scored_candidates", [])
    if not isinstance(scored_candidates, list):
        scored_candidates = []

    blocking_failure_count = _safe_int(
        results.get("regen_optimisation_blocking_failure_count"),
        default=0,
    )

    blocking_reasons = _build_recommendation_blocking_reasons(
        recommendation_enabled=recommendation_enabled,
        phase_8e_complete=phase_8e_complete,
        scored_candidates=scored_candidates,
        blocking_failure_count=blocking_failure_count,
        results=results,
    )

    recommendation_allowed = (
        recommendation_enabled
        and phase_8e_complete
        and bool(scored_candidates)
        and blocking_failure_count == 0
        and not blocking_reasons
    )

    ranked_candidates = []
    recommended_candidate = None
    recommendation_summary = None

    if recommendation_allowed:
        ranked_candidates = _rank_scored_candidates(scored_candidates)
        recommended_candidate = ranked_candidates[0] if ranked_candidates else None

        if recommended_candidate:
            recommendation_summary = _build_recommendation_summary(
                recommended_candidate=recommended_candidate,
                ranked_candidates=ranked_candidates,
            )

    status = "PASS_REGEN_OPTIMISATION_RECOMMENDATION_OWNER"

    text = build_regen_optimisation_recommendation_text(
        status=status,
        recommendation_enabled=recommendation_enabled,
        phase_8e_complete=phase_8e_complete,
        recommendation_allowed=recommendation_allowed,
        scored_candidate_count=len(scored_candidates),
        ranked_candidates=ranked_candidates,
        recommended_candidate=recommended_candidate,
        recommendation_summary=recommendation_summary,
        blocking_reasons=blocking_reasons,
        blocking_failure_count=blocking_failure_count,
    )

    return {
        "regen_optimisation_recommendation_owner_status": status,
        "regen_optimisation_recommendation_owner_complete": True,
        "regen_optimisation_recommendation_enabled": recommendation_enabled,
        "regen_optimisation_recommendation_phase_8e_complete": phase_8e_complete,
        "regen_optimisation_recommendation_allowed": recommendation_allowed,
        "regen_optimisation_recommendation_ranked_candidates": ranked_candidates,
        "regen_optimisation_recommendation_ranked_candidate_count": len(ranked_candidates),
        "regen_optimisation_recommendation_candidate": recommended_candidate,
        "regen_optimisation_recommendation_summary": recommendation_summary,
        "regen_optimisation_recommendation_blocking_reasons": blocking_reasons,
        "regen_optimisation_recommendation_blocking_failure_count": blocking_failure_count,
        "regen_optimisation_recommendation_approval_allowed": False,
        "regen_optimisation_recommendation_automatic_selection_allowed": False,
        "regen_optimisation_recommendation_geometry_application_allowed": False,
        "regen_optimisation_recommendation_text": text,
        "phase_8f_regen_optimisation_recommendation_owner_complete": True,
    }


def build_regen_optimisation_recommendation_text(
        status,
        recommendation_enabled,
        phase_8e_complete,
        recommendation_allowed,
        scored_candidate_count,
        ranked_candidates,
        recommended_candidate,
        recommendation_summary,
        blocking_reasons,
        blocking_failure_count,
):
    lines = [
        "LEAF REGEN PHASE 8F OPTIMISATION RECOMMENDATION OWNER",
        "=======================================================",
        "",
        f"Status: {status}",
        f"Recommendation enabled: {recommendation_enabled}",
        f"Phase 8E complete: {phase_8e_complete}",
        f"Recommendation allowed: {recommendation_allowed}",
        f"Scored candidate count: {scored_candidate_count}",
        f"Ranked candidate count: {len(ranked_candidates)}",
        f"Blocking failure count: {blocking_failure_count}",
        "",
        "Owned By:",
        "- regen_optimisation_recommendation_owner.py",
        "",
        "Scope:",
        "- Owns recommendation evidence.",
        "- Owns candidate ranking evidence.",
        "- Owns recommendation summary text.",
        "- Owns recommendation traceability.",
        "- Does not approve recommendations.",
        "- Does not select geometry automatically.",
        "- Does not apply geometry.",
        "- Does not act as a master gate.",
        "",
        "Phase Locks:",
        "- Recommendation approval allowed: False",
        "- Automatic selection allowed: False",
        "- Geometry application allowed: False",
        "",
        "Blocking Reasons:",
    ]

    if blocking_reasons:
        for reason in blocking_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Recommended Candidate:")

    if recommended_candidate:
        lines.append(f"- candidate_id: {recommended_candidate.get('candidate_id')}")
        lines.append(f"- total_score: {recommended_candidate.get('total_score')}")
        lines.append(f"- thermal_score: {recommended_candidate.get('thermal_score')}")
        lines.append(f"- hydraulic_score: {recommended_candidate.get('hydraulic_score')}")
        lines.append(f"- geometry_fit_score: {recommended_candidate.get('geometry_fit_score')}")
        lines.append(f"- manufacturability_score: {recommended_candidate.get('manufacturability_score')}")
    else:
        lines.append("- None.")

    if recommendation_summary:
        lines.append("")
        lines.append("Recommendation Summary:")
        lines.append(recommendation_summary)

    if ranked_candidates:
        lines.append("")
        lines.append("Ranked Candidates:")
        for candidate in ranked_candidates:
            lines.append(
                "- "
                f"rank={candidate.get('recommendation_rank')}, "
                f"candidate_id={candidate.get('candidate_id')}, "
                f"total_score={candidate.get('total_score')}"
            )

    lines.append("")
    lines.append("Next Required Action:")
    lines.append(
        "- After Phase 8F is verified, build Phase 8G optimisation master gate before any recommendation can be approved."
    )

    return "\n".join(lines)


def _build_recommendation_blocking_reasons(
        recommendation_enabled,
        phase_8e_complete,
        scored_candidates,
        blocking_failure_count,
        results,
):
    blocking = []

    if not recommendation_enabled:
        blocking.append(
            "Recommendation generation is disabled by default. Enable it with regen_optimisation_recommendation_enabled=True."
        )

    if not phase_8e_complete:
        blocking.append(
            "Phase 8E report owner is not complete, so Phase 8F recommendation evidence is blocked."
        )

    if not scored_candidates:
        blocking.append(
            "No scored candidates are available for recommendation evidence."
        )

    if blocking_failure_count > 0:
        blocking.append(
            "Blocking optimisation failures exist, so recommendation evidence is blocked until failures are resolved."
        )

    if results.get("regen_optimisation_auto_select_requested"):
        blocking.append(
            "Automatic geometry selection was requested, but Phase 8F only creates recommendation evidence."
        )

    if results.get("regen_optimisation_apply_geometry_requested"):
        blocking.append(
            "Automatic geometry application was requested, but this remains blocked until later master-gate approval exists."
        )

    return blocking


def _rank_scored_candidates(scored_candidates):
    cleaned = [
        dict(candidate)
        for candidate in scored_candidates
        if isinstance(candidate, dict)
    ]

    cleaned.sort(
        key=lambda candidate: (
            _safe_float(candidate.get("total_score"), default=0.0),
            _safe_float(candidate.get("thermal_score"), default=0.0),
            _safe_float(candidate.get("geometry_fit_score"), default=0.0),
            _safe_float(candidate.get("hydraulic_score"), default=0.0),
            _safe_float(candidate.get("manufacturability_score"), default=0.0),
            str(candidate.get("candidate_id", "")),
        ),
        reverse=True,
    )

    ranked = []

    for index, candidate in enumerate(cleaned, start=1):
        candidate["recommendation_rank"] = index
        candidate["recommendation_evidence_owner"] = "regen_optimisation_recommendation_owner.py"
        candidate["recommendation_approval_allowed"] = False
        candidate["automatic_selection_allowed"] = False
        candidate["geometry_application_allowed"] = False
        ranked.append(candidate)

    return ranked


def _build_recommendation_summary(recommended_candidate, ranked_candidates):
    candidate_id = recommended_candidate.get("candidate_id", "UNKNOWN")
    total_score = recommended_candidate.get("total_score", "UNKNOWN")
    thermal_score = recommended_candidate.get("thermal_score", "UNKNOWN")
    hydraulic_score = recommended_candidate.get("hydraulic_score", "UNKNOWN")
    geometry_fit_score = recommended_candidate.get("geometry_fit_score", "UNKNOWN")
    manufacturability_score = recommended_candidate.get(
        "manufacturability_score",
        "UNKNOWN",
    )

    return (
        f"Candidate {candidate_id} is the current recommendation evidence leader "
        f"because it has the highest available total score ({total_score}) among "
        f"{len(ranked_candidates)} scored candidates. Sub-score evidence: "
        f"thermal={thermal_score}, hydraulic={hydraulic_score}, "
        f"geometry_fit={geometry_fit_score}, "
        f"manufacturability={manufacturability_score}. "
        "This is recommendation evidence only; it is not approval to apply geometry."
    )


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


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