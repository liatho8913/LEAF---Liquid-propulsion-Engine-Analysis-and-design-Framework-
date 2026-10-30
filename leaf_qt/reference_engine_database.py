import ast
import copy

REFERENCE_ENGINE_INPUT_FIELDS = [
    "fuel",
    "oxidizer",
    "mixture_ratio",
    "mass_flow_rate",
    "chamber_pressure",
    "characteristic_length",
    "ambient_pressure",
]

CEA_DERIVED_REFERENCE_FIELDS = [
    "chamber_temperature",
    "Gamma",
    "R",
    "cea_selected_prandtl",
    "characteristic_velocity",
    "specific_impulse",
    "exhaust_velocity",
]

REFERENCE_ENGINE_COMPARISON_FIELDS = [
    "channel_count",
    "channel_width_m",
    "channel_height_m",
    "wall_thickness_m",
    "coolant_velocity_m_s",
    "pressure_drop_pa",
    "coolant_temperature_rise_k",
]

REFERENCE_ENGINE_SOURCE_FIELDS = [
    "source_title",
    "source_author",
    "source_year",
    "doi",
    "url",
]

REFERENCE_QUALITY_BANDS = [
    "PLACEHOLDER",
    "LOW_CONFIDENCE_PUBLIC",
    "PARTIAL_ENGINEERING_SOURCE",
    "SOURCED_ENGINEERING_REFERENCE",
    "HIGH_CONFIDENCE_BENCHMARK",
]

REFERENCE_REBUILD_MODES = [
    "REFERENCE_LIBRARY_ONLY",
    "REFERENCE_REBUILD_READY",
    "REFERENCE_REBUILD_PARTIAL",
    "REFERENCE_REBUILD_BLOCKED",
]

REFERENCE_ENGINE_REQUIRED_TOP_LEVEL_FIELDS = [
    "display_name",
    "class",
    "fuel",
    "oxidizer",
    "thrust_n",
    "minimum_input_overrides",
    "reference_geometry",
    "channel_count",
    "channel_width_m",
    "channel_height_m",
    "wall_thickness_m",
    "coolant_velocity_m_s",
    "pressure_drop_pa",
    "coolant_temperature_rise_k",
    "source_status",
    "data_quality_band",
    "data_quality_score",
    "data_quality_notes",
    "source_title",
    "source_author",
    "source_year",
    "doi",
    "url",
    "notes",
    "source_ledger",
    "source_targets",
    "value_origin",
    "candidate_reference_values",
]

REFERENCE_ENGINE_GEOMETRY_FIELDS = [
    "throat_area_m2",
    "exit_area_m2",
    "throat_radius_m",
    "exit_radius_m",
    "nozzle_length_m",
]

REFERENCE_ENGINE_SECTION_FIELDS = {
    "minimum_input_overrides": REFERENCE_ENGINE_INPUT_FIELDS,
    "reference_geometry": REFERENCE_ENGINE_GEOMETRY_FIELDS,
}

REFERENCE_ENGINES = {
    "RL10": {
        "display_name": "RL10",
        "class": "upper-stage expander engine",
        "fuel": "LH2",
        "oxidizer": "LOX",
        "thrust_n": None,

        "minimum_input_overrides": {
            "fuel": None,
            "oxidizer": None,
            "mixture_ratio": None,
            "mass_flow_rate": None,
            "chamber_pressure": None,
            "characteristic_length": None,
            "ambient_pressure": None,
        },

        "channel_count": None,
        "reference_geometry": {
            "throat_area_m2": None,
            "exit_area_m2": None,
            "throat_radius_m": None,
            "exit_radius_m": None,
            "nozzle_length_m": None,
        },
        "channel_width_m": None,
        "channel_height_m": None,
        "wall_thickness_m": None,
        "coolant_velocity_m_s": None,
        "pressure_drop_pa": None,
        "coolant_temperature_rise_k": None,

        "source_status": "PLACEHOLDER_REQUIRED",
        "data_quality_band": "PLACEHOLDER",
        "data_quality_score": 0,
        "data_quality_notes": "No sourced reference values added yet.",
        "source_title": None,
        "source_author": None,
        "source_year": None,
        "doi": None,
        "url": None,
        "notes": "Populate only from sourced public data.",
        "source_ledger": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "source_targets": {
            "minimum_input_overrides": {
                "fuel": "Public engine overview / manufacturer / NASA page",
                "oxidizer": "Public engine overview / manufacturer / NASA page",
                "mixture_ratio": "Technical paper, NASA report, or manufacturer data",
                "mass_flow_rate": "Technical paper, NASA report, or derived from sourced thrust/Isp only if stated",
                "chamber_pressure": "Technical paper, NASA report, or manufacturer data",
                "characteristic_length": "Rarely public; use only if explicitly sourced",
                "ambient_pressure": "Mission/operating condition assumption; document clearly",
            },
            "reference_geometry": {
                "throat_area_m2": "Technical drawing, public report, or derived from sourced throat diameter",
                "exit_area_m2": "Technical drawing, public report, or derived from sourced exit diameter",
                "throat_radius_m": "Technical drawing, public report, or derived from sourced throat diameter",
                "exit_radius_m": "Technical drawing, public report, or derived from sourced exit diameter",
                "nozzle_length_m": "Technical drawing, photo scaling with documented uncertainty, or report",
            },
            "comparison_values": {
                "channel_count": "Cooling-channel paper, patent, drawing, or high-confidence source",
                "channel_width_m": "Cooling-channel paper, patent, drawing, or measured drawing",
                "channel_height_m": "Cooling-channel paper, patent, drawing, or measured drawing",
                "wall_thickness_m": "Thrust chamber paper, drawing, material/manufacturing report",
                "coolant_velocity_m_s": "Usually derived; only use if method and assumptions are recorded",
                "pressure_drop_pa": "Usually derived or test data; record assumptions",
                "coolant_temperature_rise_k": "Usually derived or test data; record assumptions",
            },
        },
        "value_origin": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "candidate_reference_values": {
            "minimum_input_overrides": {
                "fuel": "LH2",
                "oxidizer": "LOX",
                "mixture_ratio": 5.88,
                "mass_flow_rate": 24.0,
                "chamber_pressure": 3.96e6,
                "ambient_pressure": 0.0,
            },
            "reference_geometry": {},
            "comparison_values": {},
            "notes": "Candidate public RL10 values only. Do not use for validation PASS until checked and promoted with source ledger/origin.",
        },
    },

    "Merlin_1D": {
        "display_name": "Merlin 1D class",
        "class": "booster gas-generator engine",
        "fuel": "RP-1",
        "oxidizer": "LOX",
        "thrust_n": None,

        "minimum_input_overrides": {
            "fuel": None,
            "oxidizer": None,
            "mixture_ratio": None,
            "mass_flow_rate": None,
            "chamber_pressure": None,
            "characteristic_length": None,
            "ambient_pressure": None,
        },

        "channel_count": None,
        "reference_geometry": {
            "throat_area_m2": None,
            "exit_area_m2": None,
            "throat_radius_m": None,
            "exit_radius_m": None,
            "nozzle_length_m": None,
        },
        "channel_width_m": None,
        "channel_height_m": None,
        "wall_thickness_m": None,
        "coolant_velocity_m_s": None,
        "pressure_drop_pa": None,
        "coolant_temperature_rise_k": None,

        "source_status": "PLACEHOLDER_REQUIRED",
        "data_quality_band": "PLACEHOLDER",
        "data_quality_score": 0,
        "data_quality_notes": "No sourced reference values added yet.",
        "source_title": None,
        "source_author": None,
        "source_year": None,
        "doi": None,
        "url": None,
        "notes": "Populate only from sourced public data.",
        "source_ledger": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "source_targets": {
            "minimum_input_overrides": {
                "fuel": "Public engine overview / manufacturer / NASA page",
                "oxidizer": "Public engine overview / manufacturer / NASA page",
                "mixture_ratio": "Technical paper, NASA report, or manufacturer data",
                "mass_flow_rate": "Technical paper, NASA report, or derived from sourced thrust/Isp only if stated",
                "chamber_pressure": "Technical paper, NASA report, or manufacturer data",
                "characteristic_length": "Rarely public; use only if explicitly sourced",
                "ambient_pressure": "Mission/operating condition assumption; document clearly",
            },
            "reference_geometry": {
                "throat_area_m2": "Technical drawing, public report, or derived from sourced throat diameter",
                "exit_area_m2": "Technical drawing, public report, or derived from sourced exit diameter",
                "throat_radius_m": "Technical drawing, public report, or derived from sourced throat diameter",
                "exit_radius_m": "Technical drawing, public report, or derived from sourced exit diameter",
                "nozzle_length_m": "Technical drawing, photo scaling with documented uncertainty, or report",
            },
            "comparison_values": {
                "channel_count": "Cooling-channel paper, patent, drawing, or high-confidence source",
                "channel_width_m": "Cooling-channel paper, patent, drawing, or measured drawing",
                "channel_height_m": "Cooling-channel paper, patent, drawing, or measured drawing",
                "wall_thickness_m": "Thrust chamber paper, drawing, material/manufacturing report",
                "coolant_velocity_m_s": "Usually derived; only use if method and assumptions are recorded",
                "pressure_drop_pa": "Usually derived or test data; record assumptions",
                "coolant_temperature_rise_k": "Usually derived or test data; record assumptions",
            },
        },
        "value_origin": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "candidate_reference_values": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
            "notes": "Candidate values only. Do not use for PASS until promoted into validated fields with ledger/origin.",
        },
    },

    "RS25": {
        "display_name": "RS-25",
        "class": "large staged-combustion engine",
        "fuel": "LH2",
        "oxidizer": "LOX",
        "thrust_n": None,

        "minimum_input_overrides": {
            "fuel": None,
            "oxidizer": None,
            "mixture_ratio": None,
            "mass_flow_rate": None,
            "chamber_pressure": None,
            "characteristic_length": None,
            "ambient_pressure": None,
        },

        "channel_count": None,
        "reference_geometry": {
            "throat_area_m2": None,
            "exit_area_m2": None,
            "throat_radius_m": None,
            "exit_radius_m": None,
            "nozzle_length_m": None,
        },
        "channel_width_m": None,
        "channel_height_m": None,
        "wall_thickness_m": None,
        "coolant_velocity_m_s": None,
        "pressure_drop_pa": None,
        "coolant_temperature_rise_k": None,

        "source_status": "PLACEHOLDER_REQUIRED",
        "data_quality_band": "PLACEHOLDER",
        "data_quality_score": 0,
        "data_quality_notes": "No sourced reference values added yet.",
        "source_title": None,
        "source_author": None,
        "source_year": None,
        "doi": None,
        "url": None,
        "notes": "Populate only from sourced public data.",
        "source_ledger": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "source_targets": {
            "minimum_input_overrides": {
                "fuel": "Public engine overview / manufacturer / NASA page",
                "oxidizer": "Public engine overview / manufacturer / NASA page",
                "mixture_ratio": "Technical paper, NASA report, or manufacturer data",
                "mass_flow_rate": "Technical paper, NASA report, or derived from sourced thrust/Isp only if stated",
                "chamber_pressure": "Technical paper, NASA report, or manufacturer data",
                "characteristic_length": "Rarely public; use only if explicitly sourced",
                "ambient_pressure": "Mission/operating condition assumption; document clearly",
            },
            "reference_geometry": {
                "throat_area_m2": "Technical drawing, public report, or derived from sourced throat diameter",
                "exit_area_m2": "Technical drawing, public report, or derived from sourced exit diameter",
                "throat_radius_m": "Technical drawing, public report, or derived from sourced throat diameter",
                "exit_radius_m": "Technical drawing, public report, or derived from sourced exit diameter",
                "nozzle_length_m": "Technical drawing, photo scaling with documented uncertainty, or report",
            },
            "comparison_values": {
                "channel_count": "Cooling-channel paper, patent, drawing, or high-confidence source",
                "channel_width_m": "Cooling-channel paper, patent, drawing, or measured drawing",
                "channel_height_m": "Cooling-channel paper, patent, drawing, or measured drawing",
                "wall_thickness_m": "Thrust chamber paper, drawing, material/manufacturing report",
                "coolant_velocity_m_s": "Usually derived; only use if method and assumptions are recorded",
                "pressure_drop_pa": "Usually derived or test data; record assumptions",
                "coolant_temperature_rise_k": "Usually derived or test data; record assumptions",
            },
        },
        "value_origin": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "candidate_reference_values": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
            "notes": "Candidate values only. Do not use for PASS until promoted into validated fields with ledger/origin.",
        },
    },

    "BE3": {
        "display_name": "BE-3 class",
        "class": "large hydrolox upper-stage / booster-derived engine",
        "fuel": "LH2",
        "oxidizer": "LOX",
        "thrust_n": None,

        "minimum_input_overrides": {
            "fuel": None,
            "oxidizer": None,
            "mixture_ratio": None,
            "mass_flow_rate": None,
            "chamber_pressure": None,
            "characteristic_length": None,
            "ambient_pressure": None,
        },

        "channel_count": None,
        "reference_geometry": {
            "throat_area_m2": None,
            "exit_area_m2": None,
            "throat_radius_m": None,
            "exit_radius_m": None,
            "nozzle_length_m": None,
        },
        "channel_width_m": None,
        "channel_height_m": None,
        "wall_thickness_m": None,
        "coolant_velocity_m_s": None,
        "pressure_drop_pa": None,
        "coolant_temperature_rise_k": None,

        "source_status": "PLACEHOLDER_REQUIRED",
        "data_quality_band": "PLACEHOLDER",
        "data_quality_score": 0,
        "data_quality_notes": "No sourced reference values added yet.",
        "source_title": None,
        "source_author": None,
        "source_year": None,
        "doi": None,
        "url": None,
        "notes": "Populate only from sourced public data.",
        "source_ledger": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "source_targets": {
            "minimum_input_overrides": {
                "fuel": "Public engine overview / manufacturer / NASA page",
                "oxidizer": "Public engine overview / manufacturer / NASA page",
                "mixture_ratio": "Technical paper, NASA report, or manufacturer data",
                "mass_flow_rate": "Technical paper, NASA report, or derived from sourced thrust/Isp only if stated",
                "chamber_pressure": "Technical paper, NASA report, or manufacturer data",
                "characteristic_length": "Rarely public; use only if explicitly sourced",
                "ambient_pressure": "Mission/operating condition assumption; document clearly",
            },
            "reference_geometry": {
                "throat_area_m2": "Technical drawing, public report, or derived from sourced throat diameter",
                "exit_area_m2": "Technical drawing, public report, or derived from sourced exit diameter",
                "throat_radius_m": "Technical drawing, public report, or derived from sourced throat diameter",
                "exit_radius_m": "Technical drawing, public report, or derived from sourced exit diameter",
                "nozzle_length_m": "Technical drawing, photo scaling with documented uncertainty, or report",
            },
            "comparison_values": {
                "channel_count": "Cooling-channel paper, patent, drawing, or high-confidence source",
                "channel_width_m": "Cooling-channel paper, patent, drawing, or measured drawing",
                "channel_height_m": "Cooling-channel paper, patent, drawing, or measured drawing",
                "wall_thickness_m": "Thrust chamber paper, drawing, material/manufacturing report",
                "coolant_velocity_m_s": "Usually derived; only use if method and assumptions are recorded",
                "pressure_drop_pa": "Usually derived or test data; record assumptions",
                "coolant_temperature_rise_k": "Usually derived or test data; record assumptions",
            },
        },
        "value_origin": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "candidate_reference_values": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
            "notes": "Candidate values only. Do not use for PASS until promoted into validated fields with ledger/origin.",
        },
    },

    "BE4": {
        "display_name": "BE-4 class",
        "class": "large methalox staged-combustion booster engine",
        "fuel": "LCH4",
        "oxidizer": "LOX",
        "thrust_n": None,

        "minimum_input_overrides": {
            "fuel": None,
            "oxidizer": None,
            "mixture_ratio": None,
            "mass_flow_rate": None,
            "chamber_pressure": None,
            "characteristic_length": None,
            "ambient_pressure": None,
        },

        "channel_count": None,
        "reference_geometry": {
            "throat_area_m2": None,
            "exit_area_m2": None,
            "throat_radius_m": None,
            "exit_radius_m": None,
            "nozzle_length_m": None,
        },
        "channel_width_m": None,
        "channel_height_m": None,
        "wall_thickness_m": None,
        "coolant_velocity_m_s": None,
        "pressure_drop_pa": None,
        "coolant_temperature_rise_k": None,

        "source_status": "PLACEHOLDER_REQUIRED",
        "data_quality_band": "PLACEHOLDER",
        "data_quality_score": 0,
        "data_quality_notes": "No sourced reference values added yet.",
        "source_title": None,
        "source_author": None,
        "source_year": None,
        "doi": None,
        "url": None,
        "notes": "Populate only from sourced public data.",
        "source_ledger": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "source_targets": {
            "minimum_input_overrides": {
                "fuel": "Public engine overview / manufacturer / NASA page",
                "oxidizer": "Public engine overview / manufacturer / NASA page",
                "mixture_ratio": "Technical paper, NASA report, or manufacturer data",
                "mass_flow_rate": "Technical paper, NASA report, or derived from sourced thrust/Isp only if stated",
                "chamber_pressure": "Technical paper, NASA report, or manufacturer data",
                "characteristic_length": "Rarely public; use only if explicitly sourced",
                "ambient_pressure": "Mission/operating condition assumption; document clearly",
            },
            "reference_geometry": {
                "throat_area_m2": "Technical drawing, public report, or derived from sourced throat diameter",
                "exit_area_m2": "Technical drawing, public report, or derived from sourced exit diameter",
                "throat_radius_m": "Technical drawing, public report, or derived from sourced throat diameter",
                "exit_radius_m": "Technical drawing, public report, or derived from sourced exit diameter",
                "nozzle_length_m": "Technical drawing, photo scaling with documented uncertainty, or report",
            },
            "comparison_values": {
                "channel_count": "Cooling-channel paper, patent, drawing, or high-confidence source",
                "channel_width_m": "Cooling-channel paper, patent, drawing, or measured drawing",
                "channel_height_m": "Cooling-channel paper, patent, drawing, or measured drawing",
                "wall_thickness_m": "Thrust chamber paper, drawing, material/manufacturing report",
                "coolant_velocity_m_s": "Usually derived; only use if method and assumptions are recorded",
                "pressure_drop_pa": "Usually derived or test data; record assumptions",
                "coolant_temperature_rise_k": "Usually derived or test data; record assumptions",
            },
        },
        "value_origin": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "candidate_reference_values": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
            "notes": "Candidate values only. Do not use for PASS until promoted into validated fields with ledger/origin.",
        },
    },

    "Raptor": {
        "display_name": "Raptor class",
        "class": "large methalox full-flow staged-combustion engine",
        "fuel": "LCH4",
        "oxidizer": "LOX",
        "thrust_n": None,

        "minimum_input_overrides": {
            "fuel": None,
            "oxidizer": None,
            "mixture_ratio": None,
            "mass_flow_rate": None,
            "chamber_pressure": None,
            "characteristic_length": None,
            "ambient_pressure": None,
        },

        "channel_count": None,
        "reference_geometry": {
            "throat_area_m2": None,
            "exit_area_m2": None,
            "throat_radius_m": None,
            "exit_radius_m": None,
            "nozzle_length_m": None,
        },
        "channel_width_m": None,
        "channel_height_m": None,
        "wall_thickness_m": None,
        "coolant_velocity_m_s": None,
        "pressure_drop_pa": None,
        "coolant_temperature_rise_k": None,

        "source_status": "PLACEHOLDER_REQUIRED",
        "data_quality_band": "PLACEHOLDER",
        "data_quality_score": 0,
        "data_quality_notes": "No sourced reference values added yet.",
        "source_title": None,
        "source_author": None,
        "source_year": None,
        "doi": None,
        "url": None,
        "notes": "Populate only from sourced public data.",
        "source_ledger": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "source_targets": {
            "minimum_input_overrides": {
                "fuel": "Public engine overview / manufacturer / NASA page",
                "oxidizer": "Public engine overview / manufacturer / NASA page",
                "mixture_ratio": "Technical paper, NASA report, or manufacturer data",
                "mass_flow_rate": "Technical paper, NASA report, or derived from sourced thrust/Isp only if stated",
                "chamber_pressure": "Technical paper, NASA report, or manufacturer data",
                "characteristic_length": "Rarely public; use only if explicitly sourced",
                "ambient_pressure": "Mission/operating condition assumption; document clearly",
            },
            "reference_geometry": {
                "throat_area_m2": "Technical drawing, public report, or derived from sourced throat diameter",
                "exit_area_m2": "Technical drawing, public report, or derived from sourced exit diameter",
                "throat_radius_m": "Technical drawing, public report, or derived from sourced throat diameter",
                "exit_radius_m": "Technical drawing, public report, or derived from sourced exit diameter",
                "nozzle_length_m": "Technical drawing, photo scaling with documented uncertainty, or report",
            },
            "comparison_values": {
                "channel_count": "Cooling-channel paper, patent, drawing, or high-confidence source",
                "channel_width_m": "Cooling-channel paper, patent, drawing, or measured drawing",
                "channel_height_m": "Cooling-channel paper, patent, drawing, or measured drawing",
                "wall_thickness_m": "Thrust chamber paper, drawing, material/manufacturing report",
                "coolant_velocity_m_s": "Usually derived; only use if method and assumptions are recorded",
                "pressure_drop_pa": "Usually derived or test data; record assumptions",
                "coolant_temperature_rise_k": "Usually derived or test data; record assumptions",
            },
        },
        "value_origin": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "candidate_reference_values": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
            "notes": "Candidate values only. Do not use for PASS until promoted into validated fields with ledger/origin.",
        },
    },
}


