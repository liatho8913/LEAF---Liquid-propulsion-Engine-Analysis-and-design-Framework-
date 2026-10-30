"""
LEAF Material Property Interpolation Owner
==========================================

REGEN PHASE 9A

Owns temperature-dependent material property interpolation.

This module does NOT:
- replace the regen thermal solver yet
- approve material validation by itself
- override source validation gates
"""

DEFAULT_MATERIAL_PROPERTY_TABLES = {'GRCop-42': {'mode': 'PARTIAL_SOURCE_MODE',
              'source_quality': 'MIXED_PROPERTY_SOURCE_QUALITY',
              'temperature_unit': 'K',
              'properties': {'thermal_conductivity': {'points': [{'T': 298.15, 'value': 327.5},
                                                                 {'T': 373.15, 'value': 328.7},
                                                                 {'T': 473.15, 'value': 329.4},
                                                                 {'T': 573.15, 'value': 328.4},
                                                                 {'T': 673.15, 'value': 325.0},
                                                                 {'T': 773.15, 'value': 322.1},
                                                                 {'T': 873.15, 'value': 316.9},
                                                                 {'T': 973.15, 'value': 305.8}],
                                                      'source_ids': ['CHEN_2023_GRCOP42_THERMOPHYSICAL_THERMAL_CONDUCTIVITY'],
                                                      'source_variants': [],
                                                      'evidence_type': 'AUTHOR_REPORTED_DIRECT',
                                                      'material_form': 'L_PBF',
                                                      'heat_treatment': None,
                                                      'source_quality': 'PRIMARY_DIRECT_SOURCED',
                                                      'production_eligible': True,
                                                      'authority_type': 'DIRECT_MEASURED_PROPERTY_TABLE',
                                                      'validated_temperature_range_K': [298.15, 973.15],
                                                      'range_boundaries_inclusive': True,
                                                      'extrapolation_allowed': False},
                             'density': {'points': [],
                                         'source_ids': ['NASA_TM_20205003857_GRCOP42_REFERENCE_DENSITY',
                                                        'CHEN_2023_GRCOP42_THERMAL_EXPANSION'],
                                         'source_variants': [],
                                         'evidence_type': 'DERIVED_FROM_PRIMARY_SOURCES',
                                         'material_form': 'L_PBF',
                                         'heat_treatment': None,
                                         'source_quality': 'PRIMARY_DERIVED_SOURCED',
                                         'production_eligible': True,
                                         'authority_type': 'DERIVED_PROPERTY_MODEL',
                                         'model_type': 'REFERENCE_NORMALISED_ISOTROPIC_THERMAL_EXPANSION_DENSITY',
                                         'reference_density_kg_m3': 8889.0,
                                         'reference_temperature_K': 293.0,
                                         'temperature_range_K': [293.15, 1273.15],
                                         'coefficients': {'constant': -0.000589,
                                                          'cubic': -1.88e-12,
                                                          'linear': 1.51e-05,
                                                          'quadratic': 6.28e-09,
                                                          'temperature_offset_K': 273.0},
                                         'extrapolation_allowed': False,
                                         'derived_not_measured': True},
                             'specific_heat': {'points': [{'T': 298.15, 'value': 384.0},
                                                          {'T': 373.15, 'value': 394.0},
                                                          {'T': 473.15, 'value': 406.0},
                                                          {'T': 573.15, 'value': 416.0},
                                                          {'T': 673.15, 'value': 424.0},
                                                          {'T': 773.15, 'value': 431.0},
                                                          {'T': 873.15, 'value': 439.0},
                                                          {'T': 973.15, 'value': 449.0}],
                                               'source_ids': ['CHEN_2023_GRCOP42_THERMOPHYSICAL'],
                                               'evidence_type': 'AUTHOR_REPORTED_DERIVED',
                                               'material_form': None,
                                               'heat_treatment': None,
                                               'source_quality': 'PRIMARY_DERIVED_SOURCED',
                                               'production_eligible': True},
                             'max_service_temperature': {'points': [{'T': 300.0, 'value': 1023.15},
                                                                    {'T': 1023.15, 'value': 1023.15}],
                                                         'source_ids': ['NASA_2024_GRCOP42_MAX_USE_TEMPERATURE',
                                                                        '3D_SYSTEMS_CERTIFIED_GRCOP42_SERVICE_TEMPERATURE'],
                                                         'evidence_type': 'AUTHORITATIVE_ENGINEERING_LIMIT',
                                                         'material_form': 'L_PBF',
                                                         'heat_treatment': 'HIP',
                                                         'source_quality': 'PRIMARY_AUTHORITATIVE_CORROBORATED',
                                                         'production_eligible': True,
                                                         'engineering_limit_semantics': {'limit_type': 'MAXIMUM_MATERIAL_USE_TEMPERATURE',
                                                                                         'value_C': 750.0,
                                                                                         'value_K': 1023.15,
                                                                                         'strength_allowable': False,
                                                                                         'creep_life_guarantee': False,
                                                                                         'melting_point': False,
                                                                                         'test_ceiling': False,
                                                                                         'typical_load_bearing_range_C': [400.0,
                                                                                                                          600.0]}},
                             'yield_strength': {'authority_type': 'DIRECT_MEASURED_PROPERTY_TABLE',
                                                'points': [{'T': 672.0388888888889,
                                                            'value': 149616233.2617456},
                                                           {'T': 873.15, 'value': 115142446.79590559}],
                                                'source_ids': ['NASA_NTRS_20220008606_GRCOP42_LPBF_HIP_ELEVATED_TENSILE',
                                                               'NASA_AIAA_2019_GRCOP42_AM_MECHANICAL_CONCEPT_M2',
                                                               'NASA_AIAA_2019_GRCOP42_AM_MECHANICAL_EOS_M400'],
                                                'evidence_type': 'AUTHOR_REPORTED_DIRECT_TABULATED',
                                                'material_form': 'L_PBF',
                                                'heat_treatment': 'HIP',
                                                'source_heat_treatment_detail': 'STANDARD_MSFC_HIP',
                                                'source_quality': 'PRIMARY_DIRECT_SOURCED',
                                                'production_eligible': True,
                                                'source_variants': [{'source_id': 'NASA_AIAA_2019_GRCOP42_AM_MECHANICAL_CONCEPT_M2',
                                                                     'platform': 'Concept M2',
                                                                     'T': 294.2611111111111,
                                                                     'temperature_source': 'ROOM_TEMPERATURE_70_F',
                                                                     'value': 173058408.05852586,
                                                                     'unit': 'Pa',
                                                                     'test_method': 'ASTM E8',
                                                                     'test_environment': 'AIR',
                                                                     'offset_method': None},
                                                                    {'source_id': 'NASA_AIAA_2019_GRCOP42_AM_MECHANICAL_EOS_M400',
                                                                     'platform': 'EOS M400',
                                                                     'T': 294.2611111111111,
                                                                     'temperature_source': 'ROOM_TEMPERATURE_70_F',
                                                                     'value': 172368932.32920903,
                                                                     'unit': 'Pa',
                                                                     'test_method': 'ASTM E8',
                                                                     'test_environment': 'AIR',
                                                                     'offset_method': None}],
                                                'room_temperature_variants_role': 'PROVENANCE_ONLY_NOT_INTERPOLATION_ANCHORS',
                                                'numerical_authority_source_id': 'NASA_NTRS_20220008606_GRCOP42_LPBF_HIP_ELEVATED_TENSILE',
                                                'validated_temperature_range_K': [672.0388888888889, 873.15],
                                                'range_boundaries_inclusive': True,
                                                'extrapolation_allowed': False},
                             'ultimate_tensile_strength': {'authority_type': 'DIRECT_MEASURED_PROPERTY_TABLE',
                                                           'points': [{'T': 672.0388888888889,
                                                                       'value': 193742679.9380208},
                                                                      {'T': 873.15,
                                                                       'value': 124105631.277024}],
                                                           'source_ids': ['NASA_NTRS_20220008606_GRCOP42_LPBF_HIP_ELEVATED_TENSILE',
                                                                          'NASA_AIAA_2019_GRCOP42_AM_MECHANICAL_CONCEPT_M2',
                                                                          'NASA_AIAA_2019_GRCOP42_AM_MECHANICAL_EOS_M400'],
                                                           'evidence_type': 'AUTHOR_REPORTED_DIRECT_TABULATED',
                                                           'material_form': 'L_PBF',
                                                           'heat_treatment': 'HIP',
                                                           'source_heat_treatment_detail': 'STANDARD_MSFC_HIP',
                                                           'source_quality': 'PRIMARY_DIRECT_SOURCED',
                                                           'production_eligible': True,
                                                           'source_variants': [{'source_id': 'NASA_AIAA_2019_GRCOP42_AM_MECHANICAL_CONCEPT_M2',
                                                                                'platform': 'Concept M2',
                                                                                'T': 294.2611111111111,
                                                                                'temperature_source': 'ROOM_TEMPERATURE_70_F',
                                                                                'value': 358527379.2447548,
                                                                                'unit': 'Pa',
                                                                                'test_method': 'ASTM E8',
                                                                                'test_environment': 'AIR'},
                                                                               {'source_id': 'NASA_AIAA_2019_GRCOP42_AM_MECHANICAL_EOS_M400',
                                                                                'platform': 'EOS M400',
                                                                                'T': 294.2611111111111,
                                                                                'temperature_source': 'ROOM_TEMPERATURE_70_F',
                                                                                'value': 355080000.5981706,
                                                                                'unit': 'Pa',
                                                                                'test_method': 'ASTM E8',
                                                                                'test_environment': 'AIR'}],
                                                           'room_temperature_variants_role': 'PROVENANCE_ONLY_NOT_INTERPOLATION_ANCHORS',
                                                           'numerical_authority_source_id': 'NASA_NTRS_20220008606_GRCOP42_LPBF_HIP_ELEVATED_TENSILE',
                                                           'validated_temperature_range_K': [672.0388888888889,
                                                                                             873.15],
                                                           'range_boundaries_inclusive': True,
                                                           'extrapolation_allowed': False}}},
 'Inconel 718': {'mode': 'PARTIAL_SOURCE_MODE',
                 'source_quality': 'ENGINEERING_PLACEHOLDER_PENDING_FULL_SOURCE_TABLE',
                 'temperature_unit': 'K',
                 'properties': {'thermal_conductivity': [{'T': 300.0, 'value': 11.4},
                                                         {'T': 600.0, 'value': 15.0},
                                                         {'T': 900.0, 'value': 20.0}],
                                'density': [{'T': 300.0, 'value': 8190.0}, {'T': 900.0, 'value': 8050.0}],
                                'specific_heat': [{'T': 300.0, 'value': 435.0},
                                                  {'T': 600.0, 'value': 500.0},
                                                  {'T': 900.0, 'value': 575.0}],
                                'max_service_temperature': [{'T': 300.0, 'value': 980.0},
                                                            {'T': 900.0, 'value': 980.0}]}}}


