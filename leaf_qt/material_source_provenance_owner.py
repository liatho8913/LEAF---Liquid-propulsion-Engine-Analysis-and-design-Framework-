"""
LEAF Material Source / Provenance Owner
=======================================

REGEN PHASE 9B

Owns material property source and provenance metadata.

This module does NOT:
- rank sources yet
- approve material validation
- replace solver material constants
"""

DEFAULT_MATERIAL_SOURCE_RECORDS = {'GRCop-42': {'material': 'GRCop-42',
              'mode': 'PARTIAL_SOURCE_MODE',
              'source_quality': 'MIXED_PROPERTY_SOURCE_QUALITY',
              'sources': [{'source_id': 'CHEN_2023_GRCOP42_THERMOPHYSICAL',
                           'source_type': 'peer_reviewed_primary',
                           'title': 'Thermophysical properties of additively manufactured (AM) GRCop-42 and '
                                    'GRCop-84',
                           'citation': 'Materials Today Communications 36 (2023) 106665; '
                                       'doi:10.1016/j.mtcomm.2023.106665',
                           'confidence': 0.95,
                           'properties_covered': ['specific_heat'],
                           'is_placeholder': False,
                           'evidence_type': 'AUTHOR_REPORTED_DERIVED',
                           'material_form': None,
                           'heat_treatment': None,
                           'source_quality': 'PRIMARY_DERIVED_SOURCED',
                           'production_eligible': True},
                          {'source_id': 'NASA_AIAA_2019_GRCOP42_AM_MECHANICAL_CONCEPT_M2',
                           'source_type': 'peer_reviewed_primary',
                           'title': 'GRCop-42 Development and Hot-fire Testing Using Additive Manufacturing '
                                    'Powder Bed Fusion for Channel-Cooled Combustion Chambers',
                           'citation': 'Gradl et al., AIAA-2019-4228, 55th AIAA/SAE/ASEE Joint Propulsion '
                                       'Conference, 2019',
                           'confidence': 1.0,
                           'properties_covered': ['yield_strength', 'ultimate_tensile_strength'],
                           'is_placeholder': False,
                           'evidence_type': 'AUTHOR_REPORTED_DIRECT',
                           'material_form': 'L_PBF',
                           'heat_treatment': 'HIP',
                           'source_quality': 'PRIMARY_DIRECT_SOURCED',
                           'production_eligible': False,
                           'platform': 'Concept M2',
                           'test_method': 'ASTM E8',
                           'test_environment': 'AIR',
                           'source_temperature': 'ROOM_TEMPERATURE_70_F'},
                          {'source_id': 'NASA_AIAA_2019_GRCOP42_AM_MECHANICAL_EOS_M400',
                           'source_type': 'peer_reviewed_primary',
                           'title': 'GRCop-42 Development and Hot-fire Testing Using Additive Manufacturing '
                                    'Powder Bed Fusion for Channel-Cooled Combustion Chambers',
                           'citation': 'Gradl et al., AIAA-2019-4228, 55th AIAA/SAE/ASEE Joint Propulsion '
                                       'Conference, 2019',
                           'confidence': 1.0,
                           'properties_covered': ['yield_strength', 'ultimate_tensile_strength'],
                           'is_placeholder': False,
                           'evidence_type': 'AUTHOR_REPORTED_DIRECT',
                           'material_form': 'L_PBF',
                           'heat_treatment': 'HIP',
                           'source_quality': 'PRIMARY_DIRECT_SOURCED',
                           'production_eligible': False,
                           'platform': 'EOS M400',
                           'test_method': 'ASTM E8',
                           'test_environment': 'AIR',
                           'source_temperature': 'ROOM_TEMPERATURE_70_F'},
                          {'source_id': 'NASA_2024_GRCOP42_MAX_USE_TEMPERATURE',
                           'source_type': 'government_primary',
                           'title': 'Extreme Environment Materials for Additive Manufacturing',
                           'citation': 'NASA NTRS 20240013525, Gradl et al., ASTM ICAM 2024',
                           'confidence': 1.0,
                           'properties_covered': ['max_service_temperature'],
                           'is_placeholder': False,
                           'evidence_type': 'AUTHORITATIVE_ENGINEERING_LIMIT',
                           'material_form': 'L_PBF',
                           'heat_treatment': 'HIP',
                           'source_quality': 'PRIMARY_AUTHORITATIVE_SOURCED',
                           'production_eligible': True},
                          {'source_id': '3D_SYSTEMS_CERTIFIED_GRCOP42_SERVICE_TEMPERATURE',
                           'source_type': 'certified_manufacturer_datasheet',
                           'title': 'Certified GRCop-42 Material Datasheet',
                           'citation': '3D Systems Certified GRCop-42 Datasheet, 2023-07-14',
                           'confidence': 1.0,
                           'properties_covered': ['max_service_temperature'],
                           'is_placeholder': False,
                           'evidence_type': 'AUTHORITATIVE_ENGINEERING_LIMIT',
                           'material_form': 'L_PBF',
                           'heat_treatment': 'HIP',
                           'source_quality': 'AUTHORITATIVE_CERTIFIED_DATASHEET',
                           'production_eligible': True},
                          {'source_id': 'CHEN_2023_GRCOP42_THERMOPHYSICAL_THERMAL_CONDUCTIVITY',
                           'source_type': 'peer_reviewed_primary',
                           'title': 'Thermophysical properties of additively manufactured (AM) GRCop-42 and '
                                    'GRCop-84',
                           'citation': 'Chen et al., Materials Today Communications 36 (2023) 106665; '
                                       'doi:10.1016/j.mtcomm.2023.106665',
                           'confidence': 1.0,
                           'properties_covered': ['thermal_conductivity'],
                           'is_placeholder': False,
                           'evidence_type': 'AUTHOR_REPORTED_DIRECT',
                           'material_form': 'L_PBF',
                           'heat_treatment': None,
                           'source_quality': 'PRIMARY_DIRECT_SOURCED',
                           'production_eligible': True,
                           'temperature_range_K': [298.15, 973.15]},
                          {'source_id': 'NASA_TM_20205003857_GRCOP42_REFERENCE_DENSITY',
                           'source_type': 'government_primary',
                           'title': 'In-Situ Alloying of GRCop-42 via Additive Manufacturing: Precipitate '
                                    'Analysis',
                           'citation': 'NASA/TM-20205003857',
                           'confidence': 1.0,
                           'properties_covered': ['density'],
                           'is_placeholder': False,
                           'evidence_type': 'AUTHORITATIVE_REFERENCE_VALUE',
                           'material_form': None,
                           'heat_treatment': None,
                           'source_quality': 'PRIMARY_AUTHORITATIVE_SOURCED',
                           'production_eligible': True,
                           'density_kg_m3': 8889.0,
                           'density_semantics': 'REFERENCE_MATERIAL_DENSITY'},
                          {'source_id': 'CHEN_2023_GRCOP42_THERMAL_EXPANSION',
                           'source_type': 'peer_reviewed_primary',
                           'title': 'Thermophysical properties of additively manufactured (AM) GRCop-42 and '
                                    'GRCop-84',
                           'citation': 'Chen et al., Materials Today Communications 36 (2023) 106665; '
                                       'doi:10.1016/j.mtcomm.2023.106665',
                           'confidence': 1.0,
                           'properties_covered': ['density'],
                           'is_placeholder': False,
                           'evidence_type': 'AUTHOR_REPORTED_DIRECT_REGRESSION_USED_FOR_DERIVED_DENSITY',
                           'material_form': 'L_PBF',
                           'heat_treatment': None,
                           'source_quality': 'PRIMARY_DIRECT_SOURCED',
                           'production_eligible': True,
                           'temperature_range_K': [293.15, 1273.15],
                           'derived_property': True},
                          {'source_id': 'NASA_NTRS_20220008606_GRCOP42_LPBF_HIP_ELEVATED_TENSILE',
                           'source_type': 'nasa_primary_material_process_record',
                           'title': 'GRCop-42 L-PBF Material Process Record',
                           'citation': 'NASA NTRS 20220008606, 2022',
                           'confidence': 1.0,
                           'properties_covered': ['yield_strength', 'ultimate_tensile_strength'],
                           'is_placeholder': False,
                           'evidence_type': 'AUTHOR_REPORTED_DIRECT_TABULATED',
                           'material_form': 'L_PBF',
                           'heat_treatment': 'HIP',
                           'heat_treatment_detail': 'STANDARD_MSFC_HIP',
                           'orientation': 'Z',
                           'specimen_surface': 'MACHINED',
                           'test_method': 'ASTM_E21',
                           'test_environment': 'LAB_AIR',
                           'source_temperature_range_K': [672.0388888888889, 873.15],
                           'source_quality': 'PRIMARY_DIRECT_SOURCED',
                           'production_eligible': True}]},
 'Inconel 718': {'material': 'Inconel 718',
                 'mode': 'PARTIAL_SOURCE_MODE',
                 'source_quality': 'ENGINEERING_PLACEHOLDER_PENDING_FULL_SOURCE_TABLE',
                 'sources': [{'source_id': 'IN718_PLACEHOLDER_001',
                              'source_type': 'engineering_placeholder',
                              'title': 'Placeholder Inconel 718 engineering property table',
                              'citation': 'Internal placeholder pending sourced material database.',
                              'confidence': 0.25,
                              'properties_covered': ['thermal_conductivity',
                                                     'density',
                                                     'specific_heat',
                                                     'max_service_temperature'],
                              'is_placeholder': True}]}}


