"""
PHASE 12B.1
Candidate Blueprint Generation Engine

Creates initial candidate blueprint objects from the completed 12A blueprint
ownership architecture.

Does NOT:
- run the solver
- mutate candidates
- score candidates
- accept candidates
- evolve populations
- commit geometry
"""

from datetime import datetime, timezone

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_GENERATION_ENGINE"
PHASE = "12B.1"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_GENERATION_ENGINE_PHASE_12B1"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_GENERATION_ENGINE_PHASE_12B1"


def attach_regen_candidate_blueprint_generation_engine(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_generation_engine(results))
    return results


def build_regen_candidate_blueprint_generation_engine(results):
    blockers = []

    allowed = (
        results.get("phase_12b_1_candidate_blueprint_generation_engine_allowed") is True
        and results.get("regen_candidate_blueprint_generation_engine_allowed") is True
        and results.get("regen_candidate_blueprint_ownership_architecture_complete") is True
    )

    if not allowed:
        blockers.append("12A blueprint ownership architecture has not allowed generation engine startup.")

    audit = results.get("regen_candidate_blueprint_completion_audit", {})
    if not isinstance(audit, dict) or audit.get("ready") is not True:
        blockers.append("12A.5 blueprint completion audit is missing or not ready.")

    registry = results.get("regen_candidate_blueprint_registry", {})
    if not isinstance(registry, dict) or not registry.get("candidate_blueprint_registry_id"):
        blockers.append("Blueprint registry is missing.")

    session = results.get("regen_candidate_blueprint_session", {})
    if not isinstance(session, dict) or not session.get("candidate_blueprint_session_id"):
        blockers.append("Blueprint session is missing.")

    seed_geometry = _extract_seed_geometry(results)
    if not seed_geometry:
        blockers.append("No seed geometry is available for blueprint generation.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    blueprints = []
    if ready:
        blueprints = _create_initial_blueprints(results, seed_geometry)

    report = build_report(status, ready, blueprints, blockers, seed_geometry)

    return {
        "regen_candidate_blueprint_generation_engine_complete": True,
        "phase_12b_1_regen_candidate_blueprint_generation_engine_complete": True,
        "regen_candidate_blueprint_generation_engine_ready": ready,
        "regen_candidate_blueprint_generation_engine_status": status,
        "regen_candidate_blueprint_generation_engine_blockers": blockers,

        "regen_candidate_blueprints": blueprints,
        "regen_candidate_blueprint_count": len(blueprints),
        "regen_candidate_blueprint_ids": [
            blueprint.get("blueprint_id") for blueprint in blueprints
        ],
        "regen_candidate_blueprint_generation_engine_report": report,

        "phase_12b_2_candidate_blueprint_geometry_builder_allowed": ready,
        "regen_candidate_blueprint_geometry_builder_allowed": ready,

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


def _extract_seed_geometry(results):
    sources = [
        results.get("regen_next_generation_seed_geometry"),
        results.get("regen_generation_evolution_seed_geometry"),
        _candidate_geometry(results.get("regen_optimisation_best_candidate")),
        _candidate_geometry(results.get("regen_generation_selected_candidate")),
        _manual_geometry_from_scalars(results),
    ]

    for source in sources:
        geometry = _normalise_geometry(source)
        if geometry:
            return geometry

    return {}


def _candidate_geometry(candidate):
    if isinstance(candidate, dict):
        geometry = candidate.get("candidate_geometry")
        if isinstance(geometry, dict):
            return geometry
    return {}


def _manual_geometry_from_scalars(results):
    geometry = {}

    mapping = {
        "number_of_coolant_channels": ["number_of_coolant_channels", "channel_count"],
        "coolant_channel_width": ["coolant_channel_width", "coolant_channel_width_m"],
        "coolant_channel_height": ["coolant_channel_height", "coolant_channel_height_m"],
        "rib_width": ["rib_width", "rib_width_m"],
        "hot_gas_wall_thickness": ["hot_gas_wall_thickness", "wall_thickness_m"],
        "coolant_flow_fraction": ["coolant_flow_fraction"],
    }

    for output_key, candidates in mapping.items():
        for key in candidates:
            if key in results:
                geometry[output_key] = results.get(key)
                break

    return geometry


def _normalise_geometry(source):
    if not isinstance(source, dict):
        return {}

    geometry = {}

    nch = _int(source.get("number_of_coolant_channels"))
    if nch is not None:
        geometry["number_of_coolant_channels"] = max(1, nch)

    for key in [
        "coolant_channel_width",
        "coolant_channel_height",
        "rib_width",
        "hot_gas_wall_thickness",
        "coolant_flow_fraction",
    ]:
        value = _float(source.get(key))
        if value is not None:
            geometry[key] = max(1.0e-12, value)

    required = [
        "number_of_coolant_channels",
        "coolant_channel_width",
        "coolant_channel_height",
        "rib_width",
        "hot_gas_wall_thickness",
    ]

    if not all(key in geometry for key in required):
        return {}

    if "coolant_flow_fraction" not in geometry:
        geometry["coolant_flow_fraction"] = 1.0

    return geometry


def _create_initial_blueprints(results, seed_geometry):
    registry_id = results.get("regen_candidate_blueprint_registry_id")
    session_id = results.get("regen_candidate_blueprint_session_id")
    timestamp = datetime.now(timezone.utc).isoformat()

    blueprint_variants = [
        ("seed_baseline", {}),
        ("thermal_margin_wall_plus", {"hot_gas_wall_thickness": 1.05}),
        ("cooling_area_height_plus", {"coolant_channel_height": 1.05}),
        ("manufacturing_rib_plus", {"rib_width": 1.05}),
    ]

    blueprints = []

    for index, (variant_name, multipliers) in enumerate(blueprint_variants, start=1):
        geometry = _mutate_geometry(seed_geometry, multipliers)

        blueprint_id = f"BP-12B1-{index:04d}"

        blueprints.append({
            "blueprint_id": blueprint_id,
            "blueprint_owner": OWNER_NAME,
            "blueprint_phase": PHASE,
            "blueprint_variant": variant_name,
            "blueprint_status": "CREATED_NOT_SOLVED",
            "blueprint_lifecycle_state": "BLUEPRINT_OBJECT_CREATED_EXECUTION_LOCKED",
            "created_utc": timestamp,
            "source_registry_id": registry_id,
            "source_session_id": session_id,
            "source_geometry_origin": "seed_geometry",
            "geometry_record": geometry,
            "thermal_record": {
                "status": "PENDING_12B3_THERMAL_BUILDER",
                "solver_executed": False,
            },
            "validation_record": {
                "status": "PENDING_12B4_VALIDATION_BUILDER",
                "validated": False,
            },
            "metadata_record": {
                "created_by": OWNER_NAME,
                "candidate_acceptance_allowed": False,
                "live_geometry_commit_allowed": False,
                "mutation_allowed": False,
                "solver_execution_allowed": False,
            },
        })

    return blueprints


def _mutate_geometry(seed_geometry, multipliers):
    geometry = dict(seed_geometry)

    for key, multiplier in multipliers.items():
        if key not in geometry:
            continue

        if key == "number_of_coolant_channels":
            geometry[key] = max(1, int(round(float(geometry[key]) * float(multiplier))))
        else:
            geometry[key] = max(1.0e-12, float(geometry[key]) * float(multiplier))

    return geometry


def build_report(status, ready, blueprints, blockers, seed_geometry):
    lines = [
        "PHASE 12B.1 REGEN CANDIDATE BLUEPRINT GENERATION ENGINE",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12B.2 Candidate Blueprint Geometry Builder: {ready}",
        f"Blueprint Count: {len(blueprints)}",
        "",
    ]

    if ready:
        lines.extend([
            "SEED GEOMETRY",
            f"- number_of_coolant_channels: {seed_geometry.get('number_of_coolant_channels')}",
            f"- coolant_channel_width: {seed_geometry.get('coolant_channel_width')}",
            f"- coolant_channel_height: {seed_geometry.get('coolant_channel_height')}",
            f"- rib_width: {seed_geometry.get('rib_width')}",
            f"- hot_gas_wall_thickness: {seed_geometry.get('hot_gas_wall_thickness')}",
            f"- coolant_flow_fraction: {seed_geometry.get('coolant_flow_fraction')}",
            "",
            "CREATED BLUEPRINTS",
        ])

        for blueprint in blueprints:
            lines.append(
                f"- {blueprint.get('blueprint_id')}: "
                f"{blueprint.get('blueprint_variant')} | "
                f"{blueprint.get('blueprint_lifecycle_state')}"
            )

        lines.extend([
            "",
            "SAFETY STATE",
            "- Solver execution: locked",
            "- Mutation: locked",
            "- Candidate acceptance: locked",
            "- Live geometry commit: locked",
            "",
            "RESULT",
            "12B.1 candidate blueprint generation engine is complete.",
            "Initial blueprint objects have been created.",
            "12B.2 candidate blueprint geometry builder may begin.",
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


def _float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _int(value):
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except Exception:
        return None