def attach_material_property_interpolation_owner(results):
    if not isinstance(results, dict):
        return results

    attached = build_material_property_interpolation_owner(results)
    results.update(attached)
    return results





def evaluate_derived_property_model(property_record, temperature):
    """
    Evaluate a certified derived material-property model.

    This path is deliberately fail-closed:
    - only explicitly supported model types are executable;
    - source temperature limits are mandatory;
    - extrapolation is forbidden unless explicitly authorised;
    - derived density remains labelled as derived, not directly measured.
    """
    if not isinstance(property_record, dict):
        return {
            "status": "FAIL_DERIVED_PROPERTY_INVALID_RECORD",
            "value": None,
            "temperature": temperature,
            "method": "none",
            "within_table_range": False,
        }

    authority_type = property_record.get(
        "authority_type"
    )

    model_type = property_record.get(
        "model_type"
    )

    if authority_type != "DERIVED_PROPERTY_MODEL":
        return {
            "status": "FAIL_DERIVED_PROPERTY_AUTHORITY_TYPE",
            "value": None,
            "temperature": temperature,
            "method": "none",
            "within_table_range": False,
        }

    if (
        model_type
        !=
        "REFERENCE_NORMALISED_ISOTROPIC_THERMAL_EXPANSION_DENSITY"
    ):
        return {
            "status": "FAIL_DERIVED_PROPERTY_UNSUPPORTED_MODEL",
            "value": None,
            "temperature": temperature,
            "method": "none",
            "within_table_range": False,
        }

    try:
        temperature = float(
            temperature
        )

        reference_density = float(
            property_record[
                "reference_density_kg_m3"
            ]
        )

        reference_temperature = float(
            property_record[
                "reference_temperature_K"
            ]
        )

        temperature_range = (
            property_record[
                "temperature_range_K"
            ]
        )

        Tmin = float(
            temperature_range[0]
        )

        Tmax = float(
            temperature_range[1]
        )

        coefficients = (
            property_record[
                "coefficients"
            ]
        )

        constant = float(
            coefficients[
                "constant"
            ]
        )

        linear = float(
            coefficients[
                "linear"
            ]
        )

        quadratic = float(
            coefficients[
                "quadratic"
            ]
        )

        cubic = float(
            coefficients[
                "cubic"
            ]
        )

        temperature_offset = float(
            coefficients[
                "temperature_offset_K"
            ]
        )

    except (
        KeyError,
        TypeError,
        ValueError,
        IndexError,
    ):
        return {
            "status": "FAIL_DERIVED_PROPERTY_MODEL_METADATA",
            "value": None,
            "temperature": temperature,
            "method": "none",
            "within_table_range": False,
        }

    within_range = (
        Tmin
        <= temperature
        <= Tmax
    )

    extrapolation_allowed = bool(
        property_record.get(
            "extrapolation_allowed",
            False,
        )
    )

    if (
        not within_range
        and
        not extrapolation_allowed
    ):
        return {
            "status": "FAIL_DERIVED_PROPERTY_OUTSIDE_SOURCE_RANGE",
            "value": None,
            "temperature": temperature,
            "method": "derived_model_no_extrapolation",
            "within_table_range": False,
            "source_temperature_range_K": [
                Tmin,
                Tmax,
            ],
        }

    def epsilon_fit(T):
        x = (
            float(T)
            - temperature_offset
        )

        return (
            constant
            + linear * x
            + quadratic * x**2
            + cubic * x**3
        )

    reference_epsilon = (
        epsilon_fit(
            reference_temperature
        )
    )

    relative_epsilon = (
        epsilon_fit(
            temperature
        )
        -
        reference_epsilon
    )

    denominator = (
        1.0
        +
        relative_epsilon
    )**3

    if denominator <= 0.0:
        return {
            "status": "FAIL_DERIVED_PROPERTY_NONPHYSICAL_VOLUME_RATIO",
            "value": None,
            "temperature": temperature,
            "method": "reference_normalised_thermal_expansion_density",
            "within_table_range": within_range,
        }

    density = (
        reference_density
        /
        denominator
    )

    return {
        "status": "PASS_DERIVED_PROPERTY_MODEL",
        "value": density,
        "temperature": temperature,
        "method": "reference_normalised_thermal_expansion_density",
        "within_table_range": within_range,
        "authority_type": authority_type,
        "model_type": model_type,
        "reference_density_kg_m3": reference_density,
        "reference_temperature_K": reference_temperature,
        "delta_epsilon": relative_epsilon,
        "derived_not_measured": bool(
            property_record.get(
                "derived_not_measured",
                True,
            )
        ),
        "source_temperature_range_K": [
            Tmin,
            Tmax,
        ],
    }