def get_reference_engine_names():
    return list(REFERENCE_ENGINES.keys())

def get_raw_reference_engine(name):
    if not name:
        return None

    engine = REFERENCE_ENGINES.get(str(name))

    if not engine:
        return None

    return copy.deepcopy(engine)

def get_reference_engine(name):
    if not name:
        return None

    engine = REFERENCE_ENGINES.get(str(name))

    if not engine:
        return None

    return normalise_reference_engine_record(engine)

def get_reference_engine_candidate_values(name):
    engine = get_reference_engine(name)

    if not engine:
        return {}

    candidates = engine.get("candidate_reference_values", {})

    if not isinstance(candidates, dict):
        return {}

    return candidates

def audit_reference_engine_schema(name):
    raw = get_raw_reference_engine(name)

    if not raw:
        return {
            "status": "REFERENCE_ENGINE_NOT_FOUND",
            "missing_top_level": [],
            "missing_nested": [],
            "unexpected_nested_type": [],
            "recommendation": "Reference engine was not found.",
        }

    missing_top_level = [
        field for field in REFERENCE_ENGINE_REQUIRED_TOP_LEVEL_FIELDS
        if field not in raw
    ]

    missing_nested = []
    unexpected_nested_type = []

    for section_name, required_fields in REFERENCE_ENGINE_SECTION_FIELDS.items():
        section = raw.get(section_name)

        if not isinstance(section, dict):
            unexpected_nested_type.append(section_name)
            continue

        for field in required_fields:
            if field not in section:
                missing_nested.append(f"{section_name}.{field}")

    for section_name in [
        "source_ledger",
        "source_targets",
        "value_origin",
        "candidate_reference_values",
    ]:
        section = raw.get(section_name)

        if not isinstance(section, dict):
            unexpected_nested_type.append(section_name)
            continue

        for subsection in [
            "minimum_input_overrides",
            "reference_geometry",
            "comparison_values",
        ]:
            if subsection not in section:
                missing_nested.append(f"{section_name}.{subsection}")

    candidate_values = raw.get("candidate_reference_values", {})
    if isinstance(candidate_values, dict) and "notes" not in candidate_values:
        missing_nested.append("candidate_reference_values.notes")

    if missing_top_level or missing_nested or unexpected_nested_type:
        status = "SCHEMA_INCOMPLETE"
        recommendation = "Repair missing schema fields before adding more sourced data."
    else:
        status = "SCHEMA_OK"
        recommendation = "Reference engine schema is complete."

    return {
        "status": status,
        "missing_top_level": missing_top_level,
        "missing_nested": missing_nested,
        "unexpected_nested_type": unexpected_nested_type,
        "recommendation": recommendation,
    }

def audit_all_reference_engine_schemas():
    rows = []

    for name in get_reference_engine_names():
        audit = audit_reference_engine_schema(name)
        rows.append({
            "name": name,
            "status": audit.get("status"),
            "missing_top_level_count": len(audit.get("missing_top_level", [])),
            "missing_nested_count": len(audit.get("missing_nested", [])),
            "unexpected_nested_type_count": len(audit.get("unexpected_nested_type", [])),
            "recommendation": audit.get("recommendation"),
        })

    broken = [
        row for row in rows
        if row.get("status") != "SCHEMA_OK"
    ]

    if broken:
        status = "SCHEMA_REPAIR_REQUIRED"
        recommendation = "One or more reference engines have incomplete schema."
    else:
        status = "ALL_SCHEMAS_OK"
        recommendation = "All reference engine records have complete schema."

    return {
        "status": status,
        "rows": rows,
        "broken_count": len(broken),
        "total_count": len(rows),
        "recommendation": recommendation,
    }

def build_reference_schema_repair_patch(name):
    raw = get_raw_reference_engine(name)

    if not raw:
        return f"# Reference engine '{name}' was not found."

    audit = audit_reference_engine_schema(name)

    lines = []
    lines.append(f"# Schema Repair Patch — {name}")
    lines.append("# Add/merge the following fields into this engine record.")
    lines.append("")

    defaults = {
        "minimum_input_overrides": {key: None for key in REFERENCE_ENGINE_INPUT_FIELDS},
        "reference_geometry": {key: None for key in REFERENCE_ENGINE_GEOMETRY_FIELDS},
        "source_ledger": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "source_targets": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "value_origin": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
        },
        "candidate_reference_values": {
            "minimum_input_overrides": {},
            "reference_geometry": {},
            "comparison_values": {},
            "notes": "Candidate values only. Do not use for PASS until promoted into validated fields with ledger/origin.",
        },
    }

    for field in audit.get("missing_top_level", []):
        value = defaults.get(field, None)
        lines.append(f'"{field}": {repr(value)},')

    if audit.get("missing_nested"):
        lines.append("")
        lines.append("# Missing nested fields:")
        for item in audit.get("missing_nested", []):
            lines.append(f"# - {item}")

    if audit.get("unexpected_nested_type"):
        lines.append("")
        lines.append("# Sections with wrong type:")
        for item in audit.get("unexpected_nested_type", []):
            lines.append(f"# - {item}")

    if audit.get("status") == "SCHEMA_OK":
        lines.append("# Schema already complete.")

    return "\n".join(lines)

