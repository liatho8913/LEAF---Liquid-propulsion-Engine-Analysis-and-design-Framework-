"""
PHASE 11B.3A
Candidate Population Generation Owner

Foundation-compliant population generator.

Responsibilities:
- Generate N candidate geometries around one seed geometry.
- Preserve seed metadata.
- Produce population statistics.
- Expose safety locks.
- Do NOT solve candidates.
- Do NOT rank candidates.
- Do NOT mutate future generations.
- Do NOT commit geometry.
"""


DEFAULT_REGEN_POPULATION_SIZE = 12


def attach_regen_candidate_population_generation_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_population_generation_owner(results)
    results.update(payload)
    return results



def _normalise_candidate_design_mode(
    results,
):
    raw = str(
        results.get(
            "regen_candidate_design_mode"
        )
        or
        results.get(
            "regen_automatic_design_mode"
        )
        or
        "SELECTED_MATERIAL"
    ).strip().upper()

    aliases = {
        "AUTOMATIC — SELECTED MATERIAL":
            "SELECTED_MATERIAL",

        "AUTOMATIC - SELECTED MATERIAL":
            "SELECTED_MATERIAL",

        "AUTOMATIC_SELECTED_MATERIAL":
            "SELECTED_MATERIAL",

        "AUTOMATIC — GEOMETRY + MATERIALS":
            "GEOMETRY_AND_MATERIALS",

        "AUTOMATIC - GEOMETRY + MATERIALS":
            "GEOMETRY_AND_MATERIALS",

        "GEOMETRY + MATERIALS":
            "GEOMETRY_AND_MATERIALS",

        "GEOMETRY_AND_MATERIAL":
            "GEOMETRY_AND_MATERIALS",

        "AUTOMATIC_GEOMETRY_AND_MATERIALS":
            "GEOMETRY_AND_MATERIALS",
    }

    return aliases.get(
        raw,
        raw,
    )


def _positive_material_number(
    value,
):
    try:
        return (
            value is not None
            and
            float(value) > 0.0
        )
    except (
        TypeError,
        ValueError,
    ):
        return False


def _build_material_candidate_bundles():
    try:
        from leaf_qt.material_database import (
            get_material_names,
            get_material_properties,
        )
    except ImportError:
        from material_database import (
            get_material_names,
            get_material_properties,
        )

    bundles = []
    excluded = []

    for requested_name in (
        get_material_names()
        or []
    ):
        material = (
            get_material_properties(
                requested_name
            )
        )

        if not isinstance(
            material,
            dict,
        ):
            excluded.append({
                "material":
                    requested_name,

                "blockers":
                    [
                        "Material database lookup did "
                        "not return a dictionary."
                    ],
            })

            continue

        canonical_name = (
            material.get("name")
            or
            requested_name
        )

        max_temperature = (
            material.get(
                "max_recommended_wall_temperature"
            )
            or
            material.get(
                "max_wall_temperature"
            )
        )

        conductivity = material.get(
            "thermal_conductivity"
        )

        yield_strength = material.get(
            "yield_strength"
        )

        density = material.get(
            "density"
        )

        source_mode = (
            material.get(
                "source_validation_mode"
            )
            or
            "UNKNOWN"
        )

        blockers = []

        for (
            label,
            value,
        ) in (
            (
                "max_recommended_wall_temperature",
                max_temperature,
            ),
            (
                "thermal_conductivity",
                conductivity,
            ),
            (
                "yield_strength",
                yield_strength,
            ),
            (
                "density",
                density,
            ),
        ):
            if not _positive_material_number(
                value
            ):
                blockers.append(
                    f"Missing or non-positive "
                    f"{label}."
                )

        if not str(
            canonical_name
            or ""
        ).strip():
            blockers.append(
                "Canonical material name "
                "is unavailable."
            )

        if not str(
            source_mode
            or ""
        ).strip():
            blockers.append(
                "Material source validation "
                "mode is unavailable."
            )

        if blockers:
            excluded.append({
                "material":
                    canonical_name,

                "blockers":
                    blockers,
            })

            continue

        bundle = {
            "selected_material":
                canonical_name,

            "selected_material_name":
                canonical_name,

            "material_name":
                canonical_name,

            "hot_gas_liner":
                canonical_name,

            # Absolute temperature qualification.
            "selected_material_max_temperature":
                float(
                    max_temperature
                ),

            "material_max_wall_temperature":
                float(
                    max_temperature
                ),

            # Solver-facing material properties.
            "wall_thermal_conductivity":
                float(
                    conductivity
                ),

            "material_yield_strength":
                float(
                    yield_strength
                ),

            "material_density":
                float(
                    density
                ),

            # Canonical source-quality evidence.
            "material_source_validation_mode":
                str(
                    source_mode
                ),

            "material_source_validation_score":
                material.get(
                    "source_validation_score"
                ),

            "material_source_has_citation":
                bool(
                    material.get(
                        "source_has_citation"
                    )
                ),

            "material_source_has_temperature_table":
                bool(
                    material.get(
                        "source_has_temperature_table"
                    )
                ),

            "material_source_is_placeholder":
                bool(
                    material.get(
                        "source_is_placeholder"
                    )
                ),

            "material_source_quality":
                (
                    material.get(
                        "source_quality"
                    )
                    or
                    str(
                        source_mode
                    )
                ),

            # Evaluation-only marker.
            "_leaf_candidate_material_search_active":
                True,
        }

        bundles.append({
            "material_name":
                canonical_name,

            "material_family":
                material.get(
                    "family"
                ),

            "source_validation_mode":
                str(
                    source_mode
                ),

            "source_is_placeholder":
                bool(
                    material.get(
                        "source_is_placeholder"
                    )
                ),

            "design_inputs":
                bundle,
        })

    return (
        bundles,
        excluded,
    )


