"""
PHASE 11B.4C
Candidate Ranking Report Owner

Responsibilities:
- Consume ranked population from 11B.4B.
- Explain ranking results.
- Explain why the best candidate won.
- Build report/export bundles.
- Keep ranking explanation separate from scalar outputs.
- Do NOT register reports.
- Do NOT mutate candidates.
- Do NOT evolve generations.
- Do NOT solve candidates.
- Do NOT commit live geometry.
"""


OWNER_NAME = "REGEN_CANDIDATE_RANKING_REPORT_OWNER"
PHASE = "11B.4C"

PASS_STATUS = "PASS_REGEN_CANDIDATE_RANKING_REPORT_OWNER_PHASE_11B4C"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_RANKING_REPORT_OWNER_PHASE_11B4C"

REPORT_KEY = "regen_candidate_ranking_report"
REPORT_TITLE = "Regen Candidate Ranking Report"


def attach_regen_candidate_ranking_report_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_ranking_report_owner(results)
    results.update(payload)
    return results


def build_regen_candidate_ranking_report_owner(results):
    blockers = []

    if results.get("phase_11b_4b_regen_candidate_ranking_owner_complete") is not True:
        blockers.append("Phase 11B.4B candidate ranking owner is not complete.")

    if results.get("regen_candidate_ranking_ready") is not True:
        blockers.append("Candidate ranking owner is not ready.")

    ranked_population = results.get("regen_candidate_ranked_population")

    if not isinstance(ranked_population, list) or not ranked_population:
        blockers.append("Ranked population is missing or empty.")
        ranked_population = []

    best_candidate = results.get("regen_candidate_best_candidate")

    if ranked_population and not isinstance(best_candidate, dict):
        blockers.append("Best ranked candidate is missing or invalid.")

    ranking_statistics = results.get("regen_candidate_ranking_statistics")

    if not isinstance(ranking_statistics, dict) or not ranking_statistics:
        blockers.append("Ranking statistics are missing or invalid.")
        ranking_statistics = {}

    objective = results.get("regen_candidate_ranking_objective") or "UNKNOWN"

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    summary = build_ranking_summary(
        objective=objective,
        ranked_population=ranked_population,
        ranking_statistics=ranking_statistics,
        best_candidate=best_candidate if isinstance(best_candidate, dict) else None,
    )

    explanation = build_ranking_explanation(
        objective=objective,
        ranked_population=ranked_population,
        ranking_statistics=ranking_statistics,
        best_candidate=best_candidate if isinstance(best_candidate, dict) else None,
    )

    report_text = build_ranking_report_text(
        status=status,
        ready=ready,
        objective=objective,
        blockers=blockers,
        summary=summary,
        explanation=explanation,
        ranked_population=ranked_population,
        ranking_statistics=ranking_statistics,
    )

    report_bundle = build_ranking_report_bundle(
        status=status,
        ready=ready,
        objective=objective,
        blockers=blockers,
        summary=summary,
        explanation=explanation,
        report_text=report_text,
        ranked_population=ranked_population,
        ranking_statistics=ranking_statistics,
    )

    export_bundle = build_ranking_export_bundle(report_bundle)

    return {
        "regen_candidate_ranking_report_owner_complete": True,
        "phase_11b_4c_regen_candidate_ranking_report_owner_complete": True,
        "regen_candidate_ranking_report_owner_ready": ready,
        "regen_candidate_ranking_report_owner_status": status,
        "regen_candidate_ranking_report_owner_blockers": blockers,

        "regen_candidate_ranking_summary": summary,
        "regen_candidate_ranking_explanation": explanation,
        "regen_candidate_ranking_report_bundle": report_bundle,
        "regen_candidate_ranking_export_bundle": export_bundle,
        "regen_candidate_ranking_report_text": report_text,

        # Compatibility aliases.
        "regen_ranking_report_owner_complete": True,
        "regen_ranking_report_owner_ready": ready,
        "regen_ranking_report_owner_status": status,
        "regen_ranking_report_bundle": report_bundle,
        "regen_ranking_export_bundle": export_bundle,

        # Report owner does not register anything yet.
        "regen_candidate_ranking_report_registered": False,
        "regen_candidate_ranking_report_viewer_registered": False,
        "regen_candidate_ranking_report_export_registered": False,

        # Safety locks.
        "regen_candidate_ranking_report_owner_mutation_executed": False,
        "regen_candidate_ranking_report_owner_evolution_executed": False,
        "regen_candidate_ranking_report_owner_solver_executed": False,
        "regen_candidate_ranking_report_owner_live_commit_executed": False,
        "regen_candidate_ranking_report_owner_candidate_acceptance_executed": False,
    }


