"""
PHASE 16J.3D — Ranking Input Feed Audit + Bridge

Purpose:
- Find generated/population candidates.
- Expose them under the keys expected by ranking owners.
- Does not score, rank, mutate, solve, accept, reject, or commit geometry.
"""

SOURCE_KEYS = [
    "regen_candidate_population",
    "regen_candidate_population_candidates",
    "regen_population_candidates",
    "regen_candidate_population_report_candidates",
    "regen_optimisation_candidate_generator_candidates",
    "regen_candidate_generator_candidates",
]

TARGET_KEYS = [
    "regen_candidate_ranking_input_population",
    "regen_candidate_population_for_ranking",
    "regen_candidate_ranking_population",
]


def _extract_candidates_from_bundle(bundle):
    if not isinstance(bundle, dict):
        return []

    for key in (
        "candidates",
        "population",
        "candidate_population",
        "generated_candidates",
        "regen_candidates",
    ):
        value = bundle.get(key)
        if isinstance(value, list):
            return value

    payload = bundle.get("payload")
    if isinstance(payload, dict):
        return _extract_candidates_from_bundle(payload)

    return []


def find_candidate_population(results):
    if not isinstance(results, dict):
        return None, []

    for key in SOURCE_KEYS:
        value = results.get(key)
        if isinstance(value, list) and value:
            return key, value
        if isinstance(value, dict):
            extracted = _extract_candidates_from_bundle(value)
            if extracted:
                return key, extracted

    for key in (
        "regen_candidate_population_report_bundle",
        "regen_population_report_bundle",
        "regen_candidate_population_export_bundle",
    ):
        extracted = _extract_candidates_from_bundle(results.get(key))
        if extracted:
            return key, extracted

    return None, []


def normalise_candidate_for_ranking(candidate, index):
    if not isinstance(candidate, dict):
        return {
            "candidate_id": f"CANDIDATE_{index + 1:03d}",
            "rank_input_index": index,
            "candidate_status": "INVALID_PAYLOAD",
            "candidate_geometry": {},
            "ranking_input_notes": ["Candidate payload was not a dictionary."],
        }

    out = dict(candidate)

    out.setdefault("candidate_id", out.get("id", out.get("name", f"CANDIDATE_{index + 1:03d}")))
    out.setdefault("rank_input_index", index)
    out.setdefault("candidate_status", out.get("status", "READY_FOR_RANKING_INPUT"))

    if "candidate_geometry" not in out:
        for geometry_key in ("geometry", "regen_geometry", "candidate_inputs", "inputs"):
            value = out.get(geometry_key)
            if isinstance(value, dict):
                out["candidate_geometry"] = dict(value)
                break

    out.setdefault("candidate_geometry", {})
    out.setdefault("ranking_input_notes", [])

    return out


def attach_regen_ranking_input_feed_bridge(results):
    if not isinstance(results, dict):
        return results

    source_key, candidates = find_candidate_population(results)

    normalised = [
        normalise_candidate_for_ranking(candidate, index)
        for index, candidate in enumerate(candidates)
    ]

    for key in TARGET_KEYS:
        results[key] = list(normalised)

    results["regen_ranking_input_feed_bridge_complete"] = True
    results["phase_16j3d_complete"] = True
    results["regen_ranking_input_feed_bridge_source_key"] = source_key
    results["regen_ranking_input_feed_bridge_candidate_count"] = len(normalised)
    results["regen_ranking_input_feed_bridge_population_available"] = bool(normalised)

    if normalised:
        status = "PASS_REGEN_RANKING_INPUT_FEED_BRIDGE_PHASE_16J3D"
    else:
        status = "FAIL_REGEN_RANKING_INPUT_FEED_BRIDGE_NO_POPULATION_PHASE_16J3D"

    results["regen_ranking_input_feed_bridge_status"] = status
    results["phase_16j3d_status"] = status

    results["phase_16j3e_ranking_owner_recheck_allowed"] = bool(normalised)

    return results
