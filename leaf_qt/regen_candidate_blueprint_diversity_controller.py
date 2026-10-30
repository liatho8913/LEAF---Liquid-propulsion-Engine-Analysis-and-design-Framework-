"""
PHASE 12D.3
Candidate Blueprint Diversity Controller

Creates the diversity governance layer for mutation-ready blueprint populations.

Does NOT:
- mutate geometry
- score candidates
- run solver
- accept candidates
- evolve populations
- commit geometry
"""

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_DIVERSITY_CONTROLLER"
PHASE = "12D.3"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_DIVERSITY_CONTROLLER_PHASE_12D3"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_DIVERSITY_CONTROLLER_PHASE_12D3"


def attach_regen_candidate_blueprint_diversity_controller(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_diversity_controller(results))
    return results


def build_regen_candidate_blueprint_diversity_controller(results):
    blockers = []

    allowed = (
        results.get("phase_12d_3_candidate_blueprint_diversity_controller_allowed") is True
        and results.get("regen_candidate_blueprint_diversity_controller_allowed") is True
    )

    if not allowed:
        blockers.append("12D.2 mutation validation has not allowed diversity controller creation.")

    mutation_validation = results.get("regen_candidate_blueprint_mutation_validation", {})
    population = results.get("regen_candidate_blueprint_population", {})
    blueprints = results.get("regen_candidate_blueprints", [])

    if not isinstance(mutation_validation, dict) or mutation_validation.get("ready") is not True:
        blockers.append("Mutation validation is missing or not ready.")

    if not isinstance(population, dict) or population.get("ready") is not True:
        blockers.append("Candidate blueprint population is missing or not ready.")

    if not isinstance(blueprints, list) or not blueprints:
        blockers.append("Candidate blueprints are missing.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    controller = None
    if ready:
        controller = _build_diversity_controller(population, blueprints, mutation_validation)

    report = build_report(status, ready, controller, blockers)

    return {
        "regen_candidate_blueprint_diversity_controller_complete": True,
        "phase_12d_3_regen_candidate_blueprint_diversity_controller_complete": True,
        "regen_candidate_blueprint_diversity_controller_ready": ready,
        "regen_candidate_blueprint_diversity_controller_status": status,
        "regen_candidate_blueprint_diversity_controller_blockers": blockers,

        "regen_candidate_blueprint_diversity_controller": controller,
        "regen_candidate_blueprint_diversity_registry": (
            controller.get("diversity_registry") if isinstance(controller, dict) else None
        ),
        "regen_candidate_blueprint_diversity_metrics": (
            controller.get("diversity_metrics") if isinstance(controller, dict) else None
        ),
        "regen_candidate_blueprint_diversity_controller_report": report,

        "phase_12d_4_candidate_blueprint_convergence_monitor_allowed": ready,
        "regen_candidate_blueprint_convergence_monitor_allowed": ready,

        "regen_candidate_blueprint_mutation_execution_allowed": False,
        "regen_candidate_blueprint_generation_execution_allowed": False,
        "regen_candidate_blueprint_create_blueprints_allowed": False,
        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_diversity_controller(population, blueprints, mutation_validation):
    metrics = _calculate_diversity_metrics(blueprints)

    registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "diversity_registry_id": f"DIVERSITY_REGISTRY_FOR_{population.get('population_id')}",
        "source_population_id": population.get("population_id"),
        "source_mutation_validation_state": mutation_validation.get("mutation_validation_state"),
        "registered_diversity_axes": [
            "number_of_coolant_channels",
            "coolant_channel_width_m",
            "coolant_channel_height_m",
            "rib_width_m",
            "hot_gas_wall_thickness_m",
            "hydraulic_diameter_m",
            "total_coolant_flow_area_m2",
        ],
        "registered_diversity_modes": [
            "range_span_tracking",
            "unique_value_tracking",
            "duplicate_geometry_detection",
            "baseline_preservation_tracking",
            "future_score_diversity_tracking",
        ],
        "permissions": {
            "convergence_monitor_allowed": True,
            "mutation_execution_allowed": False,
            "scoring_execution_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
        "future_linkage": {
            "convergence_monitor_key": "regen_candidate_blueprint_convergence_monitor",
            "termination_owner_key": "regen_candidate_blueprint_termination_owner",
            "optimisation_completion_audit_key": "regen_candidate_blueprint_optimisation_completion_audit",
        },
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "diversity_controller_state": "DIVERSITY_CONTROLLER_CREATED_EXECUTION_LOCKED",
        "source_population_id": population.get("population_id"),
        "diversity_registry": registry,
        "diversity_metrics": metrics,
        "diversity_lifecycle": {
            "controller_created": True,
            "diversity_assessed": True,
            "mutation_executed": False,
            "scoring_executed": False,
            "solver_executed": False,
            "candidate_accepted": False,
            "live_geometry_committed": False,
        },
        "diversity_readiness": {
            "ready_for_convergence_monitor": True,
            "ready_for_mutation_execution": False,
            "ready_for_scoring": False,
            "ready_for_solver_execution": False,
            "ready_for_candidate_acceptance": False,
            "ready_for_live_commit": False,
            "next_phase": "12D.4_CANDIDATE_BLUEPRINT_CONVERGENCE_MONITOR",
        },
    }


def _calculate_diversity_metrics(blueprints):
    geometry_signatures = []
    channel_counts = []
    widths = []
    heights = []
    ribs = []
    walls = []
    dh_values = []
    flow_areas = []

    for blueprint in blueprints:
        dims = _safe_get(blueprint, "geometry_package", "geometry_dimensions") or {}

        signature = (
            dims.get("number_of_coolant_channels"),
            dims.get("coolant_channel_width_m"),
            dims.get("coolant_channel_height_m"),
            dims.get("rib_width_m"),
            dims.get("hot_gas_wall_thickness_m"),
            dims.get("coolant_flow_fraction"),
        )
        geometry_signatures.append(signature)

        channel_counts.append(_float_or_none(dims.get("number_of_coolant_channels")))
        widths.append(_float_or_none(dims.get("coolant_channel_width_m")))
        heights.append(_float_or_none(dims.get("coolant_channel_height_m")))
        ribs.append(_float_or_none(dims.get("rib_width_m")))
        walls.append(_float_or_none(dims.get("hot_gas_wall_thickness_m")))
        dh_values.append(_float_or_none(dims.get("hydraulic_diameter_m")))
        flow_areas.append(_float_or_none(dims.get("total_coolant_flow_area_m2")))

    unique_signature_count = len(set(geometry_signatures))
    total = len(geometry_signatures)
    duplicate_count = max(0, total - unique_signature_count)
    uniqueness_ratio = _safe_div(unique_signature_count, total)

    return {
        "status": "DIVERSITY_METRICS_CREATED",
        "member_count": total,
        "unique_geometry_signature_count": unique_signature_count,
        "duplicate_geometry_signature_count": duplicate_count,
        "geometry_uniqueness_ratio": uniqueness_ratio,
        "diversity_warning": duplicate_count > 0,
        "diversity_passive_status": (
            "WARN_DUPLICATE_GEOMETRY_SIGNATURES_PRESENT"
            if duplicate_count > 0
            else "PASS_NO_DUPLICATE_GEOMETRY_SIGNATURES"
        ),
        "ranges": {
            "number_of_coolant_channels": _range(channel_counts),
            "coolant_channel_width_m": _range(widths),
            "coolant_channel_height_m": _range(heights),
            "rib_width_m": _range(ribs),
            "hot_gas_wall_thickness_m": _range(walls),
            "hydraulic_diameter_m": _range(dh_values),
            "total_coolant_flow_area_m2": _range(flow_areas),
        },
        "score_diversity_assessed": False,
        "thermal_diversity_assessed": False,
        "manufacturing_diversity_assessed": False,
    }


def build_report(status, ready, controller, blockers):
    lines = [
        "PHASE 12D.3 REGEN CANDIDATE BLUEPRINT DIVERSITY CONTROLLER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12D.4 Candidate Blueprint Convergence Monitor: {ready}",
        "",
    ]

    if controller:
        registry = controller.get("diversity_registry", {})
        metrics = controller.get("diversity_metrics", {})

        lines.extend([
            "DIVERSITY CONTROLLER",
            f"Controller State: {controller.get('diversity_controller_state')}",
            f"Source Population ID: {controller.get('source_population_id')}",
            "",
            "DIVERSITY REGISTRY",
            f"Registry ID: {registry.get('diversity_registry_id')}",
            f"Registered Axes: {registry.get('registered_diversity_axes')}",
            f"Registered Modes: {registry.get('registered_diversity_modes')}",
            "",
            "DIVERSITY METRICS",
            f"Member Count: {metrics.get('member_count')}",
            f"Unique Geometry Signatures: {metrics.get('unique_geometry_signature_count')}",
            f"Duplicate Geometry Signatures: {metrics.get('duplicate_geometry_signature_count')}",
            f"Geometry Uniqueness Ratio: {metrics.get('geometry_uniqueness_ratio')}",
            f"Passive Status: {metrics.get('diversity_passive_status')}",
            "",
            "PERMISSIONS",
        ])

        for key, value in registry.get("permissions", {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "SAFETY STATE",
            "- Convergence monitor: allowed next",
            "- Mutation execution: locked",
            "- Scoring: locked",
            "- Solver execution: locked",
            "- Candidate acceptance: locked",
            "- Live geometry commit: locked",
            "",
            "RESULT",
            "12D.3 candidate blueprint diversity controller is complete.",
            "Diversity governance exists, but mutation execution remains locked.",
            "12D.4 candidate blueprint convergence monitor may begin.",
        ])

    else:
        lines.append("BLOCKERS")
        for blocker in blockers:
            lines.append(f"- {blocker}")

    return "\n".join(lines)


def _require_locked(results, blockers):
    required_false = {
        "regen_candidate_blueprint_mutation_execution_allowed":
            "Candidate blueprint mutation execution is not safely locked.",
        "regen_candidate_blueprint_generation_execution_allowed":
            "Blueprint generation execution is not safely locked.",
        "regen_candidate_blueprint_create_blueprints_allowed":
            "Blueprint creation is not safely locked.",
        "regen_candidate_creation_create_candidates_allowed":
            "Candidate creation is not safely locked.",
        "regen_candidate_generation_create_candidates_allowed":
            "Candidate generation is not safely locked.",
        "regen_optimisation_runtime_execution_allowed":
            "Runtime optimisation execution is not safely locked.",
        "regen_optimisation_generation_advance_allowed":
            "Population generation advance is not safely locked.",
        "regen_optimisation_mutation_execution_allowed":
            "Mutation execution is not safely locked.",
        "regen_optimisation_candidate_acceptance_allowed":
            "Candidate acceptance is not safely locked.",
        "regen_optimisation_live_geometry_commit_allowed":
            "Live geometry commit is not safely locked.",
    }

    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)


def _safe_get(data, *keys):
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _float_or_none(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _range(values):
    cleaned = [value for value in values if value is not None]
    if not cleaned:
        return None
    return {
        "min": min(cleaned),
        "max": max(cleaned),
        "span": max(cleaned) - min(cleaned),
    }


def _safe_div(a, b):
    try:
        if not b:
            return 0.0
        return float(a) / float(b)
    except Exception:
        return 0.0