def _material_candidate_id_fragment(
    material_name,
):
    text = str(
        material_name
        or
        "UNKNOWN"
    ).strip().upper()

    fragment = "".join(
        character
        if character.isalnum()
        else "-"
        for character in text
    )

    while "--" in fragment:
        fragment = fragment.replace(
            "--",
            "-",
        )

    fragment = fragment.strip("-")

    return (
        fragment
        or
        "UNKNOWN"
    )


def _expand_population_across_materials(
    geometry_population,
    material_candidates,
):
    expanded = []

    for geometry_candidate in (
        geometry_population
        or []
    ):
        if not isinstance(
            geometry_candidate,
            dict,
        ):
            continue

        geometry = (
            geometry_candidate.get(
                "candidate_geometry"
            )
            or
            {}
        )

        if not isinstance(
            geometry,
            dict,
        ) or not geometry:
            continue

        geometry_id = str(
            geometry_candidate.get(
                "candidate_id"
            )
            or
            f"RPOP-{len(expanded) + 1:04d}"
        )

        for material in (
            material_candidates
            or []
        ):
            if not isinstance(
                material,
                dict,
            ):
                continue

            material_name = (
                material.get(
                    "material_name"
                )
            )

            material_inputs = (
                material.get(
                    "design_inputs"
                )
                or
                {}
            )

            if not isinstance(
                material_inputs,
                dict,
            ):
                continue

            design_inputs = dict(
                geometry
            )

            design_inputs.update(
                material_inputs
            )

            candidate = dict(
                geometry_candidate
            )

            candidate[
                "candidate_id"
            ] = (
                f"{geometry_id}__MAT-"
                f"{_material_candidate_id_fragment(material_name)}"
            )

            candidate[
                "candidate_geometry_id"
            ] = geometry_id

            candidate[
                "candidate_material_name"
            ] = material_name

            candidate[
                "candidate_material"
            ] = {
                key:
                    value
                for key, value
                in material.items()
                if key != "design_inputs"
            }

            candidate[
                "candidate_design_inputs"
            ] = design_inputs

            metadata = dict(
                candidate.get(
                    "candidate_metadata"
                )
                or
                {}
            )

            metadata.update({
                "automatic_design_mode":
                    "GEOMETRY_AND_MATERIALS",

                "material_search_enabled":
                    True,

                "material_name":
                    material_name,

                "material_source_validation_mode":
                    material.get(
                        "source_validation_mode"
                    ),

                "material_source_is_placeholder":
                    material.get(
                        "source_is_placeholder"
                    ),
            })

            candidate[
                "candidate_metadata"
            ] = metadata

            expanded.append(
                candidate
            )

    return expanded


