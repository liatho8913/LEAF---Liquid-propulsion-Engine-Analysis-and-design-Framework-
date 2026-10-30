"""
PHASE 11B.4B
Candidate Ranking Owner

Responsibilities:
- Consume candidate population from 11B.3.
- Require 11B.4A ranking input audit readiness.
- Score each generated candidate using architecture-safe geometry metrics.
- Produce ranked population, best candidate, and ranking statistics.
- Do NOT mutate candidates.
- Do NOT evolve generations.
- Do NOT solve candidates thermally.
- Do NOT commit live geometry.
"""


OWNER_NAME = "REGEN_CANDIDATE_RANKING_OWNER"
PHASE = "11B.4B"

PASS_STATUS = "PASS_REGEN_CANDIDATE_RANKING_OWNER_PHASE_11B4B"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_RANKING_OWNER_PHASE_11B4B"

DEFAULT_OBJECTIVE = "BALANCED"


def attach_regen_candidate_ranking_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_ranking_owner(results)
    results.update(payload)
    return results


def build_regen_candidate_ranking_owner(results):
    blockers = []

    if results.get("phase_11b_4a_regen_candidate_ranking_input_audit_complete") is not True:
        blockers.append("Phase 11B.4A ranking input audit is not complete.")

    if results.get("regen_candidate_ranking_input_audit_ready") is not True:
        blockers.append("Ranking input audit is not ready.")

    qualification_complete = (
        results.get(
            "regen_candidate_population_qualification_complete"
        )
        is True
    )

    if not qualification_complete:
        blockers.append(
            "Candidate population qualification is not complete."
        )

    population = results.get(
        "regen_candidate_qualified_population"
    )

    if not isinstance(population, list) or not population:
        blockers.append("Candidate population is missing or empty.")
        population = []

    objective = resolve_ranking_objective(results)

    ranked_population = []

    if not blockers:
        ranked_population = rank_candidate_population(
            population=population,
            objective=objective,
        )

    ranking_statistics = build_ranking_statistics(ranked_population)
    best_candidate = ranked_population[0] if ranked_population else None

    status = PASS_STATUS if not blockers else FAIL_STATUS
    ready = not blockers

    report = build_ranking_owner_report(
        status=status,
        ready=ready,
        objective=objective,
        blockers=blockers,
        ranked_population=ranked_population,
        ranking_statistics=ranking_statistics,
        best_candidate=best_candidate,
    )

    return {
        "regen_candidate_ranking_owner_complete": True,
        "phase_11b_4b_regen_candidate_ranking_owner_complete": True,
        "regen_candidate_ranking_ready": ready,
        "regen_candidate_ranking_status": status,
        "regen_candidate_ranking_blockers": blockers,
        "regen_candidate_ranking_objective": objective,

        "regen_candidate_ranked_population": ranked_population,
        "regen_candidate_ranked_population_count": len(ranked_population),
        "regen_candidate_best_candidate": best_candidate,
        "regen_candidate_ranking_statistics": ranking_statistics,
        "regen_candidate_ranking_report": report,

        # Compatibility aliases.
        "regen_ranked_population": ranked_population,
        "regen_ranked_population_count": len(ranked_population),
        "regen_best_ranked_candidate": best_candidate,
        "regen_ranking_statistics": ranking_statistics,

        # Ranking has executed, but only as architecture-safe ranking.
        "regen_candidate_ranking_owner_ranking_executed": ready,
        "regen_candidate_ranking_owner_scoring_executed": ready,

        # Safety locks remain active.
        "regen_candidate_ranking_owner_mutation_executed": False,
        "regen_candidate_ranking_owner_evolution_executed": False,
        "regen_candidate_ranking_owner_solver_executed": False,
        "regen_candidate_ranking_owner_live_commit_executed": False,
        "regen_candidate_ranking_owner_candidate_acceptance_executed": False,

        # Future-stage permissions remain locked.
        "regen_candidate_mutation_architecture_allowed": False,
        "regen_candidate_evolution_architecture_allowed": False,
        "regen_candidate_runtime_mutation_allowed": False,
        "regen_candidate_runtime_evolution_allowed": False,
        "regen_candidate_runtime_solver_allowed": False,
        "regen_candidate_runtime_live_commit_allowed": False,
    }


