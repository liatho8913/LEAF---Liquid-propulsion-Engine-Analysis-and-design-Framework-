"""
PHASE 11A.6
Regen Geometry Output Architecture Owner

Purpose:
    Build structured output/report data for the regen geometry improvement chain.

Rules:
    - Output architecture only.
    - Does not modify solver values.
    - Does not apply candidate geometry to user inputs.
    - Collects discovery, validation, explanation, recommendation, and candidate data.
"""


def attach_regen_geometry_output_architecture_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_regen_geometry_output_architecture(results)
    results.update(audit)
    return results


def build_regen_geometry_output_architecture(results):
    results = results if isinstance(results, dict) else {}

    discovery = _build_discovery_section(results)
    validation = _build_validation_section(results)
    explanations = _build_explanation_section(results)
    recommendations = _build_recommendation_section(results)
    candidate = _build_candidate_section(results)
    summary = _build_summary(discovery, validation, explanations, recommendations, candidate)

    owner_status = "PASS_PHASE_11A6_REGEN_GEOMETRY_OUTPUT_ARCHITECTURE_OWNER"

    engineering_status = (
        "WARN_REGEN_GEOMETRY_OUTPUT_ARCHITECTURE_ACTIONABLE"
        if summary["recommendation_count"] > 0 or summary["candidate_changed_count"] > 0
        else "PASS_REGEN_GEOMETRY_OUTPUT_ARCHITECTURE"
    )

    report = {
        "summary": summary,
        "discovery": discovery,
        "validation": validation,
        "explanations": explanations,
        "recommendations": recommendations,
        "candidate": candidate,
    }

    text = build_regen_geometry_output_architecture_text(
        owner_status=owner_status,
        engineering_status=engineering_status,
        report=report,
    )

    return {
        "phase_11a6_regen_geometry_output_architecture_owner_complete": True,
        "phase_11a6_regen_geometry_output_architecture_owner_status": owner_status,
        "phase_11a6_regen_geometry_output_architecture_owner_engineering_status": engineering_status,
        "phase_11a6_regen_geometry_output_architecture_owner_report": report,
        "phase_11a6_regen_geometry_output_architecture_owner_summary": summary,
        "phase_11a6_regen_geometry_output_architecture_owner_text": text,
        "stage_11a_regen_geometry_output_architecture_complete": True,
        "stage_11a_regen_geometry_output_architecture_status": owner_status,
        "stage_11a_regen_geometry_output_architecture_engineering_status": engineering_status,
    }


def _build_discovery_section(results):
    constraints = results.get(
        "phase_11a1_regen_geometry_constraint_discovery_audit_owner_constraints",
        [],
    )

    if not isinstance(constraints, list):
        constraints = []

    available = [item for item in constraints if isinstance(item, dict) and item.get("available")]
    missing = [item for item in constraints if isinstance(item, dict) and not item.get("available")]

    return {
        "complete": bool(results.get("phase_11a1_regen_geometry_constraint_discovery_audit_owner_complete")),
        "status": results.get("phase_11a1_regen_geometry_constraint_discovery_audit_owner_status"),
        "constraint_count": len(constraints),
        "available_count": len(available),
        "missing_count": len(missing),
        "available_constraints": available,
        "missing_constraints": missing,
    }


def _build_validation_section(results):
    validation_results = results.get(
        "phase_11a2_regen_geometry_constraint_validation_owner_results",
        [],
    )

    if not isinstance(validation_results, list):
        validation_results = []

    grouped = {
        "PASS": [],
        "WARN": [],
        "FAIL": [],
        "NOT_AVAILABLE": [],
    }

    for item in validation_results:
        if not isinstance(item, dict):
            continue
        state = item.get("validation_state", "UNKNOWN")
        grouped.setdefault(state, []).append(item)

    return {
        "complete": bool(results.get("phase_11a2_regen_geometry_constraint_validation_owner_complete")),
        "owner_status": results.get("phase_11a2_regen_geometry_constraint_validation_owner_status"),
        "engineering_status": results.get("phase_11a2_regen_geometry_constraint_validation_owner_engineering_status"),
        "pass_count": len(grouped.get("PASS", [])),
        "warn_count": len(grouped.get("WARN", [])),
        "fail_count": len(grouped.get("FAIL", [])),
        "not_available_count": len(grouped.get("NOT_AVAILABLE", [])),
        "grouped_results": grouped,
    }


def _build_explanation_section(results):
    explanations = results.get(
        "phase_11a3_regen_geometry_failure_explanation_owner_explanations",
        [],
    )

    if not isinstance(explanations, list):
        explanations = []

    return {
        "complete": bool(results.get("phase_11a3_regen_geometry_failure_explanation_owner_complete")),
        "owner_status": results.get("phase_11a3_regen_geometry_failure_explanation_owner_status"),
        "engineering_status": results.get("phase_11a3_regen_geometry_failure_explanation_owner_engineering_status"),
        "explanation_count": len(explanations),
        "explanations": explanations,
    }


def _build_recommendation_section(results):
    recommendations = results.get(
        "phase_11a4_regen_geometry_recommendation_engine_owner_recommendations",
        [],
    )

    if not isinstance(recommendations, list):
        recommendations = []

    high = [item for item in recommendations if isinstance(item, dict) and item.get("priority") == "HIGH"]
    medium = [item for item in recommendations if isinstance(item, dict) and item.get("priority") == "MEDIUM"]
    low = [item for item in recommendations if isinstance(item, dict) and item.get("priority") == "LOW"]

    return {
        "complete": bool(results.get("phase_11a4_regen_geometry_recommendation_engine_owner_complete")),
        "owner_status": results.get("phase_11a4_regen_geometry_recommendation_engine_owner_status"),
        "engineering_status": results.get("phase_11a4_regen_geometry_recommendation_engine_owner_engineering_status"),
        "recommendation_count": len(recommendations),
        "high_priority_count": len(high),
        "medium_priority_count": len(medium),
        "low_priority_count": len(low),
        "recommendations": recommendations,
    }


