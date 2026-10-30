OWNER_NAME = "REGEN_CANDIDATE_VIEWER_DATA_OWNER"
PHASE = "15A"

PASS_STATUS = "PASS_REGEN_CANDIDATE_VIEWER_DATA_OWNER_PHASE_15A"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_VIEWER_DATA_OWNER_PHASE_15A"


def attach_regen_candidate_viewer_data_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_generation_viewer_data_owner_ready") is not True:
        blockers.append("Generation viewer data owner is not ready.")

    candidates = []

    for source_key in (
        "regen_runtime_selection_ranked_candidates",
        "regen_runtime_candidate_evaluation_records",
        "regen_runtime_candidate_records",
    ):
        source = results.get(source_key, [])
        if isinstance(source, list):
            for item in source:
                if isinstance(item, dict):
                    candidates.append(_candidate_row(item, source_key))

    if not candidates:
        blockers.append("No runtime candidate data is available for the viewer backend.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_candidate_viewer_data_owner_complete": True,
        "phase_15a_candidate_viewer_data_owner_complete": True,
        "regen_candidate_viewer_data_owner_ready": ready,
        "regen_candidate_viewer_data_owner_status": status,
        "regen_candidate_viewer_data_owner_blockers": blockers,

        "optimisation_viewer_candidates": candidates if ready else [],
        "optimisation_viewer_candidate_count": len(candidates) if ready else 0,
    })

    return results


def _candidate_row(item, source_key):
    return {
        "runtime_candidate_id": (
            item.get("runtime_candidate_id")
            or item.get("candidate_id")
            or item.get("runtime_generation_candidate_id")
            or "UNKNOWN_RUNTIME_CANDIDATE"
        ),
        "score": (
            item.get("runtime_selection_score")
            if item.get("runtime_selection_score") is not None
            else item.get("candidate_score")
        ),
        "rank": item.get("runtime_selection_rank"),
        "survives": item.get("runtime_candidate_survives"),
        "selected_for_parent_pool": item.get("runtime_selected_for_parent_pool"),
        "source_key": source_key,
    }