def attach_material_source_provenance_owner(results):
    if not isinstance(results, dict):
        return results

    provenance = build_material_source_provenance_owner(results)
    results.update(provenance)
    return results



def build_material_source_provenance_owner(results):
    results = results if isinstance(results, dict) else {}

    material_name = _normalise_text(
        results.get("material_property_interpolation_material")
        or results.get("selected_material")
        or results.get("material")
        or results.get("chamber_material"),
        default="GRCop-42",
    )

    records = results.get(
        "material_source_records"
    )

    if not isinstance(
        records,
        dict,
    ):
        records = DEFAULT_MATERIAL_SOURCE_RECORDS

    record = records.get(
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

    blockers = []
    warnings = []

    process_sensitive_material = (
        material_name
        ==
        "GRCop-42"
    )

    source_material_form = None
    source_heat_treatment = None

    if isinstance(
        record,
        dict,
    ):
        source_material_form = record.get(
            "material_form"
        )

        source_heat_treatment = record.get(
            "heat_treatment"
        )

    # Legacy material-level identity gate remains intact.
    if process_sensitive_material:
        if selected_material_form is None:
            blockers.append(
                "UNBOUND_MATERIAL_STATE: "
                "GRCop-42 requires an explicit material form."
            )

        elif source_material_form not in (
            None,
            "",
        ):
            if (
                str(
                    source_material_form
                ).strip()
                !=
                selected_material_form
            ):
                blockers.append(
                    "Material-form mismatch: selected "
                    f"{selected_material_form}, "
                    f"source {source_material_form}."
                )

        elif (
            isinstance(
                record,
                dict,
            )
            and
            not any(
                isinstance(
                    source,
                    dict,
                )
                and
                any(
                    key
                    in
                    source
                    for key in (
                        "material_form",
                        "heat_treatment",
                        "evidence_type",
                        "source_quality",
                        "production_eligible",
                    )
                )
                for source in record.get(
                    "sources",
                    [],
                )
            )
        ):
            # Preserve legacy fail-closed behaviour.
            blockers.append(
                "Material source record has no material_form binding."
            )

        if source_heat_treatment not in (
            None,
            "",
        ):
            if selected_material_heat_treatment is None:
                blockers.append(
                    "UNBOUND_MATERIAL_STATE: "
                    "source record requires heat-treatment identity."
                )

            elif (
                str(
                    source_heat_treatment
                ).strip()
                !=
                selected_material_heat_treatment
            ):
                blockers.append(
                    "Heat-treatment mismatch: selected "
                    f"{selected_material_heat_treatment}, "
                    f"source {source_heat_treatment}."
                )

    if not isinstance(
        record,
        dict,
    ):
        blockers.append(
            f"No source/provenance record exists for {material_name}."
        )

        mode = "MISSING_SOURCE_MODE"
        source_quality = "NO_SOURCE"
        sources = []

    else:
        mode = _normalise_text(
            record.get(
                "mode"
            ),
            default="UNKNOWN_MODE",
        )

        source_quality = _normalise_text(
            record.get(
                "source_quality"
            ),
            default="UNKNOWN_SOURCE_QUALITY",
        )

        sources = record.get(
            "sources",
            [],
        )

        if not isinstance(
            sources,
            list,
        ):
            blockers.append(
                f"Source record for {material_name} "
                "has invalid sources list."
            )

            sources = []

    normalised_sources = [
        _normalise_source(
            source
        )
        for source in sources
    ]

    normalised_sources = [
        source
        for source in normalised_sources
        if source is not None
    ]

    if not normalised_sources:
        blockers.append(
            f"No usable source entries exist for {material_name}."
        )

    placeholder_count = sum(
        1
        for source in normalised_sources
        if source[
            "is_placeholder"
        ]
    )

    source_count = len(
        normalised_sources
    )

    confidence_values = [
        source[
            "confidence"
        ]
        for source in normalised_sources
        if source[
            "confidence"
        ]
        is not None
    ]

    average_confidence = (
        round(
            sum(
                confidence_values
            )
            /
            len(
                confidence_values
            ),
            6,
        )
        if confidence_values
        else 0.0
    )

    properties_covered = sorted(
        {
            prop
            for source in normalised_sources
            for prop in source.get(
                "properties_covered",
                [],
            )
        }
    )

    property_sources = {}
    property_status = {}
    property_source_quality = {}
    property_blockers = {}

    for property_name in (
        properties_covered
    ):
        scoped_sources = [
            source
            for source in normalised_sources
            if property_name
            in
            source.get(
                "properties_covered",
                [],
            )
        ]

        source_records = []
        property_errors = []

        for source in scoped_sources:
            source_errors = []

            source_form = source.get(
                "material_form"
            )

            source_heat = source.get(
                "heat_treatment"
            )

            if (
                source_form
                is not None
                and
                selected_material_form
                !=
                source_form
            ):
                source_errors.append(
                    "MATERIAL_FORM_MISMATCH"
                )

            if (
                source_heat
                is not None
                and
                selected_material_heat_treatment
                !=
                source_heat
            ):
                source_errors.append(
                    "HEAT_TREATMENT_MISMATCH"
                )

            if source.get(
                "is_placeholder"
            ):
                source_errors.append(
                    "PLACEHOLDER_SOURCE"
                )

            new_schema = bool(
                source.get(
                    "property_level_schema"
                )
            )

            if (
                new_schema
                and
                source.get(
                    "production_eligible"
                )
                is not True
            ):
                source_errors.append(
                    "SOURCE_NOT_PRODUCTION_ELIGIBLE"
                )

            source_record = dict(
                source
            )

            source_record[
                "property_eligible"
            ] = not source_errors

            source_record[
                "property_blockers"
            ] = source_errors

            source_records.append(
                source_record
            )

            property_errors.extend(
                source_errors
            )

        eligible_sources = [
            source
            for source in source_records
            if source[
                "property_eligible"
            ]
        ]

        property_sources[
            property_name
        ] = source_records

        property_blockers[
            property_name
        ] = sorted(
            set(
                property_errors
            )
        )

        qualities = [
            source.get(
                "source_quality"
            )
            for source in eligible_sources
            if source.get(
                "source_quality"
            )
        ]

        property_source_quality[
            property_name
        ] = (
            qualities[0]
            if len(
                set(
                    qualities
                )
            )
            ==
            1
            else
            "MIXED_PROPERTY_SOURCE_QUALITY"
            if qualities
            else
            source_quality
        )

        property_status[
            property_name
        ] = {
            "eligible":
                bool(
                    eligible_sources
                ),

            "eligible_source_count":
                len(
                    eligible_sources
                ),

            "source_count":
                len(
                    source_records
                ),

            "blockers":
                property_blockers[
                    property_name
                ],

            "identity_status":
                (
                    "PROPERTY_IDENTITY_ELIGIBLE"
                    if eligible_sources
                    else
                    "PROPERTY_IDENTITY_BLOCKED"
                ),

            "source_quality":
                property_source_quality[
                    property_name
                ],
        }

    if placeholder_count > 0:
        warnings.append(
            f"{placeholder_count} placeholder source(s) are present; "
            "conservative validation pass remains blocked."
        )

    if mode != "SOURCED_VALIDATION_MODE":
        warnings.append(
            "Material is not in SOURCED_VALIDATION_MODE; "
            f"current mode is {mode}."
        )

    property_level_schema_present = any(
        source.get(
            "property_level_schema"
        )
        for source in normalised_sources
    )

    any_property_eligible = any(
        status.get(
            "eligible"
        )
        for status in property_status.values()
    )

    if property_level_schema_present:
        conservative_pass_allowed = (
            not blockers
            and source_count > 0
            and placeholder_count == 0
            and mode == "SOURCED_VALIDATION_MODE"
            and any_property_eligible
        )

    else:
        conservative_pass_allowed = (
            not blockers
            and source_count > 0
            and placeholder_count == 0
            and mode == "SOURCED_VALIDATION_MODE"
            and source_quality == "FULLY_SOURCED"
            and average_confidence >= 0.75
        )

    complete = (
        not blockers
    )

    status = (
        "PASS_MATERIAL_SOURCE_PROVENANCE_OWNER"
        if complete
        else
        "FAIL_MATERIAL_SOURCE_PROVENANCE_OWNER"
    )

    text = build_material_source_provenance_text(
        status=status,
        material_name=material_name,
        mode=mode,
        source_quality=source_quality,
        source_count=source_count,
        placeholder_count=placeholder_count,
        average_confidence=average_confidence,
        properties_covered=properties_covered,
        sources=normalised_sources,
        blockers=blockers,
        warnings=warnings,
        conservative_pass_allowed=conservative_pass_allowed,
    )

    return {
        "material_source_provenance_owner_status":
            status,

        "material_source_provenance_owner_complete":
            complete,

        "material_source_provenance_material":
            material_name,

        "material_source_provenance_selected_material_form":
            selected_material_form,

        "material_source_provenance_selected_heat_treatment":
            selected_material_heat_treatment,

        "material_source_provenance_record_material_form":
            source_material_form,

        "material_source_provenance_record_heat_treatment":
            source_heat_treatment,

        "material_source_provenance_material_identity_status":
            (
                "BOUND_MATERIAL_STATE"
                if not blockers
                else
                "UNBOUND_OR_MISMATCHED_MATERIAL_STATE"
            ),

        "material_source_provenance_mode":
            mode,

        "material_source_provenance_source_quality":
            source_quality,

        "material_source_provenance_sources":
            normalised_sources,

        "material_source_provenance_source_count":
            source_count,

        "material_source_provenance_placeholder_count":
            placeholder_count,

        "material_source_provenance_average_confidence":
            average_confidence,

        "material_source_provenance_properties_covered":
            properties_covered,

        "material_source_provenance_blockers":
            blockers,

        "material_source_provenance_warnings":
            warnings,

        "material_source_provenance_conservative_pass_allowed":
            conservative_pass_allowed,

        "material_source_provenance_text":
            text,

        "material_source_provenance_property_sources":
            property_sources,

        "material_source_provenance_property_status":
            property_status,

        "material_source_provenance_property_source_quality":
            property_source_quality,

        "material_source_provenance_property_blockers":
            property_blockers,

        "phase_9b_material_source_provenance_owner_complete":
            complete,
    }



def build_material_source_provenance_text(
        status,
        material_name,
        mode,
        source_quality,
        source_count,
        placeholder_count,
        average_confidence,
        properties_covered,
        sources,
        blockers,
        warnings,
        conservative_pass_allowed,
):
    lines = [
        "LEAF REGEN PHASE 9B MATERIAL SOURCE / PROVENANCE OWNER",
        "=======================================================",
        "",
        f"Status: {status}",
        f"Material: {material_name}",
        f"Validation mode: {mode}",
        f"Source quality: {source_quality}",
        f"Source count: {source_count}",
        f"Placeholder source count: {placeholder_count}",
        f"Average confidence: {average_confidence}",
        f"Conservative pass allowed: {conservative_pass_allowed}",
        "",
        "Owned By:",
        "- material_source_provenance_owner.py",
        "",
        "Scope:",
        "- Owns material source metadata.",
        "- Owns material provenance evidence.",
        "- Owns placeholder-source detection.",
        "- Owns source confidence summaries.",
        "- Does not rank sources yet.",
        "- Does not approve material validation by itself.",
        "",
        "Properties Covered:",
    ]

    if properties_covered:
        for prop in properties_covered:
            lines.append(f"- {prop}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Sources:")

    if sources:
        for source in sources:
            lines.append("")
            lines.append(f"- Source ID: {source.get('source_id')}")
            lines.append(f"  Type: {source.get('source_type')}")
            lines.append(f"  Title: {source.get('title')}")
            lines.append(f"  Citation: {source.get('citation')}")
            lines.append(f"  Confidence: {source.get('confidence')}")
            lines.append(f"  Placeholder: {source.get('is_placeholder')}")
            lines.append(f"  Properties: {source.get('properties_covered')}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Warnings:")

    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
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
        "- After Phase 9B is verified, build Phase 9C source-quality ranking ownership."
    )

    return "\n".join(lines)