def _build_candidate_section(results):
    baseline = results.get(
        "phase_11a5_regen_geometry_apply_recommendation_owner_baseline_geometry",
        {},
    )

    candidate = results.get(
        "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry",
        {},
    )

    improvement = results.get(
        "phase_11a5_regen_geometry_apply_recommendation_owner_improvement",
        {},
    )

    applied_actions = results.get(
        "phase_11a5_regen_geometry_apply_recommendation_owner_applied_actions",
        [],
    )

    skipped_actions = results.get(
        "phase_11a5_regen_geometry_apply_recommendation_owner_skipped_actions",
        [],
    )

    if not isinstance(baseline, dict):
        baseline = {}

    if not isinstance(candidate, dict):
        candidate = {}

    if not isinstance(improvement, dict):
        improvement = {}

    if not isinstance(applied_actions, list):
        applied_actions = []

    if not isinstance(skipped_actions, list):
        skipped_actions = []

    comparison_rows = _build_comparison_rows(baseline, candidate, improvement)

    return {
        "complete": bool(results.get("phase_11a5_regen_geometry_apply_recommendation_owner_complete")),
        "owner_status": results.get("phase_11a5_regen_geometry_apply_recommendation_owner_status"),
        "engineering_status": results.get("phase_11a5_regen_geometry_apply_recommendation_owner_engineering_status"),
        "baseline_geometry": baseline,
        "candidate_geometry": candidate,
        "improvement": improvement,
        "comparison_rows": comparison_rows,
        "changed_count": improvement.get("changed_count", 0),
        "applied_actions": applied_actions,
        "skipped_actions": skipped_actions,
    }


def _build_comparison_rows(baseline, candidate, improvement):
    keys = sorted(set(baseline.keys()) | set(candidate.keys()))
    deltas = improvement.get("deltas", {})

    if not isinstance(deltas, dict):
        deltas = {}

    rows = []

    for key in keys:
        before = baseline.get(key)
        after = candidate.get(key)
        delta = deltas.get(key)

        changed = False
        if before is not None and after is not None:
            changed = before != after

        rows.append(
            {
                "variable": key,
                "before": before,
                "after": after,
                "delta": delta,
                "changed": changed,
            }
        )

    return rows


def _build_summary(discovery, validation, explanations, recommendations, candidate):
    return {
        "discovered_constraint_count": discovery.get("constraint_count", 0),
        "available_constraint_count": discovery.get("available_count", 0),
        "missing_constraint_count": discovery.get("missing_count", 0),
        "validation_pass_count": validation.get("pass_count", 0),
        "validation_warn_count": validation.get("warn_count", 0),
        "validation_fail_count": validation.get("fail_count", 0),
        "explanation_count": explanations.get("explanation_count", 0),
        "recommendation_count": recommendations.get("recommendation_count", 0),
        "candidate_changed_count": candidate.get("changed_count", 0),
        "candidate_action_count": len(candidate.get("applied_actions", [])),
    }


def build_regen_geometry_output_architecture_text(owner_status, engineering_status, report):
    summary = report.get("summary", {})
    candidate = report.get("candidate", {})
    recommendations = report.get("recommendations", {})
    validation = report.get("validation", {})

    lines = []
    lines.append("PHASE 11A.6 — REGEN GEOMETRY OUTPUT ARCHITECTURE OWNER")
    lines.append("======================================================")
    lines.append("")
    lines.append(f"Owner Status: {owner_status}")
    lines.append(f"Engineering Status: {engineering_status}")
    lines.append("")
    lines.append("Purpose:")
    lines.append("- Expose the regen geometry diagnostic and candidate-improvement chain as structured output.")
    lines.append("- This stage does not modify solver values or UI layout.")
    lines.append("")
    lines.append("Summary:")
    for key, value in sorted(summary.items()):
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("Validation Summary:")
    lines.append(f"- PASS: {validation.get('pass_count')}")
    lines.append(f"- WARN: {validation.get('warn_count')}")
    lines.append(f"- FAIL: {validation.get('fail_count')}")
    lines.append(f"- NOT_AVAILABLE: {validation.get('not_available_count')}")

    lines.append("")
    lines.append("Recommendation Summary:")
    lines.append(f"- Total recommendations: {recommendations.get('recommendation_count')}")
    lines.append(f"- High priority: {recommendations.get('high_priority_count')}")
    lines.append(f"- Medium priority: {recommendations.get('medium_priority_count')}")
    lines.append(f"- Low priority: {recommendations.get('low_priority_count')}")

    lines.append("")
    lines.append("Candidate Geometry Comparison:")
    comparison_rows = candidate.get("comparison_rows", [])

    if comparison_rows:
        for row in comparison_rows:
            marker = "CHANGED" if row.get("changed") else "UNCHANGED"
            lines.append(
                f"- {row.get('variable')}: "
                f"{row.get('before')} -> {row.get('after')} "
                f"(delta={row.get('delta')}; {marker})"
            )
    else:
        lines.append("- No candidate geometry comparison rows available.")

    lines.append("")
    lines.append("Conclusion:")
    lines.append(
        "The regen geometry chain is now exposed as structured output data for reports and future UI panels."
    )

    return "\n".join(lines)