def run_reference_database_self_test():
    rows = []

    for name in get_reference_engine_names():
        raw = get_raw_reference_engine(name)
        engine = get_reference_engine(name)

        schema = audit_reference_engine_schema(name)
        readiness = evaluate_reference_engine_database_record(name)
        ledger = evaluate_reference_source_ledger_coverage(engine or {})
        origin = evaluate_reference_value_origin_coverage(engine or {})
        quality = evaluate_reference_data_quality(engine or {})
        consistency = evaluate_reference_database_status_consistency(name)

        candidates = {}
        if isinstance(raw, dict):
            candidates = raw.get("candidate_reference_values", {})

        has_candidates = False
        if isinstance(candidates, dict):
            for key in ("minimum_input_overrides", "reference_geometry", "comparison_values"):
                section = candidates.get(key, {})
                if isinstance(section, dict) and section:
                    has_candidates = True

        row_statuses = [
            schema.get("status"),
            readiness.get("status"),
            ledger.get("status"),
            origin.get("status"),
            quality.get("status"),
            consistency.get("status"),
        ]

        blocking = [
            status for status in row_statuses
            if status in (
                "SCHEMA_INCOMPLETE",
                "INVALID_RECORD",
                "STATUS_MISMATCH",
                "ORIGIN_BLOCKED",
            )
        ]

        if blocking:
            overall = "REPAIR_REQUIRED"
        elif schema.get("status") == "SCHEMA_OK":
            overall = "FRAMEWORK_OK"
        else:
            overall = "CHECK_REQUIRED"

        rows.append({
            "name": name,
            "overall": overall,
            "schema": schema.get("status"),
            "readiness": readiness.get("status"),
            "ledger": ledger.get("status"),
            "origin": origin.get("status"),
            "quality": quality.get("status"),
            "consistency": consistency.get("status"),
            "has_candidates": has_candidates,
        })

    repair_count = len([row for row in rows if row.get("overall") == "REPAIR_REQUIRED"])

    if repair_count:
        status = "REFERENCE_DATABASE_REPAIR_REQUIRED"
        recommendation = "Repair schema/status/origin issues before adding more sourced values."
    else:
        status = "REFERENCE_DATABASE_FRAMEWORK_OK"
        recommendation = "Reference database framework is ready for cautious sourced-data population."

    return {
        "status": status,
        "rows": rows,
        "repair_count": repair_count,
        "total_count": len(rows),
        "recommendation": recommendation,
    }

def build_reference_database_self_test_report():
    test = run_reference_database_self_test()

    lines = []
    lines.append("Reference Database Self-Test Report")
    lines.append("=" * 64)
    lines.append("")
    lines.append(f"Status: {test.get('status')}")
    lines.append(f"Repair count: {test.get('repair_count')} / {test.get('total_count')}")
    lines.append(f"Recommendation: {test.get('recommendation')}")
    lines.append("")

    for row in test.get("rows", []):
        lines.append(row.get("name", "UNKNOWN"))
        lines.append("-" * 40)
        lines.append(f"Overall: {row.get('overall')}")
        lines.append(f"Schema: {row.get('schema')}")
        lines.append(f"Readiness: {row.get('readiness')}")
        lines.append(f"Ledger: {row.get('ledger')}")
        lines.append(f"Origin: {row.get('origin')}")
        lines.append(f"Quality: {row.get('quality')}")
        lines.append(f"Consistency: {row.get('consistency')}")
        lines.append(f"Has candidate values: {row.get('has_candidates')}")
        lines.append("")

    return "\n".join(lines)

def evaluate_candidate_promotion_readiness(name):
    raw = get_raw_reference_engine(name)

    if not raw:
        return {
            "status": "REFERENCE_ENGINE_NOT_FOUND",
            "ready_count": 0,
            "candidate_count": 0,
            "missing_requirements": [],
            "recommendation": "Reference engine was not found.",
        }

    candidates = raw.get("candidate_reference_values", {})
    if not isinstance(candidates, dict):
        candidates = {}

    ledger = raw.get("source_ledger", {})
    if not isinstance(ledger, dict):
        ledger = {}

    origins = raw.get("value_origin", {})
    if not isinstance(origins, dict):
        origins = {}

    sections = [
        "minimum_input_overrides",
        "reference_geometry",
        "comparison_values",
    ]

    ready_count = 0
    candidate_count = 0
    missing_requirements = []

    for section_key in sections:
        candidate_section = candidates.get(section_key, {})
        if not isinstance(candidate_section, dict):
            continue

        ledger_section = ledger.get(section_key, {})
        if not isinstance(ledger_section, dict):
            ledger_section = {}

        origin_section = origins.get(section_key, {})
        if not isinstance(origin_section, dict):
            origin_section = {}

        for field, value in candidate_section.items():
            if value in (None, ""):
                continue

            candidate_count += 1

            ledger_note = ledger_section.get(field)
            origin = origin_section.get(field)

            field_ref = f"{section_key}.{field}"

            if origin == "DO_NOT_USE":
                missing_requirements.append(f"{field_ref}: marked DO_NOT_USE")
                continue

            missing = []

            if ledger_note in (None, ""):
                missing.append("source_ledger")

            if origin not in ("DIRECT_SOURCE", "DERIVED_FROM_SOURCE", "ESTIMATE"):
                missing.append("value_origin")

            if missing:
                missing_requirements.append(f"{field_ref}: missing {', '.join(missing)}")
            else:
                ready_count += 1

    if candidate_count == 0:
        status = "NO_CANDIDATES"
        recommendation = "No candidate values exist for this engine."
    elif ready_count == candidate_count:
        status = "CANDIDATES_READY_FOR_PROMOTION"
        recommendation = "All candidate values have ledger notes and origin tags."
    elif ready_count > 0:
        status = "CANDIDATES_PARTIAL"
        recommendation = "Some candidate values are ready, but others need source ledger/origin tags."
    else:
        status = "CANDIDATES_NOT_READY"
        recommendation = "Candidate values exist but are missing source ledger/origin tags."

    return {
        "status": status,
        "ready_count": ready_count,
        "candidate_count": candidate_count,
        "missing_requirements": missing_requirements,
        "recommendation": recommendation,
    }

def build_candidate_promotion_readiness_report(name):
    readiness = evaluate_candidate_promotion_readiness(name)

    lines = []
    lines.append(f"Candidate Promotion Readiness — {name}")
    lines.append("=" * 64)
    lines.append("")
    lines.append(f"Status: {readiness.get('status')}")
    lines.append(f"Ready candidates: {readiness.get('ready_count')} / {readiness.get('candidate_count')}")
    lines.append(f"Recommendation: {readiness.get('recommendation')}")
    lines.append("")

    missing = readiness.get("missing_requirements", [])

    if missing:
        lines.append("Missing Requirements")
        lines.append("-" * 40)
        for item in missing:
            lines.append(f"- {item}")
    else:
        lines.append("Missing Requirements")
        lines.append("-" * 40)
        lines.append("None")

    return "\n".join(lines)

def build_candidate_promotion_patch(name):
    raw = get_raw_reference_engine(name)

    if not raw:
        return f"# Reference engine '{name}' was not found."

    readiness = evaluate_candidate_promotion_readiness(name)
    candidates = raw.get("candidate_reference_values", {})
    ledger = raw.get("source_ledger", {})
    origins = raw.get("value_origin", {})

    if not isinstance(candidates, dict):
        candidates = {}
    if not isinstance(ledger, dict):
        ledger = {}
    if not isinstance(origins, dict):
        origins = {}

    lines = []
    lines.append(f"# Candidate Promotion Patch — {name}")
    lines.append("# Paste these fields into the selected REFERENCE_ENGINES record only after review.")
    lines.append("# Only READY candidate values are included.")
    lines.append("")

    if readiness.get("status") not in ("CANDIDATES_READY_FOR_PROMOTION", "CANDIDATES_PARTIAL"):
        lines.append(f"# No promotable values. Status: {readiness.get('status')}")
        lines.append(f"# Recommendation: {readiness.get('recommendation')}")
        return "\n".join(lines)

    promoted_any = False

    for section_key in ["minimum_input_overrides", "reference_geometry", "comparison_values"]:
        candidate_section = candidates.get(section_key, {})
        ledger_section = ledger.get(section_key, {})
        origin_section = origins.get(section_key, {})

        if not isinstance(candidate_section, dict):
            continue
        if not isinstance(ledger_section, dict):
            ledger_section = {}
        if not isinstance(origin_section, dict):
            origin_section = {}

        ready_items = []

        for field, value in candidate_section.items():
            if value in (None, ""):
                continue

            ledger_note = ledger_section.get(field)
            origin = origin_section.get(field)

            if ledger_note in (None, ""):
                continue

            if origin not in ("DIRECT_SOURCE", "DERIVED_FROM_SOURCE", "ESTIMATE"):
                continue

            ready_items.append((field, value, ledger_note, origin))

        if not ready_items:
            continue

        promoted_any = True

        lines.append(f"# {section_key}")

        if section_key == "comparison_values":
            for field, value, ledger_note, origin in ready_items:
                lines.append(f'"{field}": {repr(value)},')
        else:
            lines.append(f'"{section_key}": {{')
            for field, value, ledger_note, origin in ready_items:
                lines.append(f'    "{field}": {repr(value)},')
            lines.append("},")

        lines.append("")
        lines.append(f'# source_ledger["{section_key}"]')
        lines.append(f'"source_ledger": {{')
        lines.append(f'    "{section_key}": {{')
        for field, value, ledger_note, origin in ready_items:
            lines.append(f'        "{field}": {repr(ledger_note)},')
        lines.append("    },")
        lines.append("},")
        lines.append("")
        lines.append(f'# value_origin["{section_key}"]')
        lines.append(f'"value_origin": {{')
        lines.append(f'    "{section_key}": {{')
        for field, value, ledger_note, origin in ready_items:
            lines.append(f'        "{field}": {repr(origin)},')
        lines.append("    },")
        lines.append("},")
        lines.append("")

    if not promoted_any:
        lines.append("# Candidate values exist, but none currently meet promotion requirements.")

    return "\n".join(lines)

def build_candidate_promotion_apply_preview(name):
    raw = get_raw_reference_engine(name)

    if not raw:
        return f"Reference engine '{name}' was not found."

    candidates = raw.get("candidate_reference_values", {})
    ledger = raw.get("source_ledger", {})
    origins = raw.get("value_origin", {})

    if not isinstance(candidates, dict):
        candidates = {}
    if not isinstance(ledger, dict):
        ledger = {}
    if not isinstance(origins, dict):
        origins = {}

    lines = []
    lines.append(f"Candidate Promotion Apply Preview — {name}")
    lines.append("=" * 64)
    lines.append("")
    lines.append("This preview does not modify the database.")
    lines.append("")

    for section_key in ["minimum_input_overrides", "reference_geometry", "comparison_values"]:
        candidate_section = candidates.get(section_key, {})
        ledger_section = ledger.get(section_key, {})
        origin_section = origins.get(section_key, {})

        if not isinstance(candidate_section, dict) or not candidate_section:
            continue

        if not isinstance(ledger_section, dict):
            ledger_section = {}
        if not isinstance(origin_section, dict):
            origin_section = {}

        lines.append(section_key)
        lines.append("-" * 40)

        for field, candidate_value in candidate_section.items():
            if section_key == "comparison_values":
                current_value = raw.get(field)
            else:
                current_section = raw.get(section_key, {})
                current_value = current_section.get(field) if isinstance(current_section, dict) else None

            ledger_note = ledger_section.get(field)
            origin = origin_section.get(field)

            has_current = current_value not in (None, "")
            has_candidate = candidate_value not in (None, "")
            ledger_ready = ledger_note not in (None, "")
            origin_ready = origin in ("DIRECT_SOURCE", "DERIVED_FROM_SOURCE", "ESTIMATE")
            blocked = origin == "DO_NOT_USE"

            if not has_candidate:
                status = "NO_CANDIDATE_VALUE"
            elif blocked:
                status = "BLOCKED_DO_NOT_USE"
            elif not ledger_ready or not origin_ready:
                status = "NOT_READY"
            elif has_current:
                status = "READY_OVERWRITE_REVIEW_REQUIRED"
            else:
                status = "READY_TO_APPLY"

            lines.append(f"{section_key}.{field}")
            lines.append(f"  current: {current_value}")
            lines.append(f"  candidate: {candidate_value}")
            lines.append(f"  ledger: {ledger_note}")
            lines.append(f"  origin: {origin}")
            lines.append(f"  status: {status}")
            lines.append("")

    return "\n".join(lines)