def resolve_ranking_objective(results):
    objective_candidates = [
        results.get("regen_selected_objective"),
        results.get("regen_objective_selector_value"),
        results.get("regen_objective_decision_objective"),
        results.get("regen_candidate_ranking_objective_requested"),
        results.get("objective"),
    ]

    for objective in objective_candidates:
        if isinstance(objective, str) and objective.strip():
            return normalise_objective(objective)

    return DEFAULT_OBJECTIVE


def normalise_objective(objective):
    text = str(objective).strip().upper().replace(" ", "_")

    aliases = {
        "THERMAL": "THERMAL_MARGIN",
        "MAX_THERMAL_MARGIN": "THERMAL_MARGIN",
        "PRESSURE": "PRESSURE_DROP",
        "MIN_PRESSURE_DROP": "PRESSURE_DROP",
        "MANUFACTURING": "MANUFACTURABILITY",
        "MANUFACTURE": "MANUFACTURABILITY",
        "BALANCE": "BALANCED",
    }

    return aliases.get(text, text if text else DEFAULT_OBJECTIVE)


def rank_candidate_population(population, objective):
    scored = []

    for index, candidate in enumerate(population):
        score_payload = score_candidate(candidate, objective, index)
        ranked_candidate = dict(candidate)
        ranked_candidate["ranking"] = score_payload
        ranked_candidate["candidate_rank_status"] = "RANKED_NOT_MUTATED_NOT_SOLVED_NOT_COMMITTED"
        ranked_candidate["candidate_rank_owner"] = OWNER_NAME
        ranked_candidate["candidate_rank_phase"] = PHASE
        scored.append(ranked_candidate)

    scored.sort(
        key=lambda item: item.get("ranking", {}).get("objective_score", float("-inf")),
        reverse=True,
    )

    for rank_index, candidate in enumerate(scored):
        candidate["ranking"]["rank"] = rank_index + 1
        candidate["ranking"]["is_best_candidate"] = rank_index == 0

    return scored


def score_candidate(candidate, objective, index):
    geometry = candidate.get("candidate_geometry") or {}

    channel_count = _positive(geometry.get("number_of_coolant_channels"), 1.0)
    width = _positive(geometry.get("coolant_channel_width"), 1.0e-9)
    height = _positive(geometry.get("coolant_channel_height"), 1.0e-9)
    rib = _positive(geometry.get("rib_width"), 1.0e-9)
    wall = _positive(geometry.get("hot_gas_wall_thickness"), 1.0e-9)
    coolant_fraction = _positive(geometry.get("coolant_flow_fraction"), 1.0)

    flow_area = channel_count * width * height
    hydraulic_diameter = 2.0 * width * height / max(width + height, 1.0e-12)
    rib_to_channel_ratio = rib / max(width, 1.0e-12)
    wall_to_channel_ratio = wall / max(height, 1.0e-12)
    aspect_ratio = height / max(width, 1.0e-12)

    thermal_score = clamp01(
        0.35 * normalised(width, 0.00025, 0.0040)
        + 0.35 * normalised(height, 0.00025, 0.0060)
        + 0.20 * normalised(flow_area, 1.0e-5, 8.0e-4)
        + 0.10 * normalised(coolant_fraction, 0.2, 1.2)
    )

    pressure_drop_score = clamp01(
        0.45 * inverse_normalised(flow_area, 1.0e-5, 8.0e-4)
        + 0.35 * inverse_normalised(hydraulic_diameter, 0.0002, 0.0060)
        + 0.20 * inverse_normalised(channel_count, 20.0, 300.0)
    )

    manufacturability_score = clamp01(
        0.35 * normalised(rib_to_channel_ratio, 0.10, 1.20)
        + 0.30 * normalised(wall, 0.0003, 0.0040)
        + 0.20 * inverse_penalty(aspect_ratio, target=1.5, tolerance=3.5)
        + 0.15 * inverse_penalty(channel_count, target=100.0, tolerance=160.0)
    )

    mass_score = clamp01(
        0.50 * inverse_normalised(wall, 0.0003, 0.0040)
        + 0.25 * inverse_normalised(rib, 0.00015, 0.0030)
        + 0.25 * inverse_normalised(channel_count, 20.0, 300.0)
    )

    objective_score = objective_score_from_metrics(
        objective=objective,
        thermal_score=thermal_score,
        pressure_drop_score=pressure_drop_score,
        manufacturability_score=manufacturability_score,
        mass_score=mass_score,
    )

    return {
        "rank": None,
        "objective": objective,
        "objective_score": objective_score,
        "thermal_margin_proxy_score": thermal_score,
        "pressure_drop_proxy_score": pressure_drop_score,
        "manufacturability_proxy_score": manufacturability_score,
        "mass_proxy_score": mass_score,
        "geometry_metrics": {
            "flow_area_m2": flow_area,
            "hydraulic_diameter_m": hydraulic_diameter,
            "rib_to_channel_width_ratio": rib_to_channel_ratio,
            "wall_to_channel_height_ratio": wall_to_channel_ratio,
            "aspect_ratio": aspect_ratio,
        },
        "score_method": "architecture_safe_geometry_proxy",
        "score_warning": (
            "This ranking uses geometry proxy metrics only. "
            "It does not run thermal solving, mutation, or optimisation."
        ),
        "input_index": index,
        "is_best_candidate": False,
    }


