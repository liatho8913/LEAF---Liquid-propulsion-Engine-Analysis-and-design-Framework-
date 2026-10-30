OWNER_NAME = "REGEN_CANDIDATE_IMPROVEMENT_VALIDATION_FRAMEWORK"
PHASE = "13I"
PASS_STATUS = "PASS_REGEN_CANDIDATE_IMPROVEMENT_VALIDATION_FRAMEWORK_PHASE_13I"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_IMPROVEMENT_VALIDATION_FRAMEWORK_PHASE_13I"

def attach_regen_candidate_improvement_validation_framework(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_candidate_improvement_validation_framework(results))
    return results

def build_regen_candidate_improvement_validation_framework(results):
    blockers = []

    allowed = (
        results.get("phase_13i_candidate_improvement_validation_allowed") is True
        and results.get("regen_candidate_improvement_validation_allowed") is True
    )
    if not allowed:
        blockers.append("13H multi-variable mutation framework has not allowed candidate improvement validation.")

    mv_framework = results.get("regen_multi_variable_mutation_framework", {})
    packages = results.get("regen_multi_variable_mutation_packages", [])
    population = results.get("regen_candidate_blueprint_population", {})

    if not isinstance(mv_framework, dict) or mv_framework.get("ready") is not True:
        blockers.append("Multi-variable mutation framework is missing or not ready.")
    if not isinstance(population, dict) or population.get("ready") is not True:
        blockers.append("Candidate blueprint population is missing or not ready.")
    if not isinstance(packages, list) or not packages:
        blockers.append("Multi-variable mutation packages are missing.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    framework = _build_framework(population, packages) if ready else None

    return {
        "regen_candidate_improvement_validation_framework_complete": True,
        "phase_13i_regen_candidate_improvement_validation_framework_complete": True,
        "regen_candidate_improvement_validation_framework_ready": ready,
        "regen_candidate_improvement_validation_framework_status": status,
        "regen_candidate_improvement_validation_framework_blockers": blockers,

        "regen_candidate_improvement_validation_framework": framework,
        "regen_candidate_improvement_validation_registry": framework.get("candidate_improvement_registry") if framework else None,
        "regen_candidate_improvement_validation_records": framework.get("candidate_improvement_records") if framework else [],
        "regen_candidate_improvement_validation_history": framework.get("candidate_improvement_history") if framework else None,
        "regen_candidate_improvement_validation_report": _report(status, ready, framework, blockers),

        "phase_13j_evolution_engine_foundation_allowed": ready,
        "regen_evolution_engine_foundation_allowed": ready,

        "regen_candidate_improvement_validation_execution_allowed": False,
        "regen_multi_variable_mutation_execution_allowed": False,
        "regen_real_geometry_mutation_allowed": False,
        "regen_solver_execution_from_mutation_allowed": False,
        "regen_candidate_acceptance_from_mutation_allowed": False,
        "regen_live_geometry_commit_from_mutation_allowed": False,
        "regen_candidate_blueprint_mutation_execution_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }

def _build_framework(population, packages):
    records = []
    record_id = 1

    for package in packages:
        records.append(_build_improvement_record(record_id, package))
        record_id += 1

    valid_count = len([r for r in records if r["improvement_validation"]["valid"]])
    improved_count = len([r for r in records if r["improvement_validation"]["improved_from_parent"]])

    registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "candidate_improvement_registry_id": f"CANDIDATE_IMPROVEMENT_REGISTRY_FOR_{population.get('population_id')}",
        "source_population_id": population.get("population_id"),
        "evaluation_mode": "STRUCTURAL_PROXY_NO_SOLVER_EXECUTION",
        "registered_scores": [
            "thermal_proxy_score",
            "pressure_drop_proxy_score",
            "geometry_proxy_score",
            "manufacturing_proxy_score",
            "overall_proxy_score",
        ],
        "permissions": {
            "evolution_engine_foundation_allowed": True,
            "candidate_improvement_validation_execution_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
    }

    history = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "history_state": "CANDIDATE_IMPROVEMENT_RECORDS_CREATED_NO_EXECUTION",
        "record_count": len(records),
        "valid_record_count": valid_count,
        "invalid_record_count": len(records) - valid_count,
        "improved_record_count": improved_count,
        "solver_execution_count": 0,
        "candidate_acceptance_count": 0,
        "live_commit_count": 0,
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "candidate_improvement_state": "CANDIDATE_IMPROVEMENT_VALIDATION_CREATED_EXECUTION_LOCKED",
        "candidate_improvement_registry": registry,
        "candidate_improvement_records": records,
        "candidate_improvement_history": history,
        "candidate_improvement_readiness": {
            "ready_for_evolution_engine_foundation": True,
            "ready_for_real_solver_scoring": False,
            "ready_for_candidate_acceptance": False,
            "ready_for_live_commit": False,
            "next_phase": "13J_EVOLUTION_ENGINE_FOUNDATION",
        },
    }

def _build_improvement_record(record_id, package):
    package_validation = package.get("package_validation", {})
    selected = package.get("selected_proposals", {})

    valid_package = package_validation.get("valid") is True
    scores = _proxy_scores(selected)

    overall = (
        scores["thermal_proxy_score"]
        + scores["pressure_drop_proxy_score"]
        + scores["geometry_proxy_score"]
        + scores["manufacturing_proxy_score"]
    ) / 4.0

    improved = valid_package and overall >= 0.50

    blockers = []
    if not valid_package:
        blockers.append("Source mutation package is invalid.")
    if overall < 0.50:
        blockers.append("Overall structural proxy score is below improvement threshold.")

    return {
        "record_id": f"CANDIDATE_IMPROVEMENT_RECORD_{record_id:04d}",
        "source_package_id": package.get("package_id"),
        "source_blueprint_id": package.get("source_blueprint_id"),
        "evaluation_mode": "STRUCTURAL_PROXY_NO_SOLVER_EXECUTION",
        "scores": {
            "thermal_proxy_score": scores["thermal_proxy_score"],
            "pressure_drop_proxy_score": scores["pressure_drop_proxy_score"],
            "geometry_proxy_score": scores["geometry_proxy_score"],
            "manufacturing_proxy_score": scores["manufacturing_proxy_score"],
            "overall_proxy_score": overall,
        },
        "improvement_validation": {
            "valid": valid_package,
            "improved_from_parent": improved,
            "blockers": blockers,
            "solver_executed": False,
            "candidate_accepted": False,
            "live_geometry_committed": False,
        },
        "record_state": (
            "CANDIDATE_IMPROVEMENT_RECORD_VALID_EXECUTION_LOCKED"
            if valid_package
            else "CANDIDATE_IMPROVEMENT_RECORD_INVALID"
        ),
        "execution_permissions": {
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
    }

def _proxy_scores(selected):
    axis_count = len(selected)
    completeness = min(axis_count / 6.0, 1.0)

    has_wall = "hot_gas_wall_thickness" in selected
    has_coolant = "coolant_flow_fraction" in selected
    has_geometry = all(k in selected for k in [
        "number_of_coolant_channels",
        "coolant_channel_width",
        "coolant_channel_height",
        "rib_width",
    ])

    return {
        "thermal_proxy_score": 0.7 if has_wall and has_coolant else 0.4,
        "pressure_drop_proxy_score": 0.6 if has_coolant and has_geometry else 0.4,
        "geometry_proxy_score": 0.7 if has_geometry else 0.3,
        "manufacturing_proxy_score": 0.6 if completeness >= 1.0 else 0.4,
    }

def _require_locked(results, blockers):
    required_false = {
        "regen_multi_variable_mutation_execution_allowed": "Multi-variable mutation execution is not safely locked.",
        "regen_real_geometry_mutation_allowed": "Real geometry mutation is not safely locked.",
        "regen_solver_execution_from_mutation_allowed": "Solver execution from mutation is not safely locked.",
        "regen_candidate_acceptance_from_mutation_allowed": "Candidate acceptance from mutation is not safely locked.",
        "regen_live_geometry_commit_from_mutation_allowed": "Live geometry commit from mutation is not safely locked.",
        "regen_candidate_blueprint_mutation_execution_allowed": "Candidate blueprint mutation execution is not safely locked.",
        "regen_optimisation_mutation_execution_allowed": "Optimisation mutation execution is not safely locked.",
        "regen_optimisation_live_geometry_commit_allowed": "Optimisation live geometry commit is not safely locked.",
    }
    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)

def _report(status, ready, framework, blockers):
    if not ready:
        return "PHASE 13I BLOCKED\n" + "\n".join(f"- {b}" for b in blockers)
    history = framework["candidate_improvement_history"]
    return (
        "PHASE 13I REGEN CANDIDATE IMPROVEMENT VALIDATION FRAMEWORK\n"
        f"Status: {status}\n"
        f"Record Count: {history.get('record_count')}\n"
        f"Improved Records: {history.get('improved_record_count')}\n"
        "Solver execution remains locked.\n"
        "13J evolution engine foundation may begin."
    )