def evaluate_candidate_promotion_completeness_delta(name):
    raw = get_raw_reference_engine(name)

    if not raw:
        return {
            "status": "REFERENCE_ENGINE_NOT_FOUND",
            "before": {},
            "after": {},
            "improved_fields": [],
            "recommendation": "Reference engine was not found.",
        }

    before_validation = validate_reference_engine_record_data(raw)

    simulated = copy.deepcopy(raw)

    candidates = raw.get("candidate_reference_values", {})
    ledger = raw.get("source_ledger", {})
    origins = raw.get("value_origin", {})

    if not isinstance(candidates, dict):
        candidates = {}
    if not isinstance(ledger, dict):
        ledger = {}
    if not isinstance(origins, dict):
        origins = {}

    improved_fields = []

    for section_key in ["minimum_input_overrides", "reference_geometry", "comparison_values"]:
        candidate_section = candidates.get(section_key, {})
        ledger_section = ledger.get(section_key, {})
        origin_section = origins.get(section_key, {})

        if not isinstance(candidate_section, dict):
            continue
        if not isinstance(ledger_section, dict):
            ledger_section = {}
        if not isinstance(origin_section, dict):
            origin_section = {}

        for field, candidate_value in candidate_section.items():
            if candidate_value in (None, ""):
                continue

            ledger_note = ledger_section.get(field)
            origin = origin_section.get(field)

            if ledger_note in (None, ""):
                continue

            if origin not in ("DIRECT_SOURCE", "DERIVED_FROM_SOURCE", "ESTIMATE"):
                continue

            if section_key == "comparison_values":
                old_value = simulated.get(field)
                if old_value in (None, ""):
                    simulated[field] = candidate_value
                    improved_fields.append(f"{section_key}.{field}")
            else:
                section = simulated.get(section_key, {})
                if not isinstance(section, dict):
                    section = {}
                    simulated[section_key] = section

                old_value = section.get(field)
                if old_value in (None, ""):
                    section[field] = candidate_value
                    improved_fields.append(f"{section_key}.{field}")

    after_validation = validate_reference_engine_record_data(simulated)

    before = {
        "filled_inputs": before_validation.get("filled_input_count", 0),
        "filled_comparison": before_validation.get("filled_comparison_count", 0),
        "filled_sources": before_validation.get("filled_source_count", 0),
        "status": before_validation.get("status"),
        "input_status": before_validation.get("input_preset_status"),
        "comparison_status": before_validation.get("comparison_status"),
    }

    after = {
        "filled_inputs": after_validation.get("filled_input_count", 0),
        "filled_comparison": after_validation.get("filled_comparison_count", 0),
        "filled_sources": after_validation.get("filled_source_count", 0),
        "status": after_validation.get("status"),
        "input_status": after_validation.get("input_preset_status"),
        "comparison_status": after_validation.get("comparison_status"),
    }

    if not improved_fields:
        status = "NO_COMPLETENESS_GAIN"
        recommendation = "No ready candidate values would improve empty database fields."
    elif after["filled_inputs"] > before["filled_inputs"] or after["filled_comparison"] > before["filled_comparison"]:
        status = "COMPLETENESS_IMPROVES"
        recommendation = "Ready candidate values would improve the reference record."
    else:
        status = "MINOR_OR_METADATA_ONLY_GAIN"
        recommendation = "Promotion may improve traceability but not input/comparison completeness."

    return {
        "status": status,
        "before": before,
        "after": after,
        "improved_fields": improved_fields,
        "recommendation": recommendation,
    }

def build_candidate_promotion_completeness_delta_report(name):
    delta = evaluate_candidate_promotion_completeness_delta(name)

    lines = []
    lines.append(f"Candidate Promotion Completeness Delta — {name}")
    lines.append("=" * 64)
    lines.append("")
    lines.append(f"Status: {delta.get('status')}")
    lines.append(f"Recommendation: {delta.get('recommendation')}")
    lines.append("")

    before = delta.get("before", {})
    after = delta.get("after", {})

    lines.append("Before")
    lines.append("-" * 40)
    lines.append(f"Filled inputs: {before.get('filled_inputs')}")
    lines.append(f"Filled comparison: {before.get('filled_comparison')}")
    lines.append(f"Filled sources: {before.get('filled_sources')}")
    lines.append(f"Status: {before.get('status')}")
    lines.append(f"Input status: {before.get('input_status')}")
    lines.append(f"Comparison status: {before.get('comparison_status')}")
    lines.append("")

    lines.append("After hypothetical promotion")
    lines.append("-" * 40)
    lines.append(f"Filled inputs: {after.get('filled_inputs')}")
    lines.append(f"Filled comparison: {after.get('filled_comparison')}")
    lines.append(f"Filled sources: {after.get('filled_sources')}")
    lines.append(f"Status: {after.get('status')}")
    lines.append(f"Input status: {after.get('input_status')}")
    lines.append(f"Comparison status: {after.get('comparison_status')}")
    lines.append("")

    lines.append("Improved fields")
    lines.append("-" * 40)

    improved = delta.get("improved_fields", [])
    if improved:
        for field in improved:
            lines.append(f"- {field}")
    else:
        lines.append("None")

    return "\n".join(lines)

def evaluate_reference_rebuild_readiness(name):
    engine = get_reference_engine(name)

    if not engine:
        return {
            "status": "REFERENCE_ENGINE_NOT_FOUND",
            "mode": "REFERENCE_REBUILD_BLOCKED",
            "input_ready": False,
            "geometry_ready": False,
            "comparison_ready": False,
            "recommendation": "Reference engine was not found.",
        }

    validation = validate_reference_engine_record_data(engine)

    filled_inputs = validation.get("filled_input_count", 0)
    filled_comparison = validation.get("filled_comparison_count", 0)

    reference_geometry = engine.get("reference_geometry", {})
    if not isinstance(reference_geometry, dict):
        reference_geometry = {}

    geometry_fields = [
        "throat_area_m2",
        "exit_area_m2",
        "throat_radius_m",
        "exit_radius_m",
        "nozzle_length_m",
    ]

    filled_geometry = len([
        key for key in geometry_fields
        if reference_geometry.get(key) not in (None, "")
    ])

    input_ready = filled_inputs == len(REFERENCE_ENGINE_INPUT_FIELDS)
    geometry_ready = filled_geometry > 0
    comparison_ready = filled_comparison > 0

    if input_ready and geometry_ready and comparison_ready:
        status = "REFERENCE_REBUILD_READY"
        mode = "REFERENCE_REBUILD_READY"
        recommendation = "Reference engine has enough data for rebuild and comparison."
    elif filled_inputs > 0 or filled_geometry > 0 or filled_comparison > 0:
        status = "REFERENCE_REBUILD_PARTIAL"
        mode = "REFERENCE_REBUILD_PARTIAL"
        recommendation = "Some reference data exists, but rebuild validation is incomplete."
    else:
        status = "REFERENCE_LIBRARY_ONLY"
        mode = "REFERENCE_LIBRARY_ONLY"
        recommendation = "Reference can be viewed, but cannot yet rebuild/validate against LEAF."

    return {
        "status": status,
        "mode": mode,
        "input_ready": input_ready,
        "geometry_ready": geometry_ready,
        "comparison_ready": comparison_ready,
        "filled_inputs": filled_inputs,
        "filled_geometry": filled_geometry,
        "filled_comparison": filled_comparison,
        "recommendation": recommendation,
    }

def build_reference_rebuild_readiness_report(name):
    readiness = evaluate_reference_rebuild_readiness(name)

    lines = []
    lines.append(f"Reference Rebuild Readiness — {name}")
    lines.append("=" * 64)
    lines.append("")
    lines.append(f"Status: {readiness.get('status')}")
    lines.append(f"Mode: {readiness.get('mode')}")
    lines.append(f"Input ready: {readiness.get('input_ready')}")
    lines.append(f"Geometry ready: {readiness.get('geometry_ready')}")
    lines.append(f"Comparison ready: {readiness.get('comparison_ready')}")
    lines.append("")
    lines.append(f"Filled inputs: {readiness.get('filled_inputs')}")
    lines.append(f"Filled geometry fields: {readiness.get('filled_geometry')}")
    lines.append(f"Filled comparison fields: {readiness.get('filled_comparison')}")
    lines.append("")
    lines.append(f"Recommendation: {readiness.get('recommendation')}")

    return "\n".join(lines)

def build_reference_rebuild_input_export(name):
    engine = get_reference_engine(name)

    if not engine:
        return f"# Reference engine '{name}' was not found."

    overrides = engine.get("minimum_input_overrides", {})
    if not isinstance(overrides, dict):
        overrides = {}

    readiness = evaluate_reference_rebuild_readiness(name)

    lines = []
    lines.append(f"# Reference Rebuild Input Export — {name}")
    lines.append("# Paste/load these values into LEAF only after checking source status.")
    lines.append("# CEA-derived values are intentionally excluded.")
    lines.append("")
    lines.append(f"# Rebuild status: {readiness.get('status')}")
    lines.append(f"# Rebuild mode: {readiness.get('mode')}")
    lines.append("")

    lines.append("reference_rebuild_inputs = {")
    for field in REFERENCE_ENGINE_INPUT_FIELDS:
        value = overrides.get(field)
        lines.append(f'    "{field}": {repr(value)},')
    lines.append("}")

    lines.append("")
    lines.append("# Missing values:")
    for field in REFERENCE_ENGINE_INPUT_FIELDS:
        if overrides.get(field) in (None, ""):
            lines.append(f"# - {field}")

    return "\n".join(lines)

def build_reference_rebuild_input_load_preview(name, leaf_results):
    engine = get_reference_engine(name)

    if not engine:
        return f"Reference engine '{name}' was not found."

    overrides = engine.get("minimum_input_overrides", {})
    if not isinstance(overrides, dict):
        overrides = {}

    lines = []
    lines.append(f"Reference Rebuild Input Load Preview — {name}")
    lines.append("=" * 64)
    lines.append("")
    lines.append("This preview does not modify current LEAF inputs.")
    lines.append("")

    safe_count = 0
    overwrite_count = 0
    missing_count = 0

    for field in REFERENCE_ENGINE_INPUT_FIELDS:
        reference_value = overrides.get(field)
        current_value = leaf_results.get(field)

        reference_missing = reference_value in (None, "")
        current_filled = current_value not in (None, "")

        if reference_missing:
            status = "REFERENCE_VALUE_MISSING"
            missing_count += 1
        elif current_filled:
            if str(current_value) == str(reference_value):
                status = "SAME_VALUE"
            else:
                status = "OVERWRITE_REVIEW_REQUIRED"
                overwrite_count += 1
        else:
            status = "SAFE_TO_LOAD"
            safe_count += 1

        lines.append(field)
        lines.append("-" * 40)
        lines.append(f"Current LEAF value: {current_value}")
        lines.append(f"Reference value: {reference_value}")
        lines.append(f"Status: {status}")
        lines.append("")

    lines.append("Summary")
    lines.append("-" * 40)
    lines.append(f"Safe to load: {safe_count}")
    lines.append(f"Overwrite review required: {overwrite_count}")
    lines.append(f"Reference values missing: {missing_count}")

    return "\n".join(lines)

def build_reference_rebuild_session_record(name, leaf_results):
    """
    Builds a non-destructive reference rebuild session record.

    This does NOT:
    - modify LEAF inputs
    - promote candidate values
    - create validation PASS
    - run geometry comparison
    - run regen comparison
    - run thermal comparison
    """

    import datetime

    engine = get_reference_engine(name)

    if not engine:
        return {
            "session_status": "REFERENCE_ENGINE_NOT_FOUND",
            "reference_engine": name,
            "error": f"Reference engine '{name}' was not found.",
            "modifies_leaf_inputs": False,
            "candidate_values_used": False,
            "validation_run": False,
        }

    if not isinstance(leaf_results, dict):
        leaf_results = {}

    readiness = evaluate_reference_rebuild_readiness(name)
    input_preview = build_reference_rebuild_input_load_preview(name, leaf_results)

    session_id = (
        f"REF_REBUILD_{name}_"
        f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    warnings = []

    if readiness.get("mode") == "REFERENCE_LIBRARY_ONLY":
        warnings.append(
            "Reference engine is currently library-only and cannot fully rebuild LEAF."
        )

    if not readiness.get("input_ready"):
        warnings.append(
            "Reference minimum input overrides are incomplete."
        )

    if not readiness.get("geometry_ready"):
        warnings.append(
            "Reference geometry data is incomplete."
        )

    if not readiness.get("comparison_ready"):
        warnings.append(
            "Reference regen/comparison values are incomplete."
        )

    session_status = "SESSION_CREATED"

    if warnings:
        session_status = "SESSION_CREATED_WITH_WARNINGS"

    return {
        "session_id": session_id,
        "session_status": session_status,
        "reference_engine": name,
        "display_name": engine.get("display_name", name),
        "class": engine.get("class"),
        "fuel": engine.get("fuel"),
        "oxidizer": engine.get("oxidizer"),
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),

        "readiness_status": readiness.get("status"),
        "readiness_mode": readiness.get("mode"),
        "input_ready": readiness.get("input_ready"),
        "geometry_ready": readiness.get("geometry_ready"),
        "comparison_ready": readiness.get("comparison_ready"),
        "readiness_recommendation": readiness.get("recommendation"),

        "input_preview_text": input_preview,
        "warnings": warnings,

        "future_validation_slots": {
            "geometry_comparison": "NOT_RUN",
            "regen_comparison": "NOT_RUN",
            "thermal_comparison": "NOT_RUN",
            "material_comparison": "NOT_RUN",
            "coating_comparison": "NOT_RUN",
            "overall_confidence": "NOT_RUN",
        },

        "modifies_leaf_inputs": False,
        "candidate_values_used": False,
        "validation_run": False,
    }


