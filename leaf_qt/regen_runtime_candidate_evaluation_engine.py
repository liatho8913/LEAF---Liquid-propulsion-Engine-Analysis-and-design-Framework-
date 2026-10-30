OWNER_NAME = "REGEN_RUNTIME_CANDIDATE_EVALUATION_ENGINE"
PHASE = "14B"

PASS_STATUS = "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_ENGINE_PHASE_14B"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CANDIDATE_EVALUATION_ENGINE_PHASE_14B"


def attach_regen_runtime_candidate_evaluation_engine(results):
    if not isinstance(results, dict):
        return results

    records = results.get("regen_runtime_candidate_records", [])
    registry_ready = results.get("regen_runtime_candidate_evaluation_registry_ready") is True
    blockers = []

    if not registry_ready:
        blockers.append("Runtime candidate evaluation registry is not ready.")

    if not isinstance(records, list) or not records:
        blockers.append("No runtime candidate records are available.")

    evaluations = []

    if isinstance(records, list):
        for index, candidate in enumerate(records):
            if not isinstance(candidate, dict):
                blockers.append(f"Runtime candidate at index {index} is not a dictionary.")
                continue

            evaluations.append(_evaluate_candidate(candidate, index))

    if not evaluations:
        blockers.append("No runtime candidate evaluations were produced.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_candidate_evaluation_engine_complete": True,
        "phase_14b_runtime_candidate_evaluation_engine_complete": True,
        "regen_runtime_candidate_evaluation_engine_ready": ready,
        "regen_runtime_candidate_evaluation_engine_status": status,
        "regen_runtime_candidate_evaluation_engine_blockers": blockers,

        "regen_runtime_candidate_evaluation_records": evaluations if ready else [],
        "regen_runtime_candidate_evaluation_record_count": len(evaluations) if ready else 0,
        "regen_runtime_candidate_evaluations": evaluations if ready else [],
        "regen_runtime_candidate_evaluation_count": len(evaluations) if ready else 0,

        "regen_runtime_candidate_evaluation_performed": ready,
        "regen_runtime_candidate_solver_executed": ready,

        "regen_runtime_candidate_acceptance_allowed": False,
        "regen_runtime_candidate_accepted": False,
        "regen_runtime_candidate_generation_advanced": False,
        "regen_runtime_candidate_live_geometry_committed": False,
    })

    return results


def _evaluate_candidate(candidate, index):
    candidate_id = (
        candidate.get("runtime_candidate_id")
        or candidate.get("candidate_id")
        or f"RUNTIME_CANDIDATE_14B_{index:04d}"
    )

    mutation_vector = candidate.get("mutation_vector")
    if not isinstance(mutation_vector, dict):
        mutation_vector = {}

    score = _score_mutation_vector(mutation_vector)

    return {
        "runtime_candidate_id": candidate_id,
        "runtime_candidate_evaluation_id": f"RUNTIME_CANDIDATE_EVALUATION_14B_{index:04d}",
        "source_runtime_mutation_execution_id": candidate.get("runtime_mutation_execution_id"),
        "phase": PHASE,
        "owner": OWNER_NAME,

        "evaluation_complete": True,
        "solver_executed": True,
        "evaluation_mode": "CONTROLLED_RUNTIME_EVALUATION_PLACEHOLDER_SOLVER_BRIDGE",

        "candidate_score": score,
        "candidate_rank": None,
        "thermal_status": "EVALUATED_PLACEHOLDER",
        "pressure_drop_status": "EVALUATED_PLACEHOLDER",
        "geometry_status": "EVALUATED_PLACEHOLDER",

        "source_candidate": candidate,

        "candidate_accepted": False,
        "generation_advanced": False,
        "live_geometry_committed": False,
    }


def _score_mutation_vector(vector):
    score = 100.0

    if "coolant_channel_count" in vector:
        try:
            count = float(vector["coolant_channel_count"])
            if count <= 0:
                score -= 50.0
            elif 40 <= count <= 240:
                score += 10.0
        except Exception:
            score -= 10.0

    if "coolant_channel_width" in vector:
        try:
            width = float(vector["coolant_channel_width"])
            if width <= 0:
                score -= 50.0
            elif 0.0003 <= width <= 0.006:
                score += 10.0
        except Exception:
            score -= 10.0

    if "coolant_channel_height" in vector:
        try:
            height = float(vector["coolant_channel_height"])
            if height <= 0:
                score -= 50.0
            elif 0.0005 <= height <= 0.010:
                score += 10.0
        except Exception:
            score -= 10.0

    if "wall_thickness" in vector:
        try:
            wall = float(vector["wall_thickness"])
            if wall <= 0:
                score -= 50.0
            elif 0.0004 <= wall <= 0.006:
                score += 10.0
        except Exception:
            score -= 10.0

    return max(0.0, score)
