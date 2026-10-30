"""
PHASE 16J.1 — Ranking Payload Bridge

Purpose:
- Expose ranked/scored candidate payloads consistently to the Candidate Ranking Inspector.
- Does not rank candidates itself.
- Does not solve, mutate, accept, reject, or commit geometry.
"""

SOURCE_KEYS = [
    "regen_candidate_ranking_inspector_ranked_candidates",
    "regen_optimisation_recommendation_ranked_candidates",
    "regen_optimisation_selection_ranked_candidates",
    "regen_optimisation_scored_candidates",
    "regen_candidate_ranking_ranked_candidates",
    "ranked_candidates",
]


def _normalise_candidate(candidate, index):
    if not isinstance(candidate, dict):
        return {
            "candidate_id": f"CANDIDATE_{index + 1:03d}",
            "rank": index + 1,
            "score": 0.0,
            "candidate_status": "INVALID_CANDIDATE_PAYLOAD",
            "ranking_explanation": "Candidate payload was not a dictionary.",
        }

    candidate = dict(candidate)

    candidate.setdefault("candidate_id", candidate.get("id", f"CANDIDATE_{index + 1:03d}"))
    candidate.setdefault("rank", candidate.get("candidate_rank", index + 1))
    candidate.setdefault("score", candidate.get("candidate_score", candidate.get("total_score", 0.0)))
    candidate.setdefault("candidate_status", candidate.get("status", "RANKED_OR_SCORED"))
    candidate.setdefault("winner", index == 0)

    if "candidate_geometry" not in candidate:
        if isinstance(candidate.get("geometry"), dict):
            candidate["candidate_geometry"] = dict(candidate["geometry"])
        elif isinstance(candidate.get("regen_geometry"), dict):
            candidate["candidate_geometry"] = dict(candidate["regen_geometry"])
        else:
            candidate["candidate_geometry"] = {}

    if "score_breakdown" not in candidate:
        if isinstance(candidate.get("scores"), dict):
            candidate["score_breakdown"] = dict(candidate["scores"])
        elif isinstance(candidate.get("metrics"), dict):
            candidate["score_breakdown"] = dict(candidate["metrics"])
        else:
            candidate["score_breakdown"] = {}

    candidate.setdefault(
        "ranking_explanation",
        "Ranking payload bridge exposed this candidate from an upstream scoring/ranking source."
    )

    return candidate


def _find_payload(results):
    for key in SOURCE_KEYS:
        payload = results.get(key)
        if isinstance(payload, list) and payload:
            return key, payload
    return None, []


def attach_regen_candidate_ranking_payload_bridge(results):
    if not isinstance(results, dict):
        return results

    source_key, payload = _find_payload(results)

    normalised = [
        _normalise_candidate(candidate, index)
        for index, candidate in enumerate(payload)
    ]

    results["regen_candidate_ranking_payload_bridge_complete"] = True
    results["phase_16j1_complete"] = True

    if normalised:
        results["regen_candidate_ranking_payload_bridge_status"] = (
            "PASS_REGEN_CANDIDATE_RANKING_PAYLOAD_BRIDGE_PHASE_16J1"
        )
        results["phase_16j1_status"] = (
            "PASS_REGEN_CANDIDATE_RANKING_PAYLOAD_BRIDGE_PHASE_16J1"
        )
    else:
        results["regen_candidate_ranking_payload_bridge_status"] = (
            "WARN_REGEN_CANDIDATE_RANKING_PAYLOAD_BRIDGE_NO_RANKED_CANDIDATES_PHASE_16J1"
        )
        results["phase_16j1_status"] = (
            "WARN_REGEN_CANDIDATE_RANKING_PAYLOAD_BRIDGE_NO_RANKED_CANDIDATES_PHASE_16J1"
        )

    results["regen_candidate_ranking_payload_bridge_source_key"] = source_key
    results["regen_candidate_ranking_payload_bridge_candidate_count"] = len(normalised)
    results["regen_candidate_ranking_inspector_ranked_candidates"] = normalised
    results["regen_candidate_ranking_inspector_candidate_count"] = len(normalised)

    results["phase_16k_recommendation_explanation_viewer_allowed"] = bool(normalised)

    return results