def build_reference_rebuild_session_report(name, leaf_results):
    session = build_reference_rebuild_session_record(name, leaf_results)

    lines = []

    lines.append("Reference Rebuild Session Manager")
    lines.append("=" * 64)
    lines.append("")
    lines.append(f"Session ID: {session.get('session_id', 'N/A')}")
    lines.append(f"Session status: {session.get('session_status')}")
    lines.append(f"Reference engine: {session.get('reference_engine')}")
    lines.append(f"Display name: {session.get('display_name')}")
    lines.append(f"Class: {session.get('class')}")
    lines.append(f"Fuel: {session.get('fuel')}")
    lines.append(f"Oxidizer: {session.get('oxidizer')}")
    lines.append(f"Timestamp: {session.get('timestamp', 'N/A')}")
    lines.append("")

    lines.append("SAFETY RULES")
    lines.append("-" * 64)
    lines.append(f"Modifies LEAF inputs: {session.get('modifies_leaf_inputs')}")
    lines.append(f"Candidate values used: {session.get('candidate_values_used')}")
    lines.append(f"Validation run: {session.get('validation_run')}")
    lines.append("")

    lines.append("READINESS")
    lines.append("-" * 64)
    lines.append(f"Readiness status: {session.get('readiness_status')}")
    lines.append(f"Readiness mode: {session.get('readiness_mode')}")
    lines.append(f"Input ready: {session.get('input_ready')}")
    lines.append(f"Geometry ready: {session.get('geometry_ready')}")
    lines.append(f"Comparison ready: {session.get('comparison_ready')}")
    lines.append(f"Recommendation: {session.get('readiness_recommendation')}")
    lines.append("")

    lines.append("WARNINGS")
    lines.append("-" * 64)

    warnings = session.get("warnings", [])

    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("No session warnings.")

    lines.append("")

    lines.append("FUTURE VALIDATION SLOTS")
    lines.append("-" * 64)

    slots = session.get("future_validation_slots", {})

    for key, value in slots.items():
        lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("INPUT LOAD PREVIEW")
    lines.append("-" * 64)
    lines.append(session.get("input_preview_text", "No input preview available."))

    return "\n".join(lines)

def build_reference_rebuild_run_record(name, leaf_results):
    """
    Builds a non-destructive reference rebuild run record.

    This records the current rebuild attempt state.

    It does NOT:
    - modify LEAF inputs
    - promote candidate values
    - create validation PASS
    - run geometry comparison
    - run regen comparison
    - run thermal comparison
    """

    import datetime

    session = build_reference_rebuild_session_record(name, leaf_results)

    run_id = (
        f"REF_RUN_{name}_"
        f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    run_status = "RUN_RECORD_CREATED"

    warnings = list(session.get("warnings", []))

    if session.get("session_status") == "REFERENCE_ENGINE_NOT_FOUND":
        run_status = "RUN_RECORD_BLOCKED"
        warnings.append("Cannot create rebuild run because reference engine was not found.")

    elif session.get("readiness_mode") in (
        "REFERENCE_LIBRARY_ONLY",
        "REFERENCE_REBUILD_BLOCKED",
    ):
        run_status = "RUN_RECORD_CREATED_BLOCKED"

    elif warnings:
        run_status = "RUN_RECORD_CREATED_WITH_WARNINGS"

    return {
        "run_id": run_id,
        "run_status": run_status,
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),

        "session_id": session.get("session_id"),
        "session_status": session.get("session_status"),

        "reference_engine": session.get("reference_engine"),
        "display_name": session.get("display_name"),
        "class": session.get("class"),
        "fuel": session.get("fuel"),
        "oxidizer": session.get("oxidizer"),

        "readiness_status": session.get("readiness_status"),
        "readiness_mode": session.get("readiness_mode"),
        "input_ready": session.get("input_ready"),
        "geometry_ready": session.get("geometry_ready"),
        "comparison_ready": session.get("comparison_ready"),

        "warnings": warnings,

        "rebuild_attempt": {
            "inputs_loaded": False,
            "solver_ran": False,
            "solver_success": False,
            "solver_error": None,
        },

        "validation_results": {
            "geometry_comparison": "NOT_RUN",
            "regen_comparison": "NOT_RUN",
            "thermal_comparison": "NOT_RUN",
            "material_comparison": "NOT_RUN",
            "coating_comparison": "NOT_RUN",
            "confidence_score": "NOT_RUN",
        },

        "safety_flags": {
            "modifies_leaf_inputs": False,
            "candidate_values_used": False,
            "validation_pass_created": False,
            "placeholder_pass_allowed": False,
            "partial_source_pass_allowed": False,
        },

        "input_preview_text": session.get("input_preview_text"),
    }


def build_reference_rebuild_run_record_report(name, leaf_results):
    run = build_reference_rebuild_run_record(name, leaf_results)

    lines = []

    lines.append("Reference Rebuild Run Record")
    lines.append("=" * 64)
    lines.append("")
    lines.append(f"Run ID: {run.get('run_id')}")
    lines.append(f"Run status: {run.get('run_status')}")
    lines.append(f"Created at: {run.get('created_at')}")
    lines.append("")
    lines.append(f"Session ID: {run.get('session_id')}")
    lines.append(f"Session status: {run.get('session_status')}")
    lines.append("")
    lines.append(f"Reference engine: {run.get('reference_engine')}")
    lines.append(f"Display name: {run.get('display_name')}")
    lines.append(f"Class: {run.get('class')}")
    lines.append(f"Fuel: {run.get('fuel')}")
    lines.append(f"Oxidizer: {run.get('oxidizer')}")
    lines.append("")

    lines.append("READINESS SNAPSHOT")
    lines.append("-" * 64)
    lines.append(f"Readiness status: {run.get('readiness_status')}")
    lines.append(f"Readiness mode: {run.get('readiness_mode')}")
    lines.append(f"Input ready: {run.get('input_ready')}")
    lines.append(f"Geometry ready: {run.get('geometry_ready')}")
    lines.append(f"Comparison ready: {run.get('comparison_ready')}")
    lines.append("")

    lines.append("REBUILD ATTEMPT")
    lines.append("-" * 64)

    attempt = run.get("rebuild_attempt", {})

    lines.append(f"Inputs loaded: {attempt.get('inputs_loaded')}")
    lines.append(f"Solver ran: {attempt.get('solver_ran')}")
    lines.append(f"Solver success: {attempt.get('solver_success')}")
    lines.append(f"Solver error: {attempt.get('solver_error')}")
    lines.append("")

    lines.append("VALIDATION RESULTS")
    lines.append("-" * 64)

    for key, value in run.get("validation_results", {}).items():
        lines.append(f"{key}: {value}")

    lines.append("")

    lines.append("SAFETY FLAGS")
    lines.append("-" * 64)

    for key, value in run.get("safety_flags", {}).items():
        lines.append(f"{key}: {value}")

    lines.append("")

    lines.append("WARNINGS")
    lines.append("-" * 64)

    warnings = run.get("warnings", [])

    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("No warnings.")

    lines.append("")
    lines.append("INPUT PREVIEW")
    lines.append("-" * 64)
    lines.append(run.get("input_preview_text") or "No input preview available.")

    return "\n".join(lines)

def build_reference_rebuild_result_export(name, leaf_results):
    """
    Builds a complete non-destructive reference rebuild export package.

    This does NOT:
    - modify LEAF inputs
    - promote candidate values
    - create validation PASS
    - run geometry comparison
    - run regen comparison
    - run thermal comparison
    """

    lines = []

    lines.append("LEAF Reference Rebuild Result Export")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Reference engine: {name}")
    lines.append("")
    lines.append("SAFETY SUMMARY")
    lines.append("-" * 72)
    lines.append("Modifies LEAF inputs: False")
    lines.append("Candidate values used: False")
    lines.append("Validation PASS created: False")
    lines.append("Geometry comparison run: False")
    lines.append("Regen comparison run: False")
    lines.append("Thermal comparison run: False")
    lines.append("")

    lines.append("SECTION 1 — REBUILD READINESS REPORT")
    lines.append("=" * 72)
    lines.append(build_reference_rebuild_readiness_report(name))
    lines.append("")

    lines.append("SECTION 2 — REBUILD INPUT EXPORT")
    lines.append("=" * 72)
    lines.append(build_reference_rebuild_input_export(name))
    lines.append("")

    lines.append("SECTION 3 — REBUILD INPUT APPLY PLAN")
    lines.append("=" * 72)

    if "build_reference_rebuild_input_apply_plan" in globals():
        lines.append(build_reference_rebuild_input_apply_plan(name, leaf_results))
    else:
        lines.append(build_reference_rebuild_input_load_preview(name, leaf_results))

    lines.append("")

    lines.append("SECTION 4 — REBUILD SESSION REPORT")
    lines.append("=" * 72)
    lines.append(build_reference_rebuild_session_report(name, leaf_results))
    lines.append("")

    lines.append("SECTION 5 — REBUILD RUN RECORD")
    lines.append("=" * 72)
    lines.append(build_reference_rebuild_run_record_report(name, leaf_results))
    lines.append("")

    lines.append("END OF REFERENCE REBUILD RESULT EXPORT")
    lines.append("=" * 72)

    return "\n".join(lines)

def _safe_float(value):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


def _percent_error(leaf_value, reference_value):
    leaf_value = _safe_float(leaf_value)
    reference_value = _safe_float(reference_value)

    if leaf_value is None or reference_value is None:
        return None

    if reference_value == 0:
        return None

    return abs((leaf_value - reference_value) / reference_value) * 100.0


def evaluate_reference_geometry_comparison(name, leaf_results, tolerance_percent=10.0):
    """
    Compares LEAF-generated geometry against promoted reference geometry.

    This does NOT use candidate values.
    This does NOT create a final validation PASS.
    """

    engine = get_reference_engine(name)

    if not engine:
        return {
            "status": "REFERENCE_ENGINE_NOT_FOUND",
            "rows": [],
            "summary": {},
        }

    if not isinstance(leaf_results, dict):
        leaf_results = {}

    reference_geometry = engine.get("reference_geometry", {})
    if not isinstance(reference_geometry, dict):
        reference_geometry = {}

    comparison_map = [
        ("throat_radius", "throat_radius_m", "Throat radius", "m"),
        ("exit_radius", "exit_radius_m", "Exit radius", "m"),
        ("throat_area", "throat_area_m2", "Throat area", "m^2"),
        ("exit_area", "exit_area_m2", "Exit area", "m^2"),
        ("nozzle_length", "nozzle_length_m", "Nozzle length", "m"),
    ]

    rows = []

    compared_count = 0
    pass_count = 0
    warn_count = 0
    missing_count = 0

    for leaf_key, ref_key, label, unit in comparison_map:
        leaf_value = leaf_results.get(leaf_key)
        reference_value = reference_geometry.get(ref_key)

        error_percent = _percent_error(leaf_value, reference_value)

        if reference_value in (None, ""):
            status = "MISSING_REFERENCE_VALUE"
            missing_count += 1
        elif leaf_value in (None, ""):
            status = "MISSING_LEAF_VALUE"
            missing_count += 1
        elif error_percent is None:
            status = "COMPARISON_BLOCKED"
            missing_count += 1
        elif error_percent <= tolerance_percent:
            status = "GEOMETRY_MATCH"
            compared_count += 1
            pass_count += 1
        elif error_percent <= tolerance_percent * 2.0:
            status = "GEOMETRY_WARN"
            compared_count += 1
            warn_count += 1
        else:
            status = "GEOMETRY_MISMATCH"
            compared_count += 1

        rows.append({
            "label": label,
            "leaf_key": leaf_key,
            "reference_key": ref_key,
            "leaf_value": leaf_value,
            "reference_value": reference_value,
            "unit": unit,
            "error_percent": error_percent,
            "status": status,
        })

    leaf_throat_area = _safe_float(leaf_results.get("throat_area"))
    leaf_exit_area = _safe_float(leaf_results.get("exit_area"))

    ref_throat_area = _safe_float(reference_geometry.get("throat_area_m2"))
    ref_exit_area = _safe_float(reference_geometry.get("exit_area_m2"))

    leaf_expansion_ratio = None
    reference_expansion_ratio = None

    if leaf_throat_area and leaf_exit_area:
        leaf_expansion_ratio = leaf_exit_area / leaf_throat_area

    if ref_throat_area and ref_exit_area:
        reference_expansion_ratio = ref_exit_area / ref_throat_area

    expansion_error = _percent_error(
        leaf_expansion_ratio,
        reference_expansion_ratio,
    )

    if reference_expansion_ratio is None:
        expansion_status = "MISSING_REFERENCE_VALUE"
        missing_count += 1
    elif leaf_expansion_ratio is None:
        expansion_status = "MISSING_LEAF_VALUE"
        missing_count += 1
    elif expansion_error <= tolerance_percent:
        expansion_status = "GEOMETRY_MATCH"
        compared_count += 1
        pass_count += 1
    elif expansion_error <= tolerance_percent * 2.0:
        expansion_status = "GEOMETRY_WARN"
        compared_count += 1
        warn_count += 1
    else:
        expansion_status = "GEOMETRY_MISMATCH"
        compared_count += 1

    rows.append({
        "label": "Expansion ratio",
        "leaf_key": "exit_area / throat_area",
        "reference_key": "exit_area_m2 / throat_area_m2",
        "leaf_value": leaf_expansion_ratio,
        "reference_value": reference_expansion_ratio,
        "unit": "-",
        "error_percent": expansion_error,
        "status": expansion_status,
    })

    if compared_count == 0:
        overall_status = "GEOMETRY_COMPARISON_BLOCKED"
    elif pass_count == compared_count and missing_count == 0:
        overall_status = "GEOMETRY_ORDER_OF_MAGNITUDE_PASS"
    elif pass_count + warn_count == compared_count:
        overall_status = "GEOMETRY_PARTIAL_WARN"
    else:
        overall_status = "GEOMETRY_MISMATCH_REVIEW_REQUIRED"

    return {
        "status": overall_status,
        "rows": rows,
        "summary": {
            "compared_count": compared_count,
            "pass_count": pass_count,
            "warn_count": warn_count,
            "missing_count": missing_count,
            "tolerance_percent": tolerance_percent,
            "candidate_values_used": False,
            "validation_pass_created": False,
        },
    }