def build_material_property_interpolation_owner(results):
    results = results if isinstance(results, dict) else {}

    material_name = _normalise_text(
        results.get("selected_material")
        or results.get("material")
        or results.get("chamber_material"),
        default="GRCop-42",
    )

    query_temperature = _safe_float(
        results.get("material_property_query_temperature")
        or results.get("wall_temperature_hot_gas")
        or results.get("Twg")
        or results.get("T_wall_hot"),
        default=900.0,
    )

    tables = results.get(
        "material_property_tables"
    )

    if not isinstance(
        tables,
        dict,
    ):
        tables = DEFAULT_MATERIAL_PROPERTY_TABLES

    material_table = tables.get(
        material_name
    )

    selected_material_form = results.get(
        "selected_material_form"
    )

    selected_material_heat_treatment = results.get(
        "selected_material_heat_treatment"
    )

    selected_material_form = (
        str(
            selected_material_form
        ).strip()
        if selected_material_form not in (
            None,
            "",
        )
        else None
    )

    selected_material_heat_treatment = (
        str(
            selected_material_heat_treatment
        ).strip()
        if selected_material_heat_treatment not in (
            None,
            "",
        )
        else None
    )

    interpolation_results = {}
    blockers = []

    property_metadata = {}
    property_blockers = {}
    eligible_properties = []
    blocked_properties = []

    process_sensitive_material = (
        material_name
        ==
        "GRCop-42"
    )

    table_material_form = None
    table_heat_treatment = None

    if isinstance(
        material_table,
        dict,
    ):
        table_material_form = material_table.get(
            "material_form"
        )

        table_heat_treatment = material_table.get(
            "heat_treatment"
        )

    if not isinstance(
        material_table,
        dict,
    ):
        blockers.append(
            f"No material property table exists for {material_name}."
        )

        mode = "MISSING_TABLE_MODE"
        source_quality = "NO_SOURCE"
        properties = {}

    else:
        mode = material_table.get(
            "mode",
            "UNKNOWN_MODE",
        )

        source_quality = material_table.get(
            "source_quality",
            "UNKNOWN_SOURCE_QUALITY",
        )

        properties = material_table.get(
            "properties",
            {},
        )

        if not isinstance(
            properties,
            dict,
        ):
            blockers.append(
                f"Material table for {material_name} "
                "has no property dictionary."
            )

            properties = {}

    property_level_schema_present = any(
        isinstance(
            value,
            dict,
        )
        and
        "points"
        in
        value
        for value in properties.values()
    )

    # Pure legacy tables retain the original material-wide gate.
    if (
        process_sensitive_material
        and
        not property_level_schema_present
    ):
        if selected_material_form is None:
            blockers.append(
                "UNBOUND_MATERIAL_STATE: "
                "GRCop-42 requires an explicit material form."
            )

        elif table_material_form in (
            None,
            "",
        ):
            blockers.append(
                "Material property table has no material_form binding."
            )

        elif (
            str(
                table_material_form
            ).strip()
            !=
            selected_material_form
        ):
            blockers.append(
                "Material-form mismatch: selected "
                f"{selected_material_form}, "
                f"table {table_material_form}."
            )

        if table_heat_treatment not in (
            None,
            "",
        ):
            if selected_material_heat_treatment is None:
                blockers.append(
                    "UNBOUND_MATERIAL_STATE: "
                    "source table requires heat-treatment identity."
                )

            elif (
                str(
                    table_heat_treatment
                ).strip()
                !=
                selected_material_heat_treatment
            ):
                blockers.append(
                    "Heat-treatment mismatch: selected "
                    f"{selected_material_heat_treatment}, "
                    f"table {table_heat_treatment}."
                )

    if not blockers:
        for property_name, property_record in (
            properties.items()
        ):

            # ----------------------------------------------------------
            # LEGACY LIST PROPERTY
            #
            # In a pure legacy table the old material-wide gate above
            # owns identity.
            #
            # In a MIXED table this individual legacy property must
            # independently retain the same legacy gate. A neighbouring
            # new property object must never disable legacy fail-closed
            # behaviour.
            # ----------------------------------------------------------
            if isinstance(
                property_record,
                list,
            ):
                local_blockers = []

                if (
                    process_sensitive_material
                    and
                    property_level_schema_present
                ):
                    if selected_material_form is None:
                        local_blockers.append(
                            "LEGACY_PROPERTY_UNBOUND_MATERIAL_FORM"
                        )

                    elif table_material_form in (
                        None,
                        "",
                    ):
                        local_blockers.append(
                            "LEGACY_PROPERTY_MISSING_TABLE_MATERIAL_FORM"
                        )

                    elif (
                        str(
                            table_material_form
                        ).strip()
                        !=
                        selected_material_form
                    ):
                        local_blockers.append(
                            "LEGACY_PROPERTY_MATERIAL_FORM_MISMATCH"
                        )

                    if table_heat_treatment not in (
                        None,
                        "",
                    ):
                        if selected_material_heat_treatment is None:
                            local_blockers.append(
                                "LEGACY_PROPERTY_UNBOUND_HEAT_TREATMENT"
                            )

                        elif (
                            str(
                                table_heat_treatment
                            ).strip()
                            !=
                            selected_material_heat_treatment
                        ):
                            local_blockers.append(
                                "LEGACY_PROPERTY_HEAT_TREATMENT_MISMATCH"
                            )

                property_metadata[
                    property_name
                ] = {
                    "schema":
                        "LEGACY_LIST",

                    "material_form":
                        table_material_form,

                    "heat_treatment":
                        table_heat_treatment,

                    "source_quality":
                        source_quality,

                    "production_eligible":
                        (
                            not local_blockers
                        ),

                    "identity_status":
                        (
                            "LEGACY_MATERIAL_LEVEL_GATE"
                            if not local_blockers
                            else
                            "LEGACY_PROPERTY_IDENTITY_BLOCKED"
                        ),
                }

                property_blockers[
                    property_name
                ] = local_blockers

                if local_blockers:
                    blocked_properties.append(
                        property_name
                    )

                    continue

                interpolation_results[
                    property_name
                ] = interpolate_property_table(
                    points=property_record,
                    temperature=query_temperature,
                )

                eligible_properties.append(
                    property_name
                )

                continue

            # ----------------------------------------------------------
            # NEW PROPERTY-OBJECT SCHEMA
            # ----------------------------------------------------------
            if not isinstance(
                property_record,
                dict,
            ):
                property_blockers[
                    property_name
                ] = [
                    "INVALID_PROPERTY_RECORD"
                ]

                blocked_properties.append(
                    property_name
                )

                continue

            points = property_record.get(
                "points",
                [],
            )

            authority_type = property_record.get(
                "authority_type"
            )

            model_type = property_record.get(
                "model_type"
            )

            source_variants = property_record.get(
                "source_variants",
                [],
            )

            source_ids = property_record.get(
                "source_ids",
                [],
            )

            evidence_type = property_record.get(
                "evidence_type"
            )

            property_form = property_record.get(
                "material_form"
            )

            property_heat = property_record.get(
                "heat_treatment"
            )

            property_quality = property_record.get(
                "source_quality",
                source_quality,
            )

            production_eligible = bool(
                property_record.get(
                    "production_eligible",
                    False,
                )
            )

            local_blockers = []

            property_form = (
                str(
                    property_form
                ).strip()
                if property_form not in (
                    None,
                    "",
                )
                else None
            )

            property_heat = (
                str(
                    property_heat
                ).strip()
                if property_heat not in (
                    None,
                    "",
                )
                else None
            )

            if not production_eligible:
                local_blockers.append(
                    "PROPERTY_NOT_PRODUCTION_ELIGIBLE"
                )

            if (
                property_form
                is not None
                and
                selected_material_form
                !=
                property_form
            ):
                local_blockers.append(
                    "PROPERTY_MATERIAL_FORM_MISMATCH"
                )

            if (
                property_heat
                is not None
                and
                selected_material_heat_treatment
                !=
                property_heat
            ):
                local_blockers.append(
                    "PROPERTY_HEAT_TREATMENT_MISMATCH"
                )

            if not isinstance(
                source_ids,
                list,
            ):
                local_blockers.append(
                    "INVALID_PROPERTY_SOURCE_IDS"
                )

            if not isinstance(
                source_variants,
                list,
            ):
                local_blockers.append(
                    "INVALID_PROPERTY_SOURCE_VARIANTS"
                )

            if not evidence_type:
                local_blockers.append(
                    "MISSING_PROPERTY_EVIDENCE_TYPE"
                )

            if not property_quality:
                local_blockers.append(
                    "MISSING_PROPERTY_SOURCE_QUALITY"
                )

            property_metadata[
                property_name
            ] = {
                "schema":
                    "PROPERTY_OBJECT",

                "source_ids":
                    source_ids,

                "source_variants":
                    source_variants,

                "evidence_type":
                    evidence_type,

                "material_form":
                    property_form,

                "heat_treatment":
                    property_heat,

                "source_quality":
                    property_quality,

                "production_eligible":
                    production_eligible,

                "authority_type":
                    authority_type,

                "model_type":
                    model_type,

                "identity_status":
                    (
                        "PROPERTY_IDENTITY_ELIGIBLE"
                        if not local_blockers
                        else
                        "PROPERTY_IDENTITY_BLOCKED"
                    ),
            }

            property_blockers[
                property_name
            ] = local_blockers

            if local_blockers:
                blocked_properties.append(
                    property_name
                )

                continue

            if (
                authority_type
                ==
                "DERIVED_PROPERTY_MODEL"
            ):
                property_result = (
                    evaluate_derived_property_model(
                        property_record=
                            property_record,
                        temperature=
                            query_temperature,
                    )
                )

                if not str(
                    property_result.get(
                        "status",
                        "",
                    )
                ).startswith("PASS_"):
                    property_blockers[
                        property_name
                    ] = [
                        property_result.get(
                            "status",
                            "FAIL_DERIVED_PROPERTY_MODEL",
                        )
                    ]

                    blocked_properties.append(
                        property_name
                    )

                    continue

                interpolation_results[
                    property_name
                ] = property_result

            else:
                property_runtime_result = (
                    interpolate_property_table_with_range_contract(
                        points=points,
                        temperature=query_temperature,
                        validated_temperature_range_K=(
                            property_record.get(
                                "validated_temperature_range_K"
                            )
                            or
                            property_record.get(
                                "temperature_range_K"
                            )
                        ),
                        extrapolation_allowed=bool(
                            property_record.get(
                                "extrapolation_allowed",
                                True,
                            )
                        ),
                    )
                )

                interpolation_results[
                    property_name
                ] = property_runtime_result

                if (
                    property_runtime_result.get(
                        "status"
                    )
                    ==
                    "FAIL_PROPERTY_TEMPERATURE_OUT_OF_VALIDATED_RANGE"
                ):
                    property_blockers[
                        property_name
                    ].append(
                        "PROPERTY_TEMPERATURE_OUT_OF_VALIDATED_RANGE"
                    )

                    if (
                        property_name
                        not in
                        blocked_properties
                    ):
                        blocked_properties.append(
                            property_name
                        )

                    continue

                if (
                    property_runtime_result.get(
                        "status"
                    )
                    ==
                    "FAIL_PROPERTY_INVALID_VALIDATED_TEMPERATURE_RANGE"
                ):
                    property_blockers[
                        property_name
                    ].append(
                        "PROPERTY_INVALID_VALIDATED_TEMPERATURE_RANGE"
                    )

                    if (
                        property_name
                        not in
                        blocked_properties
                    ):
                        blocked_properties.append(
                            property_name
                        )

                    continue

            eligible_properties.append(
                property_name
            )

    table_complete = (
        bool(
            interpolation_results
        )
        and
        not blockers
    )

    if property_level_schema_present:
        eligible_qualities = [
            property_metadata[
                name
            ].get(
                "source_quality"
            )
            for name in eligible_properties
            if name
            in
            property_metadata
        ]

        conservative_pass_allowed = (
            table_complete
            and
            mode == "SOURCED_VALIDATION_MODE"
            and
            bool(
                eligible_properties
            )
            and
            all(
                quality
                not in (
                    None,
                    "",
                    "NO_SOURCE",
                    "UNKNOWN_SOURCE_QUALITY",
                    "ENGINEERING_PLACEHOLDER_PENDING_FULL_SOURCE_TABLE",
                )
                for quality in eligible_qualities
            )
        )

    else:
        conservative_pass_allowed = (
            table_complete
            and
            mode == "SOURCED_VALIDATION_MODE"
            and
            source_quality
            ==
            "FULLY_SOURCED"
        )

    status = (
        "PASS_MATERIAL_PROPERTY_INTERPOLATION_OWNER"
        if table_complete
        else
        "FAIL_MATERIAL_PROPERTY_INTERPOLATION_OWNER"
    )

    text = build_material_property_interpolation_text(
        status=status,
        material_name=material_name,
        query_temperature=query_temperature,
        mode=mode,
        source_quality=source_quality,
        interpolation_results=interpolation_results,
        blockers=blockers,
        conservative_pass_allowed=conservative_pass_allowed,
    )

    return {
        "material_property_interpolation_owner_status":
            status,

        "material_property_interpolation_owner_complete":
            table_complete,

        "material_property_interpolation_material":
            material_name,

        "material_property_interpolation_selected_material_form":
            selected_material_form,

        "material_property_interpolation_selected_heat_treatment":
            selected_material_heat_treatment,

        "material_property_interpolation_table_material_form":
            table_material_form,

        "material_property_interpolation_table_heat_treatment":
            table_heat_treatment,

        "material_property_interpolation_material_identity_status":
            (
                "BOUND_MATERIAL_STATE"
                if not blockers
                else
                "UNBOUND_OR_MISMATCHED_MATERIAL_STATE"
            ),

        "material_property_interpolation_query_temperature":
            query_temperature,

        "material_property_interpolation_mode":
            mode,

        "material_property_interpolation_source_quality":
            source_quality,

        "material_property_interpolation_results":
            interpolation_results,

        "material_property_interpolation_blockers":
            blockers,

        "material_property_interpolation_conservative_pass_allowed":
            conservative_pass_allowed,

        "material_property_interpolation_text":
            text,

        "material_property_interpolation_property_metadata":
            property_metadata,

        "material_property_interpolation_property_blockers":
            property_blockers,

        "material_property_interpolation_eligible_properties":
            eligible_properties,

        "material_property_interpolation_blocked_properties":
            blocked_properties,

        "phase_9a_material_property_interpolation_owner_complete":
            table_complete,
    }