def build_ranking_summary(
    objective,
    ranked_population,
    ranking_statistics,
    best_candidate,
):
    best_ranking = {}

    if isinstance(best_candidate, dict):
        best_ranking = best_candidate.get("ranking") or {}

    return {
        "objective": objective,
        "population_size": len(ranked_population),
        "best_candidate_id": (
            best_candidate.get("candidate_id")
            if isinstance(best_candidate, dict)
            else None
        ),
        "best_score": ranking_statistics.get("best_score"),
        "worst_score": ranking_statistics.get("worst_score"),
        "mean_score": ranking_statistics.get("mean_score"),
        "score_spread": ranking_statistics.get("score_spread"),
        "best_candidate_rank": best_ranking.get("rank"),
        "best_candidate_method": best_ranking.get("score_method"),
        "ranking_method": "architecture_safe_geometry_proxy",
        "ranking_limitations": [
            "Ranking uses geometry proxy metrics only.",
            "Ranking does not run thermal solving.",
            "Ranking does not calculate true pressure drop.",
            "Ranking does not mutate or evolve candidates.",
            "Ranking does not commit geometry.",
        ],
    }


def build_ranking_explanation(
    objective,
    ranked_population,
    ranking_statistics,
    best_candidate,
):
    if not isinstance(best_candidate, dict):
        return {
            "best_candidate_reason": "No best candidate was available.",
            "score_distribution_reason": "No ranked population was available.",
            "methodology_reason": "Ranking report owner could not explain missing ranking data.",
        }

    ranking = best_candidate.get("ranking") or {}
    metrics = ranking.get("geometry_metrics") or {}

    best_reason_parts = [
        f"Candidate {best_candidate.get('candidate_id')} ranked first",
        f"under objective '{objective}'",
        f"with objective score {ranking.get('objective_score')}.",
    ]

    metric_reason = (
        "Its proxy metrics included "
        f"thermal={ranking.get('thermal_margin_proxy_score')}, "
        f"pressure={ranking.get('pressure_drop_proxy_score')}, "
        f"manufacturability={ranking.get('manufacturability_proxy_score')}, "
        f"mass={ranking.get('mass_proxy_score')}."
    )

    geometry_reason = (
        "Geometry metrics used by the ranking owner included "
        f"flow_area_m2={metrics.get('flow_area_m2')}, "
        f"hydraulic_diameter_m={metrics.get('hydraulic_diameter_m')}, "
        f"rib_to_channel_width_ratio={metrics.get('rib_to_channel_width_ratio')}, "
        f"wall_to_channel_height_ratio={metrics.get('wall_to_channel_height_ratio')}, "
        f"aspect_ratio={metrics.get('aspect_ratio')}."
    )

    return {
        "best_candidate_reason": " ".join(best_reason_parts),
        "best_candidate_metric_reason": metric_reason,
        "best_candidate_geometry_reason": geometry_reason,
        "score_distribution_reason": (
            f"The ranked population contains {len(ranked_population)} candidates. "
            f"Best score={ranking_statistics.get('best_score')}, "
            f"worst score={ranking_statistics.get('worst_score')}, "
            f"mean score={ranking_statistics.get('mean_score')}, "
            f"spread={ranking_statistics.get('score_spread')}."
        ),
        "methodology_reason": (
            "The ranking owner used architecture-safe geometry proxy scoring. "
            "This gives early ranking structure without pretending to be final thermal optimisation."
        ),
        "safety_reason": (
            "No mutation, evolution, candidate solving, live geometry commit, or candidate acceptance "
            "was performed by the ranking report owner."
        ),
    }


