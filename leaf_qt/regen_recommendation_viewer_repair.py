"""
PHASE 16J.3G — Recommendation Viewer Repair

Purpose:
- Consume the Phase 16J.3F recommendation viewer feed.
- Produce a stable, readable recommendation viewer payload.
- Display candidate ID, score, rank, advantages, penalties, and reasoning.
- Do NOT apply geometry.
- Do NOT mutate live solver inputs.
"""

PASS_STATUS = "PASS_REGEN_RECOMMENDATION_VIEWER_REPAIR_PHASE_16J3G"
FAIL_STATUS = "FAIL_REGEN_RECOMMENDATION_VIEWER_REPAIR_PHASE_16J3G"


def attach_regen_recommendation_viewer_repair(results):
    if not isinstance(results, dict):
        return results

    recommendation = (
        results.get("regen_recommendation_viewer_feed_payload")
        or results.get("regen_candidate_recommendation")
        or results.get("regen_recommendation_feed_repair_recommendation_payload")
    )

    explanation = (
        results.get("regen_recommendation_viewer_feed_explanation_report")
        or results.get("regen_recommendation_feed_repair_explanation_report")
        or ""
    )

    blockers = []

    if not isinstance(recommendation, dict) or not recommendation:
        blockers.append("No recommendation payload was available for the viewer.")

    viewer_payload = None

    if not blockers:
        viewer_payload = _build_viewer_payload(recommendation, explanation)

    status = PASS_STATUS if viewer_payload and not blockers else FAIL_STATUS

    results["regen_recommendation_viewer_repair_complete"] = True
    results["phase_16j3g_complete"] = status == PASS_STATUS
    results["regen_recommendation_viewer_repair_status"] = status
    results["phase_16j3g_status"] = status
    results["regen_recommendation_viewer_repair_blockers"] = blockers
    results["regen_recommendation_viewer_payload"] = viewer_payload
    results["regen_recommendation_viewer_report"] = (
        _build_viewer_report(viewer_payload, blockers, status)
    )

    # Compatibility keys for UI/report systems.
    results["regen_recommendation_display_candidate_id"] = (
        viewer_payload or {}
    ).get("candidate_id")
    results["regen_recommendation_display_rank"] = (
        viewer_payload or {}
    ).get("rank")
    results["regen_recommendation_display_score"] = (
        viewer_payload or {}
    ).get("score")
    results["regen_recommendation_display_reasoning"] = (
        viewer_payload or {}
    ).get("reasoning")
    results["regen_recommendation_display_advantages"] = (
        viewer_payload or {}
    ).get("advantages", [])
    results["regen_recommendation_display_penalties"] = (
        viewer_payload or {}
    ).get("penalties", [])

    # Safety locks remain active.
    results["regen_recommendation_viewer_live_geometry_commit_executed"] = False
    results["regen_recommendation_viewer_geometry_application_executed"] = False
    results["regen_candidate_geometry_application_allowed"] = False
    results["regen_candidate_manual_overwrite_allowed"] = False

    # Next phase permission.
    results["phase_16j3h_end_to_end_selection_validation_allowed"] = (
        status == PASS_STATUS
    )

    return results


def _build_viewer_payload(recommendation, explanation):
    candidate = (
        recommendation.get("candidate")
        or recommendation.get("selected_candidate")
        or recommendation
    )

    score = (
        recommendation.get("score")
        or recommendation.get("candidate_rank_score")
        or candidate.get("candidate_rank_score")
        or candidate.get("score")
        or candidate.get("total_score")
    )

    rank = (
        recommendation.get("rank")
        or recommendation.get("candidate_rank")
        or candidate.get("candidate_rank")
        or candidate.get("rank")
        or 1
    )

    reasoning = (
        recommendation.get("reasoning")
        or recommendation.get("recommendation_reason")
        or candidate.get("recommended_regen_candidate_reason")
        or candidate.get("candidate_ranking_reason")
        or "Candidate recommended from ranked regen candidate feed."
    )

    advantages = _normalise_list(
        recommendation.get("advantages")
        or recommendation.get("pass_reasons")
        or candidate.get("pass_reasons")
        or []
    )

    penalties = _normalise_list(
        recommendation.get("penalties")
        or recommendation.get("failure_reasons")
        or candidate.get("failure_reasons")
        or []
    )

    geometry = (
        candidate.get("candidate_geometry")
        or candidate.get("inputs")
        or recommendation.get("candidate_geometry")
        or {}
    )

    return {
        "candidate_id": (
            recommendation.get("candidate_id")
            or candidate.get("candidate_id")
            or "UNKNOWN_CANDIDATE"
        ),
        "rank": rank,
        "score": score,
        "status": recommendation.get("status"),
        "confidence": recommendation.get("confidence"),
        "reasoning": reasoning,
        "advantages": advantages,
        "penalties": penalties,
        "geometry": geometry,
        "source": "PHASE_16J3G_RECOMMENDATION_VIEWER_REPAIR",
        "upstream_explanation": explanation,
        "geometry_application_state": "LOCKED_NOT_APPLIED",
    }


def _normalise_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, tuple):
        return [str(v) for v in value]
    return [str(value)]


def _build_viewer_report(viewer_payload, blockers, status):
    lines = [
        "LEAF PHASE 16J.3G RECOMMENDATION VIEWER REPAIR",
        "==================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Receives recommendation payload from Phase 16J.3F.",
        "- Converts recommendation into viewer-readable display data.",
        "- Shows candidate ID, score, rank, advantages, penalties, and reasoning.",
        "- Does not apply geometry.",
        "- Does not mutate live inputs.",
        "",
    ]

    if blockers:
        lines.append("Blocking Reasons:")
        for blocker in blockers:
            lines.append(f"- {blocker}")
        return "\n".join(lines)

    lines.extend([
        "Recommendation Display:",
        f"- Candidate ID: {viewer_payload.get('candidate_id')}",
        f"- Rank: {viewer_payload.get('rank')}",
        f"- Score: {viewer_payload.get('score')}",
        f"- Status: {viewer_payload.get('status')}",
        f"- Confidence: {viewer_payload.get('confidence')}",
        "",
        "Reasoning:",
        f"{viewer_payload.get('reasoning')}",
        "",
        "Advantages:",
    ])

    advantages = viewer_payload.get("advantages") or []
    if advantages:
        for item in advantages:
            lines.append(f"- {item}")
    else:
        lines.append("- None provided.")

    lines.append("")
    lines.append("Penalties:")

    penalties = viewer_payload.get("penalties") or []
    if penalties:
        for item in penalties:
            lines.append(f"- {item}")
    else:
        lines.append("- None provided.")

    lines.extend([
        "",
        "Safety State:",
        "- Geometry application: LOCKED",
        "- Live commit: NOT EXECUTED",
        "",
        "Next Required Phase:",
        "- 16J.3H End-to-End Candidate Selection Validation.",
    ])

    return "\n".join(lines)