def interpolate_property_table_with_range_contract(
        points,
        temperature,
        validated_temperature_range_K=None,
        extrapolation_allowed=True,
):
    """
    Property-table evaluator with optional validated-temperature limits.

    Legacy interpolation remains unchanged when no restrictive contract
    is supplied. Range-contracted PROPERTY_OBJECTS fail closed outside
    their validated domain. Boundaries are inclusive.
    """

    clean_points = _normalise_points(
        points
    )

    if not clean_points:
        return {
            "status":
                "FAIL_INTERPOLATION_NO_POINTS",

            "value":
                None,

            "temperature":
                temperature,

            "method":
                "none",

            "within_table_range":
                False,

            "validated_temperature_range_K":
                validated_temperature_range_K,

            "extrapolation_allowed":
                extrapolation_allowed,
        }

    point_min = float(
        clean_points[0]["T"]
    )

    point_max = float(
        clean_points[-1]["T"]
    )

    range_min = point_min
    range_max = point_max

    if validated_temperature_range_K not in (
        None,
        "",
    ):
        if not (
            isinstance(
                validated_temperature_range_K,
                (list, tuple),
            )
            and
            len(
                validated_temperature_range_K
            )
            == 2
        ):
            return {
                "status":
                    "FAIL_PROPERTY_INVALID_VALIDATED_TEMPERATURE_RANGE",

                "value":
                    None,

                "temperature":
                    temperature,

                "method":
                    "none",

                "within_table_range":
                    False,

                "validated_temperature_range_K":
                    validated_temperature_range_K,

                "extrapolation_allowed":
                    extrapolation_allowed,
            }

        try:
            declared_min = float(
                validated_temperature_range_K[0]
            )

            declared_max = float(
                validated_temperature_range_K[1]
            )

        except (
            TypeError,
            ValueError,
        ):
            return {
                "status":
                    "FAIL_PROPERTY_INVALID_VALIDATED_TEMPERATURE_RANGE",

                "value":
                    None,

                "temperature":
                    temperature,

                "method":
                    "none",

                "within_table_range":
                    False,

                "validated_temperature_range_K":
                    validated_temperature_range_K,

                "extrapolation_allowed":
                    extrapolation_allowed,
            }

        range_min = max(
            point_min,
            declared_min,
        )

        range_max = min(
            point_max,
            declared_max,
        )

    if range_min > range_max:
        return {
            "status":
                "FAIL_PROPERTY_INVALID_VALIDATED_TEMPERATURE_RANGE",

            "value":
                None,

            "temperature":
                temperature,

            "method":
                "none",

            "within_table_range":
                False,

            "validated_temperature_range_K": [
                range_min,
                range_max,
            ],

            "extrapolation_allowed":
                extrapolation_allowed,
        }

    if (
        not extrapolation_allowed
        and
        (
            temperature < range_min
            or temperature > range_max
        )
    ):
        return {
            "status":
                "FAIL_PROPERTY_TEMPERATURE_OUT_OF_VALIDATED_RANGE",

            "value":
                None,

            "temperature":
                temperature,

            "method":
                "none",

            "within_table_range":
                False,

            "validated_temperature_range_K": [
                range_min,
                range_max,
            ],

            "extrapolation_allowed":
                False,
        }

    result = interpolate_property_table(
        points=points,
        temperature=temperature,
    )

    result[
        "validated_temperature_range_K"
    ] = [
        range_min,
        range_max,
    ]

    result[
        "extrapolation_allowed"
    ] = bool(
        extrapolation_allowed
    )

    if (
        range_min
        <= temperature
        <= range_max
    ):
        result[
            "within_table_range"
        ] = True

    return result


