from dataclasses import dataclass
from collections import OrderedDict

from leaf_data import (
    LABEL_TO_VAR as LEGACY_LABEL_TO_VAR,
    SYMBOLS as LEGACY_SYMBOLS,
    UNITS as LEGACY_UNITS,
    SECTIONS as LEGACY_SECTIONS,
    HIDDEN_INPUT_VARS as LEGACY_HIDDEN_INPUT_VARS,
    UNIT_GROUPS as LEGACY_UNIT_GROUPS,
    UNIT_PREFERENCES as LEGACY_UNIT_PREFERENCES,
)


@dataclass(frozen=True)
class VariableDefinition:
    key: str
    label: str
    symbol: str = ""
    unit: str = ""
    section: str = "General"
    unit_group: str = ""
    is_input: bool = False
    input_role: str = ""
    input_owner: str = ""
    is_output: bool = True
    is_graphable: bool = True
    output_visibility: str = "SCALAR_OUTPUT"
    report_owner: str = "MAIN_OUTPUT"
    validation_owner: str = ""
    diagnostic_owner: str = ""
    recommendation_owner: str = ""
    tooltip: str = ""


OUTPUT_ONLY_KEYS = {
    'active_bond_coat',
    'active_bond_coat_family',
    'active_bond_coat_is_placeholder',
    'active_bond_coat_max_practical_thickness',
    'active_bond_coat_max_stress_reduction_fraction',
    'active_bond_coat_reason',
    'active_bond_coat_source_mode',
    'active_bond_coat_source_quality',
    'active_bond_coat_source_score',
    'active_bond_coat_status',
    'active_coating_family',
    'active_coating_is_placeholder',
    'active_coating_material',
    'active_coating_max_practical_thickness',
    'active_coating_max_surface_temperature',
    'active_coating_reason',
    'active_coating_role',
    'active_coating_source_mode',
    'active_coating_source_quality',
    'active_coating_source_score',
    'active_coating_stack_pass',
    'active_coating_stack_reason',
    'active_coating_stack_status',
    'active_coating_status',
    'active_coating_thermal_conductivity',
    'available_bond_coats',
    'available_coating_materials',
    'before_after_comparison_attachment_message',
    'before_after_comparison_attachment_status',
    'before_after_comparison_count',
    'before_after_comparison_rows',
    'before_after_comparison_status',
    'before_after_comparison_text',
    'benchmark_comparison_count',
    'benchmark_evaluation',
    'benchmark_evaluation_attachment_message',
    'benchmark_evaluation_attachment_status',
    'benchmark_failed_count',
    'benchmark_major_failed_count',
    'benchmark_minor_failed_count',
    'benchmark_missing_count',
    'benchmark_report_text',
    'benchmark_selected_case',
    'benchmark_status',
    'best_full_engine_regen_below_target_reynolds_count',
    'best_full_engine_regen_design',
    'best_full_engine_regen_failed_fit_count',
    'best_full_engine_regen_failed_reynolds_count',
    'best_full_engine_regen_failed_thermal_count',
    'best_full_engine_regen_failed_velocity_count',
    'best_full_engine_regen_max_hot_wall_temperature',
    'best_full_engine_regen_max_pressure_drop',
    'best_full_engine_regen_max_velocity',
    'best_full_engine_regen_min_reynolds',
    'best_full_engine_regen_missing_data_count',
    'best_full_engine_regen_pass',
    'best_full_engine_regen_reason',
    'best_full_engine_regen_score',
    'best_full_engine_regen_status',
    'best_full_engine_regen_thermal_margin',
    'bond_coat_candidate_count',
    'bond_coat_placeholder_count',
    'coating_candidate_count',
    'coating_database_readiness',
    'coating_database_reason',
    'coating_database_status',
    'coating_placeholder_count',
    'coating_stack_source_data_gate',
    'coating_stack_source_data_gate_reason',
    'coating_stack_source_data_report_visibility',
    'coating_stack_source_data_severity',
    'coating_stack_source_data_status_line',
    'coating_stack_source_data_weighted_gate',
    'conical_half_angle_deg',
    'density',
    'design_history_count',
    'design_history_iteration_number',
    'design_history_latest_summary',
    'design_history_text',
    'design_iteration_attempt_count',
    'design_iteration_narrative',
    'design_iteration_narrative_attachment_message',
    'design_iteration_narrative_attachment_status',
    'design_iteration_narrative_status',
    'design_iteration_narrative_text',
    'dynamic_viscosity',
    'engine_reproduction_attachment_message',
    'engine_reproduction_attachment_status',
    'engine_reproduction_case',
    'engine_reproduction_confidence',
    'engine_reproduction_reasons',
    'engine_reproduction_report_text',
    'engine_reproduction_score',
    'engine_reproduction_status',
    'explicit_coating_base_hot_wall_temperature',
    'explicit_coating_density',
    'explicit_coating_family',
    'explicit_coating_is_placeholder',
    'explicit_coating_liner_hot_wall_temperature',
    'explicit_coating_liner_limit',
    'explicit_coating_liner_margin',
    'explicit_coating_mass_total',
    'explicit_coating_material',
    'explicit_coating_max_practical_thickness',
    'explicit_coating_physical_sanity_reason',
    'explicit_coating_physical_sanity_status',
    'explicit_coating_preview_pass',
    'explicit_coating_preview_reason',
    'explicit_coating_preview_status',
    'explicit_coating_raw_liner_hot_wall_temperature',
    'explicit_coating_role',
    'explicit_coating_source_mode',
    'explicit_coating_source_quality',
    'explicit_coating_surface_area_total',
    'explicit_coating_surface_limit',
    'explicit_coating_surface_margin',
    'explicit_coating_surface_temperature',
    'explicit_coating_temperature_drop',
    'explicit_coating_thermal_conductivity',
    'explicit_coating_thermal_resistance',
    'explicit_coating_thickness',
    'explicit_coating_thickness_margin',
    'failure_root_cause_attachment_message',
    'failure_root_cause_attachment_status',
    'failure_root_cause_categories',
    'failure_root_cause_count',
    'failure_root_cause_items',
    'failure_root_cause_status',
    'failure_root_cause_summary',
    'failure_root_cause_text',
    'foundation_attachment_audit',
    'foundation_attachment_benchmark_case',
    'foundation_attachment_pipeline_completed',
    'foundation_attachment_pipeline_completed_at',
    'foundation_attachment_pipeline_started',
    'foundation_attachment_pipeline_started_at',
    'foundation_attachment_pipeline_status',
    'foundation_attachment_summary',
    'foundation_regression_attachment_message',
    'foundation_regression_attachment_status',
    'foundation_regression_failed_count',
    'foundation_regression_passed_count',
    'foundation_regression_status',
    'foundation_regression_tests',
    'foundation_regression_text',
    'foundation_result_key_audit_attachment_error_type',
    'foundation_result_key_audit_attachment_message',
    'foundation_result_key_audit_attachment_status',
    'foundation_result_key_audit_attachment_traceback',
    'foundation_result_key_audit_known_development_count',
    'foundation_result_key_audit_known_development_keys',
    'foundation_result_key_audit_possible_pollution',
    'foundation_result_key_audit_registered_count',
    'foundation_result_key_audit_status',
    'foundation_result_key_audit_text',
    'foundation_result_key_audit_unregistered_count',
    'foundation_result_key_audit_visibility_counts',
    'foundation_result_key_audit_wrong_visibility',
    'full_engine_regen_below_target_reynolds_count',
    'full_engine_regen_failed_fit_count',
    'full_engine_regen_failed_reynolds_count',
    'full_engine_regen_failed_thermal_count',
    'full_engine_regen_failed_velocity_count',
    'full_engine_regen_geometry_pass',
    'full_engine_regen_geometry_station_count',
    'full_engine_regen_geometry_status',
    'full_engine_regen_max_hot_wall_temperature',
    'full_engine_regen_max_pressure_drop',
    'full_engine_regen_max_velocity',
    'full_engine_regen_min_reynolds',
    'full_engine_regen_minimum_turbulent_reynolds',
    'full_engine_regen_missing_data_count',
    'full_engine_regen_pressure_drop_pass',
    'full_engine_regen_target_reynolds',
    'live_startup_health_used_after_load',
    'loaded_project_startup_health_snapshot',
    'loaded_project_startup_health_snapshot_preserved',
    'mach_number',
    'material_aware_combined_base_hot_wall_temperature',
    'material_aware_combined_best_film_effectiveness',
    'material_aware_combined_best_heat_load_reduction',
    'material_aware_combined_best_material',
    'material_aware_combined_best_material_limit',
    'material_aware_combined_best_material_source_quality',
    'material_aware_combined_best_regen_improvement_factor',
    'material_aware_combined_candidate_count',
    'material_aware_combined_failed_station_count',
    'material_aware_combined_max_hot_wall_temperature',
    'material_aware_combined_pass',
    'material_aware_combined_passing_count',
    'material_aware_combined_predicted_hot_wall_temperature',
    'material_aware_combined_reason',
    'material_aware_combined_score',
    'material_aware_combined_source_mode',
    'material_aware_combined_source_validation_ready',
    'material_aware_combined_station_count',
    'material_aware_combined_status',
    'material_aware_combined_thermal_margin',
    'material_aware_combined_worst_margin',
    'nozzle_geometry_model',
    'nozzle_geometry_smoothness_status',
    'output_ownership_audit_status',
    'output_ownership_audit_text',
    'output_ownership_non_scalar_registered_key_count',
    'output_ownership_scalar_key_count',
    'output_ownership_suspected_pollution_keys',
    'output_ownership_unregistered_key_count',
    'output_ownership_unregistered_keys',
    'prandtl',
    'pressure',
    'rao_length_fraction',
    'recommendation_explanation_attachment_message',
    'recommendation_explanation_attachment_status',
    'recommendation_explanation_count',
    'recommendation_explanation_items',
    'recommendation_explanation_status',
    'recommendation_explanation_text',
    'recommended_bond_coat',
    'recommended_bond_coat_is_placeholder',
    'recommended_bond_coat_source_mode',
    'recommended_bond_coat_source_quality',
    'recommended_bond_coat_thickness',
    'recommended_channel_count',
    'recommended_channel_fit_ratio',
    'recommended_channel_height',
    'recommended_channel_pitch',
    'recommended_channel_width',
    'recommended_circumferential_cooling_coverage',
    'recommended_coating_is_placeholder',
    'recommended_coating_material',
    'recommended_coating_source_mode',
    'recommended_coating_source_quality',
    'recommended_coating_stack_pass',
    'recommended_coating_stack_reason',
    'recommended_coating_stack_status',
    'recommended_coating_thickness',
    'recommended_coolant_velocity',
    'recommended_design_package',
    'recommended_design_package_key_count',
    'recommended_design_package_keys',
    'recommended_design_package_status',
    'recommended_effective_rib_width',
    'recommended_geometry_status',
    'recommended_reynolds_number',
    'recommended_rib_width',
    'recommended_tightest_gas_radius',
    'regen_optimisation_coating_preview_physical',
    'regen_optimisation_coating_sanity_note',
    'regen_optimisation_manual_geometry_valid',
    'regen_optimisation_pressure_drop_pass',
    'regen_optimisation_proof_attachment_message',
    'regen_optimisation_proof_attachment_status',
    'regen_optimisation_proof_failure_type',
    'regen_optimisation_proof_lines',
    'regen_optimisation_proof_next_step',
    'regen_optimisation_proof_reason',
    'regen_optimisation_proof_status',
    'regen_optimisation_proof_text',
    'regen_optimisation_recommended_geometry_valid',
    'report_dashboard_attachment_message',
    'report_dashboard_attachment_status',
    'report_dashboard_items',
    'report_dashboard_status',
    'report_dashboard_text',
    'specific_impulse',
    'startup_health_optional_warning_count',
    'startup_health_required_failure_count',
    'startup_health_rows',
    'startup_health_status',
    'startup_health_text',
    'temperature',
    'thermal_conductivity',
    'thrust',
}