def build_regen_candidate_population_generation_owner(results):
    seed = extract_population_seed_geometry(results)
    blockers = []

    if not seed.get("geometry"):
        blockers.append("No valid seed geometry was available for population generation.")

    population_size = int(
        _num(
            results.get("regen_population_requested_size"),
            DEFAULT_REGEN_POPULATION_SIZE,
        )
    )

    if population_size <= 0:
        blockers.append("Population size must be greater than zero.")

    raw_population = []
    manufacturability_rejected_candidates = []

    design_mode = (
        _normalise_candidate_design_mode(
            results
        )
    )

    material_search_enabled = (
        design_mode
        ==
        "GEOMETRY_AND_MATERIALS"
    )

    manufacturable_geometry_population = []
    material_candidates = []
    material_excluded_candidates = []

    if blockers:
        population = []
        statistics = {}
        ready = False
        status = "FAIL_REGEN_CANDIDATE_POPULATION_GENERATION_BLOCKED"
        reason = "Population generation blocked."
    else:
        raw_population = generate_population_from_seed(
            seed=seed,
            population_size=population_size,
        )

        population = []
        manufacturability_rejected_candidates = []

        try:
            from leaf_qt.regen_manufacturability_geometry_gate_phase_16q3 import (
                evaluate_manufacturability_geometry,
            )
        except ImportError:
            from regen_manufacturability_geometry_gate_phase_16q3 import (
                evaluate_manufacturability_geometry,
            )

        for candidate in raw_population:
            geometry = candidate.get(
                "candidate_geometry"
            )

            gate_result = (
                evaluate_manufacturability_geometry(
                    geometry
                )
            )

            if not isinstance(
                gate_result,
                dict,
            ):
                gate_result = {
                    "status":
                        "FAIL_REGEN_MANUFACTURABILITY_GEOMETRY_GATE_INVALID_RESULT",

                    "passed":
                        False,

                    "blockers": [
                        "Canonical manufacturability gate returned an invalid result."
                    ],

                    "warnings":
                        [],
                }

            gate_result = dict(
                gate_result
            )

            gate_passed = bool(
                gate_result.get(
                    "passed"
                )
            )

            candidate_with_gate = dict(
                candidate
            )

            candidate_with_gate[
                "candidate_manufacturability_gate_result"
            ] = gate_result

            candidate_with_gate[
                "candidate_manufacturability_gate_status"
            ] = gate_result.get(
                "status"
            )

            candidate_with_gate[
                "candidate_manufacturability_gate_pass"
            ] = gate_passed

            metadata = dict(
                candidate_with_gate.get(
                    "candidate_metadata"
                )
                or
                {}
            )

            metadata[
                "manufacturability_gate_evaluated"
            ] = True

            metadata[
                "manufacturability_gate_passed"
            ] = gate_passed

            metadata[
                "manufacturability_gate_owner"
            ] = (
                "regen_manufacturability_geometry_gate_phase_16q3"
            )

            candidate_with_gate[
                "candidate_metadata"
            ] = metadata

            if gate_passed:
                population.append(
                    candidate_with_gate
                )
            else:
                manufacturability_rejected_candidates.append(
                    candidate_with_gate
                )

        manufacturable_geometry_population = list(
            population
        )

        if (
            material_search_enabled
            and
            manufacturable_geometry_population
        ):
            (
                material_candidates,
                material_excluded_candidates,
            ) = (
                _build_material_candidate_bundles()
            )

            if material_candidates:
                population = (
                    _expand_population_across_materials(
                        manufacturable_geometry_population,
                        material_candidates,
                    )
                )

            else:
                population = []

                blockers.append(
                    "Geometry + Materials mode found "
                    "manufacturable geometry, but no "
                    "complete material database candidate "
                    "was available."
                )

        statistics = build_population_statistics(
            population
        )

        if population:
            ready = True

            if material_search_enabled:
                status = (
                    "PASS_REGEN_GEOMETRY_MATERIAL_"
                    "CANDIDATE_POPULATION_GENERATION"
                )

                reason = (
                    f"{len(manufacturable_geometry_population)} "
                    "manufacturable geometry candidates were "
                    f"expanded across {len(material_candidates)} "
                    "complete material candidates. "
                    f"Combined candidate count: {len(population)}."
                )

            else:
                status = (
                    "PASS_REGEN_CANDIDATE_POPULATION_GENERATION_OWNER_PHASE_11B3A"
                )

                reason = (
                    "Candidate population generated from seed geometry and "
                    "filtered through the canonical manufacturability geometry gate."
                )

        else:
            ready = False

            if (
                material_search_enabled
                and
                manufacturable_geometry_population
                and
                not material_candidates
            ):
                status = (
                    "FAIL_REGEN_CANDIDATE_POPULATION_"
                    "NO_ELIGIBLE_MATERIAL_CANDIDATES"
                )

                reason = (
                    "Manufacturable geometry exists, but no "
                    "complete material database candidate was "
                    "available for Geometry + Materials mode."
                )

            else:
                status = (
                    "FAIL_REGEN_CANDIDATE_POPULATION_NO_MANUFACTURABLE_CANDIDATES"
                )

                reason = (
                    "Raw candidate population was generated, but no candidate "
                    "passed the canonical manufacturability geometry gate."
                )

                blockers.append(
                    "No raw candidate passed the canonical manufacturability "
                    "geometry gate; full candidate solving is blocked."
                )

    report = build_population_generation_owner_report(
        status=status,
        ready=ready,
        reason=reason,
        blockers=blockers,
        seed=seed,
        population=population,
        statistics=statistics,
    )
    manufacturability_report_lines = [
        "",
        "Early manufacturability pre-filter:",
        (
            "- Canonical owner: "
            "regen_manufacturability_geometry_gate_phase_16q3"
        ),
        f"- Raw candidate count: {len(raw_population)}",
        (
            "- Manufacturable geometry count: "
            f"{len(manufacturable_geometry_population)}"
        ),
        (
            "- Automatic design mode: "
            f"{design_mode}"
        ),
        (
            "- Material search enabled: "
            f"{material_search_enabled}"
        ),
        (
            "- Complete material candidate count: "
            f"{len(material_candidates)}"
        ),
        (
            "- Geometry/material combined candidate count: "
            f"{len(population)}"
        ),
        (
            "- Manufacturability rejected count: "
            f"{len(manufacturability_rejected_candidates)}"
        ),
        "- Manufacturing tolerance qualification performed here: False",
        "- Full solver execution performed here: False",
    ]

    if manufacturability_rejected_candidates:
        manufacturability_report_lines.append(
            "- Rejected candidates:"
        )

        for rejected_candidate in (
            manufacturability_rejected_candidates
        ):
            gate_result = (
                rejected_candidate.get(
                    "candidate_manufacturability_gate_result"
                )
                or
                {}
            )

            gate_blockers = (
                gate_result.get(
                    "blockers"
                )
                or
                []
            )

            blocker_text = (
                "; ".join(
                    str(item)
                    for item in gate_blockers
                )
                if gate_blockers
                else
                "Canonical manufacturability geometry gate failed."
            )

            manufacturability_report_lines.append(
                "- "
                f"{rejected_candidate.get('candidate_id')}: "
                f"{blocker_text}"
            )

    report = (
        report
        +
        "\n"
        +
        "\n".join(
            manufacturability_report_lines
        )
    )

    return {
        "regen_candidate_population_generation_owner_complete": True,
        "phase_11b_3a_regen_candidate_population_generation_owner_complete": True,
        "regen_candidate_population_generation_status": status,
        "regen_candidate_population_generation_ready": ready,
        "regen_candidate_population_generation_reason": reason,
        "regen_candidate_population_generation_blockers": blockers,

        "regen_candidate_population_seed": seed,
        "regen_candidate_population_raw":
            raw_population,

        "regen_candidate_population_raw_count":
            len(
                raw_population
            ),

        "regen_candidate_population_manufacturable_count":
            len(
                manufacturable_geometry_population
            ),

        "regen_candidate_population_manufacturable_geometry_count":
            len(
                manufacturable_geometry_population
            ),

        "regen_candidate_design_mode":
            design_mode,

        "regen_candidate_material_search_enabled":
            material_search_enabled,

        "regen_candidate_material_candidate_count":
            len(
                material_candidates
            ),

        "regen_candidate_material_candidate_names":
            [
                item.get(
                    "material_name"
                )
                for item in material_candidates
            ],

        "regen_candidate_material_candidates":
            material_candidates,

        "regen_candidate_material_excluded_candidates":
            material_excluded_candidates,

        "regen_candidate_material_excluded_count":
            len(
                material_excluded_candidates
            ),

        "regen_candidate_geometry_material_combination_count":
            len(
                population
            ),

        "regen_candidate_population_manufacturability_rejected_count":
            len(
                manufacturability_rejected_candidates
            ),

        "regen_candidate_population_manufacturability_rejected_candidates":
            manufacturability_rejected_candidates,

        "regen_candidate_population_manufacturability_rejected_ids":
            [
                candidate.get(
                    "candidate_id"
                )
                for candidate in (
                    manufacturability_rejected_candidates
                )
            ],

        "regen_candidate_population_manufacturability_gate_owner":
            (
                "regen_manufacturability_geometry_gate_phase_16q3"
            ),

        "regen_candidate_population_manufacturing_tolerance_evaluated_early":
            False,
        "regen_candidate_population": population,
        "regen_candidate_population_count": len(population),
        "regen_candidate_population_ids": [
            candidate.get("candidate_id") for candidate in population
        ],
        "regen_candidate_population_statistics": statistics,
        "regen_candidate_population_generation_report": report,

        # Compatibility aliases for older viewer/search systems.
        "regen_multi_candidate_population": population,
        "regen_multi_candidate_count": len(population),
        "regen_multi_candidate_ids": [
            candidate.get("candidate_id") for candidate in population
        ],

        # Safety locks.
        "regen_candidate_population_solver_executed": False,
        "regen_candidate_population_live_geometry_modified": False,
        "regen_candidate_population_candidate_committed": False,
        "regen_candidate_population_ranking_executed": False,
        "regen_candidate_population_mutation_executed": False,
    }