def interpolate_property_table(points, temperature):
    clean_points = _normalise_points(points)

    if not clean_points:
        return {
            "status": "FAIL_INTERPOLATION_NO_POINTS",
            "value": None,
            "temperature": temperature,
            "method": "none",
            "within_table_range": False,
        }

    if len(clean_points) == 1:
        return {
            "status": "PASS_INTERPOLATION_SINGLE_POINT",
            "value": clean_points[0]["value"],
            "temperature": temperature,
            "method": "single_point_hold",
            "within_table_range": temperature == clean_points[0]["T"],
            "lower_point": clean_points[0],
            "upper_point": clean_points[0],
        }

    lower = clean_points[0]
    upper = clean_points[-1]

    if temperature <= clean_points[0]["T"]:
        lower = clean_points[0]
        upper = clean_points[1]
        within = False
    elif temperature >= clean_points[-1]["T"]:
        lower = clean_points[-2]
        upper = clean_points[-1]
        within = False
    else:
        within = True
        for index in range(len(clean_points) - 1):
            left = clean_points[index]
            right = clean_points[index + 1]
            if left["T"] <= temperature <= right["T"]:
                lower = left
                upper = right
                break

    interpolated = _linear_interpolate(
        x=temperature,
        x0=lower["T"],
        y0=lower["value"],
        x1=upper["T"],
        y1=upper["value"],
    )

    return {
        "status": "PASS_INTERPOLATION",
        "value": interpolated,
        "temperature": temperature,
        "method": "linear_interpolation",
        "within_table_range": within,
        "lower_point": lower,
        "upper_point": upper,
    }


