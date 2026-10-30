"""
PHASE 12C.1
Candidate Blueprint Population Builder

Builds a managed population object from engineering-complete candidate
blueprints.

Does NOT:
- mutate candidates
- score candidates
- run solver
- accept candidates
- evolve populations
- commit geometry
"""

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_POPULATION_BUILDER"
PHASE = "12C.1"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_POPULATION_BUILDER_PHASE_12C1"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_POPULATION_BUILDER_PHASE_12C1"


def attach_regen_candidate_blueprint_population_builder(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_population_builder(results))
    return results


def build_regen_candidate_blueprint_population_builder(results):
    blockers = []

    allowed = (
        results.get("phase_12c_1_candidate_blueprint_population_builder_allowed") is True
        and results.get("regen_candidate_blueprint_population_builder_allowed") is True
    )

    if not allowed:
        blockers.append("12B.5 engineering completion audit has not allowed population building.")

    blueprints = results.get("regen_candidate_blueprints", [])
    if not isinstance(blueprints, list) or not blueprints:
        blockers.append("No engineering-complete candidate blueprints are available.")

    complete_blueprints = []
    if isinstance(blueprints, list):
        for blueprint in blueprints:
            if _blueprint_engineering_complete(blueprint):
                complete_blueprints.append(blueprint)
            else:
                blockers.append(
                    f"Blueprint {blueprint.get('blueprint_id')} is not engineering-complete."
                )

    _require_locked(results, blockers)

    ready = len(blockers) == 0 and len(complete_blueprints) > 0
    status = PASS_STATUS if ready else FAIL_STATUS

    population = None
    if ready:
        population = _build_population(results, complete_blueprints)

    report = build_report(status, ready, population, blockers)

    return {
        "regen_candidate_blueprint_population_builder_complete": True,
        "phase_12c_1_regen_candidate_blueprint_population_builder_complete": True,
        "regen_candidate_blueprint_population_builder_ready": ready,
        "regen_candidate_blueprint_population_builder_status": status,
        "regen_candidate_blueprint_population_builder_blockers": blockers,

        "regen_candidate_blueprint_population": population,
        "regen_candidate_blueprint_population_id": (
            population.get("population_id") if isinstance(population, dict) else None
        ),
        "regen_candidate_blueprint_population_member_count": (
            population.get("member_count") if isinstance(population, dict) else 0
        ),
        "regen_candidate_blueprint_population_member_ids": (
            population.get("member_ids") if isinstance(population, dict) else []
        ),
        "regen_candidate_blueprint_population_builder_report": report,

        "phase_12c_2_candidate_blueprint_population_registration_allowed": ready,
        "regen_candidate_blueprint_population_registration_allowed": ready,

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


def _build_population(results, blueprints):
    member_ids = [blueprint.get("blueprint_id") for blueprint in blueprints]
    population_id = _build_population_id(results)

    members = []
    for index, blueprint in enumerate(blueprints, start=1):
        members.append({
            "population_index": index,
            "blueprint_id": blueprint.get("blueprint_id"),
            "blueprint_variant": blueprint.get("blueprint_variant"),
            "blueprint_engineering_status": blueprint.get("blueprint_engineering_status"),
            "blueprint_lifecycle_state": blueprint.get("blueprint_lifecycle_state"),
            "geometry_summary": _geometry_summary(blueprint),
            "thermal_summary": _thermal_summary(blueprint),
            "validation_summary": _validation_summary(blueprint),
            "completion_summary": _completion_summary(blueprint),
        })

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "population_id": population_id,
        "population_lifecycle_state": "BLUEPRINT_POPULATION_CREATED_EXECUTION_LOCKED",
        "population_source": "12B.5_engineering_complete_blueprints",
        "source_blueprint_engineering_completion_audit_status": results.get(
            "regen_candidate_blueprint_engineering_completion_audit_status"
        ),
        "member_count": len(blueprints),
        "member_ids": member_ids,
        "members": members,
        "population_statistics": _population_statistics(blueprints),
        "population_provenance": {
            "source_phase": "12B.5",
            "derived_by": OWNER_NAME,
            "derived_phase": PHASE,
            "mutation_executed": False,
            "scoring_executed": False,
            "solver_executed": False,
            "candidate_acceptance_executed": False,
            "live_geometry_modified": False,
        },
        "population_readiness": {
            "ready_for_population_registration": True,
            "ready_for_population_validation": False,
            "ready_for_mutation": False,
            "ready_for_scoring": False,
            "ready_for_solver_execution": False,
            "ready_for_candidate_acceptance": False,
            "ready_for_live_commit": False,
            "next_phase": "12C.2_CANDIDATE_BLUEPRINT_POPULATION_REGISTRATION",
        },
    }


def _build_population_id(results):
    audit = results.get("regen_candidate_blueprint_engineering_completion_audit", {})
    if isinstance(audit, dict) and audit.get("phase"):
        return f"BLUEPRINT_POPULATION_FROM_{audit.get('phase').replace('.', '')}"
    return "BLUEPRINT_POPULATION_12C1"