def _normalise_source(source):
    if not isinstance(source, dict):
        return None

    source_id = _normalise_text(
        source.get("source_id"),
        default="UNIDENTIFIED_SOURCE",
    )

    source_type = _normalise_text(
        source.get("source_type"),
        default="unknown",
    )

    title = _normalise_text(
        source.get("title"),
        default="Untitled source",
    )

    citation = _normalise_text(
        source.get("citation"),
        default="",
    )

    confidence = source.get(
        "confidence"
    )

    try:
        confidence = (
            float(confidence)
            if confidence is not None
            else None
        )
    except Exception:
        confidence = None

    properties_covered = source.get(
        "properties_covered",
        [],
    )

    if not isinstance(
        properties_covered,
        (
            list,
            tuple,
            set,
        ),
    ):
        properties_covered = []

    properties_covered = [
        str(value).strip()
        for value in properties_covered
        if value not in (
            None,
            "",
        )
    ]

    is_placeholder = bool(
        source.get(
            "is_placeholder",
            False,
        )
    )

    new_schema_present = any(
        key
        in
        source
        for key in (
            "evidence_type",
            "material_form",
            "heat_treatment",
            "source_quality",
            "production_eligible",
        )
    )

    evidence_type = (
        _normalise_text(
            source.get(
                "evidence_type"
            ),
            default="UNSPECIFIED_EVIDENCE",
        )
        if new_schema_present
        else None
    )

    material_form = source.get(
        "material_form"
    )

    material_form = (
        str(
            material_form
        ).strip()
        if material_form not in (
            None,
            "",
        )
        else None
    )

    heat_treatment = source.get(
        "heat_treatment"
    )

    heat_treatment = (
        str(
            heat_treatment
        ).strip()
        if heat_treatment not in (
            None,
            "",
        )
        else None
    )

    source_quality = source.get(
        "source_quality"
    )

    source_quality = (
        str(
            source_quality
        ).strip()
        if source_quality not in (
            None,
            "",
        )
        else None
    )

    if new_schema_present:
        production_eligible = bool(
            source.get(
                "production_eligible",
                False,
            )
        )
    else:
        production_eligible = None

    return {
        "source_id":
            source_id,

        "source_type":
            source_type,

        "title":
            title,

        "citation":
            citation,

        "confidence":
            confidence,

        "properties_covered":
            properties_covered,

        "is_placeholder":
            is_placeholder,

        "evidence_type":
            evidence_type,

        "material_form":
            material_form,

        "heat_treatment":
            heat_treatment,

        "source_quality":
            source_quality,

        "production_eligible":
            production_eligible,

        "platform":
            (
                _normalise_text(
                    source.get("platform"),
                    default="",
                )
                or
                None
            ),

        "test_method":
            (
                _normalise_text(
                    source.get("test_method"),
                    default="",
                )
                or
                None
            ),

        "test_environment":
            (
                _normalise_text(
                    source.get("test_environment"),
                    default="",
                )
                or
                None
            ),

        "source_temperature":
            (
                _normalise_text(
                    source.get("source_temperature"),
                    default="",
                )
                or
                None
            ),

        "property_level_schema":
            new_schema_present,
    }



def _normalise_text(value, default=""):
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _clamp01(value):
    return max(0.0, min(1.0, float(value)))


def _bool_value(value, default=False):
    if value is None:
        return bool(default)

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value_l = value.strip().lower()

        if value_l in {"true", "1", "yes", "y", "enabled", "on"}:
            return True

        if value_l in {"false", "0", "no", "n", "disabled", "off"}:
            return False

    return bool(value)