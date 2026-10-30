"""
PHASE 16J.3H — End-to-End Candidate Selection Validation

Purpose:
Validate the full non-committing optimisation chain:

Candidate population
→ ranking
→ best candidate
→ recommendation feed
→ recommendation viewer payload
→ selection traceability

This phase does NOT apply live geometry.
"""

PASS_STATUS = "PASS_REGEN_END_TO_END_CANDIDATE_SELECTION_VALIDATION_PHASE_16J3H"
FAIL_STATUS = "FAIL_REGEN_END_TO_END_CANDIDATE_SELECTION_VALIDATION_PHASE_16J3H"


def attach_regen_end_to_end_candidate_selection_validation(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    population = (
        results.get("regen_candidate_ranking_input_population")
        or results.get("regen_candidate_generation_population")
        or results.get("regen_candidate_population")
        or []
    )

    ranked = (
        results.get("regen_candidate_ranking_inspector_ranked_candidates")
        or results.get("regen_candidate_ranker_ranked_candidates")
        or results.get("regen_candidate_ranked_population")
        or []
    )

    best = (
        results.get("regen_candidate_ranking_best_candidate")
        or results.get("best_full_engine_regen_design")
        or results.get("regen_best_ranked_candidate")
    )

    recommendation = (
        results.get("regen_candidate_recommendation")
        or results.get("regen_recommendation_feed_repair_recommendation_payload")
    )

    viewer_payload = results.get("regen_recommendation_viewer_payload")

    selected = (
        results.get("regen_recommendation_feed_repair_selected_candidate")
        or results.get("regen_candidate_selector_selected_candidate")
    )

    if not isinstance(population, list) or len(population) == 0:
        blockers.append("Candidate population is missing.")

    if not isinstance(ranked, list) or len(ranked) == 0:
        blockers.append("Ranked candidate population is missing.")

    if not isinstance(best, dict) or not best:
        blockers.append("Best ranked candidate is missing.")

    if not isinstance(recommendation, dict) or not recommendation:
        blockers.append("Recommendation payload is missing.")

    if not isinstance(viewer_payload, dict) or not viewer_payload:
        blockers.append("Recommendation viewer payload is missing.")

    if not isinstance(selected, dict) or not selected:
        blockers.append("Selected candidate compatibility payload is missing.")

    trace = _build_trace(
        population=population,
        ranked=ranked,
        best=best,
        recommendation=recommendation,
        viewer_payload=viewer_payload,
        selected=selected,
    )

    trace_errors = _validate_trace_consistency(trace)

    blockers.extend(trace_errors)

    status = PASS_STATUS if not blockers else FAIL_STATUS

    report = _build_report(status, blockers, trace)

    results["regen_end_to_end_candidate_selection_validation_complete"] = True
    results["phase_16j3h_complete"] = status == PASS_STATUS
    results["regen_end_to_end_candidate_selection_validation_status"] = status
    results["phase_16j3h_status"] = status
    results["regen_end_to_end_candidate_selection_validation_blockers"] = blockers
    results["regen_end_to_end_candidate_selection_trace"] = trace
    results["regen_end_to_end_candidate_selection_report"] = report

    # Safety locks.
    results["regen_end_to_end_candidate_selection_live_geometry_commit_executed"] = False
    results["regen_end_to_end_candidate_selection_geometry_application_executed"] = False
    results["regen_candidate_geometry_application_allowed"] = False
    results["regen_candidate_manual_overwrite_allowed"] = False

    # Next phase permission.
    results["phase_16j4_candidate_acceptance_integration_allowed"] = (
        status == PASS_STATUS
    )

    return results


def _candidate_id(obj):
    if not isinstance(obj, dict):
        return None
    return obj.get("candidate_id") or obj.get("id") or obj.get("name")


def _build_trace(population, ranked, best, recommendation, viewer_payload, selected):
    population_ids = [_candidate_id(c) for c in population if isinstance(c, dict)]
    ranked_ids = [_candidate_id(c) for c in ranked if isinstance(c, dict)]

    return {
        "population_count": len(population) if isinstance(population, list) else 0,
        "ranked_count": len(ranked) if isinstance(ranked, list) else 0,
        "population_candidate_ids": population_ids,
        "ranked_candidate_ids": ranked_ids,
        "best_candidate_id": _candidate_id(best),
        "selected_candidate_id": _candidate_id(selected),
        "recommendation_candidate_id": _candidate_id(recommendation),
        "viewer_candidate_id": _candidate_id(viewer_payload),
        "best_rank": (
            best.get("rank")
            or best.get("candidate_rank")
            if isinstance(best, dict)
            else None
        ),
        "viewer_rank": (
            viewer_payload.get("rank")
            if isinstance(viewer_payload, dict)
            else None
        ),
        "viewer_score": (
            viewer_payload.get("score")
            if isinstance(viewer_payload, dict)
            else None
        ),
        "geometry_application_state": (
            viewer_payload.get("geometry_application_state")
            if isinstance(viewer_payload, dict)
            else None
        ),
    }


def _validate_trace_consistency(trace):
    errors = []

    ids = [
        trace.get("best_candidate_id"),
        trace.get("selected_candidate_id"),
        trace.get("recommendation_candidate_id"),
        trace.get("viewer_candidate_id"),
    ]

    if any(v is None for v in ids):
        errors.append("One or more candidate IDs are missing in the end-to-end trace.")
        return errors

    if len(set(ids)) != 1:
        errors.append(
            "Candidate ID mismatch across best/selected/recommendation/viewer payloads."
        )

    best_id = trace.get("best_candidate_id")

    if best_id not in trace.get("population_candidate_ids", []):
        errors.append("Best candidate ID does not exist in original candidate population.")

    if best_id not in trace.get("ranked_candidate_ids", []):
        errors.append("Best candidate ID does not exist in ranked candidate population.")

    if trace.get("geometry_application_state") != "LOCKED_NOT_APPLIED":
        errors.append("Geometry application state is not safely locked.")

    return errors


def _build_report(status, blockers, trace):
    lines = [
        "LEAF PHASE 16J.3H END-TO-END CANDIDATE SELECTION VALIDATION",
        "================================================================",
        "",
        f"Status: {status}",
        "",
        "Validated Chain:",
        "- Candidate population",
        "- Ranking",
        "- Best candidate",
        "- Recommendation feed",
        "- Recommendation viewer payload",
        "- Selection traceability",
        "",
        "Trace:",
        f"- Population count: {trace.get('population_count')}",
        f"- Ranked count: {trace.get('ranked_count')}",
        f"- Best candidate ID: {trace.get('best_candidate_id')}",
        f"- Selected candidate ID: {trace.get('selected_candidate_id')}",
        f"- Recommendation candidate ID: {trace.get('recommendation_candidate_id')}",
        f"- Viewer candidate ID: {trace.get('viewer_candidate_id')}",
        f"- Viewer rank: {trace.get('viewer_rank')}",
        f"- Viewer score: {trace.get('viewer_score')}",
        f"- Geometry application state: {trace.get('geometry_application_state')}",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Safety State:",
        "- Live geometry commit: NOT EXECUTED",
        "- Geometry application: LOCKED",
        "- Manual overwrite: LOCKED",
        "",
        "Next Required Phase:",
        "- 16J.4 Candidate Acceptance Integration.",
    ])

    return "\n".join(lines)
