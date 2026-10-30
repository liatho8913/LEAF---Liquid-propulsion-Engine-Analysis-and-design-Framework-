"""
PHASE 12B.2
Candidate Blueprint Geometry Builder

Enriches candidate blueprint objects with geometry packages.

Does NOT:
- run thermal calculations
- run the solver
- mutate candidates
- score candidates
- accept candidates
- evolve populations
- commit geometry
"""

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_GEOMETRY_BUILDER"
PHASE = "12B.2"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_GEOMETRY_BUILDER_PHASE_12B2"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_GEOMETRY_BUILDER_PHASE_12B2"


def attach_regen_candidate_blueprint_geometry_builder(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_geometry_builder(results))
    return results


def build_regen_candidate_blueprint_geometry_builder(results):
    blockers = []

    allowed = (
        results.get("phase_12b_2_candidate_blueprint_geometry_builder_allowed") is True
        and results.get("regen_candidate_blueprint_geometry_builder_allowed") is True
    )

    if not allowed:
        blockers.append("12B.1 blueprint generation engine has not allowed geometry building.")

    blueprints = results.get("regen_candidate_blueprints", [])
    if not isinstance(blueprints, list) or not blueprints:
        blockers.append("No candidate blueprints are available.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    enriched_blueprints = []
    if ready:
        for blueprint in blueprints:
            enriched_blueprints.append(_enrich_blueprint_geometry(blueprint))

    report = build_report(status, ready, enriched_blueprints, blockers)

    return {
        "regen_candidate_blueprint_geometry_builder_complete": True,
        "phase_12b_2_regen_candidate_blueprint_geometry_builder_complete": True,
        "regen_candidate_blueprint_geometry_builder_ready": ready,
        "regen_candidate_blueprint_geometry_builder_status": status,
        "regen_candidate_blueprint_geometry_builder_blockers": blockers,

        "regen_candidate_blueprints": enriched_blueprints,
        "regen_candidate_blueprint_geometry_package_count": len(enriched_blueprints),
        "regen_candidate_blueprint_geometry_ready_ids": [
            blueprint.get("blueprint_id") for blueprint in enriched_blueprints
        ],
        "regen_candidate_blueprint_geometry_builder_report": report,

        "phase_12b_3_candidate_blueprint_thermal_builder_allowed": ready,
        "regen_candidate_blueprint_thermal_builder_allowed": ready,

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


def _enrich_blueprint_geometry(blueprint):
    updated = dict(blueprint)
    geometry = dict(updated.get("geometry_record", {}))

    package = _build_geometry_package(geometry)

    updated["geometry_package"] = package
    updated["geometry_record"] = geometry
    updated["blueprint_geometry_status"] = "GEOMETRY_PACKAGE_CREATED_NOT_THERMALLY_SOLVED"
    updated["blueprint_lifecycle_state"] = "BLUEPRINT_GEOMETRY_READY_THERMAL_LOCKED"

    metadata = dict(updated.get("metadata_record", {}))
    metadata.update({
        "geometry_builder": OWNER_NAME,
        "geometry_package_created": True,
        "thermal_builder_allowed": False,
        "solver_execution_allowed": False,
        "live_geometry_commit_allowed": False,
    })
    updated["metadata_record"] = metadata

    return updated


def _build_geometry_package(geometry):
    nch = _int(geometry.get("number_of_coolant_channels"), 0)
    width = _float(geometry.get("coolant_channel_width"), 0.0)
    height = _float(geometry.get("coolant_channel_height"), 0.0)
    rib = _float(geometry.get("rib_width"), 0.0)
    wall = _float(geometry.get("hot_gas_wall_thickness"), 0.0)
    flow_fraction = _float(geometry.get("coolant_flow_fraction"), 1.0)

    hydraulic_diameter = _hydraulic_diameter(width, height)
    single_channel_area = max(0.0, width * height)
    total_flow_area = max(0.0, single_channel_area * nch)
    pitch = max(0.0, width + rib)
    aspect_ratio = _safe_div(height, width)

    constraints = _build_constraint_package(
        nch=nch,
        width=width,
        height=height,
        rib=rib,
        wall=wall,
        flow_fraction=flow_fraction,
        hydraulic_diameter=hydraulic_diameter,
        total_flow_area=total_flow_area,
        aspect_ratio=aspect_ratio,
    )

    readiness = _build_readiness_package(constraints)

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": "GEOMETRY_PACKAGE_CREATED",
        "geometry_dimensions": {
            "number_of_coolant_channels": nch,
            "coolant_channel_width_m": width,
            "coolant_channel_height_m": height,
            "rib_width_m": rib,
            "hot_gas_wall_thickness_m": wall,
            "coolant_flow_fraction": flow_fraction,
            "channel_pitch_m": pitch,
            "single_channel_area_m2": single_channel_area,
            "total_coolant_flow_area_m2": total_flow_area,
            "hydraulic_diameter_m": hydraulic_diameter,
            "channel_aspect_ratio": aspect_ratio,
        },
        "geometry_constraints": constraints,
        "geometry_provenance": {
            "source": "12B.1_blueprint_generation_engine_geometry_record",
            "derived_by": OWNER_NAME,
            "derived_phase": PHASE,
            "solver_executed": False,
            "thermal_solved": False,
            "live_geometry_modified": False,
        },
        "geometry_readiness": readiness,
    }


def _build_constraint_package(
        nch,
        width,
        height,
        rib,
        wall,
        flow_fraction,
        hydraulic_diameter,
        total_flow_area,
        aspect_ratio,
):
    checks = [
        _check("channel_count_positive", nch > 0, "Channel count is positive."),
        _check("channel_width_positive", width > 0.0, "Channel width is positive."),
        _check("channel_height_positive", height > 0.0, "Channel height is positive."),
        _check("rib_width_positive", rib > 0.0, "Rib width is positive."),
        _check("wall_thickness_positive", wall > 0.0, "Wall thickness is positive."),
        _check(
            "coolant_flow_fraction_positive",
            flow_fraction > 0.0,
            "Coolant flow fraction is positive.",
        ),
        _check(
            "hydraulic_diameter_positive",
            hydraulic_diameter > 0.0,
            "Hydraulic diameter is positive.",
        ),
        _check(
            "total_flow_area_positive",
            total_flow_area > 0.0,
            "Total coolant flow area is positive.",
        ),
        _check(
            "aspect_ratio_reasonable",
            0.1 <= aspect_ratio <= 20.0,
            "Channel aspect ratio is within broad geometric bounds.",
        ),
    ]

    failed = [check for check in checks if not check["passed"]]

    return {
        "status": "PASS_GEOMETRY_CONSTRAINT_PACKAGE" if not failed else "FAIL_GEOMETRY_CONSTRAINT_PACKAGE",
        "checks": checks,
        "failed_checks": failed,
    }


def _build_readiness_package(constraints):
    ready = constraints.get("status") == "PASS_GEOMETRY_CONSTRAINT_PACKAGE"

    return {
        "geometry_ready_for_thermal_builder": ready,
        "geometry_ready_for_solver_execution": False,
        "geometry_ready_for_mutation": False,
        "geometry_ready_for_candidate_acceptance": False,
        "geometry_ready_for_live_commit": False,
        "next_phase": "12B.3_CANDIDATE_BLUEPRINT_THERMAL_BUILDER" if ready else None,
    }


def build_report(status, ready, blueprints, blockers):
    lines = [
        "PHASE 12B.2 REGEN CANDIDATE BLUEPRINT GEOMETRY BUILDER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12B.3 Candidate Blueprint Thermal Builder: {ready}",
        f"Geometry Package Count: {len(blueprints)}",
        "",
    ]

    if ready:
        lines.append("BLUEPRINT GEOMETRY PACKAGES")
        for blueprint in blueprints:
            package = blueprint.get("geometry_package", {})
            dims = package.get("geometry_dimensions", {})
            lines.append(
                "- {bid}: Nch={nch}, w={w}, h={h}, rib={rib}, wall={wall}, Dh={dh}".format(
                    bid=blueprint.get("blueprint_id"),
                    nch=dims.get("number_of_coolant_channels"),
                    w=dims.get("coolant_channel_width_m"),
                    h=dims.get("coolant_channel_height_m"),
                    rib=dims.get("rib_width_m"),
                    wall=dims.get("hot_gas_wall_thickness_m"),
                    dh=dims.get("hydraulic_diameter_m"),
                )
            )

        lines.extend([
            "",
            "SAFETY STATE",
            "- Thermal solving: locked",
            "- Solver execution: locked",
            "- Mutation: locked",
            "- Candidate acceptance: locked",
            "- Live geometry commit: locked",
            "",
            "RESULT",
            "12B.2 candidate blueprint geometry builder is complete.",
            "Geometry packages have been attached to all blueprint objects.",
            "12B.3 candidate blueprint thermal builder may begin.",
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


def _hydraulic_diameter(width, height):
    for value in (width, height):
        if (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and (
                value != value
                or value == float("inf")
                or value == float("-inf")
            )
        ):
            return None

    area = width * height
    perimeter = 2.0 * (width + height)
    return _safe_div(4.0 * area, perimeter)


def _safe_div(a, b):
    try:
        if b == 0:
            return 0.0
        return float(a) / float(b)
    except Exception:
        return 0.0


def _float(value, default):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _int(value, default):
    try:
        if value is None:
            return default
        return int(round(float(value)))
    except Exception:
        return default


def _check(name, passed, message):
    return {
        "name": name,
        "passed": bool(passed),
        "message": message,
    }