def build_reference_geometry_comparison_report(name, leaf_results, tolerance_percent=10.0):
    comparison = evaluate_reference_geometry_comparison(
        name,
        leaf_results,
        tolerance_percent=tolerance_percent,
    )

    lines = []

    lines.append(f"Reference Geometry Comparison — {name}")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Status: {comparison.get('status')}")
    lines.append("")
    lines.append("SAFETY RULES")
    lines.append("-" * 72)
    lines.append("Candidate values used: False")
    lines.append("Validation PASS created: False")
    lines.append("This is an order-of-magnitude geometry comparison only.")
    lines.append("")

    summary = comparison.get("summary", {})

    lines.append("SUMMARY")
    lines.append("-" * 72)
    lines.append(f"Compared fields: {summary.get('compared_count', 0)}")
    lines.append(f"Matched fields: {summary.get('pass_count', 0)}")
    lines.append(f"Warning fields: {summary.get('warn_count', 0)}")
    lines.append(f"Missing / blocked fields: {summary.get('missing_count', 0)}")
    lines.append(f"Tolerance: ±{summary.get('tolerance_percent', tolerance_percent)}%")
    lines.append("")

    lines.append("FIELD COMPARISON")
    lines.append("-" * 72)

    for row in comparison.get("rows", []):
        error = row.get("error_percent")

        if error is None:
            error_text = "N/A"
        else:
            error_text = f"{error:.3f}%"

        lines.append(row.get("label", "Unknown field"))
        lines.append(f"  LEAF key: {row.get('leaf_key')}")
        lines.append(f"  Reference key: {row.get('reference_key')}")
        lines.append(f"  LEAF value: {row.get('leaf_value')} {row.get('unit')}")
        lines.append(f"  Reference value: {row.get('reference_value')} {row.get('unit')}")
        lines.append(f"  Error: {error_text}")
        lines.append(f"  Status: {row.get('status')}")
        lines.append("")

    return "\n".join(lines)

def evaluate_reference_regen_geometry_comparison(name, leaf_results, tolerance_percent=20.0):
    """
    Compares LEAF regen geometry/cooling outputs against promoted reference values.

    This does NOT:
    - use candidate values
    - promote candidate values
    - create final validation PASS
    - run thermal validation
    """

    engine = get_reference_engine(name)

    if not engine:
        return {
            "status": "REFERENCE_ENGINE_NOT_FOUND",
            "rows": [],
            "summary": {},
        }

    if not isinstance(leaf_results, dict):
        leaf_results = {}

    comparison_map = [
        ("number_of_coolant_channels", "channel_count", "Channel count", "-"),
        ("coolant_channel_width", "channel_width_m", "Channel width", "m"),
        ("coolant_channel_height", "channel_height_m", "Channel height", "m"),
        ("hot_gas_wall_thickness", "wall_thickness_m", "Wall thickness", "m"),
        ("coolant_velocity", "coolant_velocity_m_s", "Coolant velocity", "m/s"),
        ("regen_pressure_drop", "pressure_drop_pa", "Pressure drop", "Pa"),
        ("coolant_temperature_rise", "coolant_temperature_rise_k", "Coolant temperature rise", "K"),
    ]

    fallback_leaf_keys = {
        "number_of_coolant_channels": [
            "recommended_channel_count",
            "recommended_number_of_coolant_channels",
        ],
        "coolant_channel_width": [
            "recommended_channel_width",
            "recommended_coolant_channel_width",
        ],
        "coolant_channel_height": [
            "recommended_channel_height",
            "recommended_coolant_channel_height",
        ],
        "hot_gas_wall_thickness": [
            "recommended_hot_gas_wall_thickness",
            "wall_thickness",
        ],
        "coolant_velocity": [
            "recommended_coolant_velocity",
            "coolant_velocity_m_s",
        ],
        "regen_pressure_drop": [
            "recommended_pressure_drop",
            "pressure_drop_pa",
            "coolant_pressure_drop",
        ],
        "coolant_temperature_rise": [
            "recommended_coolant_temperature_rise",
            "coolant_delta_t",
            "coolant_temperature_rise_k",
        ],
    }

    rows = []

    compared_count = 0
    pass_count = 0
    warn_count = 0
    missing_count = 0

    for leaf_key, reference_key, label, unit in comparison_map:
        leaf_value = leaf_results.get(leaf_key)

        if leaf_value in (None, ""):
            for fallback_key in fallback_leaf_keys.get(leaf_key, []):
                fallback_value = leaf_results.get(fallback_key)
                if fallback_value not in (None, ""):
                    leaf_value = fallback_value
                    break

        reference_value = engine.get(reference_key)

        error_percent = _percent_error(leaf_value, reference_value)

        if reference_value in (None, ""):
            status = "MISSING_REFERENCE_VALUE"
            missing_count += 1
        elif leaf_value in (None, ""):
            status = "MISSING_LEAF_VALUE"
            missing_count += 1
        elif error_percent is None:
            status = "COMPARISON_BLOCKED"
            missing_count += 1
        elif error_percent <= tolerance_percent:
            status = "REGEN_GEOMETRY_MATCH"
            compared_count += 1
            pass_count += 1
        elif error_percent <= tolerance_percent * 2.0:
            status = "REGEN_GEOMETRY_WARN"
            compared_count += 1
            warn_count += 1
        else:
            status = "REGEN_GEOMETRY_MISMATCH"
            compared_count += 1

        rows.append({
            "label": label,
            "leaf_key": leaf_key,
            "reference_key": reference_key,
            "leaf_value": leaf_value,
            "reference_value": reference_value,
            "unit": unit,
            "error_percent": error_percent,
            "status": status,
        })

    if compared_count == 0:
        overall_status = "REGEN_GEOMETRY_COMPARISON_BLOCKED"
    elif pass_count == compared_count and missing_count == 0:
        overall_status = "REGEN_GEOMETRY_ORDER_OF_MAGNITUDE_PASS"
    elif pass_count + warn_count == compared_count:
        overall_status = "REGEN_GEOMETRY_PARTIAL_WARN"
    else:
        overall_status = "REGEN_GEOMETRY_MISMATCH_REVIEW_REQUIRED"

    return {
        "status": overall_status,
        "rows": rows,
        "summary": {
            "compared_count": compared_count,
            "pass_count": pass_count,
            "warn_count": warn_count,
            "missing_count": missing_count,
            "tolerance_percent": tolerance_percent,
            "candidate_values_used": False,
            "validation_pass_created": False,
            "thermal_validation_run": False,
        },
    }


def build_reference_regen_geometry_comparison_report(name, leaf_results, tolerance_percent=20.0):
    comparison = evaluate_reference_regen_geometry_comparison(
        name,
        leaf_results,
        tolerance_percent=tolerance_percent,
    )

    lines = []

    lines.append(f"Reference Regen Geometry Comparison — {name}")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Status: {comparison.get('status')}")
    lines.append("")

    lines.append("SAFETY RULES")
    lines.append("-" * 72)
    lines.append("Candidate values used: False")
    lines.append("Validation PASS created: False")
    lines.append("Thermal validation run: False")
    lines.append("This is a regen geometry/cooling comparison only.")
    lines.append("")

    summary = comparison.get("summary", {})

    lines.append("SUMMARY")
    lines.append("-" * 72)
    lines.append(f"Compared fields: {summary.get('compared_count', 0)}")
    lines.append(f"Matched fields: {summary.get('pass_count', 0)}")
    lines.append(f"Warning fields: {summary.get('warn_count', 0)}")
    lines.append(f"Missing / blocked fields: {summary.get('missing_count', 0)}")
    lines.append(f"Tolerance: ±{summary.get('tolerance_percent', tolerance_percent)}%")
    lines.append("")

    lines.append("FIELD COMPARISON")
    lines.append("-" * 72)

    for row in comparison.get("rows", []):
        error = row.get("error_percent")
        error_text = "N/A" if error is None else f"{error:.3f}%"

        lines.append(row.get("label", "Unknown field"))
        lines.append(f"  LEAF key: {row.get('leaf_key')}")
        lines.append(f"  Reference key: {row.get('reference_key')}")
        lines.append(f"  LEAF value: {row.get('leaf_value')} {row.get('unit')}")
        lines.append(f"  Reference value: {row.get('reference_value')} {row.get('unit')}")
        lines.append(f"  Error: {error_text}")
        lines.append(f"  Status: {row.get('status')}")
        lines.append("")

    return "\n".join(lines)

def build_reference_rebuild_input_apply_plan(name, leaf_results):
    engine = get_reference_engine(name)

    if not engine:
        return f"Reference engine '{name}' was not found."

    if not isinstance(leaf_results, dict):
        leaf_results = {}

    overrides = engine.get("minimum_input_overrides", {})
    if not isinstance(overrides, dict):
        overrides = {}

    lines = []
    lines.append(f"Reference Rebuild Input Apply Plan — {name}")
    lines.append("=" * 64)
    lines.append("")
    lines.append("This plan is non-destructive.")
    lines.append("No LEAF inputs are modified.")
    lines.append("Candidate values are not used.")
    lines.append("CEA-derived values are intentionally excluded.")
    lines.append("")

    safe_count = 0
    same_count = 0
    overwrite_count = 0
    missing_count = 0

    future_apply_sequence = []

    lines.append("INPUT APPLY PLAN")
    lines.append("-" * 64)

    for field in REFERENCE_ENGINE_INPUT_FIELDS:
        reference_value = overrides.get(field)
        current_value = leaf_results.get(field)

        reference_missing = reference_value in (None, "")
        current_filled = current_value not in (None, "")

        if reference_missing:
            status = "MISSING_REFERENCE_VALUE"
            missing_count += 1
        elif current_filled and str(current_value) == str(reference_value):
            status = "SAME_VALUE"
            same_count += 1
            future_apply_sequence.append(field)
        elif current_filled:
            status = "OVERWRITE_REVIEW_REQUIRED"
            overwrite_count += 1
            future_apply_sequence.append(field)
        else:
            status = "SAFE_TO_LOAD"
            safe_count += 1
            future_apply_sequence.append(field)

        lines.append(f"{field}")
        lines.append(f"  Current LEAF value: {current_value}")
        lines.append(f"  Reference value: {reference_value}")
        lines.append(f"  Status: {status}")
        lines.append("")

    lines.append("SUMMARY")
    lines.append("-" * 64)
    lines.append(f"Safe to load: {safe_count}")
    lines.append(f"Same value: {same_count}")
    lines.append(f"Overwrite review required: {overwrite_count}")
    lines.append(f"Missing reference values: {missing_count}")
    lines.append(f"Can apply without overwrite review: {overwrite_count == 0}")
    lines.append("")

    lines.append("FUTURE APPLY SEQUENCE")
    lines.append("-" * 64)

    if future_apply_sequence:
        for index, field in enumerate(future_apply_sequence, start=1):
            lines.append(f"{index}. {field}")
    else:
        lines.append("No reference inputs are ready for future apply.")

    return "\n".join(lines)

def get_reference_engine_input_overrides(name):
    engine = get_reference_engine(name)

    if not engine:
        return {}

    overrides = engine.get("minimum_input_overrides", {})

    if not isinstance(overrides, dict):
        return {}

    clean = {}

    for key in REFERENCE_ENGINE_INPUT_FIELDS:
        value = overrides.get(key)

        if value not in (None, ""):
            clean[key] = value

    return clean

