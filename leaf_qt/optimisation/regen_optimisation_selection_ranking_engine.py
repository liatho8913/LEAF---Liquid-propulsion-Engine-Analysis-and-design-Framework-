OWNER_NAME = "REGEN_OPTIMISATION_SELECTION_RANKING_ENGINE"
PHASE = "13K"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_SELECTION_RANKING_ENGINE_PHASE_13K"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_SELECTION_RANKING_ENGINE_PHASE_13K"


def attach_regen_optimisation_selection_ranking_engine(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_selection_ranking_engine(results)
    results.update(payload)
    return results


def build_regen_optimisation_selection_ranking_engine(results):
    blockers = []

    allowed = (
        results.get("phase_13k_optimisation_selection_framework_allowed") is True
        or results.get("regen_optimisation_selection_framework_allowed") is True
        or results.get("regen_evolution_engine_foundation_ready") is True
    )

    if not allowed:
        blockers.append("Phase 13J evolution foundation has not unlocked 13K selection framework.")

    records = _collect_candidate_records(results)

    if not records:
        blockers.append("No candidate improvement/evaluation records are available for selection ranking.")

    ranked = []

    for index, record in enumerate(records):
        candidate_id = _candidate_id(record, index)
        score = _selection_score(record)
        survives = _survival_decision(record, score)

        ranked.append({
            "candidate_id": candidate_id,
            "source_index": index,
            "selection_score": score,
            "selection_rank": None,
            "selected_for_parent_pool": False,
            "survives_generation": survives,
            "selection_reason": _reason(record, score, survives),
            "source_record": record,
        })

    ranked = sorted(
        ranked,
        key=lambda item: (
            float(item.get("selection_score", 0.0)),
            1 if item.get("survives_generation") else 0,
        ),
        reverse=True,
    )

    for rank, item in enumerate(ranked, start=1):
        item["selection_rank"] = rank

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_optimisation_selection_ranking_engine_complete": True,
        "phase_13k_selection_ranking_engine_complete": True,
        "regen_optimisation_selection_ranking_engine_ready": ready,
        "regen_optimisation_selection_ranking_engine_status": status,
        "regen_optimisation_selection_ranking_engine_blockers": blockers,
        "regen_optimisation_selection_ranked_candidates": ranked if ready else [],
        "regen_optimisation_selection_candidate_count": len(ranked),
        "regen_optimisation_selection_best_candidate": ranked[0] if ready and ranked else None,

        "regen_optimisation_selection_solver_executed": False,
        "regen_optimisation_selection_geometry_modified": False,
        "regen_optimisation_selection_candidate_accepted": False,
        "regen_optimisation_selection_live_geometry_committed": False,
    }


def _collect_candidate_records(results):
    candidate_sources = [
        "regen_candidate_improvement_validation_records",
        "regen_candidate_evaluation_records",
        "regen_multi_variable_mutation_evaluation_records",
        "regen_candidate_blueprint_population_records",
        "regen_candidate_population_records",
    ]

    for key in candidate_sources:
        value = results.get(key)
        if isinstance(value, list) and value:
            return [item for item in value if isinstance(item, dict)]

    population = results.get("regen_candidate_blueprint_population")
    if isinstance(population, dict):
        for key in ("records", "candidates", "candidate_records"):
            value = population.get(key)
            if isinstance(value, list) and value:
                return [item for item in value if isinstance(item, dict)]

    return []


def _candidate_id(record, index):
    for key in ("candidate_id", "blueprint_id", "mutation_package_id", "record_id"):
        value = record.get(key)
        if value:
            return str(value)
    return f"SELECTION_CANDIDATE_{index:04d}"


def _selection_score(record):
    explicit_keys = (
        "selection_score",
        "candidate_score",
        "improvement_score",
        "evaluation_score",
        "fitness_score",
        "score",
    )

    for key in explicit_keys:
        value = record.get(key)
        if _is_number(value):
            return float(value)

    validation = record.get("improvement_validation")
    if isinstance(validation, dict):
        score = 0.0

        if validation.get("valid") is True:
            score += 40.0
        if validation.get("improved_from_parent") is True:
            score += 40.0
        if validation.get("thermal_margin_improved") is True:
            score += 10.0
        if validation.get("pressure_drop_acceptable") is True:
            score += 10.0

        return score

    score = 0.0

    if record.get("valid") is True:
        score += 40.0
    if record.get("improved_from_parent") is True:
        score += 40.0
    if record.get("thermal_pass") is True:
        score += 10.0
    if record.get("pressure_drop_pass") is True:
        score += 10.0

    return score


def _survival_decision(record, score):
    if record.get("valid") is False:
        return False

    validation = record.get("improvement_validation")
    if isinstance(validation, dict) and validation.get("valid") is False:
        return False

    return float(score) > 0.0


def _reason(record, score, survives):
    if not survives:
        return "Candidate did not survive because it is invalid or has no positive selection score."

    validation = record.get("improvement_validation")
    if isinstance(validation, dict):
        if validation.get("improved_from_parent") is True:
            return "Candidate survives because improvement validation shows positive parent improvement."
        if validation.get("valid") is True:
            return "Candidate survives because it is valid and has a positive selection score."

    return f"Candidate survives with selection score {score:.3f}."


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)
