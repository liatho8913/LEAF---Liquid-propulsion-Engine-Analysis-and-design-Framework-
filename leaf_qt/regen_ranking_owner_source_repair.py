"""
PHASE 16J.3E — Ranking Owner Source Repair

Purpose:
- Consume bridged candidate population.
- Produce a conservative ranked population.
- Produce best candidate.
- Populate ranking/recommendation keys used by viewers.
- Does not mutate, solve, accept/reject, or commit geometry.
"""

def _candidate_id(candidate, index):
    if isinstance(candidate, dict):
        return candidate.get("candidate_id") or candidate.get("id") or f"CANDIDATE_{index + 1:03d}"
    return f"CANDIDATE_{index + 1:03d}"


def _geometry(candidate):
    if not isinstance(candidate, dict):
        return {}
    for key in ("candidate_geometry", "geometry", "regen_geometry", "candidate_inputs", "inputs"):
        value = candidate.get(key)
        if isinstance(value, dict):
            return dict(value)
    return {}


def _float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _score_candidate(candidate, index):
    geometry = _geometry(candidate)

    channel_count = _float(geometry.get("number_of_coolant_channels"), 0.0)
    channel_width = _float(geometry.get("coolant_channel_width"), 0.0)
    channel_height = _float(geometry.get("coolant_channel_height"), 0.0)
    rib_width = _float(geometry.get("rib_width"), 0.0)
    wall = _float(geometry.get("hot_gas_wall_thickness"), 0.0)

    score = 100.0

    penalties = {}

    if channel_count <= 0:
        penalties["missing_channel_count"] = -25.0
    if channel_width <= 0:
        penalties["missing_channel_width"] = -20.0
    if channel_height <= 0:
        penalties["missing_channel_height"] = -20.0
    if rib_width <= 0:
        penalties["missing_rib_width"] = -15.0
    if wall <= 0:
        penalties["missing_wall_thickness"] = -15.0

    if channel_count > 0:
        score -= abs(channel_count - 80.0) * 0.05

    if channel_width > 0:
        score -= abs(channel_width - 0.0015) * 10000.0

    if channel_height > 0:
        score -= abs(channel_height - 0.0020) * 6000.0

    if rib_width > 0:
        score -= abs(rib_width - 0.0010) * 8000.0

    if wall > 0:
        score -= abs(wall - 0.0010) * 7000.0

    score += sum(penalties.values())
    score -= index * 0.01

    return max(0.0, round(score, 6)), penalties


def _source_population(results):
    for key in (
        "regen_candidate_ranking_input_population",
        "regen_candidate_population_for_ranking",
        "regen_candidate_ranking_population",
        "regen_candidate_population_candidates",
        "regen_population_candidates",
        "regen_optimisation_candidate_generator_candidates",
    ):
        value = results.get(key)
        if isinstance(value, list) and value:
            return key, value
    return None, []


def attach_regen_ranking_owner_source_repair(results):
    if not isinstance(results, dict):
        return results

    source_key, population = _source_population(results)

    ranked = []
    for index, candidate in enumerate(population):
        geometry = _geometry(candidate)
        score, penalties = _score_candidate(candidate, index)

        ranked_candidate = dict(candidate) if isinstance(candidate, dict) else {}
        ranked_candidate["candidate_id"] = _candidate_id(candidate, index)
        ranked_candidate["candidate_geometry"] = geometry
        ranked_candidate["rank_input_index"] = index
        ranked_candidate["score"] = score
        ranked_candidate["candidate_score"] = score
        ranked_candidate["total_score"] = score
        ranked_candidate["score_breakdown"] = {
            "geometry_completeness": 100.0 + sum(penalties.values()),
            "nominal_geometry_similarity": score,
        }
        ranked_candidate["penalties"] = penalties
        ranked_candidate["candidate_status"] = (
            "RANKED_CONSERVATIVE"
            if not penalties else
            "RANKED_WITH_MISSING_GEOMETRY_WARNINGS"
        )
        ranked_candidate["ranking_explanation"] = (
            "Candidate ranked by Phase 16J.3E source repair using conservative "
            "geometry-completeness and nominal-similarity scoring. This does not "
            "run solver optimisation or commit geometry."
        )
        ranked.append(ranked_candidate)

    ranked.sort(key=lambda item: item.get("score", 0.0), reverse=True)

    for rank, candidate in enumerate(ranked, 1):
        candidate["rank"] = rank
        candidate["candidate_rank"] = rank
        candidate["winner"] = rank == 1

    best = ranked[0] if ranked else None

    status = (
        "PASS_REGEN_RANKING_OWNER_SOURCE_REPAIR_PHASE_16J3E"
        if ranked else
        "FAIL_REGEN_RANKING_OWNER_SOURCE_REPAIR_NO_POPULATION_PHASE_16J3E"
    )

    results["regen_ranking_owner_source_repair_complete"] = True
    results["phase_16j3e_complete"] = True
    results["regen_ranking_owner_source_repair_status"] = status
    results["phase_16j3e_status"] = status
    results["regen_ranking_owner_source_repair_source_key"] = source_key
    results["regen_ranking_owner_source_repair_population_count"] = len(population)
    results["regen_ranking_owner_source_repair_ranked_count"] = len(ranked)

    results["regen_optimisation_selection_ranked_candidates"] = ranked
    results["regen_optimisation_recommendation_ranked_candidates"] = ranked
    results["regen_optimisation_scored_candidates"] = ranked
    results["regen_candidate_ranking_inspector_ranked_candidates"] = ranked

    results["regen_optimisation_selection_candidate_count"] = len(ranked)
    results["regen_optimisation_recommendation_ranked_candidate_count"] = len(ranked)
    results["regen_optimisation_scored_candidate_count"] = len(ranked)
    results["regen_candidate_ranking_inspector_candidate_count"] = len(ranked)

    results["regen_candidate_ranking_best_candidate"] = best
    results["regen_optimisation_best_candidate"] = best
    results["best_full_engine_regen_design"] = best

    results["regen_candidate_ranking_owner_status"] = (
        "PASS_REGEN_CANDIDATE_RANKING_OWNER_PHASE_16J3E"
        if ranked else
        "FAIL_REGEN_CANDIDATE_RANKING_OWNER_NO_RANKED_POPULATION_PHASE_16J3E"
    )

    results["regen_candidate_ranking_owner_complete"] = bool(ranked)
    results["phase_16j3f_recommendation_feed_repair_allowed"] = bool(ranked)

    return results