def build_reference_engine_source_template(name):
    engine = get_reference_engine(name)

    if not engine:
        return ""

    lines = []
    lines.append(f"# Reference Engine Source Template — {engine.get('display_name', name)}")
    lines.append("")
    lines.append("Minimum input fields for future input-window loading:")
    for field in REFERENCE_ENGINE_INPUT_FIELDS:
        lines.append(f"- {field}")
    lines.append("")
    lines.append("Do not manually source/load these CEA-derived fields:")
    for field in CEA_DERIVED_REFERENCE_FIELDS:
        lines.append(f"- {field}")
    lines.append("")
    lines.append("Required sourced fields:")
    lines.append("- channel_count")
    lines.append("- channel_width_m")
    lines.append("- channel_height_m")
    lines.append("- wall_thickness_m")
    lines.append("- coolant_velocity_m_s")
    lines.append("- pressure_drop_pa")
    lines.append("- coolant_temperature_rise_k")
    lines.append("")
    lines.append("Source metadata:")
    lines.append("- source_title")
    lines.append("- source_author")
    lines.append("- source_year")
    lines.append("- doi")
    lines.append("- url")
    lines.append("")
    lines.append("Python dictionary update template:")
    lines.append("")
    lines.append(f'"{name}": {{')
    lines.append(f'    "display_name": "{engine.get("display_name", name)}",')
    lines.append(f'    "class": "{engine.get("class", "")}",')
    lines.append(f'    "fuel": "{engine.get("fuel", "")}",')
    lines.append(f'    "oxidizer": "{engine.get("oxidizer", "")}",')
    lines.append('    "thrust_n": None,')
    lines.append("")
    lines.append('    "minimum_input_overrides": {')
    lines.append('        "fuel": None,')
    lines.append('        "oxidizer": None,')
    lines.append('        "mixture_ratio": None,')
    lines.append('        "mass_flow_rate": None,')
    lines.append('        "chamber_pressure": None,')
    lines.append('        "characteristic_length": None,')
    lines.append('        "ambient_pressure": None,')
    lines.append("    },")
    lines.append("")
    lines.append('    "reference_geometry": {')
    lines.append('        "throat_area_m2": None,')
    lines.append('        "exit_area_m2": None,')
    lines.append('        "throat_radius_m": None,')
    lines.append('        "exit_radius_m": None,')
    lines.append('        "nozzle_length_m": None,')
    lines.append("    },")
    lines.append('    "channel_count": None,')
    lines.append('    "channel_width_m": None,')
    lines.append('    "channel_height_m": None,')
    lines.append('    "wall_thickness_m": None,')
    lines.append('    "coolant_velocity_m_s": None,')
    lines.append('    "pressure_drop_pa": None,')
    lines.append('    "coolant_temperature_rise_k": None,')
    lines.append("")
    lines.append('    "source_status": "PLACEHOLDER_REQUIRED",')
    lines.append('    "source_title": "",')
    lines.append('    "source_author": "",')
    lines.append('    "source_year": None,')
    lines.append('    "doi": "",')
    lines.append('    "url": "",')
    lines.append('    "notes": "",')
    lines.append("},")
    lines.append('    "source_ledger": {')
    lines.append('        "minimum_input_overrides": {},')
    lines.append('        "reference_geometry": {},')
    lines.append('        "comparison_values": {},')
    lines.append("    },")
    lines.append('    "source_targets": {')
    lines.append('        "minimum_input_overrides": {},')
    lines.append('        "reference_geometry": {},')
    lines.append('        "comparison_values": {},')
    lines.append("    },")
    lines.append('    "value_origin": {')
    lines.append('        "minimum_input_overrides": {},')
    lines.append('        "reference_geometry": {},')
    lines.append('        "comparison_values": {},')
    lines.append("    },")
    lines.append('    "candidate_reference_values": {')
    lines.append('        "minimum_input_overrides": {},')
    lines.append('        "reference_geometry": {},')
    lines.append('        "comparison_values": {},')
    lines.append('        "notes": "Candidate values only. Do not use for PASS until promoted into validated fields with ledger/origin.",')
    lines.append("    },")
    lines.append("")

    return "\n".join(lines)

def build_reference_engine_input_summary(name):
    engine = get_reference_engine(name)

    if not engine:
        return "Reference engine not found."

    overrides = engine.get("minimum_input_overrides", {})

    lines = []
    lines.append(f"Reference Engine Input Preset — {engine.get('display_name', name)}")
    lines.append("=" * 56)
    lines.append("")
    lines.append("Allowed minimum input fields:")

    for key in REFERENCE_ENGINE_INPUT_FIELDS:
        lines.append(f"- {key}: {overrides.get(key, 'N/A')}")

    lines.append("")
    lines.append("Excluded CEA-derived fields:")

    for key in CEA_DERIVED_REFERENCE_FIELDS:
        lines.append(f"- {key}")

    lines.append("")
    lines.append("Note:")
    lines.append(
        "CEA-derived values should not be manually loaded from the reference preset. "
        "They should be calculated later by the CEA/property workflow."
    )

    return "\n".join(lines)

def validate_reference_engine_source_record(name):
    engine = get_reference_engine(name)

    if not engine:
        return {
            "status": "REFERENCE_ENGINE_NOT_FOUND",
            "missing_inputs": [],
            "missing_comparison_fields": [],
            "missing_source_fields": [],
            "filled_comparison_count": 0,
            "filled_source_count": 0,
            "recommendation": "Reference engine was not found in REFERENCE_ENGINES.",
        }

    overrides = engine.get("minimum_input_overrides", {})
    if not isinstance(overrides, dict):
        overrides = {}

    missing_inputs = [
        key for key in REFERENCE_ENGINE_INPUT_FIELDS
        if overrides.get(key) in (None, "")
    ]

    missing_comparison_fields = [
        key for key in REFERENCE_ENGINE_COMPARISON_FIELDS
        if engine.get(key) in (None, "")
    ]

    missing_source_fields = [
        key for key in REFERENCE_ENGINE_SOURCE_FIELDS
        if engine.get(key) in (None, "")
    ]

    filled_comparison_count = (
        len(REFERENCE_ENGINE_COMPARISON_FIELDS)
        - len(missing_comparison_fields)
    )

    filled_source_count = (
        len(REFERENCE_ENGINE_SOURCE_FIELDS)
        - len(missing_source_fields)
    )

    if filled_comparison_count == 0:
        status = "PLACEHOLDER_REQUIRED"
        recommendation = "Add sourced comparison geometry/cooling values before validation."

    elif missing_source_fields:
        status = "SOURCED_PARTIAL"
        recommendation = "Some comparison values exist, but source metadata is incomplete."

    elif missing_comparison_fields:
        status = "SOURCED_PARTIAL"
        recommendation = "Source metadata exists, but comparison fields are incomplete."

    else:
        status = "SOURCED_VALIDATION_READY"
        recommendation = "Reference record has comparison values and source metadata."

    return {
        "status": status,
        "missing_inputs": missing_inputs,
        "missing_comparison_fields": missing_comparison_fields,
        "missing_source_fields": missing_source_fields,
        "filled_comparison_count": filled_comparison_count,
        "filled_source_count": filled_source_count,
        "recommendation": recommendation,
    }

def parse_reference_engine_template_text(template_text):
    """
    Parses the Python dictionary block from an exported reference-engine template.

    This does not execute code.
    It only uses ast.literal_eval on the dictionary body.
    """

    if not template_text:
        return None, "EMPTY_TEMPLATE"

    text = str(template_text)

    start = text.find('"')
    if start < 0:
        return None, "NO_ENGINE_BLOCK_FOUND"

    colon = text.find(":", start)
    if colon < 0:
        return None, "NO_ENGINE_KEY_FOUND"

    engine_key = text[start:colon].strip().strip('"').strip("'")

    brace_start = text.find("{", colon)
    brace_end = text.rfind("},")

    if brace_end < 0:
        brace_end = text.rfind("}")

    if brace_start < 0 or brace_end < 0:
        return None, "NO_DICTIONARY_BODY_FOUND"

    dictionary_text = text[brace_start:brace_end + 1]

    try:
        data = ast.literal_eval(dictionary_text)
    except Exception as exc:
        return None, f"PARSE_FAILED: {exc}"

    if not isinstance(data, dict):
        return None, "PARSED_OBJECT_NOT_DICT"

    data["reference_engine_key"] = engine_key

    return data, "PARSE_OK"

def validate_reference_engine_record_data(data):
    if not isinstance(data, dict):
        return {
            "status": "INVALID_RECORD",
            "input_preset_status": "INVALID_RECORD",
            "comparison_status": "INVALID_RECORD",
            "missing_inputs": [],
            "missing_comparison_fields": [],
            "missing_source_fields": [],
            "filled_input_count": 0,
            "filled_comparison_count": 0,
            "filled_source_count": 0,
            "recommendation": "Parsed template did not contain a valid dictionary.",
        }

    overrides = data.get("minimum_input_overrides", {})
    if not isinstance(overrides, dict):
        overrides = {}

    missing_inputs = [
        key for key in REFERENCE_ENGINE_INPUT_FIELDS
        if overrides.get(key) in (None, "")
    ]

    missing_comparison_fields = [
        key for key in REFERENCE_ENGINE_COMPARISON_FIELDS
        if data.get(key) in (None, "")
    ]

    missing_source_fields = [
        key for key in REFERENCE_ENGINE_SOURCE_FIELDS
        if data.get(key) in (None, "")
    ]

    filled_input_count = len(REFERENCE_ENGINE_INPUT_FIELDS) - len(missing_inputs)
    filled_comparison_count = len(REFERENCE_ENGINE_COMPARISON_FIELDS) - len(missing_comparison_fields)
    filled_source_count = len(REFERENCE_ENGINE_SOURCE_FIELDS) - len(missing_source_fields)

    if filled_input_count == 0:
        input_preset_status = "INPUT_PRESET_EMPTY"
    elif missing_inputs:
        input_preset_status = "INPUT_PRESET_PARTIAL"
    else:
        input_preset_status = "INPUT_PRESET_READY"

    if filled_comparison_count == 0:
        comparison_status = "COMPARISON_DATA_EMPTY"
    elif missing_comparison_fields:
        comparison_status = "COMPARISON_DATA_PARTIAL"
    else:
        comparison_status = "COMPARISON_DATA_READY"

    if filled_comparison_count == 0:
        status = "PLACEHOLDER_REQUIRED"
        recommendation = "Template contains no sourced comparison values yet."
    elif missing_source_fields:
        status = "SOURCED_PARTIAL"
        recommendation = "Template has comparison values but missing source metadata."
    elif missing_comparison_fields:
        status = "SOURCED_PARTIAL"
        recommendation = "Template has source metadata but incomplete comparison fields."
    elif missing_inputs:
        status = "SOURCED_COMPARISON_READY_INPUTS_INCOMPLETE"
        recommendation = "Comparison data is ready, but minimum input preset fields are incomplete."
    else:
        status = "SOURCED_VALIDATION_READY"
        recommendation = "Template has comparison values, source metadata, and minimum input fields."

    return {
        "status": status,
        "input_preset_status": input_preset_status,
        "comparison_status": comparison_status,
        "missing_inputs": missing_inputs,
        "missing_comparison_fields": missing_comparison_fields,
        "missing_source_fields": missing_source_fields,
        "filled_input_count": filled_input_count,
        "filled_comparison_count": filled_comparison_count,
        "filled_source_count": filled_source_count,
        "recommendation": recommendation,
    }

def evaluate_reference_engine_readiness(data):
    validation = validate_reference_engine_record_data(data)

    input_status = validation.get("input_preset_status", "INVALID_RECORD")
    comparison_status = validation.get("comparison_status", "INVALID_RECORD")
    missing_source = validation.get("missing_source_fields", [])

    input_ready = input_status == "INPUT_PRESET_READY"
    comparison_ready = comparison_status == "COMPARISON_DATA_READY"
    source_ready = len(missing_source) == 0

    if input_ready and comparison_ready and source_ready:
        status = "REFERENCE_FULLY_READY"
        recommendation = "Reference engine can load inputs and support sourced comparison."
    elif comparison_ready and source_ready:
        status = "REFERENCE_COMPARISON_READY_INPUTS_INCOMPLETE"
        recommendation = "Comparison is ready, but minimum input preset is incomplete."
    elif input_ready and not comparison_ready:
        status = "REFERENCE_INPUT_READY_COMPARISON_INCOMPLETE"
        recommendation = "Input preset is ready, but comparison data is incomplete."
    elif comparison_status == "COMPARISON_DATA_PARTIAL":
        status = "REFERENCE_PARTIAL_COMPARISON"
        recommendation = "Some comparison values exist, but more sourced fields are required."
    else:
        status = "REFERENCE_PLACEHOLDER_ONLY"
        recommendation = "Add sourced inputs, comparison values, and metadata."

    return {
        "status": status,
        "input_ready": input_ready,
        "comparison_ready": comparison_ready,
        "source_ready": source_ready,
        "recommendation": recommendation,
        "validation": validation,
    }

def evaluate_reference_engine_database_record(name):
    engine = get_reference_engine(name)

    if not engine:
        return {
            "status": "REFERENCE_ENGINE_NOT_FOUND",
            "input_ready": False,
            "comparison_ready": False,
            "source_ready": False,
            "recommendation": "Reference engine key was not found.",
            "validation": {},
        }

    data = dict(engine)
    data["reference_engine_key"] = name

    return evaluate_reference_engine_readiness(data)