OUTPUT_VISIBILITY_SCALAR = "SCALAR_OUTPUT"
OUTPUT_VISIBILITY_AXIAL_REPORT = "AXIAL_REPORT_ONLY"
OUTPUT_VISIBILITY_VALIDATION = "VALIDATION_ONLY"
OUTPUT_VISIBILITY_DIAGNOSTIC = "DIAGNOSTIC_ONLY"
OUTPUT_VISIBILITY_RECOMMENDATION = "RECOMMENDATION_ONLY"
OUTPUT_VISIBILITY_INTERNAL = "INTERNAL_ONLY"


VALIDATION_KEY_SUFFIXES = (
    "_status",
    "_pass",
    "_valid",
    "_gate",
    "_severity",
)

DIAGNOSTIC_KEY_SUFFIXES = (
    "_reason",
    "_note",
    "_message",
    "_text",
    "_rows",
    "_items",
    "_summary",
    "_audit",
    "_traceback",
    "_error_type",
)

RECOMMENDATION_KEY_PREFIXES = (
    "recommended_",
    "best_full_engine_",
)

AXIAL_REPORT_KEY_PREFIXES = (
    "regen_axial_",
    "full_engine_regen_",
)

INTERNAL_KEY_PREFIXES = (
    "volume_debug_",
)

INTERNAL_KEY_SUFFIXES = (
    "_raw",
    "_debug",
)