def build_material_property_interpolation_text(
        status,
        material_name,
        query_temperature,
        mode,
        source_quality,
        interpolation_results,
        blockers,
        conservative_pass_allowed,
):
    lines = [
        "LEAF REGEN PHASE 9A MATERIAL PROPERTY INTERPOLATION OWNER",
        "==========================================================",
        "",
        f"Status: {status}",
        f"Material: {material_name}",
        f"Query temperature: {query_temperature} K",
        f"Validation mode: {mode}",
        f"Source quality: {source_quality}",
        f"Conservative pass allowed: {conservative_pass_allowed}",
        "",
        "Owned By:",
        "- material_property_interpolation_owner.py",
        "",
        "Scope:",
        "- Owns temperature-dependent material property interpolation.",
        "- Owns interpolation provenance evidence.",
        "- Owns material-table missing-data blockers.",
        "- Does not replace regen thermal solver yet.",
        "- Does not override source validation gates.",
        "",
        "Interpolated Properties:",
    ]

    if interpolation_results:
        for property_name, result in interpolation_results.items():
            lines.append(
                f"- {property_name}: value={result.get('value')}, "
                f"status={result.get('status')}, "
                f"method={result.get('method')}, "
                f"within_range={result.get('within_table_range')}"
            )
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Blockers:")

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Next Required Action:")
    lines.append(
        "- After Phase 9A is verified, build material source/provenance ownership before solver replacement."
    )

    return "\n".join(lines)


def _normalise_points(points):
    if not isinstance(points, (list, tuple)):
        return []

    clean = []

    for point in points:
        if not isinstance(point, dict):
            continue

        try:
            temperature = float(point.get("T"))
            value = float(point.get("value"))
        except (TypeError, ValueError):
            continue

        clean.append({
            "T": temperature,
            "value": value,
        })

    clean.sort(key=lambda item: item["T"])
    return clean


def _linear_interpolate(x, x0, y0, x1, y1):
    if x1 == x0:
        return float(y0)

    fraction = (float(x) - float(x0)) / (float(x1) - float(x0))
    return float(y0) + fraction * (float(y1) - float(y0))


def _safe_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _normalise_text(value, default=""):
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default