def evaluate_reference_source_ledger_coverage(data):
    if not isinstance(data, dict):
        return {
            "status": "INVALID_RECORD",
            "covered_count": 0,
            "filled_count": 0,
            "coverage_percent": 0.0,
            "missing_ledger_notes": [],
            "recommendation": "Invalid reference record.",
        }

    ledger = data.get("source_ledger", {})
    if not isinstance(ledger, dict):
        ledger = {}

    sections = [
        (
            "minimum_input_overrides",
            data.get("minimum_input_overrides", {}),
            REFERENCE_ENGINE_INPUT_FIELDS,
        ),
        (
            "reference_geometry",
            data.get("reference_geometry", {}),
            [
                "throat_area_m2",
                "exit_area_m2",
                "throat_radius_m",
                "exit_radius_m",
                "nozzle_length_m",
            ],
        ),
        (
            "comparison_values",
            data,
            REFERENCE_ENGINE_COMPARISON_FIELDS,
        ),
    ]

    filled_count = 0
    covered_count = 0
    missing_ledger_notes = []

    for ledger_section, value_source, fields in sections:
        if not isinstance(value_source, dict):
            value_source = {}

        ledger_values = ledger.get(ledger_section, {})
        if not isinstance(ledger_values, dict):
            ledger_values = {}

        for field in fields:
            value = value_source.get(field)

            if value in (None, ""):
                continue

            filled_count += 1

            note = ledger_values.get(field)

            if note not in (None, ""):
                covered_count += 1
            else:
                missing_ledger_notes.append(f"{ledger_section}.{field}")

    coverage_percent = 100.0 * covered_count / max(filled_count, 1)

    if filled_count == 0:
        status = "NO_FILLED_VALUES"
        recommendation = "No filled reference values require ledger notes yet."
    elif covered_count == filled_count:
        status = "LEDGER_COMPLETE"
        recommendation = "All filled reference values have source-ledger notes."
    elif coverage_percent >= 50.0:
        status = "LEDGER_PARTIAL"
        recommendation = "Some filled values are missing source-ledger notes."
    else:
        status = "LEDGER_INSUFFICIENT"
        recommendation = "Most filled values are missing value-level source notes."

    return {
        "status": status,
        "covered_count": covered_count,
        "filled_count": filled_count,
        "coverage_percent": round(coverage_percent, 2),
        "missing_ledger_notes": missing_ledger_notes,
        "recommendation": recommendation,
    }

def evaluate_reference_value_origin_coverage(data):
    if not isinstance(data, dict):
        return {
            "status": "INVALID_RECORD",
            "filled_count": 0,
            "origin_count": 0,
            "missing_origin_fields": [],
            "blocked_fields": [],
            "recommendation": "Invalid reference record.",
        }

    origins = data.get("value_origin", {})
    if not isinstance(origins, dict):
        origins = {}

    sections = [
        (
            "minimum_input_overrides",
            data.get("minimum_input_overrides", {}),
            REFERENCE_ENGINE_INPUT_FIELDS,
        ),
        (
            "reference_geometry",
            data.get("reference_geometry", {}),
            [
                "throat_area_m2",
                "exit_area_m2",
                "throat_radius_m",
                "exit_radius_m",
                "nozzle_length_m",
            ],
        ),
        (
            "comparison_values",
            data,
            REFERENCE_ENGINE_COMPARISON_FIELDS,
        ),
    ]

    filled_count = 0
    origin_count = 0
    missing_origin_fields = []
    blocked_fields = []

    valid_origins = {
        "DIRECT_SOURCE",
        "DERIVED_FROM_SOURCE",
        "ESTIMATE",
        "DO_NOT_USE",
    }

    for section_key, source_dict, fields in sections:
        if not isinstance(source_dict, dict):
            source_dict = {}

        origin_section = origins.get(section_key, {})
        if not isinstance(origin_section, dict):
            origin_section = {}

        for field in fields:
            value = source_dict.get(field)

            if value in (None, ""):
                continue

            filled_count += 1
            origin = origin_section.get(field)

            if origin in valid_origins:
                origin_count += 1

                if origin == "DO_NOT_USE":
                    blocked_fields.append(f"{section_key}.{field}")
            else:
                missing_origin_fields.append(f"{section_key}.{field}")

    if filled_count == 0:
        status = "NO_FILLED_VALUES"
        recommendation = "No filled values require origin tags yet."
    elif blocked_fields:
        status = "ORIGIN_BLOCKED"
        recommendation = "Some filled values are marked DO_NOT_USE."
    elif origin_count == filled_count:
        status = "ORIGIN_COMPLETE"
        recommendation = "All filled values have value-origin tags."
    else:
        status = "ORIGIN_INCOMPLETE"
        recommendation = "Some filled values are missing value-origin tags."

    return {
        "status": status,
        "filled_count": filled_count,
        "origin_count": origin_count,
        "missing_origin_fields": missing_origin_fields,
        "blocked_fields": blocked_fields,
        "recommendation": recommendation,
    }

def build_reference_value_entry_checklist(data):
    if not isinstance(data, dict):
        return []

    ledger = data.get("source_ledger", {})
    if not isinstance(ledger, dict):
        ledger = {}

    origins = data.get("value_origin", {})
    if not isinstance(origins, dict):
        origins = {}

    sections = [
        (
            "minimum_input_overrides",
            data.get("minimum_input_overrides", {}),
            REFERENCE_ENGINE_INPUT_FIELDS,
        ),
        (
            "reference_geometry",
            data.get("reference_geometry", {}),
            [
                "throat_area_m2",
                "exit_area_m2",
                "throat_radius_m",
                "exit_radius_m",
                "nozzle_length_m",
            ],
        ),
        (
            "comparison_values",
            data,
            REFERENCE_ENGINE_COMPARISON_FIELDS,
        ),
    ]

    rows = []

    for section_key, source_dict, fields in sections:
        if not isinstance(source_dict, dict):
            source_dict = {}

        ledger_section = ledger.get(section_key, {})
        if not isinstance(ledger_section, dict):
            ledger_section = {}

        origin_section = origins.get(section_key, {})
        if not isinstance(origin_section, dict):
            origin_section = {}

        for field in fields:
            value = source_dict.get(field)
            ledger_note = ledger_section.get(field)
            origin = origin_section.get(field)

            value_filled = value not in (None, "")
            ledger_ready = ledger_note not in (None, "")
            origin_ready = origin in (
                "DIRECT_SOURCE",
                "DERIVED_FROM_SOURCE",
                "ESTIMATE",
                "DO_NOT_USE",
            )
            blocked = origin == "DO_NOT_USE"

            ready = value_filled and ledger_ready and origin_ready and not blocked

            if not value_filled:
                status = "EMPTY"
                action = "Add sourced value or leave as None."
            elif blocked:
                status = "BLOCKED_DO_NOT_USE"
                action = "Remove/replace this value before validation."
            elif not ledger_ready and not origin_ready:
                status = "MISSING_LEDGER_AND_ORIGIN"
                action = "Add source_ledger note and value_origin tag."
            elif not ledger_ready:
                status = "MISSING_LEDGER"
                action = "Add value-level source ledger note."
            elif not origin_ready:
                status = "MISSING_ORIGIN"
                action = "Add DIRECT_SOURCE, DERIVED_FROM_SOURCE, ESTIMATE, or DO_NOT_USE."
            else:
                status = "READY"
                action = "Value is traceable."

            rows.append({
                "section": section_key,
                "field": field,
                "value": value,
                "ledger_note": ledger_note,
                "origin": origin,
                "ready": ready,
                "status": status,
                "action": action,
            })

    return rows

def evaluate_reference_data_quality(data):
    if not isinstance(data, dict):
        return {
            "band": "PLACEHOLDER",
            "score": 0,
            "status": "INVALID_RECORD",
            "recommendation": "Invalid reference record.",
        }

    validation = validate_reference_engine_record_data(data)
    ledger = evaluate_reference_source_ledger_coverage(data)

    filled_inputs = validation.get("filled_input_count", 0)
    filled_comparison = validation.get("filled_comparison_count", 0)
    filled_sources = validation.get("filled_source_count", 0)
    ledger_status = ledger.get("status", "NO_FILLED_VALUES")
    ledger_coverage = ledger.get("coverage_percent", 0.0)

    score = 0

    score += min(20, filled_inputs * 3)
    score += min(35, filled_comparison * 5)
    score += min(20, filled_sources * 4)

    if ledger_status == "LEDGER_COMPLETE":
        score += 25
    elif ledger_coverage >= 50:
        score += 10

    score = max(0, min(100, int(score)))

    if score == 0:
        band = "PLACEHOLDER"
        status = "QUALITY_PLACEHOLDER"
        recommendation = "Add sourced values before using this reference record."
    elif score < 35:
        band = "LOW_CONFIDENCE_PUBLIC"
        status = "QUALITY_LOW"
        recommendation = "Record has limited data. Use only for rough context."
    elif score < 65:
        band = "PARTIAL_ENGINEERING_SOURCE"
        status = "QUALITY_PARTIAL"
        recommendation = "Record may support preliminary comparison, but is incomplete."
    elif score < 90:
        band = "SOURCED_ENGINEERING_REFERENCE"
        status = "QUALITY_ENGINEERING"
        recommendation = "Record is suitable for order-of-magnitude validation."
    else:
        band = "HIGH_CONFIDENCE_BENCHMARK"
        status = "QUALITY_HIGH"
        recommendation = "Record is strong enough for benchmark-style comparison."

    return {
        "band": band,
        "score": score,
        "status": status,
        "recommendation": recommendation,
    }

def normalise_reference_engine_record(data):
    if not isinstance(data, dict):
        return {}

    normalised = copy.deepcopy(data)

    validation = validate_reference_engine_record_data(normalised)
    quality = evaluate_reference_data_quality(normalised)
    ledger = evaluate_reference_source_ledger_coverage(normalised)

    normalised["source_status"] = validation.get("status", "PLACEHOLDER_REQUIRED")
    normalised["data_quality_band"] = quality.get("band", "PLACEHOLDER")
    normalised["data_quality_score"] = quality.get("score", 0)
    normalised["data_quality_notes"] = quality.get("recommendation", "")

    normalised["ledger_status"] = ledger.get("status", "NO_FILLED_VALUES")
    normalised["ledger_coverage_percent"] = ledger.get("coverage_percent", 0.0)

    return normalised

def evaluate_reference_status_consistency(data):
    if not isinstance(data, dict):
        return {
            "status": "INVALID_RECORD",
            "mismatch_count": 0,
            "mismatches": [],
            "recommendation": "Invalid reference record.",
        }

    stored_source_status = data.get("source_status")
    stored_quality_band = data.get("data_quality_band")
    stored_quality_score = data.get("data_quality_score")

    derived = normalise_reference_engine_record(data)

    derived_source_status = derived.get("source_status")
    derived_quality_band = derived.get("data_quality_band")
    derived_quality_score = derived.get("data_quality_score")

    mismatches = []

    if stored_source_status not in (None, "") and stored_source_status != derived_source_status:
        mismatches.append(
            f"source_status stored={stored_source_status} derived={derived_source_status}"
        )

    if stored_quality_band not in (None, "") and stored_quality_band != derived_quality_band:
        mismatches.append(
            f"data_quality_band stored={stored_quality_band} derived={derived_quality_band}"
        )

    if stored_quality_score not in (None, ""):
        try:
            if int(stored_quality_score) != int(derived_quality_score):
                mismatches.append(
                    f"data_quality_score stored={stored_quality_score} derived={derived_quality_score}"
                )
        except Exception:
            mismatches.append(
                f"data_quality_score stored={stored_quality_score} derived={derived_quality_score}"
            )

    if mismatches:
        status = "STATUS_MISMATCH"
        recommendation = "Update raw database status fields or rely on auto-derived status."
    else:
        status = "STATUS_CONSISTENT"
        recommendation = "Stored raw status fields match derived record state."

    return {
        "status": status,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "recommendation": recommendation,
        "stored_source_status": stored_source_status,
        "stored_quality_band": stored_quality_band,
        "stored_quality_score": stored_quality_score,
        "derived_source_status": derived_source_status,
        "derived_quality_band": derived_quality_band,
        "derived_quality_score": derived_quality_score,
    }

def evaluate_reference_database_status_consistency(name):
    raw = get_raw_reference_engine(name)

    if not raw:
        return {
            "status": "REFERENCE_ENGINE_NOT_FOUND",
            "mismatch_count": 0,
            "mismatches": [],
            "recommendation": "Reference engine was not found.",
        }

    return evaluate_reference_status_consistency(raw)

def build_reference_engine_database_patch(data):
    if not isinstance(data, dict):
        return ""

    key = data.get("reference_engine_key")
    if not key:
        return ""

    validation = validate_reference_engine_record_data(data)
    corrected_status = validation.get("status", "PLACEHOLDER_REQUIRED")

    patched_data = dict(data)
    patched_data["source_status"] = corrected_status
    patched_data.pop("reference_engine_key", None)

    ordered_keys = [
        "display_name",
        "class",
        "fuel",
        "oxidizer",
        "thrust_n",

        "minimum_input_overrides",
        "reference_geometry",

        "channel_count",
        "channel_width_m",
        "channel_height_m",
        "wall_thickness_m",
        "coolant_velocity_m_s",
        "pressure_drop_pa",
        "coolant_temperature_rise_k",

        "source_status",
        "data_quality_band",
        "data_quality_score",
        "data_quality_notes",

        "source_title",
        "source_author",
        "source_year",
        "doi",
        "url",
        "notes",

        "source_ledger",
        "source_targets",
        "value_origin",
        "candidate_reference_values",
    ]

    def render_value(value, indent=8):
        space = " " * indent

        if isinstance(value, str):
            return f'"{value}"'

        if value is None:
            return "None"

        if isinstance(value, bool):
            return "True" if value else "False"

        if isinstance(value, (int, float)):
            return repr(value)

        if isinstance(value, dict):
            lines = ["{"]
            for sub_key, sub_value in value.items():
                lines.append(
                    f'{space}    "{sub_key}": {render_value(sub_value, indent + 4)},'
                )
            lines.append(f"{space}}}")
            return "\n".join(lines)

        return repr(value)

    lines = []
    lines.append(f'    "{key}": {{')

    for field in ordered_keys:
        if field not in patched_data:
            continue

        value_text = render_value(patched_data.get(field), indent=8)
        lines.append(f'        "{field}": {value_text},')

    lines.append("    },")
    return "\n".join(lines)