def build_ranking_report_text(
    status,
    ready,
    objective,
    blockers,
    summary,
    explanation,
    ranked_population,
    ranking_statistics,
):
    lines = [
        "LEAF PHASE 11B.4C CANDIDATE RANKING REPORT OWNER",
        "=================================================",
        "",
        f"Owner: {OWNER_NAME}",
        f"Phase: {PHASE}",
        f"Status: {status}",
        f"Report ready: {ready}",
        f"Objective: {objective}",
        "",
        "Purpose:",
        "- Explains the ranked candidate population.",
        "- Explains why the best candidate won.",
        "- Packages ranking outputs for future registration/export.",
        "- Does not mutate, evolve, solve, accept, or commit candidates.",
        "",
        "Blockers:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Ranking Summary:",
    ])

    for key, value in summary.items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "Ranking Explanation:",
    ])

    for key, value in explanation.items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "Ranking Statistics:",
    ])

    for key, value in ranking_statistics.items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "Ranked Candidate Table:",
        "rank | candidate_id | objective_score | thermal | pressure | manufacturability | mass",
        "-----|--------------|-----------------|---------|----------|-------------------|-----",
    ])

    if ranked_population:
        for candidate in ranked_population:
            ranking = candidate.get("ranking") or {}
            lines.append(
                f"{ranking.get('rank')} | "
                f"{candidate.get('candidate_id')} | "
                f"{ranking.get('objective_score')} | "
                f"{ranking.get('thermal_margin_proxy_score')} | "
                f"{ranking.get('pressure_drop_proxy_score')} | "
                f"{ranking.get('manufacturability_proxy_score')} | "
                f"{ranking.get('mass_proxy_score')}"
            )
    else:
        lines.append("None | None | None | None | None | None | None")

    lines.extend([
        "",
        "Safety Locks:",
        "- Mutation executed: False",
        "- Evolution executed: False",
        "- Solver executed: False",
        "- Live commit executed: False",
        "- Candidate acceptance executed: False",
        "",
        "Completion Meaning:",
        "- 11B.4C proves ranking output is report-owned.",
        "- 11B.4D must register this report before ranking completion audit.",
        "- Mutation and evolution remain forbidden.",
    ])

    return "\n".join(lines)


def build_ranking_report_bundle(
    status,
    ready,
    objective,
    blockers,
    summary,
    explanation,
    report_text,
    ranked_population,
    ranking_statistics,
):
    return {
        "report_key": REPORT_KEY,
        "report_title": REPORT_TITLE,
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": status,
        "ready": ready,
        "complete": True,
        "objective": objective,
        "blockers": list(blockers),
        "summary": summary,
        "explanation": explanation,
        "statistics": ranking_statistics,
        "ranked_candidate_count": len(ranked_population),
        "best_candidate_id": summary.get("best_candidate_id"),
        "text": report_text,
        "architecture": {
            "ranking_owner_required": True,
            "ranking_report_owner_complete": True,
            "ranking_registration_owner_complete": False,
            "ranking_completion_audit_complete": False,
            "ranking_master_gate_complete": False,
            "mutation_allowed": False,
            "evolution_allowed": False,
            "solver_allowed": False,
            "live_commit_allowed": False,
            "candidate_acceptance_allowed": False,
        },
    }


def build_ranking_export_bundle(report_bundle):
    return {
        "export_key": "regen_candidate_ranking_export",
        "owner": OWNER_NAME,
        "phase": PHASE,
        "formats": ["txt", "json"],
        "report_key": report_bundle.get("report_key"),
        "title": report_bundle.get("report_title"),
        "export_ready": report_bundle.get("ready"),
        "payload": {
            "summary": report_bundle.get("summary"),
            "explanation": report_bundle.get("explanation"),
            "statistics": report_bundle.get("statistics"),
            "text": report_bundle.get("text"),
        },
    }