def classify_output_visibility(key, label="", section=""):
    key_l = str(key).lower()
    label_l = str(label).lower()
    section_l = str(section).lower()

    # CANONICAL_MAIN_OUTPUT_NONSCALAR_EXCEPTIONS
    # Evidence/status values remain in the complete result
    # payload but do not belong to the primary Main Outputs.
    if key_l in {
        "available_coating_materials",
        "coating_stack_source_data_report_visibility",
        "thermo_r_error",
        "thermo_r_error_percent",
    }:
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l in {
        "coating_stack_source_data_status_line",
    }:
        return OUTPUT_VISIBILITY_VALIDATION


    if key_l.startswith(INTERNAL_KEY_PREFIXES) or key_l.endswith(INTERNAL_KEY_SUFFIXES):
        return OUTPUT_VISIBILITY_INTERNAL

    if key_l.startswith("design_iteration_"):
        return OUTPUT_VISIBILITY_AXIAL_REPORT

    if key_l.startswith("regen_optimisation_proof_"):
        return OUTPUT_VISIBILITY_AXIAL_REPORT

    if key_l.startswith("failure_root_cause_"):
        return OUTPUT_VISIBILITY_AXIAL_REPORT

    if key_l.startswith(AXIAL_REPORT_KEY_PREFIXES):
        return OUTPUT_VISIBILITY_AXIAL_REPORT

    if key_l.startswith(RECOMMENDATION_KEY_PREFIXES):
        return OUTPUT_VISIBILITY_RECOMMENDATION

    if key_l.startswith("stage_v"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("regen_scalability_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("stage_w"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("real_engine_benchmark_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("foundation_verification_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l == "foundation_layer_verified":
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("foundation_save_load_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("foundation_ui_launch_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("foundation_final_signoff_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("foundation_completion_handover_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.endswith(VALIDATION_KEY_SUFFIXES):
        return OUTPUT_VISIBILITY_VALIDATION

    if key_l.endswith(DIAGNOSTIC_KEY_SUFFIXES):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("recommendation_explanation_"):
        return OUTPUT_VISIBILITY_RECOMMENDATION

    if key_l.startswith("recommendation_owner_"):
        return OUTPUT_VISIBILITY_RECOMMENDATION

    if key_l.startswith("before_after_comparison_"):
        return OUTPUT_VISIBILITY_AXIAL_REPORT

    if key_l.startswith("report_dashboard_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("foundation_regression_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if "diagnostic" in section_l or "diagnostic" in label_l:
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if "validation" in section_l or "validation" in label_l:
        return OUTPUT_VISIBILITY_VALIDATION

    if "recommend" in section_l or "recommend" in label_l:
        return OUTPUT_VISIBILITY_RECOMMENDATION

    if key_l.startswith("benchmark_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("engine_reproduction_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("startup_health_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("regen_source_validation_"):
        return OUTPUT_VISIBILITY_VALIDATION

    if key_l.startswith("regen_provenance_"):
        return OUTPUT_VISIBILITY_VALIDATION

    if key_l.startswith("regen_conservative_validation_gate_"):
        return OUTPUT_VISIBILITY_VALIDATION

    if key_l.startswith("regen_property_table_owner_"):
        return OUTPUT_VISIBILITY_VALIDATION

    if key_l.startswith("regen_validation_master_gate_"):
        return OUTPUT_VISIBILITY_VALIDATION

    if key_l.startswith("regen_completion_audit_"):
        return OUTPUT_VISIBILITY_VALIDATION

    if key_l.startswith("stage_u_regen_validation_complete"):
        return OUTPUT_VISIBILITY_VALIDATION

    if key_l.startswith("foundation_result_key_audit_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("foundation_attachment_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.endswith("_attachment_status"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.endswith("_attachment_message"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.endswith("_attachment_error_type"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.endswith("_attachment_traceback"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("output_visibility_architecture_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("output_ownership_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("loaded_project_startup_health_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("live_startup_health_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("design_history_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("recommendation_ownership_final_audit_"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    if key_l.startswith("stage_t_recommendation_ownership_complete"):
        return OUTPUT_VISIBILITY_DIAGNOSTIC

    return OUTPUT_VISIBILITY_SCALAR


def classify_report_owner(output_visibility):
    if output_visibility == OUTPUT_VISIBILITY_AXIAL_REPORT:
        return "AXIAL_THERMAL_REPORT"

    if output_visibility == OUTPUT_VISIBILITY_VALIDATION:
        return "VALIDATION_REPORT"

    if output_visibility == OUTPUT_VISIBILITY_DIAGNOSTIC:
        return "DIAGNOSTICS_PANEL"

    if output_visibility == OUTPUT_VISIBILITY_RECOMMENDATION:
        return "RECOMMENDED_DESIGN_PANEL"

    if output_visibility == OUTPUT_VISIBILITY_INTERNAL:
        return "INTERNAL"

    return "MAIN_OUTPUT"

def _build_label_to_section():
    label_to_section = {}

    for section_name, labels in LEGACY_SECTIONS.items():
        for label in labels:
            label_to_section[label] = section_name

    return label_to_section


def _is_graphable(label, key, unit):
    non_graphable_keywords = [
        "Name",
        "Valid",
        "Mode",
        "Status",
        "Pass",
        "Used",
        "Note",
        "Reason",
    ]

    if any(word in label for word in non_graphable_keywords):
        return False

    if key.endswith("_status"):
        return False

    if key.endswith("_pass"):
        return False

    if key.endswith("_reason"):
        return False

    if unit == "-":
        return False

    return True



INPUT_CLASSIFICATION = {
    'ambient_pressure': ('DESIGN_CHOICE', 'MANUAL'),
    'chamber_pressure': ('DESIGN_CHOICE', 'MANUAL'),
    'coolant_inlet_pressure': ('DESIGN_CHOICE', 'MANUAL'),
    'chamber_contraction_ratio': ('DESIGN_CHOICE', 'MANUAL'),
    'chamber_converging_half_angle_deg': ('DESIGN_CHOICE', 'MANUAL'),
    'characteristic_length': ('DESIGN_CHOICE', 'MANUAL'),
    'mass_flow_rate': ('DESIGN_CHOICE', 'MANUAL'),
    'mixture_ratio': ('DESIGN_CHOICE', 'CEA'),
    'coating_thickness': ('ADVANCED_OVERRIDE', 'MANUAL'),
    'coolant_side_wall_temperature': ('ADVANCED_OVERRIDE', 'REGEN'),
    'corrosion_allowance': ('ADVANCED_OVERRIDE', 'MANUAL'),
    'minimum_wall_thickness': ('ADVANCED_OVERRIDE', 'MANUAL'),
    'selected_length': ('ADVANCED_OVERRIDE', 'GEOMETRY'),
    'selected_station_length': ('ADVANCED_OVERRIDE', 'REGEN'),
    'wall_joint_efficiency': ('ADVANCED_OVERRIDE', 'MANUAL'),
    'wall_safety_factor': ('ADVANCED_OVERRIDE', 'MANUAL'),
    'coolant_channel_height': ('ADVANCED_OVERRIDE', 'REGEN'),
    'coolant_channel_width': ('ADVANCED_OVERRIDE', 'REGEN'),
    'coolant_flow_fraction': ('ADVANCED_OVERRIDE', 'REGEN'),
    'hot_gas_wall_thickness': ('ADVANCED_OVERRIDE', 'REGEN'),
    'number_of_coolant_channels': ('ADVANCED_OVERRIDE', 'REGEN'),
    'outer_jacket_thickness': ('ADVANCED_OVERRIDE', 'REGEN'),
    'rib_width': ('ADVANCED_OVERRIDE', 'REGEN'),
    'expansion_ratio': ('DESIGN_CHOICE', 'MANUAL'),
}


def build_variable_registry():
    label_to_section = _build_label_to_section()
    registry = OrderedDict()

    explicit_input_keys = {
        "mass_flow_rate",
        "mixture_ratio",
        "chamber_pressure",
        "chamber_contraction_ratio",
        "chamber_converging_half_angle_deg",
        "characteristic_length",
        "selected_length",
        "ambient_pressure",
        "coolant_inlet_pressure",

        "hot_gas_wall_thickness",
        "minimum_wall_thickness",
        "corrosion_allowance",
        "coating_thickness",
        "wall_safety_factor",
        "wall_joint_efficiency",
        "coolant_side_wall_temperature",

        "coolant_channel_height",
        "coolant_channel_width",
        "rib_width",
        "outer_jacket_thickness",
        "number_of_coolant_channels",
        "selected_station_length",
        "coolant_flow_fraction",
    }

    for label, key in LEGACY_LABEL_TO_VAR.items():
        symbol = LEGACY_SYMBOLS.get(key, "")
        unit = LEGACY_UNITS.get(key, "")
        section = label_to_section.get(label, "General")
        unit_group = LEGACY_UNIT_GROUPS.get(key, "")

        is_hidden_input = (
            key in LEGACY_HIDDEN_INPUT_VARS
            or key in OUTPUT_ONLY_KEYS
        )

        output_visibility = classify_output_visibility(
            key=key,
            label=label,
            section=section,
        )

        report_owner = classify_report_owner(output_visibility)

        is_output = (
                label in label_to_section
                and output_visibility == OUTPUT_VISIBILITY_SCALAR
        )

        is_input = key in explicit_input_keys and not is_hidden_input
        input_role, input_owner = INPUT_CLASSIFICATION.get(key, ("", ""))
        is_graphable = (
                _is_graphable(label, key, unit)
                and output_visibility == OUTPUT_VISIBILITY_SCALAR
        )

        registry[key] = VariableDefinition(
            key=key,
            label=label,
            symbol=symbol,
            unit=unit,
            section=section,
            unit_group=unit_group,
            is_input=is_input,
            input_role=input_role,
            input_owner=input_owner,
            is_output=is_output,
            is_graphable=is_graphable,
            output_visibility=output_visibility,
            report_owner=report_owner,
            validation_owner="VALIDATION_REPORT" if output_visibility == OUTPUT_VISIBILITY_VALIDATION else "",
            diagnostic_owner="DIAGNOSTICS_PANEL" if output_visibility == OUTPUT_VISIBILITY_DIAGNOSTIC else "",
            recommendation_owner="RECOMMENDED_DESIGN_PANEL" if output_visibility == OUTPUT_VISIBILITY_RECOMMENDATION else "",
        )

    return registry

def add_foundation_registry_entries(registry):
    entries = [
        VariableDefinition(
            key="foundation_attachment_pipeline_status",
            label="Foundation Attachment Pipeline Status",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="foundation_attachment_summary",
            label="Foundation Attachment Summary",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="foundation_attachment_audit",
            label="Foundation Attachment Audit",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="foundation_attachment_benchmark_case",
            label="Foundation Attachment Benchmark Case",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="foundation_attachment_pipeline_started_at",
            label="Foundation Attachment Pipeline Started At",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="foundation_attachment_pipeline_completed_at",
            label="Foundation Attachment Pipeline Completed At",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),

        VariableDefinition(
            key="recommendation_owner_items",
            label="Recommendation Owner Items",
            section="Recommendation Ownership",
            output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
            report_owner="RECOMMENDATION_OWNER",
            recommendation_owner="RECOMMENDATION_OWNER",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_owner_count",
            label="Recommendation Owner Count",
            section="Recommendation Ownership",
            output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
            report_owner="RECOMMENDATION_OWNER",
            recommendation_owner="RECOMMENDATION_OWNER",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_owner_status",
            label="Recommendation Owner Status",
            section="Recommendation Ownership",
            output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
            report_owner="RECOMMENDATION_OWNER",
            recommendation_owner="RECOMMENDATION_OWNER",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_owner_text",
            label="Recommendation Owner Report",
            section="Recommendation Ownership",
            output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
            report_owner="RECOMMENDATION_OWNER",
            recommendation_owner="RECOMMENDATION_OWNER",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_owner_primary_recommendation",
            label="Primary Recommendation",
            section="Recommendation Ownership",
            output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
            report_owner="RECOMMENDATION_OWNER",
            recommendation_owner="RECOMMENDATION_OWNER",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_owner_primary_reason",
            label="Primary Recommendation Reason",
            section="Recommendation Ownership",
            output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
            report_owner="RECOMMENDATION_OWNER",
            recommendation_owner="RECOMMENDATION_OWNER",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_owner_primary_priority_score",
            label="Primary Recommendation Priority Score",
            section="Recommendation Ownership",
            output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
            report_owner="RECOMMENDATION_OWNER",
            recommendation_owner="RECOMMENDATION_OWNER",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="output_visibility_architecture_status",
            label="Output Visibility Architecture Status",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="output_visibility_architecture_visibility_counts",
            label="Output Visibility Architecture Visibility Counts",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="output_visibility_architecture_scalar_pollution",
            label="Output Visibility Architecture Scalar Pollution",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="output_visibility_architecture_unregistered_keys",
            label="Output Visibility Architecture Unregistered Keys",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="output_visibility_architecture_invalid_visibility_keys",
            label="Output Visibility Architecture Invalid Visibility Keys",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="output_visibility_architecture_non_scalar_registered_count",
            label="Output Visibility Architecture Non-Scalar Registered Count",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="output_visibility_architecture_text",
            label="Output Visibility Architecture Report",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_owner_rejected_items",
            label="Recommendation Owner Rejected Items",
            section="Recommendation Ownership",
            output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
            report_owner="RECOMMENDATION_OWNER",
            recommendation_owner="RECOMMENDATION_OWNER",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_owner_rejected_count",
            label="Recommendation Owner Rejected Count",
            section="Recommendation Ownership",
            output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
            report_owner="RECOMMENDATION_OWNER",
            recommendation_owner="RECOMMENDATION_OWNER",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_owner_evidence_status",
            label="Recommendation Owner Evidence Status",
            section="Recommendation Ownership",
            output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
            report_owner="RECOMMENDATION_OWNER",
            recommendation_owner="RECOMMENDATION_OWNER",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_owner_primary_source",
            label="Primary Recommendation Source",
            section="Recommendation Ownership",
            output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
            report_owner="RECOMMENDATION_OWNER",
            recommendation_owner="RECOMMENDATION_OWNER",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_ownership_final_audit_status",
            label="Recommendation Ownership Final Audit Status",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_ownership_final_audit_missing_required_keys",
            label="Recommendation Ownership Missing Required Keys",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_ownership_final_audit_missing_stage_t4_keys",
            label="Recommendation Ownership Missing Stage T4 Keys",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_ownership_final_audit_failed_checks",
            label="Recommendation Ownership Failed Checks",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_ownership_final_audit_warnings",
            label="Recommendation Ownership Warnings",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_ownership_final_audit_item_count",
            label="Recommendation Ownership Final Audit Item Count",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="recommendation_ownership_final_audit_text",
            label="Recommendation Ownership Final Audit Report",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="stage_t_recommendation_ownership_complete",
            label="Stage T Recommendation Ownership Complete",
            section="Foundation Diagnostics",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="DIAGNOSTICS_PANEL",
            diagnostic_owner="FOUNDATION_STATUS_PANEL",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_source_validation_gate_status",
            label="Regen Source Validation Gate Status",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_source_validation_pass_allowed",
            label="Regen Source Validation Pass Allowed",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_source_validation_material_mode",
            label="Material Source Validation Mode",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_source_validation_coating_mode",
            label="Coating Source Validation Mode",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_source_validation_material_score",
            label="Material Source Validation Score",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_source_validation_coating_score",
            label="Coating Source Validation Score",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_source_validation_blocking_reasons",
            label="Regen Source Validation Blocking Reasons",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_source_validation_warning_reasons",
            label="Regen Source Validation Warning Reasons",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_source_validation_text",
            label="Regen Source Validation Report",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_conservative_validation_gate_status",
            label="Regen Conservative Validation Gate Status",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_conservative_validation_gate_reason",
            label="Regen Conservative Validation Gate Reason",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_provenance_report_status",
            label="Regen Provenance Report Status",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_provenance_report_text",
            label="Regen Provenance Report",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_provenance_material_name",
            label="Regen Provenance Material Name",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_provenance_coating_name",
            label="Regen Provenance Coating Name",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_provenance_material_mode",
            label="Regen Provenance Material Mode",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_provenance_coating_mode",
            label="Regen Provenance Coating Mode",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_provenance_material_score",
            label="Regen Provenance Material Score",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_provenance_coating_score",
            label="Regen Provenance Coating Score",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_property_table_owner_status",
            label="Regen Property Table Owner Status",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_property_table_owner_wall_temperature",
            label="Regen Property Table Wall Temperature",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_property_table_owner_blocking_reasons",
            label="Regen Property Table Blocking Reasons",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_property_table_owner_warning_reasons",
            label="Regen Property Table Warning Reasons",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_property_table_owner_text",
            label="Regen Property Table Ownership Report",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_property_table_owner_pass_allowed",
            label="Regen Property Table Pass Allowed",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_validation_master_gate_status",
            label="Regen Validation Master Gate Status",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_validation_master_gate_pass_allowed",
            label="Regen Validation Master Gate Pass Allowed",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_validation_master_gate_blocking_reasons",
            label="Regen Validation Master Gate Blocking Reasons",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_validation_master_gate_warning_reasons",
            label="Regen Validation Master Gate Warning Reasons",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_validation_master_gate_text",
            label="Regen Validation Master Gate Report",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_completion_audit_status",
            label="Regen Completion Audit Status",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_completion_audit_complete",
            label="Regen Completion Audit Complete",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_completion_audit_missing_keys",
            label="Regen Completion Missing Keys",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_completion_audit_failures",
            label="Regen Completion Failures",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_completion_audit_warnings",
            label="Regen Completion Warnings",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="regen_completion_audit_text",
            label="Regen Completion Audit Report",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="stage_u_regen_validation_complete",
            label="Stage U Regen Validation Complete",
            section="Regen Validation",
            output_visibility=OUTPUT_VISIBILITY_VALIDATION,
            report_owner="VALIDATION_REPORT",
            validation_owner="REGEN_VALIDATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="foundation_verification_status",
            label="Foundation Verification Status",
            section="Foundation Verification",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="FOUNDATION_VERIFICATION",
            diagnostic_owner="FOUNDATION_VERIFICATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="foundation_verification_passed_count",
            label="Foundation Verification Passed Count",
            section="Foundation Verification",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="FOUNDATION_VERIFICATION",
            diagnostic_owner="FOUNDATION_VERIFICATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="foundation_verification_failed_count",
            label="Foundation Verification Failed Count",
            section="Foundation Verification",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="FOUNDATION_VERIFICATION",
            diagnostic_owner="FOUNDATION_VERIFICATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="foundation_verification_tests",
            label="Foundation Verification Tests",
            section="Foundation Verification",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="FOUNDATION_VERIFICATION",
            diagnostic_owner="FOUNDATION_VERIFICATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="foundation_verification_text",
            label="Foundation Verification Report",
            section="Foundation Verification",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="FOUNDATION_VERIFICATION",
            diagnostic_owner="FOUNDATION_VERIFICATION",
            is_output=False,
            is_graphable=False,
        ),
        VariableDefinition(
            key="foundation_layer_verified",
            label="Foundation Layer Verified",
            section="Foundation Verification",
            output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
            report_owner="FOUNDATION_VERIFICATION",
            diagnostic_owner="FOUNDATION_VERIFICATION",
            is_output=False,
            is_graphable=False,
        ),
    ]

    prefix_registry_entries = [
        ("design_iteration_attempt_count", "Design Iteration Attempt Count", "Design History", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("design_iteration_narrative", "Design Iteration Narrative", "Design History", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("design_iteration_narrative_status", "Design Iteration Narrative Status", "Design History", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("design_iteration_narrative_text", "Design Iteration Narrative Text", "Design History", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),

        ("regen_optimisation_proof_failure_type", "Regen Optimisation Proof Failure Type", "Optimisation Proof", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("regen_optimisation_proof_lines", "Regen Optimisation Proof Lines", "Optimisation Proof", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("regen_optimisation_proof_next_step", "Regen Optimisation Proof Next Step", "Optimisation Proof", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("regen_optimisation_proof_text", "Regen Optimisation Proof Text", "Optimisation Proof", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),

        ("failure_root_cause_categories", "Failure Root Cause Categories", "Failure Ownership", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("failure_root_cause_count", "Failure Root Cause Count", "Failure Ownership", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("failure_root_cause_items", "Failure Root Cause Items", "Failure Ownership", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("failure_root_cause_status", "Failure Root Cause Status", "Failure Ownership", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("failure_root_cause_summary", "Failure Root Cause Summary", "Failure Ownership", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("failure_root_cause_text", "Failure Root Cause Text", "Failure Ownership", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),

        ("before_after_comparison_count", "Before/After Comparison Count", "Design Comparison", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("before_after_comparison_rows", "Before/After Comparison Rows", "Design Comparison", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("before_after_comparison_status", "Before/After Comparison Status", "Design Comparison", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),
        ("before_after_comparison_text", "Before/After Comparison Text", "Design Comparison", OUTPUT_VISIBILITY_AXIAL_REPORT, "AXIAL_REPORT"),

        ("recommendation_explanation_count", "Recommendation Explanation Count", "Recommendation Ownership", OUTPUT_VISIBILITY_RECOMMENDATION, "RECOMMENDATION_OWNER"),
        ("recommendation_explanation_items", "Recommendation Explanation Items", "Recommendation Ownership", OUTPUT_VISIBILITY_RECOMMENDATION, "RECOMMENDATION_OWNER"),
        ("recommendation_explanation_status", "Recommendation Explanation Status", "Recommendation Ownership", OUTPUT_VISIBILITY_RECOMMENDATION, "RECOMMENDATION_OWNER"),
        ("recommendation_explanation_text", "Recommendation Explanation Text", "Recommendation Ownership", OUTPUT_VISIBILITY_RECOMMENDATION, "RECOMMENDATION_OWNER"),

        ("report_dashboard_items", "Report Dashboard Items", "Foundation Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("report_dashboard_status", "Report Dashboard Status", "Foundation Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("report_dashboard_text", "Report Dashboard Text", "Foundation Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),

        ("foundation_regression_failed_count", "Foundation Regression Failed Count", "Foundation Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("foundation_regression_passed_count", "Foundation Regression Passed Count", "Foundation Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("foundation_regression_status", "Foundation Regression Status", "Foundation Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("foundation_regression_tests", "Foundation Regression Tests", "Foundation Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("foundation_regression_text", "Foundation Regression Text", "Foundation Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),

        ("benchmark_evaluation", "Benchmark Evaluation", "Benchmark Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("benchmark_reference_engine", "Benchmark Reference Engine", "Benchmark Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("benchmark_report_text", "Benchmark Report Text", "Benchmark Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("benchmark_selected_case", "Benchmark Selected Case", "Benchmark Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("benchmark_status", "Benchmark Status", "Benchmark Diagnostics", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),

        ("engine_reproduction_case", "Engine Reproduction Case", "Engine Reproduction", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("engine_reproduction_confidence", "Engine Reproduction Confidence", "Engine Reproduction", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("engine_reproduction_reasons", "Engine Reproduction Reasons", "Engine Reproduction", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("engine_reproduction_report_text", "Engine Reproduction Report Text", "Engine Reproduction", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("engine_reproduction_score", "Engine Reproduction Score", "Engine Reproduction", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),
        ("engine_reproduction_status", "Engine Reproduction Status", "Engine Reproduction", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),

        ("startup_health_attached_to_results", "Startup Health Attached To Results", "Startup Health", OUTPUT_VISIBILITY_DIAGNOSTIC, "DIAGNOSTICS_PANEL"),

        ("regen_property_table_owner_coating_required", "Regen Property Table Coating Required", "Regen Validation", OUTPUT_VISIBILITY_VALIDATION, "VALIDATION_REPORT"),
    ]

    for key, label, section, visibility, owner in prefix_registry_entries:
        entries.append(
            VariableDefinition(
                key=key,
                label=label,
                section=section,
                output_visibility=visibility,
                report_owner=owner,
                validation_owner="REGEN_VALIDATION" if visibility == OUTPUT_VISIBILITY_VALIDATION else "",
                diagnostic_owner="FOUNDATION_STATUS_PANEL" if visibility == OUTPUT_VISIBILITY_DIAGNOSTIC else "",
                recommendation_owner="RECOMMENDATION_OWNER" if visibility == OUTPUT_VISIBILITY_RECOMMENDATION else "",
                is_output=False,
                is_graphable=False,
            )
        )

    extra_foundation_keys = [
        # Stage V — Regen Scalability
        ("regen_scalability_blocking_reasons", "Regen Scalability Blocking Reasons", "Regen Scalability"),
        ("regen_scalability_engine_class", "Regen Scalability Engine Class", "Regen Scalability"),
        ("regen_scalability_framework_pass_allowed", "Regen Scalability Framework Pass Allowed", "Regen Scalability"),
        ("regen_scalability_framework_status", "Regen Scalability Framework Status", "Regen Scalability"),
        ("regen_scalability_text", "Regen Scalability Framework Report", "Regen Scalability"),
        ("regen_scalability_warning_reasons", "Regen Scalability Warning Reasons", "Regen Scalability"),
        ("regen_scalability_report_owner_status", "Regen Scalability Report Owner Status", "Regen Scalability"),
        ("regen_scalability_report_owner_text", "Regen Scalability Report Owner Report", "Regen Scalability"),
        ("regen_scalability_failure_corrective_actions", "Regen Scalability Corrective Actions", "Regen Scalability"),
        ("regen_scalability_failure_owner_status", "Regen Scalability Failure Owner Status", "Regen Scalability"),
        ("regen_scalability_failure_owner_text", "Regen Scalability Failure Owner Report", "Regen Scalability"),
        ("regen_scalability_failure_root_causes", "Regen Scalability Failure Root Causes", "Regen Scalability"),
        ("regen_scalability_master_gate_blocking_reasons", "Regen Scalability Master Gate Blocking Reasons",
         "Regen Scalability"),
        ("regen_scalability_master_gate_pass_allowed", "Regen Scalability Master Gate Pass Allowed",
         "Regen Scalability"),
        ("regen_scalability_master_gate_status", "Regen Scalability Master Gate Status", "Regen Scalability"),
        ("regen_scalability_master_gate_text", "Regen Scalability Master Gate Report", "Regen Scalability"),
        ("regen_scalability_master_gate_warning_reasons", "Regen Scalability Master Gate Warning Reasons",
         "Regen Scalability"),
        ("regen_scalability_completion_audit_blocking_reasons", "Regen Scalability Completion Audit Blocking Reasons",
         "Regen Scalability"),
        ("regen_scalability_completion_audit_status", "Regen Scalability Completion Audit Status", "Regen Scalability"),
        ("regen_scalability_completion_audit_text", "Regen Scalability Completion Audit Report", "Regen Scalability"),
        ("regen_scalability_completion_audit_warning_reasons", "Regen Scalability Completion Audit Warning Reasons",
         "Regen Scalability"),

        ("stage_v1_regen_scalability_framework_complete", "Stage V.1 Regen Scalability Framework Complete",
         "Regen Scalability"),
        ("stage_v2_regen_scalability_report_ownership_complete",
         "Stage V.2 Regen Scalability Report Ownership Complete", "Regen Scalability"),
        ("stage_v3_regen_scalability_failure_ownership_complete",
         "Stage V.3 Regen Scalability Failure Ownership Complete", "Regen Scalability"),
        ("stage_v4_regen_scalability_master_gate_complete", "Stage V.4 Regen Scalability Master Gate Complete",
         "Regen Scalability"),
        ("stage_v_scalability_complete", "Stage V Regen Scalability Complete", "Regen Scalability"),

        # Stage W — Real Engine Benchmarking
        ("real_engine_benchmark_comparison", "Real Engine Benchmark Comparison", "Real Engine Benchmarking"),
        ("real_engine_benchmark_reference_data", "Real Engine Benchmark Reference Data", "Real Engine Benchmarking"),
        ("real_engine_benchmark_reference_engine", "Real Engine Benchmark Reference Engine",
         "Real Engine Benchmarking"),
        ("real_engine_benchmarking_framework_blocking_reasons", "Real Engine Benchmarking Framework Blocking Reasons",
         "Real Engine Benchmarking"),
        ("real_engine_benchmarking_framework_pass_allowed", "Real Engine Benchmarking Framework Pass Allowed",
         "Real Engine Benchmarking"),
        ("real_engine_benchmarking_framework_status", "Real Engine Benchmarking Framework Status",
         "Real Engine Benchmarking"),
        ("real_engine_benchmarking_framework_text", "Real Engine Benchmarking Framework Report",
         "Real Engine Benchmarking"),
        ("real_engine_benchmarking_framework_warning_reasons", "Real Engine Benchmarking Framework Warning Reasons",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_source_blocking_reasons", "Real Engine Benchmark Source Blocking Reasons",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_source_owner_pass_allowed", "Real Engine Benchmark Source Owner Pass Allowed",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_source_owner_status", "Real Engine Benchmark Source Owner Status",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_source_owner_text", "Real Engine Benchmark Source Owner Report",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_source_warning_reasons", "Real Engine Benchmark Source Warning Reasons",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_band_blocking_reasons", "Real Engine Benchmark Band Blocking Reasons",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_band_comparison", "Real Engine Benchmark Band Comparison", "Real Engine Benchmarking"),
        ("real_engine_benchmark_band_owner_pass_allowed", "Real Engine Benchmark Band Owner Pass Allowed",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_band_owner_status", "Real Engine Benchmark Band Owner Status",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_band_owner_text", "Real Engine Benchmark Band Owner Report",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_band_warning_reasons", "Real Engine Benchmark Band Warning Reasons",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_numeric_bands", "Real Engine Benchmark Numeric Bands", "Real Engine Benchmarking"),
        ("real_engine_benchmark_failure_corrective_actions", "Real Engine Benchmark Failure Corrective Actions",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_failure_owner_status", "Real Engine Benchmark Failure Owner Status",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_failure_owner_text", "Real Engine Benchmark Failure Owner Report",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_failure_root_causes", "Real Engine Benchmark Failure Root Causes",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_master_gate_blocking_reasons", "Real Engine Benchmark Master Gate Blocking Reasons",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_master_gate_pass_allowed", "Real Engine Benchmark Master Gate Pass Allowed",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_master_gate_status", "Real Engine Benchmark Master Gate Status",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_master_gate_text", "Real Engine Benchmark Master Gate Report",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_master_gate_warning_reasons", "Real Engine Benchmark Master Gate Warning Reasons",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_completion_audit_blocking_reasons",
         "Real Engine Benchmark Completion Audit Blocking Reasons", "Real Engine Benchmarking"),
        ("real_engine_benchmark_completion_audit_status", "Real Engine Benchmark Completion Audit Status",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_completion_audit_text", "Real Engine Benchmark Completion Audit Report",
         "Real Engine Benchmarking"),
        ("real_engine_benchmark_completion_audit_warning_reasons",
         "Real Engine Benchmark Completion Audit Warning Reasons", "Real Engine Benchmarking"),

        ("stage_w1_real_engine_benchmarking_framework_complete",
         "Stage W.1 Real Engine Benchmarking Framework Complete", "Real Engine Benchmarking"),
        ("stage_w2_public_benchmark_source_ownership_complete", "Stage W.2 Public Benchmark Source Ownership Complete",
         "Real Engine Benchmarking"),
        ("stage_w3_numeric_benchmark_band_ownership_complete", "Stage W.3 Numeric Benchmark Band Ownership Complete",
         "Real Engine Benchmarking"),
        ("stage_w4_real_engine_benchmark_failure_ownership_complete",
         "Stage W.4 Real Engine Benchmark Failure Ownership Complete", "Real Engine Benchmarking"),
        ("stage_w5_real_engine_benchmark_master_gate_complete", "Stage W.5 Real Engine Benchmark Master Gate Complete",
         "Real Engine Benchmarking"),
        ("stage_w_real_engine_benchmarking_complete", "Stage W Real Engine Benchmarking Complete",
         "Real Engine Benchmarking"),
        # Foundation verification seed / material source keys
        ("material_name", "Material Name", "Foundation Verification Seed"),
        ("selected_material_form", "Selected Material Form", "Foundation Verification Seed"),
        ("selected_material_heat_treatment", "Selected Material Heat Treatment", "Foundation Verification Seed"),
        ("coating_name", "Coating Name", "Foundation Verification Seed"),
        ("material_source_validation_mode", "Material Source Validation Mode", "Foundation Verification Seed"),
        ("material_source_validation_score", "Material Source Validation Score", "Foundation Verification Seed"),
        ("material_source_is_placeholder", "Material Source Is Placeholder", "Foundation Verification Seed"),
        ("coating_source_validation_mode", "Coating Source Validation Mode", "Foundation Verification Seed"),
        ("coating_source_validation_score", "Coating Source Validation Score", "Foundation Verification Seed"),
        ("coating_source_is_placeholder", "Coating Source Is Placeholder", "Foundation Verification Seed"),
        ("material_temperature_table_status", "Material Temperature Table Status", "Foundation Verification Seed"),
        ("material_property_interpolation_status", "Material Property Interpolation Status",
         "Foundation Verification Seed"),
        ("material_table_min_temperature", "Material Table Minimum Temperature", "Foundation Verification Seed"),
        ("material_table_max_temperature", "Material Table Maximum Temperature", "Foundation Verification Seed"),
        ("max_wall_temperature", "Maximum Wall Temperature", "Foundation Verification Seed"),
        ("regen_validation_status", "Regen Validation Status", "Foundation Verification Seed"),
        ("regen_coolant_velocity", "Regen Coolant Velocity", "Foundation Verification Seed"),
        ("regen_pressure_drop", "Regen Pressure Drop", "Foundation Verification Seed"),
        ("propellant_pair", "Propellant Pair", "Foundation Verification Seed"),
        ("cycle_type", "Cycle Type", "Foundation Verification Seed"),
        ("coating_temperature_table_status", "Coating Temperature Table Status", "Foundation Verification Seed"),
        ("coating_property_interpolation_status", "Coating Property Interpolation Status",
         "Foundation Verification Seed"),

        # Output ownership audit keys
        ("output_ownership_audit_status", "Output Ownership Audit Status", "Output Ownership Audit"),
        ("output_ownership_scalar_key_count", "Output Ownership Scalar Key Count", "Output Ownership Audit"),
        ("output_ownership_non_scalar_registered_key_count", "Output Ownership Non-Scalar Registered Key Count",
         "Output Ownership Audit"),
        ("output_ownership_unregistered_key_count", "Output Ownership Unregistered Key Count",
         "Output Ownership Audit"),
        ("output_ownership_suspected_pollution_keys", "Output Ownership Suspected Pollution Keys",
         "Output Ownership Audit"),
        ("output_ownership_unregistered_keys", "Output Ownership Unregistered Keys", "Output Ownership Audit"),
        ("output_ownership_audit_text", "Output Ownership Audit Report", "Output Ownership Audit"),
        ("foundation_save_load_verification_status", "Foundation Save/Load Verification Status",
         "Foundation Save/Load Verification"),
        ("foundation_save_load_verified", "Foundation Save/Load Verified", "Foundation Save/Load Verification"),
        ("foundation_save_load_missing_keys", "Foundation Save/Load Missing Keys", "Foundation Save/Load Verification"),
        ("foundation_save_load_changed_values", "Foundation Save/Load Changed Values",
         "Foundation Save/Load Verification"),
        ("foundation_save_load_checked_key_count", "Foundation Save/Load Checked Key Count",
         "Foundation Save/Load Verification"),
        ("foundation_save_load_verification_error", "Foundation Save/Load Verification Error",
         "Foundation Save/Load Verification"),
        ("foundation_save_load_verification_text", "Foundation Save/Load Verification Report",
         "Foundation Save/Load Verification"),
        ("foundation_ui_launch_verification_status", "Foundation UI Launch Verification Status",
         "Foundation UI Verification"),
        ("foundation_ui_launch_verified", "Foundation UI Launch Verified", "Foundation UI Verification"),
        ("foundation_ui_launch_passed_count", "Foundation UI Launch Passed Count", "Foundation UI Verification"),
        ("foundation_ui_launch_failed_count", "Foundation UI Launch Failed Count", "Foundation UI Verification"),
        ("foundation_ui_launch_tests", "Foundation UI Launch Tests", "Foundation UI Verification"),
        ("foundation_ui_launch_blocking_reasons", "Foundation UI Launch Blocking Reasons",
         "Foundation UI Verification"),
        ("foundation_ui_launch_verification_text", "Foundation UI Launch Verification Report",
         "Foundation UI Verification"),
        ("foundation_final_signoff_status", "Foundation Final Sign-Off Status", "Foundation Final Sign-Off"),
        ("foundation_final_signoff_complete", "Foundation Final Sign-Off Complete", "Foundation Final Sign-Off"),
        ("foundation_final_signoff_blocking_reasons", "Foundation Final Sign-Off Blocking Reasons",
         "Foundation Final Sign-Off"),
        ("foundation_final_signoff_warning_reasons", "Foundation Final Sign-Off Warning Reasons",
         "Foundation Final Sign-Off"),
        ("foundation_final_signoff_text", "Foundation Final Sign-Off Report", "Foundation Final Sign-Off"),
        ("foundation_completion_handover_status", "Foundation Completion Handover Status",
         "Foundation Completion Handover"),
        ("foundation_completion_handover_ready_for_regen_geometry", "Ready For Regen Geometry",
         "Foundation Completion Handover"),
        ("foundation_completion_handover_blocking_reasons", "Foundation Completion Handover Blocking Reasons",
         "Foundation Completion Handover"),
        ("foundation_completion_handover_text", "Foundation Completion Handover Report",
         "Foundation Completion Handover"),
        # Phase 16N — Regen UI recommendation / acceptance / apply / regeneration flow
        ("phase_16n6_accept_recommendation_status", "Phase 16N.6 Accept Recommendation Status", "Phase 16N UI Integration"),
        ("phase_16n6_recommendation_accepted", "Phase 16N.6 Recommendation Accepted", "Phase 16N UI Integration"),
        ("phase_16n6_accepted_staged_geometry", "Phase 16N.6 Accepted Staged Geometry", "Phase 16N UI Integration"),
        ("phase_16n6_accept_recommendation_reasons", "Phase 16N.6 Accept Recommendation Reasons", "Phase 16N UI Integration"),
        ("phase_16n6_geometry_applied", "Phase 16N.6 Geometry Applied Safety Lock", "Phase 16N UI Integration"),
        ("phase_16n6_solver_regenerated", "Phase 16N.6 Solver Regenerated Safety Lock", "Phase 16N UI Integration"),
        ("phase_16n6_live_geometry_modified", "Phase 16N.6 Live Geometry Modified Safety Lock", "Phase 16N UI Integration"),

        ("phase_16n7_apply_geometry_status", "Phase 16N.7 Apply Geometry Status", "Phase 16N UI Integration"),
        ("phase_16n7_geometry_applied", "Phase 16N.7 Geometry Applied", "Phase 16N UI Integration"),
        ("phase_16n7_applied_geometry", "Phase 16N.7 Applied Geometry", "Phase 16N UI Integration"),
        ("phase_16n7_apply_geometry_reasons", "Phase 16N.7 Apply Geometry Reasons", "Phase 16N UI Integration"),
        ("phase_16n7_solver_regenerated", "Phase 16N.7 Solver Regenerated Safety Lock", "Phase 16N UI Integration"),
        ("phase_16n7_cea_rerun", "Phase 16N.7 CEA Rerun Safety Lock", "Phase 16N UI Integration"),

        ("phase_16n8_solver_regeneration_request_status", "Phase 16N.8 Solver Regeneration Request Status", "Phase 16N UI Integration"),
        ("phase_16n8_solver_regeneration_requested", "Phase 16N.8 Solver Regeneration Requested", "Phase 16N UI Integration"),
        ("phase_16n8_solver_regeneration_geometry", "Phase 16N.8 Solver Regeneration Geometry", "Phase 16N UI Integration"),
        ("phase_16n8_solver_regeneration_reasons", "Phase 16N.8 Solver Regeneration Reasons", "Phase 16N UI Integration"),
        ("phase_16n8_solver_regenerated", "Phase 16N.8 Solver Regenerated Safety Lock", "Phase 16N UI Integration"),
        ("phase_16n8_cea_rerun", "Phase 16N.8 CEA Rerun Safety Lock", "Phase 16N UI Integration"),

        ("phase_16n9_before_after_comparison_status", "Phase 16N.9 Before/After Comparison Status", "Phase 16N UI Integration"),
        ("phase_16n9_before_after_comparison_available", "Phase 16N.9 Before/After Comparison Available", "Phase 16N UI Integration"),
        ("phase_16n9_before_after_comparison_report", "Phase 16N.9 Before/After Comparison Report", "Phase 16N UI Integration"),
        ("phase_16n9_before_after_comparison_reasons", "Phase 16N.9 Before/After Comparison Reasons", "Phase 16N UI Integration"),
        ("phase_16n9_before_after_change_count", "Phase 16N.9 Before/After Change Count", "Phase 16N UI Integration"),
        ("phase_16n9_before_after_changes", "Phase 16N.9 Before/After Changes", "Phase 16N UI Integration"),

        ("regen_ui_applied_geometry", "Regen UI Applied Geometry", "Phase 16N UI Integration"),
        ("regen_current_geometry", "Regen Current Geometry", "Phase 16N UI Integration"),

        # Phase 16O.2D — Remaining engineering variables
        ("coolant_mass_flow_fraction", "Coolant Mass Flow Fraction", "Regen Cooling"),
        ("effective_material_temperature_limit", "Effective Material Temperature Limit", "Materials"),
        ("sourced_material_density", "Sourced Material Density", "Materials"),
        ("sourced_material_specific_heat_cp", "Sourced Material Specific Heat Cp", "Materials"),
        ("sourced_wall_thermal_conductivity", "Sourced Wall Thermal Conductivity", "Materials"),
        ("wall_thermal_conductivity_source", "Wall Thermal Conductivity Source", "Materials"),


        # Phase 11A.8B/C — Regen Geometry Acceptance Patch Enforcement
        ("regen_geometry_acceptance_patch_keys", "Regen Geometry Acceptance Patch Keys", "Regen Geometry Acceptance"),
        ("regen_geometry_acceptance_patch_key_count", "Regen Geometry Acceptance Patch Key Count",
         "Regen Geometry Acceptance"),
        ("regen_geometry_candidate_acceptance_status", "Regen Geometry Candidate Acceptance Status",
         "Regen Geometry Acceptance"),
        ("regen_geometry_candidate_acceptance_complete", "Regen Geometry Candidate Acceptance Complete",
         "Regen Geometry Acceptance"),
        ("regen_geometry_candidate_acceptance_reason", "Regen Geometry Candidate Acceptance Reason",
         "Regen Geometry Acceptance"),
        # Phase 11A.8D — Regen Geometry Candidate Acceptance Patch
        ("regen_geometry_acceptance_patch_keys", "Regen Geometry Acceptance Patch Keys", "Regen Geometry Acceptance"),
        ("regen_geometry_acceptance_patch_key_count", "Regen Geometry Acceptance Patch Key Count",
         "Regen Geometry Acceptance"),
        ("regen_geometry_candidate_acceptance_status", "Regen Geometry Candidate Acceptance Status",
         "Regen Geometry Acceptance"),
        ("regen_geometry_candidate_acceptance_complete", "Regen Geometry Candidate Acceptance Complete",
         "Regen Geometry Acceptance"),
        ("regen_geometry_candidate_acceptance_reason", "Regen Geometry Candidate Acceptance Reason",
         "Regen Geometry Acceptance"),
    ]

    for key, label, section in extra_foundation_keys:
        entries.append(
            VariableDefinition(
                key=key,
                label=label,
                section=section,
                output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
                report_owner="DIAGNOSTICS_PANEL",
                diagnostic_owner="FOUNDATION_STATUS_PANEL",
                is_output=False,
                is_graphable=False,
            )
        )

    for entry in entries:
        registry[entry.key] = entry

    return registry

VARIABLES = add_foundation_registry_entries(build_variable_registry())

# D3.7B-R — concise user-facing cost-estimate scalar outputs.
# Calculation remains owned by cost_intelligence_owner.py.

VARIABLES.update({
    "base_wall_mass": VariableDefinition(
        key="base_wall_mass",
        label="Base Wall Mass",
        symbol="m_wall",
        unit="kg",
        section="Cost Estimates",
        is_output=True,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_SCALAR,
    ),

    "cost_base_material": VariableDefinition(
        key="cost_base_material",
        label="Base Material Cost",
        symbol="C_base",
        section="Cost Estimates",
        is_output=True,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_SCALAR,
    ),

    "cost_base_material_status": VariableDefinition(
        key="cost_base_material_status",
        label="Base Material Cost Status",
        section="Cost Estimates",
        is_output=False,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_VALIDATION,
        report_owner="VALIDATION_REPORT",
    ),

    "cost_coating_material": VariableDefinition(
        key="cost_coating_material",
        label="Coating Material Cost",
        symbol="C_coating",
        section="Cost Estimates",
        is_output=True,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_SCALAR,
    ),

    "cost_coating_material_status": VariableDefinition(
        key="cost_coating_material_status",
        label="Coating Material Cost Status",
        section="Cost Estimates",
        is_output=False,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_VALIDATION,
        report_owner="VALIDATION_REPORT",
    ),

    "cost_manufacturing": VariableDefinition(
        key="cost_manufacturing",
        label="Manufacturing Cost",
        symbol="C_mfg",
        section="Cost Estimates",
        is_output=True,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_SCALAR,
    ),

    "cost_manufacturing_status": VariableDefinition(
        key="cost_manufacturing_status",
        label="Manufacturing Cost Status",
        section="Cost Estimates",
        is_output=False,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_VALIDATION,
        report_owner="VALIDATION_REPORT",
    ),

    "cost_partial_total": VariableDefinition(
        key="cost_partial_total",
        label="Partial Cost Estimate",
        symbol="C_partial",
        section="Cost Estimates",
        is_output=True,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_SCALAR,
    ),

    "cost_partial_currency": VariableDefinition(
        key="cost_partial_currency",
        label="Partial Estimate Currency",
        section="Cost Estimates",
        is_output=True,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_SCALAR,
    ),

    "cost_partial_status": VariableDefinition(
        key="cost_partial_status",
        label="Partial Estimate Status",
        section="Cost Estimates",
        is_output=False,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_VALIDATION,
        report_owner="VALIDATION_REPORT",
    ),

    "cost_total": VariableDefinition(
        key="cost_total",
        label="Total Cost Estimate",
        symbol="C_total",
        section="Cost Estimates",
        is_output=True,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_SCALAR,
    ),

    "cost_total_currency": VariableDefinition(
        key="cost_total_currency",
        label="Total Estimate Currency",
        section="Cost Estimates",
        is_output=True,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_SCALAR,
    ),

    "cost_total_status": VariableDefinition(
        key="cost_total_status",
        label="Total Estimate Status",
        section="Cost Estimates",
        is_output=False,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_VALIDATION,
        report_owner="VALIDATION_REPORT",
    ),

    "cost_total_complete": VariableDefinition(
        key="cost_total_complete",
        label="Complete Cost Estimate",
        section="Cost Estimates",
        is_output=True,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_SCALAR,
    ),

    # CANONICAL_RECOMMENDED_GEOMETRY_RESULT_OWNERSHIP
    # Fixed recommendation result fields follow the same
    # canonical visibility and ownership as recommended_geometry_status.
    "recommended_geometry_valid": VariableDefinition(
        key="recommended_geometry_valid",
        label="Recommended Geometry Valid",
        section='Regenerative Cooling',
        is_output=False,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
        report_owner="RECOMMENDED_DESIGN_PANEL",
        recommendation_owner="RECOMMENDED_DESIGN_PANEL",
    ),

    "recommended_geometry_reason": VariableDefinition(
        key="recommended_geometry_reason",
        label="Recommended Geometry Reason",
        section='Regenerative Cooling',
        is_output=False,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
        report_owner="RECOMMENDED_DESIGN_PANEL",
        recommendation_owner="RECOMMENDED_DESIGN_PANEL",
    ),

    "recommended_geometry_note": VariableDefinition(
        key="recommended_geometry_note",
        label="Recommended Geometry Note",
        section='Regenerative Cooling',
        is_output=False,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_RECOMMENDATION,
        report_owner="RECOMMENDED_DESIGN_PANEL",
        recommendation_owner="RECOMMENDED_DESIGN_PANEL",
    ),


    # CANONICAL_SOURCE_VALIDATION_RESULT_OWNERSHIP
    # Aggregate material/coating source-validation state follows
    # the existing regen validation ownership contract.
    "source_validation_conservative_gate": VariableDefinition(
        key="source_validation_conservative_gate",
        label="Source Validation Conservative Gate",
        section="Regen Validation",
        is_output=False,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_VALIDATION,
        report_owner="VALIDATION_REPORT",
        validation_owner="REGEN_VALIDATION",
    ),

    "source_validation_mode": VariableDefinition(
        key="source_validation_mode",
        label="Source Validation Mode",
        section="Regen Validation",
        is_output=False,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_VALIDATION,
        report_owner="VALIDATION_REPORT",
        validation_owner="REGEN_VALIDATION",
    ),


    # CANONICAL_CEA_AUTHORITY_STATE_OWNERSHIP
    # CEA authority/provenance state is diagnostic evidence,
    # not a scalar engineering output.
    "cea_authoritative_used": VariableDefinition(
        key="cea_authoritative_used",
        label="CEA Authoritative Used",
        section="CEA Chemical Outputs",
        is_output=False,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
        report_owner="DIAGNOSTICS_PANEL",
        diagnostic_owner="DIAGNOSTICS_PANEL",
    ),

    "cea_authoritative_mode": VariableDefinition(
        key="cea_authoritative_mode",
        label="CEA Authoritative Mode",
        section="CEA Chemical Outputs",
        is_output=False,
        is_graphable=False,
        output_visibility=OUTPUT_VISIBILITY_DIAGNOSTIC,
        report_owner="DIAGNOSTICS_PANEL",
        diagnostic_owner="DIAGNOSTICS_PANEL",
    ),

    # FILM_COOLING_REQUIREMENT_SCALAR_OUTPUT_OWNERSHIP
    # Canonical scalar engineering results produced by
    # engine_solver.estimate_film_cooling_requirement().
    "film_required_wall_temperature_drop": VariableDefinition(
        key="film_required_wall_temperature_drop",
        label="Required Film-Cooling Wall Temperature Drop",
        unit="K",
        section="Regenerative Cooling",
        is_input=False,
        is_output=True,
        is_graphable=True,
        output_visibility="SCALAR_OUTPUT",
        report_owner="MAIN_OUTPUT",
    ),

    "film_required_effectiveness": VariableDefinition(
        key="film_required_effectiveness",
        label="Required Film Effectiveness",
        unit="-",
        section="Regenerative Cooling",
        is_input=False,
        is_output=True,
        is_graphable=False,
        output_visibility="SCALAR_OUTPUT",
        report_owner="MAIN_OUTPUT",
    ),

    "film_estimated_film_fraction_of_available_fuel": VariableDefinition(
        key="film_estimated_film_fraction_of_available_fuel",
        label="Estimated Film Fraction of Available Fuel",
        unit="-",
        section="Regenerative Cooling",
        is_input=False,
        is_output=True,
        is_graphable=False,
        output_visibility="SCALAR_OUTPUT",
        report_owner="MAIN_OUTPUT",
    ),

    "film_estimated_mass_flow_rate": VariableDefinition(
        key="film_estimated_mass_flow_rate",
        label="Estimated Film Mass Flow Rate",
        unit="kg/s",
        section="Regenerative Cooling",
        unit_group="mass_flow",
        is_input=False,
        is_output=True,
        is_graphable=True,
        output_visibility="SCALAR_OUTPUT",
        report_owner="MAIN_OUTPUT",
    ),

    "film_estimated_fraction_of_fuel_flow": VariableDefinition(
        key="film_estimated_fraction_of_fuel_flow",
        label="Estimated Film Fraction of Fuel Flow",
        unit="-",
        section="Regenerative Cooling",
        is_input=False,
        is_output=True,
        is_graphable=False,
        output_visibility="SCALAR_OUTPUT",
        report_owner="MAIN_OUTPUT",
    ),

    # COMBINED_COOLING_PREDICTION_SCALAR_OUTPUT_OWNERSHIP
    # Canonical scalar engineering results produced by
    # engine_solver.predict_combined_cooling_outcome().
    "combined_predicted_hot_wall_temperature": VariableDefinition(
        key="combined_predicted_hot_wall_temperature",
        label="Combined Predicted Hot-Wall Temperature",
        unit="K",
        section="Regenerative Cooling",
        is_input=False,
        is_output=True,
        is_graphable=True,
        output_visibility="SCALAR_OUTPUT",
        report_owner="MAIN_OUTPUT",
    ),

    "combined_predicted_material_limit": VariableDefinition(
        key="combined_predicted_material_limit",
        label="Combined Predicted Material Limit",
        unit="K",
        section="Regenerative Cooling",
        is_input=False,
        is_output=True,
        is_graphable=True,
        output_visibility="SCALAR_OUTPUT",
        report_owner="MAIN_OUTPUT",
    ),

    "combined_predicted_material_margin": VariableDefinition(
        key="combined_predicted_material_margin",
        label="Combined Predicted Material Margin",
        unit="K",
        section="Regenerative Cooling",
        is_input=False,
        is_output=True,
        is_graphable=True,
        output_visibility="SCALAR_OUTPUT",
        report_owner="MAIN_OUTPUT",
    ),

    "combined_prediction_coolant_reference_temperature": VariableDefinition(
        key="combined_prediction_coolant_reference_temperature",
        label="Combined Prediction Coolant Reference Temperature",
        unit="K",
        section="Regenerative Cooling",
        is_input=False,
        is_output=True,
        is_graphable=True,
        output_visibility="SCALAR_OUTPUT",
        report_owner="MAIN_OUTPUT",
    ),

    # COOLING_STRATEGY_TRADE_STUDY_OWNERSHIP
    # Canonical outputs produced by
    # engine_solver.evaluate_cooling_strategy_trade_study().
    #
    # Requirement scalars are normal Regenerative Cooling scalar
    # engineering results. Selection text is recommendation-only.
    "cooling_trade_required_heat_load_fraction": VariableDefinition(
        key="cooling_trade_required_heat_load_fraction",
        label="Cooling Trade Required Heat-Load Fraction",
        unit="-",
        section="Regenerative Cooling",
        is_input=False,
        is_output=True,
        is_graphable=False,
        output_visibility="SCALAR_OUTPUT",
        report_owner="MAIN_OUTPUT",
    ),

    "cooling_trade_required_heat_load_reduction_fraction": VariableDefinition(
        key="cooling_trade_required_heat_load_reduction_fraction",
        label="Cooling Trade Required Heat-Load Reduction Fraction",
        unit="-",
        section="Regenerative Cooling",
        is_input=False,
        is_output=True,
        is_graphable=False,
        output_visibility="SCALAR_OUTPUT",
        report_owner="MAIN_OUTPUT",
    ),

    "cooling_trade_required_material_factor": VariableDefinition(
        key="cooling_trade_required_material_factor",
        label="Cooling Trade Required Material Factor",
        unit="-",
        section="Regenerative Cooling",
        is_input=False,
        is_output=True,
        is_graphable=False,
        output_visibility="SCALAR_OUTPUT",
        report_owner="MAIN_OUTPUT",
    ),

    "cooling_trade_selected_option": VariableDefinition(
        key="cooling_trade_selected_option",
        label="Cooling Trade Selected Option",
        unit="-",
        section="Regenerative Cooling",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="RECOMMENDATION_ONLY",
        report_owner="RECOMMENDED_DESIGN_PANEL",
        recommendation_owner="RECOMMENDED_DESIGN_PANEL",
    ),

    "cooling_trade_selected_reason": VariableDefinition(
        key="cooling_trade_selected_reason",
        label="Cooling Trade Selected Reason",
        unit="-",
        section="Regenerative Cooling",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="RECOMMENDATION_ONLY",
        report_owner="RECOMMENDED_DESIGN_PANEL",
        recommendation_owner="RECOMMENDED_DESIGN_PANEL",
    ),

    # COMBINED_COOLING_AXIAL_SUMMARY_REPORT_OWNERSHIP
    # Canonical axial summary quantities produced by
    # engine_solver.build_combined_cooling_axial_preview().
    "combined_axial_failed_station_count": VariableDefinition(
        key="combined_axial_failed_station_count",
        label="Combined Axial Failed Station Count",
        unit="",
        section="Regenerative Cooling",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="AXIAL_REPORT_ONLY",
        report_owner="AXIAL_THERMAL_REPORT",
    ),

    "combined_axial_max_hot_wall_temperature": VariableDefinition(
        key="combined_axial_max_hot_wall_temperature",
        label="Combined Axial Max Hot-Wall Temperature",
        unit="K",
        section="Regenerative Cooling",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="AXIAL_REPORT_ONLY",
        report_owner="AXIAL_THERMAL_REPORT",
    ),

    "combined_axial_max_hot_wall_temperature_location": VariableDefinition(
        key="combined_axial_max_hot_wall_temperature_location",
        label="Combined Axial Max Hot-Wall Temperature Location",
        unit="m",
        section="Regenerative Cooling",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="AXIAL_REPORT_ONLY",
        report_owner="AXIAL_THERMAL_REPORT",
    ),

    "combined_axial_station_count": VariableDefinition(
        key="combined_axial_station_count",
        label="Combined Axial Station Count",
        unit="",
        section="Regenerative Cooling",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="AXIAL_REPORT_ONLY",
        report_owner="AXIAL_THERMAL_REPORT",
    ),

    "combined_axial_worst_material_margin": VariableDefinition(
        key="combined_axial_worst_material_margin",
        label="Combined Axial Worst Material Margin",
        unit="K",
        section="Regenerative Cooling",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="AXIAL_REPORT_ONLY",
        report_owner="AXIAL_THERMAL_REPORT",
    ),

    "combined_axial_worst_material_margin_location": VariableDefinition(
        key="combined_axial_worst_material_margin_location",
        label="Combined Axial Worst Material Margin Location",
        unit="m",
        section="Regenerative Cooling",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="AXIAL_REPORT_ONLY",
        report_owner="AXIAL_THERMAL_REPORT",
    ),

    # COMBINED_COOLING_CONFIDENCE_DIAGNOSTIC_OWNERSHIP
    # Canonical diagnostic results produced by
    # engine_solver.assess_combined_cooling_confidence().
    "combined_cooling_confidence": VariableDefinition(
        key="combined_cooling_confidence",
        label="Combined Cooling Confidence",
        unit="-",
        section="Regenerative Cooling",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="DIAGNOSTIC_ONLY",
        report_owner="DIAGNOSTICS_PANEL",
        diagnostic_owner="DIAGNOSTICS_PANEL",
    ),

    "combined_cooling_confidence_score": VariableDefinition(
        key="combined_cooling_confidence_score",
        label="Combined Cooling Confidence Score",
        unit="-",
        section="Regenerative Cooling",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="DIAGNOSTIC_ONLY",
        report_owner="DIAGNOSTICS_PANEL",
        diagnostic_owner="DIAGNOSTICS_PANEL",
    ),

    # RECOMMENDED_REGEN_VIABILITY_VALIDATION_OWNERSHIP
    # Assessment metrics produced by
    # engine_solver.validate_recommended_regen_viability().
    # These support the regen-validation decision and are not
    # primary user-facing Main Output scalars.
    "recommended_regen_pressure_drop_limit_ratio": VariableDefinition(
        key="recommended_regen_pressure_drop_limit_ratio",
        label="Recommended Regen Pressure-Drop Limit Ratio",
        unit="-",
        section="Regen Validation",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="VALIDATION_ONLY",
        report_owner="VALIDATION_REPORT",
        validation_owner="REGEN_VALIDATION",
    ),

    "recommended_regen_reynolds_target_ratio": VariableDefinition(
        key="recommended_regen_reynolds_target_ratio",
        label="Recommended Regen Reynolds Target Ratio",
        unit="-",
        section="Regen Validation",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="VALIDATION_ONLY",
        report_owner="VALIDATION_REPORT",
        validation_owner="REGEN_VALIDATION",
    ),

    "recommended_regen_viability_score": VariableDefinition(
        key="recommended_regen_viability_score",
        label="Recommended Regen Viability Score",
        unit="-",
        section="Regen Validation",
        is_input=False,
        is_output=False,
        is_graphable=False,
        output_visibility="VALIDATION_ONLY",
        report_owner="VALIDATION_REPORT",
        validation_owner="REGEN_VALIDATION",
    ),

})

# D3.7B_R_COST_ESTIMATES_REGISTRY_END

LABEL_TO_VAR = {
    definition.label: key
    for key, definition in VARIABLES.items()
}


VAR_TO_LABEL = {
    key: definition.label
    for key, definition in VARIABLES.items()
}


SYMBOLS = {
    key: definition.symbol
    for key, definition in VARIABLES.items()
}


UNITS = {
    key: definition.unit
    for key, definition in VARIABLES.items()
}


UNIT_GROUPS = {
    key: definition.unit_group
    for key, definition in VARIABLES.items()
    if definition.unit_group
}


UNIT_PREFERENCES = dict(LEGACY_UNIT_PREFERENCES)


HIDDEN_INPUT_VARS = set(LEGACY_HIDDEN_INPUT_VARS) | OUTPUT_ONLY_KEYS


def get_graphable_labels():
    return [
        definition.label
        for definition in VARIABLES.values()
        if definition.is_graphable
    ]


def get_output_sections():
    sections = OrderedDict()

    for section_name in LEGACY_SECTIONS.keys():
        sections[section_name] = []

    for definition in VARIABLES.values():
        if not definition.is_output:
            continue

        sections.setdefault(definition.section, [])
        sections[definition.section].append(definition.label)

    return {
        section: labels
        for section, labels in sections.items()
        if labels
    }


def get_variable(key):
    return VARIABLES.get(key)

def is_input_variable(key):
    definition = get_variable(key)
    return bool(definition is not None and definition.is_input)


def get_input_role(key):
    definition = get_variable(key)
    return "" if definition is None else definition.input_role


def get_input_owner(key):
    definition = get_variable(key)
    return "" if definition is None else definition.input_owner


def is_default_manual_input(key):
    definition = get_variable(key)

    return bool(
        definition is not None
        and definition.is_input
        and definition.input_owner == "MANUAL"
        and definition.input_role in {"REQUIRED", "DESIGN_CHOICE"}
    )


def is_advanced_input(key):
    definition = get_variable(key)

    return bool(
        definition is not None
        and definition.is_input
        and definition.input_role == "ADVANCED_OVERRIDE"
    )


def get_label(key):
    definition = get_variable(key)
    return definition.label if definition else key


def get_symbol(key):
    definition = get_variable(key)
    return definition.symbol if definition else ""


def get_unit(key):
    definition = get_variable(key)
    return definition.unit if definition else ""


def is_graphable(key):
    definition = get_variable(key)
    return bool(definition and definition.is_graphable)


def get_input_labels():
    return [
        definition.label
        for definition in VARIABLES.values()
        if definition.is_input
    ]


def get_output_labels():
    return [
        definition.label
        for definition in VARIABLES.values()
        if definition.is_output
    ]


def get_output_keys():
    return [
        definition.key
        for definition in VARIABLES.values()
        if definition.is_output
    ]


def get_input_keys():
    return [
        definition.key
        for definition in VARIABLES.values()
        if definition.is_input
    ]


def get_output_sections_by_key():
    sections = OrderedDict()

    for section_name in LEGACY_SECTIONS.keys():
        sections[section_name] = []

    for definition in VARIABLES.values():
        if not definition.is_output:
            continue

        sections.setdefault(definition.section, [])
        sections[definition.section].append(definition.key)

    return {
        section: keys
        for section, keys in sections.items()
        if keys
    }


def get_graphable_keys():
    return [
        definition.key
        for definition in VARIABLES.values()
        if definition.is_graphable
    ]

def get_keys_by_visibility(output_visibility):
    return [
        definition.key
        for definition in VARIABLES.values()
        if definition.output_visibility == output_visibility
    ]


def get_scalar_output_keys():
    return [
        definition.key
        for definition in VARIABLES.values()
        if (
            definition.is_output
            and definition.output_visibility == OUTPUT_VISIBILITY_SCALAR
        )
    ]


def get_axial_report_keys():
    return get_keys_by_visibility(OUTPUT_VISIBILITY_AXIAL_REPORT)


def get_validation_output_keys():
    return get_keys_by_visibility(OUTPUT_VISIBILITY_VALIDATION)


def get_diagnostic_output_keys():
    return get_keys_by_visibility(OUTPUT_VISIBILITY_DIAGNOSTIC)


def get_recommendation_output_keys():
    return get_keys_by_visibility(OUTPUT_VISIBILITY_RECOMMENDATION)


def get_internal_output_keys():
    return get_keys_by_visibility(OUTPUT_VISIBILITY_INTERNAL)


def get_output_visibility(key):
    definition = get_variable(key)
    return definition.output_visibility if definition else OUTPUT_VISIBILITY_INTERNAL


def is_scalar_output(key):
    definition = get_variable(key)

    return bool(
        definition is not None
        and definition.is_output
        and definition.output_visibility == OUTPUT_VISIBILITY_SCALAR
    )


def get_scalar_output_sections_by_key():
    sections = OrderedDict()

    for section_name in LEGACY_SECTIONS.keys():
        sections[section_name] = []

    for definition in VARIABLES.values():
        if definition.output_visibility != OUTPUT_VISIBILITY_SCALAR:
            continue

        if not definition.is_output:
            continue

        sections.setdefault(definition.section, [])
        sections[definition.section].append(definition.key)

    return {
        section: keys
        for section, keys in sections.items()
        if keys
    }