def extract_population_seed_geometry(results):

    # R5Y_CANONICAL_RECOMMENDED_GEOMETRY_SEED
    #
    # RPOP should reuse the already-established canonical
    # geometry-aware recommendation before falling back to the
    # ordinary live/manual scalar geometry.
    #
    # This introduces no new geometry calculation or search rule.
    # It only changes which existing solved geometry is used as
    # the population seed when that recommendation is explicitly
    # valid and circumference-fit.
    recommended_status = str(
        results.get(
            "recommended_geometry_status"
        )
        or
        ""
    ).strip().upper()

    recommended_valid = _num(
        results.get(
            "recommended_geometry_valid"
        ),
        None,
    )

    recommended_fit_ratio = _num(
        results.get(
            "recommended_channel_fit_ratio"
        ),
        None,
    )

    recommended_geometry = {
        "number_of_coolant_channels": _num(
            results.get(
                "recommended_channel_count"
            ),
            None,
        ),
        "coolant_channel_width": _num(
            results.get(
                "recommended_channel_width"
            ),
            None,
        ),
        "coolant_channel_height": _num(
            results.get(
                "recommended_channel_height"
            ),
            None,
        ),
        "rib_width": _num(
            results.get(
                "recommended_rib_width"
            ),
            None,
        ),

        # Wall thickness remains sourced from the existing solver
        # state. R5Y does not adjudicate wall-thickness ownership.
        "hot_gas_wall_thickness": _num(
            results.get(
                "hot_gas_wall_thickness"
            ),
            0.0012,
        ),
        "coolant_flow_fraction": _num(
            results.get(
                "coolant_flow_fraction"
            ),
            1.0,
        ),
    }

    recommended_required_values = (
        recommended_geometry.get(
            "number_of_coolant_channels"
        ),
        recommended_geometry.get(
            "coolant_channel_width"
        ),
        recommended_geometry.get(
            "coolant_channel_height"
        ),
        recommended_geometry.get(
            "rib_width"
        ),
    )

    recommended_geometry_complete = all(
        value is not None
        and
        value > 0
        for value in recommended_required_values
    )

    if (
        recommended_status.startswith(
            "PASS"
        )
        and
        recommended_valid
        ==
        1.0
        and
        recommended_fit_ratio
        is not None
        and
        recommended_fit_ratio
        >=
        1.0
        and
        recommended_geometry_complete
    ):
        return {
            "seed_candidate_id":
                "canonical_recommended_geometry_seed",

            "seed_source":
                "existing_geometry_aware_recommendation",

            "geometry":
                normalise_population_geometry(
                    recommended_geometry
                ),

            "metadata": {
                "source":
                    "canonical_recommended_geometry",

                "recommended_geometry_status":
                    recommended_status,

                "recommended_geometry_valid":
                    recommended_valid,

                "recommended_channel_fit_ratio":
                    recommended_fit_ratio,
            },
        }

    geometry = {
        "number_of_coolant_channels": _num(
            results.get("number_of_coolant_channels"),
            80,
        ),
        "coolant_channel_width": _num(
            results.get("coolant_channel_width"),
            0.0015,
        ),
        "coolant_channel_height": _num(
            results.get("coolant_channel_height"),
            0.0020,
        ),
        "rib_width": _num(
            results.get("rib_width"),
            0.0010,
        ),
        "hot_gas_wall_thickness": _num(
            results.get("hot_gas_wall_thickness"),
            0.0012,
        ),
        "coolant_flow_fraction": _num(
            results.get("coolant_flow_fraction"),
            1.0,
        ),
    }

    return {
        "seed_candidate_id": "live_solver_geometry_seed",
        "seed_source": "solver_results",
        "geometry": normalise_population_geometry(geometry),
        "metadata": {
            "source": "final_results_scalar_geometry",
        },
    }