def _blueprint_engineering_complete(blueprint):
    if not isinstance(blueprint, dict):
        return False

    return (
        blueprint.get("blueprint_completion_status")
        == "PASS_BLUEPRINT_ENGINEERING_COMPLETION_AUDIT"
        and blueprint.get("blueprint_engineering_status")
        == "ENGINEERING_BLUEPRINT_COMPLETE_READY_FOR_POPULATION"
        and blueprint.get("blueprint_lifecycle_state")
        == "BLUEPRINT_ENGINEERING_COMPLETE_POPULATION_LOCKED"
        and isinstance(blueprint.get("geometry_package"), dict)
        and isinstance(blueprint.get("thermal_package"), dict)
        and isinstance(blueprint.get("validation_package"), dict)
        and isinstance(blueprint.get("blueprint_completion_audit"), dict)
    )


def _geometry_summary(blueprint):
    dims = _safe_get(blueprint, "geometry_package", "geometry_dimensions") or {}
    return {
        "number_of_coolant_channels": dims.get("number_of_coolant_channels"),
        "coolant_channel_width_m": dims.get("coolant_channel_width_m"),
        "coolant_channel_height_m": dims.get("coolant_channel_height_m"),
        "rib_width_m": dims.get("rib_width_m"),
        "hot_gas_wall_thickness_m": dims.get("hot_gas_wall_thickness_m"),
        "hydraulic_diameter_m": dims.get("hydraulic_diameter_m"),
        "total_coolant_flow_area_m2": dims.get("total_coolant_flow_area_m2"),
    }


def _thermal_summary(blueprint):
    state = _safe_get(blueprint, "thermal_package", "thermal_state") or {}
    return {
        "regen_heat_flux_reference": state.get("regen_heat_flux_reference"),
        "regen_pressure_drop_reference": state.get("regen_pressure_drop_reference"),
        "regen_validation_status_reference": state.get("regen_validation_status_reference"),
    }


def _validation_summary(blueprint):
    package = blueprint.get("validation_package", {})
    readiness = package.get("validation_readiness", {}) if isinstance(package, dict) else {}
    return {
        "validation_status": package.get("status") if isinstance(package, dict) else None,
        "ready_for_completion_audit": readiness.get("blueprint_ready_for_completion_audit"),
        "ready_for_population_builder": readiness.get("blueprint_ready_for_population_builder"),
    }


def _completion_summary(blueprint):
    audit = blueprint.get("blueprint_completion_audit", {})
    return {
        "completion_status": audit.get("status") if isinstance(audit, dict) else None,
        "completion_ready": audit.get("ready") if isinstance(audit, dict) else None,
        "completion_state": audit.get("blueprint_completion_state") if isinstance(audit, dict) else None,
    }


def _population_statistics(blueprints):
    widths = []
    heights = []
    ribs = []
    walls = []
    channels = []

    for blueprint in blueprints:
        dims = _safe_get(blueprint, "geometry_package", "geometry_dimensions") or {}
        widths.append(_float_or_none(dims.get("coolant_channel_width_m")))
        heights.append(_float_or_none(dims.get("coolant_channel_height_m")))
        ribs.append(_float_or_none(dims.get("rib_width_m")))
        walls.append(_float_or_none(dims.get("hot_gas_wall_thickness_m")))
        channels.append(_float_or_none(dims.get("number_of_coolant_channels")))

    return {
        "member_count": len(blueprints),
        "channel_count_range": _range(channels),
        "channel_width_range_m": _range(widths),
        "channel_height_range_m": _range(heights),
        "rib_width_range_m": _range(ribs),
        "wall_thickness_range_m": _range(walls),
        "diversity_assessed": False,
        "scoring_assessed": False,
    }


def build_report(status, ready, population, blockers):
    lines = [
        "PHASE 12C.1 REGEN CANDIDATE BLUEPRINT POPULATION BUILDER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12C.2 Candidate Blueprint Population Registration: {ready}",
        "",
    ]

    if population:
        lines.extend([
            "POPULATION",
            f"Population ID: {population.get('population_id')}",
            f"Lifecycle State: {population.get('population_lifecycle_state')}",
            f"Member Count: {population.get('member_count')}",
            "",
            "MEMBERS",
        ])

        for member in population.get("members", []):
            lines.append(
                "- #{idx} {bid}: variant={variant}; engineering={eng}".format(
                    idx=member.get("population_index"),
                    bid=member.get("blueprint_id"),
                    variant=member.get("blueprint_variant"),
                    eng=member.get("blueprint_engineering_status"),
                )
            )

        lines.extend([
            "",
            "STATISTICS",
            f"Channel Count Range: {population.get('population_statistics', {}).get('channel_count_range')}",
            f"Channel Width Range: {population.get('population_statistics', {}).get('channel_width_range_m')}",
            f"Channel Height Range: {population.get('population_statistics', {}).get('channel_height_range_m')}",
            f"Rib Width Range: {population.get('population_statistics', {}).get('rib_width_range_m')}",
            f"Wall Thickness Range: {population.get('population_statistics', {}).get('wall_thickness_range_m')}",
            "",
            "SAFETY STATE",
            "- Mutation: locked",
            "- Scoring: locked",
            "- Solver execution: locked",
            "- Candidate acceptance: locked",
            "- Live geometry commit: locked",
            "",
            "RESULT",
            "12C.1 candidate blueprint population builder is complete.",
            "A managed blueprint population object has been created.",
            "12C.2 candidate blueprint population registration may begin.",
        ])
    else:
        lines.append("BLOCKERS")
        for blocker in blockers:
            lines.append(f"- {blocker}")

    return "\n".join(lines)


def _require_locked(results, blockers):
    required_false = {
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