def objective_score_from_metrics(
    objective,
    thermal_score,
    pressure_drop_score,
    manufacturability_score,
    mass_score,
):
    objective = normalise_objective(objective)

    if objective == "THERMAL_MARGIN":
        return thermal_score

    if objective == "PRESSURE_DROP":
        return pressure_drop_score

    if objective == "MANUFACTURABILITY":
        return manufacturability_score

    if objective == "MINIMUM_MASS":
        return mass_score

    return clamp01(
        0.35 * thermal_score
        + 0.25 * pressure_drop_score
        + 0.25 * manufacturability_score
        + 0.15 * mass_score
    )


def build_ranking_statistics(ranked_population):
    if not ranked_population:
        return {
            "population_size": 0,
            "best_score": None,
            "worst_score": None,
            "mean_score": None,
            "score_spread": None,
        }

    scores = [
        float(candidate.get("ranking", {}).get("objective_score", 0.0))
        for candidate in ranked_population
    ]

    return {
        "population_size": len(ranked_population),
        "best_score": max(scores),
        "worst_score": min(scores),
        "mean_score": sum(scores) / len(scores),
        "score_spread": max(scores) - min(scores),
        "best_candidate_id": ranked_population[0].get("candidate_id"),
        "worst_candidate_id": ranked_population[-1].get("candidate_id"),
    }


def build_ranking_owner_report(
    status,
    ready,
    objective,
    blockers,
    ranked_population,
    ranking_statistics,
    best_candidate,
):
    lines = [
        "LEAF PHASE 11B.4B CANDIDATE RANKING OWNER",
        "==========================================",
        "",
        f"Owner: {OWNER_NAME}",
        f"Phase: {PHASE}",
        f"Status: {status}",
        f"Ranking ready: {ready}",
        f"Objective: {objective}",
        "",
        "Purpose:",
        "- Scores and ranks generated regen candidates.",
        "- Uses architecture-safe geometry proxy metrics.",
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
        "Ranking Statistics:",
    ])

    for key, value in ranking_statistics.items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "Best Candidate:",
    ])

    if best_candidate:
        ranking = best_candidate.get("ranking", {})
        lines.extend([
            f"- candidate_id: {best_candidate.get('candidate_id')}",
            f"- score: {ranking.get('objective_score')}",
            f"- rank: {ranking.get('rank')}",
        ])
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Ranked Candidates:",
        "rank | candidate_id | score | thermal | pressure | manufacturability | mass",
        "-----|--------------|-------|---------|----------|-------------------|-----",
    ])

    if ranked_population:
        for candidate in ranked_population:
            ranking = candidate.get("ranking", {})
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
        "- Candidate solving executed: False",
        "- Live geometry commit executed: False",
        "- Candidate acceptance executed: False",
        "",
        "Completion Meaning:",
        "- 11B.4B creates the ranking owner.",
        "- 11B.4C must create the ranking report owner.",
        "- 11B.4D must register ranking outputs.",
        "- 11B.4E and 11B.4F must audit and gate ranking before mutation work begins.",
    ])

    return "\n".join(lines)


def clamp01(value):
    return max(0.0, min(1.0, float(value)))


def normalised(value, low, high):
    value = float(value)
    low = float(low)
    high = float(high)
    if high <= low:
        return 0.0
    return clamp01((value - low) / (high - low))


def inverse_normalised(value, low, high):
    return 1.0 - normalised(value, low, high)


def inverse_penalty(value, target, tolerance):
    value = float(value)
    target = float(target)
    tolerance = max(float(tolerance), 1.0e-12)
    return clamp01(1.0 - abs(value - target) / tolerance)


def _positive(value, default):
    try:
        value = float(value)
        if value > 0.0:
            return value
    except Exception:
        pass
    return float(default)