def normalise_population_geometry(geometry):
    return {
        "number_of_coolant_channels": max(
            1,
            int(round(_num(geometry.get("number_of_coolant_channels"), 80))),
        ),
        "coolant_channel_width": max(
            1.0e-9,
            _num(
                geometry.get("coolant_channel_width"),
                _num(geometry.get("coolant_channel_width_m"), 0.0015),
            ),
        ),
        "coolant_channel_height": max(
            1.0e-9,
            _num(
                geometry.get("coolant_channel_height"),
                _num(geometry.get("coolant_channel_height_m"), 0.0020),
            ),
        ),
        "rib_width": max(
            1.0e-9,
            _num(
                geometry.get("rib_width"),
                _num(geometry.get("rib_width_m"), 0.0010),
            ),
        ),
        "hot_gas_wall_thickness": max(
            1.0e-9,
            _num(geometry.get("hot_gas_wall_thickness"), 0.0012),
        ),
        "coolant_flow_fraction": max(
            1.0e-9,
            _num(geometry.get("coolant_flow_fraction"), 1.0),
        ),
    }


def generate_population_from_seed(seed, population_size):
    base = dict(seed.get("geometry") or {})

    variation_plan = [
        ("seed_baseline", {}),
        ("channel_count_up", {"number_of_coolant_channels": 1.05}),
        ("channel_count_down", {"number_of_coolant_channels": 0.95}),
        ("channel_width_up", {"coolant_channel_width": 1.08}),
        ("channel_width_down", {"coolant_channel_width": 0.92}),
        ("channel_height_up", {"coolant_channel_height": 1.08}),
        ("channel_height_down", {"coolant_channel_height": 0.92}),
        ("rib_width_up", {"rib_width": 1.08}),
        ("rib_width_down", {"rib_width": 0.92}),
        (
            "width_up_height_down",
            {"coolant_channel_width": 1.06, "coolant_channel_height": 0.94},
        ),
        (
            "width_down_height_up",
            {"coolant_channel_width": 0.94, "coolant_channel_height": 1.06},
        ),
        (
            "rib_manufacturing_margin_up",
            {"rib_width": 1.05},
        ),
    ]

    population = []

    for index in range(population_size):
        reason, multipliers = variation_plan[index % len(variation_plan)]
        geometry = apply_population_variation(base, multipliers)

        candidate_id = f"RPOP-G0-{index + 1:04d}"

        population.append({
            "candidate_id": candidate_id,
            "candidate_generation": 0,
            "candidate_parent": seed.get("seed_candidate_id"),
            "candidate_reason": reason,
            "candidate_geometry": geometry,
            "candidate_changes": multipliers,
            "candidate_source": "regen_candidate_population_generation_owner",
            "candidate_status": "GENERATED_NOT_SOLVED_NOT_RANKED",
            "candidate_metadata": {
                "phase": "11B.3A",
                "owner": "REGEN_CANDIDATE_POPULATION_GENERATION_OWNER",
                "seed_source": seed.get("seed_source"),
                "ranking_allowed": False,
                "mutation_allowed": False,
                "solver_executed": False,
                "live_geometry_modified": False,
                "candidate_committed": False,
            },
        })

    return population


