OWNER_NAME = "REGEN_RUNTIME_SELECTION_RANKING_ENGINE"
PHASE = "14C"

PASS_STATUS = "PASS_REGEN_RUNTIME_SELECTION_RANKING_ENGINE_PHASE_14C"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_SELECTION_RANKING_ENGINE_PHASE_14C"


def attach_regen_runtime_selection_ranking_engine(results):
    if not isinstance(results, dict):
        return results

    evaluations = results.get("regen_runtime_candidate_evaluation_records", [])
    blockers = []

    if results.get("regen_runtime_selection_registry_ready") is not True:
        blockers.append("Runtime selection registry is not ready.")

    if not isinstance(evaluations, list) or not evaluations:
        blockers.append("No runtime candidate evaluations are available.")

    ranked = []

    if isinstance(evaluations, list):
        for index, record in enumerate(evaluations):
            if not isinstance(record, dict):
                blockers.append(f"Evaluation at index {index} is not a dictionary.")
                continue

            candidate_id = record.get("runtime_candidate_id") or f"RUNTIME_CANDIDATE_{index:04d}"
            score = _score(record)

            ranked.append({
                "runtime_candidate_id": candidate_id,
                "runtime_selection_score": score,
                "runtime_selection_rank": None,
                "runtime_candidate_survives": score > 0.0,
                "runtime_candidate_eliminated": score <= 0.0,
                "runtime_selected_for_parent_pool": False,
                "source_evaluation": record,
                "selection_reason": _reason(score),
            })

    ranked = sorted(
        ranked,
        key=lambda item: float(item.get("runtime_selection_score", 0.0)),
        reverse=True,
    )

    for rank, item in enumerate(ranked, start=1):
        item["runtime_selection_rank"] = rank

    if not ranked:
        blockers.append("No ranked runtime candidates were produced.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_selection_ranking_engine_complete": True,
        "phase_14c_runtime_selection_ranking_engine_complete": True,
        "regen_runtime_selection_ranking_engine_ready": ready,
        "regen_runtime_selection_ranking_engine_status": status,
        "regen_runtime_selection_ranking_engine_blockers": blockers,

        "regen_runtime_selection_ranked_candidates": ranked if ready else [],
        "regen_runtime_selection_ranked_candidate_count": len(ranked) if ready else 0,
        "regen_runtime_selection_best_candidate": ranked[0] if ready and ranked else None,

        "runtime_selection_rank": ranked[0].get("runtime_selection_rank") if ready and ranked else None,
        "runtime_selection_score": ranked[0].get("runtime_selection_score") if ready and ranked else None,
    })

    return results


def _score(record):
    value = record.get("candidate_score")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)

    return 0.0


def _reason(score):
    if score <= 0.0:
        return "Candidate eliminated because runtime selection score is non-positive."
    return f"Candidate survives with runtime selection score {score:.3f}."