def apply_population_variation(base, multipliers):
    geometry = dict(base)

    for key, multiplier in multipliers.items():
        value = geometry.get(key)

        if value is None:
            continue

        if key == "number_of_coolant_channels":
            geometry[key] = max(1, int(round(float(value) * float(multiplier))))
        else:
            geometry[key] = max(1.0e-9, float(value) * float(multiplier))

    return geometry


def build_population_statistics(population):
    if not population:
        return {}

    geometries = [
        candidate.get("candidate_geometry", {})
        for candidate in population
        if isinstance(candidate.get("candidate_geometry"), dict)
    ]

    return {
        "population_size": len(population),
        "number_of_coolant_channels": _stats(
            [g.get("number_of_coolant_channels") for g in geometries]
        ),
        "coolant_channel_width": _stats(
            [g.get("coolant_channel_width") for g in geometries]
        ),
        "coolant_channel_height": _stats(
            [g.get("coolant_channel_height") for g in geometries]
        ),
        "rib_width": _stats(
            [g.get("rib_width") for g in geometries]
        ),
        "hot_gas_wall_thickness": _stats(
            [g.get("hot_gas_wall_thickness") for g in geometries]
        ),
        "coolant_flow_fraction": _stats(
            [g.get("coolant_flow_fraction") for g in geometries]
        ),
    }


def build_population_generation_owner_report(
    status,
    ready,
    reason,
    blockers,
    seed,
    population,
    statistics,
):
    lines = [
        "LEAF PHASE 11B.3A CANDIDATE POPULATION GENERATION OWNER",
        "========================================================",
        "",
        f"Status: {status}",
        f"Ready: {ready}",
        f"Reason: {reason}",
        "",
        "Scope:",
        "- Generates a candidate population around a seed geometry.",
        "- Does not solve candidates.",
        "- Does not rank candidates.",
        "- Does not mutate future generations.",
        "- Does not commit or modify live geometry.",
        "",
        "Seed:",
        f"- Seed candidate id: {seed.get('seed_candidate_id')}",
        f"- Seed source: {seed.get('seed_source')}",
        "",
        "Population:",
        f"- Candidate count: {len(population)}",
        "",
        "Blockers:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Statistics:",
    ])

    if statistics:
        for key, value in statistics.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Candidates:",
    ])

    if population:
        for candidate in population:
            geometry = candidate.get("candidate_geometry", {})
            lines.append(
                "- "
                f"{candidate.get('candidate_id')} | "
                f"{candidate.get('candidate_reason')} | "
                f"Nch={geometry.get('number_of_coolant_channels')} | "
                f"w={geometry.get('coolant_channel_width')} | "
                f"h={geometry.get('coolant_channel_height')} | "
                f"rib={geometry.get('rib_width')}"
            )
    else:
        lines.append("- None.")

    return "\n".join(lines)


def _stats(values):
    cleaned = []

    for value in values:
        try:
            if value is not None:
                cleaned.append(float(value))
        except Exception:
            pass

    if not cleaned:
        return {
            "min": None,
            "max": None,
            "mean": None,
        }

    return {
        "min": min(cleaned),
        "max": max(cleaned),
        "mean": sum(cleaned) / len(cleaned),
    }


def _num(value, default):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default
