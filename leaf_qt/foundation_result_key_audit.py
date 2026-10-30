try:
    from foundation_dynamic_registry_seed_phase_16o2 import classify_dynamic_key
except Exception:
    classify_dynamic_key = None

from variable_registry import (
    VARIABLES,
    get_output_visibility,
)


EXPECTED_PREFIX_VISIBILITY = {
    # Phase 16N — Regen UI Completion / Viewer Workflow
    "phase_16n_": "DIAGNOSTIC_ONLY",
    "phase_16n1_": "DIAGNOSTIC_ONLY",
    "phase_16n2_": "DIAGNOSTIC_ONLY",
    "phase_16n3_": "DIAGNOSTIC_ONLY",
    "phase_16n4_": "DIAGNOSTIC_ONLY",
    "phase_16n5_": "DIAGNOSTIC_ONLY",
    "phase_16n6_": "DIAGNOSTIC_ONLY",
    "phase_16n7_": "DIAGNOSTIC_ONLY",
    "phase_16n8_": "DIAGNOSTIC_ONLY",
    "phase_16n9_": "DIAGNOSTIC_ONLY",
    "phase_16n10_": "DIAGNOSTIC_ONLY",
    "regen_ui_applied_geometry": "DIAGNOSTIC_ONLY",
    "regen_current_geometry": "DIAGNOSTIC_ONLY",
    "regen_geometry_commit_": "DIAGNOSTIC_ONLY",
    "regen_autonomous_geometry_commit_": "DIAGNOSTIC_ONLY",
    "regen_autonomous_geometry_staged_candidate": "DIAGNOSTIC_ONLY",
    "regen_recommendation_viewer_": "REPORT_ONLY",
    "regen_recommendation_feed_repair_": "DIAGNOSTIC_ONLY",
    "regen_ranking_owner_source_repair_": "DIAGNOSTIC_ONLY",
    "phase_16j3e_": "DIAGNOSTIC_ONLY",
    "phase_16j3f_": "DIAGNOSTIC_ONLY",
    "regen_ranking_input_feed_bridge_": "DIAGNOSTIC_ONLY",
    "phase_16j3d_": "DIAGNOSTIC_ONLY",
    "phase_16j3e_": "DIAGNOSTIC_ONLY",
    "regen_candidate_base_geometry_population_repair_": "DIAGNOSTIC_ONLY",
    "phase_16j3c_": "DIAGNOSTIC_ONLY",
    "phase_16j3d_": "DIAGNOSTIC_ONLY",
    "regen_candidate_generator_data_source_repair_": "DIAGNOSTIC_ONLY",
    "phase_16j3a_": "DIAGNOSTIC_ONLY",
    "phase_16j3b_": "DIAGNOSTIC_ONLY",
    "regen_coolant_flow_activation_layer_": "DIAGNOSTIC_ONLY",
    "phase_16j2a_": "DIAGNOSTIC_ONLY",
    "phase_16j2b_": "DIAGNOSTIC_ONLY",
    "regen_candidate_ranking_payload_bridge_": "DIAGNOSTIC_ONLY",
    "phase_16j1_": "DIAGNOSTIC_ONLY",
    "phase_16k_": "DIAGNOSTIC_ONLY",
    "regen_candidate_ranking_inspector_": "DIAGNOSTIC_ONLY",
    "phase_16j_": "DIAGNOSTIC_ONLY",
    "phase_16k_": "DIAGNOSTIC_ONLY",
    "regen_architecture_visibility_audit_": "DIAGNOSTIC_ONLY",
    "phase_16i_": "DIAGNOSTIC_ONLY",
    "phase_16j_": "DIAGNOSTIC_ONLY",
    "regen_candidate_population_inspector_": "DIAGNOSTIC_ONLY",
    "regen_coolant_property_resolution_repair_": "DIAGNOSTIC_ONLY",
    "recommended_geometry_status_previous": "DIAGNOSTIC_ONLY",
    "regen_input_mapping_repair_": "DIAGNOSTIC_ONLY",
    "regen_workflow_": "DIAGNOSTIC_ONLY",
    "phase_16f_": "DIAGNOSTIC_ONLY",
    "regen_completion_": "DIAGNOSTIC_ONLY",
    "regen_system_": "DIAGNOSTIC_ONLY",
    "leaf_regen_": "DIAGNOSTIC_ONLY",
    "phase_16e_": "DIAGNOSTIC_ONLY",
    "phase_16f_": "DIAGNOSTIC_ONLY",
    "regen_system_signoff_": "DIAGNOSTIC_ONLY",
    "phase_16d_": "DIAGNOSTIC_ONLY",
    "phase_16e_": "DIAGNOSTIC_ONLY",
    "regen_unified_validation_": "DIAGNOSTIC_ONLY",
    "unified_regen_validation_": "DIAGNOSTIC_ONLY",
    "phase_16c_": "DIAGNOSTIC_ONLY",
    "phase_16d_": "DIAGNOSTIC_ONLY",
    "regen_unified_report_": "DIAGNOSTIC_ONLY",
    "unified_regen_report_": "DIAGNOSTIC_ONLY",
    "phase_16b_": "DIAGNOSTIC_ONLY",
    "phase_16c_": "DIAGNOSTIC_ONLY",
    "regen_unified_viewer_": "DIAGNOSTIC_ONLY",
    "unified_regen_viewer_": "DIAGNOSTIC_ONLY",
    "phase_16a_": "DIAGNOSTIC_ONLY",
    "phase_16b_": "DIAGNOSTIC_ONLY",
    "regen_unified_": "DIAGNOSTIC_ONLY",
    "unified_regen_": "DIAGNOSTIC_ONLY",
    "optimisation_report_backend_payload": "DIAGNOSTIC_ONLY",
    "optimisation_report_backend_report": "DIAGNOSTIC_ONLY",
    "optimisation_report_backend_source_count": "DIAGNOSTIC_ONLY",
    "optimisation_report_backend_summary": "DIAGNOSTIC_ONLY",
    "optimisation_report_history": "DIAGNOSTIC_ONLY",
    "optimisation_report_html_exported": "DIAGNOSTIC_ONLY",
    "optimisation_report_metrics": "DIAGNOSTIC_ONLY",
    "optimisation_report_pdf_exported": "DIAGNOSTIC_ONLY",
    "optimisation_report_qt_window_created": "DIAGNOSTIC_ONLY",
    "optimisation_report_section_count": "DIAGNOSTIC_ONLY",
    "optimisation_report_sections": "DIAGNOSTIC_ONLY",
    "phase_16_unified_regen_ecosystem_allowed": "DIAGNOSTIC_ONLY",
    "optimisation_report_backend_": "DIAGNOSTIC_ONLY",
    "optimisation_report_": "DIAGNOSTIC_ONLY",
    "phase_16_": "DIAGNOSTIC_ONLY",
    "phase_15c_": "DIAGNOSTIC_ONLY",
    "phase_15d_": "DIAGNOSTIC_ONLY",
    "regen_evolution_tree_": "DIAGNOSTIC_ONLY",
    "evolution_tree_": "DIAGNOSTIC_ONLY",
    "phase_15b_": "DIAGNOSTIC_ONLY",
    "phase_15c_": "DIAGNOSTIC_ONLY",
    "regen_candidate_comparison_": "DIAGNOSTIC_ONLY",
    "candidate_comparison_": "DIAGNOSTIC_ONLY",
    "phase_15a_": "DIAGNOSTIC_ONLY",
    "phase_15b_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_viewer_": "DIAGNOSTIC_ONLY",
    "regen_generation_viewer_": "DIAGNOSTIC_ONLY",
    "regen_candidate_viewer_": "DIAGNOSTIC_ONLY",
    "regen_improvement_viewer_": "DIAGNOSTIC_ONLY",
    "optimisation_viewer_": "DIAGNOSTIC_ONLY",
    "phase_14f_": "DIAGNOSTIC_ONLY",
    "phase_14_runtime_backend_": "DIAGNOSTIC_ONLY",
    "phase_15a_": "DIAGNOSTIC_ONLY",
    "regen_runtime_optimisation_completion_": "DIAGNOSTIC_ONLY",
    "regen_runtime_optimisation_backend_": "DIAGNOSTIC_ONLY",
    "regen_runtime_final_": "DIAGNOSTIC_ONLY",
    "runtime_optimisation_": "DIAGNOSTIC_ONLY",
    "regen_runtime_optimisation_complete": "DIAGNOSTIC_ONLY",
    "phase_14e_": "DIAGNOSTIC_ONLY",
    "regen_runtime_convergence_": "DIAGNOSTIC_ONLY",
    "regen_runtime_improvement_": "DIAGNOSTIC_ONLY",
    "regen_runtime_stagnation_": "DIAGNOSTIC_ONLY",
    "regen_runtime_stop_condition_": "DIAGNOSTIC_ONLY",
    "runtime_current_best_": "DIAGNOSTIC_ONLY",
    "runtime_previous_best_": "DIAGNOSTIC_ONLY",
    "runtime_generation_improvement": "DIAGNOSTIC_ONLY",
    "runtime_improvement_": "DIAGNOSTIC_ONLY",
    "runtime_stagnated_": "DIAGNOSTIC_ONLY",
    "runtime_stagnation_": "DIAGNOSTIC_ONLY",
    "runtime_convergence_": "DIAGNOSTIC_ONLY",
    "runtime_max_generation_": "DIAGNOSTIC_ONLY",
    "runtime_stop_": "DIAGNOSTIC_ONLY",
    "runtime_baseline_best_": "DIAGNOSTIC_ONLY",
    "runtime_previous_stagnation_": "DIAGNOSTIC_ONLY",
    "runtime_max_generations": "DIAGNOSTIC_ONLY",
    "regen_runtime_parent_lineage": "DIAGNOSTIC_ONLY",
    "regen_runtime_parent_lineage_count": "DIAGNOSTIC_ONLY",
    "runtime_next_generation_number": "DIAGNOSTIC_ONLY",
    "regen_runtime_parent_lineage": "DIAGNOSTIC_ONLY",
    "runtime_next_generation_": "DIAGNOSTIC_ONLY",
    "phase_14d_": "DIAGNOSTIC_ONLY",
    "regen_runtime_evolution_": "DIAGNOSTIC_ONLY",
    "regen_runtime_generation_": "DIAGNOSTIC_ONLY",
    "regen_runtime_population_": "DIAGNOSTIC_ONLY",
    "runtime_generation_": "DIAGNOSTIC_ONLY",
    "runtime_parent_lineage": "DIAGNOSTIC_ONLY",
    "phase_14c_": "DIAGNOSTIC_ONLY",
    "regen_runtime_selection_": "DIAGNOSTIC_ONLY",
    "regen_runtime_parent_pool": "DIAGNOSTIC_ONLY",
    "runtime_selection_": "DIAGNOSTIC_ONLY",
    "runtime_candidate_": "DIAGNOSTIC_ONLY",
    "phase_14b_": "DIAGNOSTIC_ONLY",
    "regen_runtime_candidate_evaluation_": "DIAGNOSTIC_ONLY",
    "regen_runtime_candidate_solver_": "DIAGNOSTIC_ONLY",
    "regen_runtime_candidate_acceptance_": "DIAGNOSTIC_ONLY",
    "regen_runtime_candidate_generation_": "DIAGNOSTIC_ONLY",
    "regen_runtime_candidate_live_": "DIAGNOSTIC_ONLY",
    "phase_14_runtime_optimisation_allowed": "DIAGNOSTIC_ONLY",
    "regen_evolution_engine_execution_allowed": "DIAGNOSTIC_ONLY",
    "regen_generation_advance_execution_allowed": "DIAGNOSTIC_ONLY",

    "phase_13k_": "DIAGNOSTIC_ONLY",
    "phase_13l_": "DIAGNOSTIC_ONLY",
    "phase_14a_": "DIAGNOSTIC_ONLY",
    "phase_14b_": "DIAGNOSTIC_ONLY",
    "phase_14c_": "DIAGNOSTIC_ONLY",
    "phase_14d_": "DIAGNOSTIC_ONLY",
    "phase_14e_": "DIAGNOSTIC_ONLY",
    "phase_14f_": "DIAGNOSTIC_ONLY",
    "selection_": "DIAGNOSTIC_ONLY",
    "selected_for_parent_pool": "DIAGNOSTIC_ONLY",
    "survives_generation": "DIAGNOSTIC_ONLY",
    "regen_optimisation_selection_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_parent_pool": "DIAGNOSTIC_ONLY",
    "regen_optimisation_parent_pool_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_foundation_": "DIAGNOSTIC_ONLY",
    "optimisation_foundation_": "DIAGNOSTIC_ONLY",
    "regen_runtime_mutation_": "DIAGNOSTIC_ONLY",
    "regen_runtime_candidate_": "DIAGNOSTIC_ONLY",

    "design_iteration_": "AXIAL_REPORT_ONLY",
    "regen_optimisation_proof_": "AXIAL_REPORT_ONLY",
    "failure_root_cause_": "AXIAL_REPORT_ONLY",
    "recommendation_explanation_": "RECOMMENDATION_ONLY",
    "recommendation_owner_": "RECOMMENDATION_ONLY",
    "before_after_comparison_": "AXIAL_REPORT_ONLY",
    "report_dashboard_": "DIAGNOSTIC_ONLY",
    "foundation_regression_": "DIAGNOSTIC_ONLY",
    "foundation_result_key_audit_": "DIAGNOSTIC_ONLY",
    "output_visibility_architecture_": "DIAGNOSTIC_ONLY",
    "foundation_attachment_": "DIAGNOSTIC_ONLY",
    "foundation_pipeline_": "DIAGNOSTIC_ONLY",
    "startup_health_": "DIAGNOSTIC_ONLY",
    "benchmark_": "DIAGNOSTIC_ONLY",
    "engine_reproduction_": "DIAGNOSTIC_ONLY",
    "recommendation_ownership_final_audit_": "DIAGNOSTIC_ONLY",
    "regen_source_validation_": "VALIDATION_ONLY",
    "regen_conservative_validation_gate_": "VALIDATION_ONLY",
    "regen_provenance_": "VALIDATION_ONLY",
    "regen_property_table_owner_": "VALIDATION_ONLY",
    "regen_validation_master_gate_": "VALIDATION_ONLY",
    "regen_completion_audit_": "DIAGNOSTIC_ONLY",
    "stage_v": "DIAGNOSTIC_ONLY",
    "regen_scalability_": "DIAGNOSTIC_ONLY",
    "stage_w": "DIAGNOSTIC_ONLY",
    "real_engine_benchmark_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_profile_": "DIAGNOSTIC_ONLY",
    "phase_8a_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_candidate_generator_": "DIAGNOSTIC_ONLY",
    "phase_8b_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_scoring_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_score_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_scored_": "DIAGNOSTIC_ONLY",
    "phase_8c_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_failure_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_blocking_": "DIAGNOSTIC_ONLY",
    "phase_8d_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_report_": "DIAGNOSTIC_ONLY",
    "phase_8e_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_recommendation_": "DIAGNOSTIC_ONLY",
    "phase_8f_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_master_gate_": "DIAGNOSTIC_ONLY",
    "phase_8g_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_completion_audit_": "DIAGNOSTIC_ONLY",
    "phase_8h_": "DIAGNOSTIC_ONLY",
    "stage_8_regen_optimisation_": "DIAGNOSTIC_ONLY",
    "material_property_interpolation_": "DIAGNOSTIC_ONLY",
    "phase_9a_": "DIAGNOSTIC_ONLY",
    "material_source_provenance_": "DIAGNOSTIC_ONLY",
    "correlation_source_provenance_": "DIAGNOSTIC_ONLY",
    "phase_9b_": "DIAGNOSTIC_ONLY",
    "material_source_quality_ranking_": "DIAGNOSTIC_ONLY",
    "phase_9c_": "DIAGNOSTIC_ONLY",
    "material_validation_": "DIAGNOSTIC_ONLY",
    "phase_9d_": "DIAGNOSTIC_ONLY",
    "material_completion_audit_": "DIAGNOSTIC_ONLY",
    "phase_9e_": "DIAGNOSTIC_ONLY",
    "coating_source_provenance_": "DIAGNOSTIC_ONLY",
    "phase_9f_": "DIAGNOSTIC_ONLY",
    "coating_validation_": "DIAGNOSTIC_ONLY",
    "phase_9g_": "DIAGNOSTIC_ONLY",
    "material_and_coating_foundation_audit_": "DIAGNOSTIC_ONLY",
    "phase_9h_": "DIAGNOSTIC_ONLY",
    "stage_9_material_and_coating_foundation_": "DIAGNOSTIC_ONLY",
    "stage_9_material_foundation_": "DIAGNOSTIC_ONLY",
    "foundation_verification_": "DIAGNOSTIC_ONLY",
    "phase_10a_": "DIAGNOSTIC_ONLY",
    "stage_10_solver_integration_": "DIAGNOSTIC_ONLY",
    "phase_10b1_": "DIAGNOSTIC_ONLY",
    "stage_10b_material_property_": "DIAGNOSTIC_ONLY",
    "phase_10b2_": "DIAGNOSTIC_ONLY",
    "stage_10b_material_thermal_conductivity_": "DIAGNOSTIC_ONLY",
    "phase_10b3_": "DIAGNOSTIC_ONLY",
    "stage_10b_material_specific_heat_": "DIAGNOSTIC_ONLY",
    "phase_10b4_": "DIAGNOSTIC_ONLY",
    "stage_10b_material_density_": "DIAGNOSTIC_ONLY",
    "phase_10b5_": "DIAGNOSTIC_ONLY",
    "stage_10b_material_temperature_limit_": "DIAGNOSTIC_ONLY",
    "phase_10b6_": "DIAGNOSTIC_ONLY",
    "stage_10b_material_strength_limit_": "DIAGNOSTIC_ONLY",
    "phase_10b7_": "DIAGNOSTIC_ONLY",
    "stage_10b_material_integration_validation_": "DIAGNOSTIC_ONLY",
    "phase_10b8_": "DIAGNOSTIC_ONLY",
    "stage_10b_material_integration_": "DIAGNOSTIC_ONLY",
    "phase_10c1_": "DIAGNOSTIC_ONLY",
    "stage_10c_coating_property_": "DIAGNOSTIC_ONLY",
    "phase_10c2_": "DIAGNOSTIC_ONLY",
    "stage_10c_coating_thermal_conductivity_": "DIAGNOSTIC_ONLY",
    "phase_10c3_": "DIAGNOSTIC_ONLY",
    "stage_10c_coating_thickness_": "DIAGNOSTIC_ONLY",
    "phase_10c4_": "DIAGNOSTIC_ONLY",
    "stage_10c_coating_thermal_resistance_": "DIAGNOSTIC_ONLY",
    "phase_10c5_": "DIAGNOSTIC_ONLY",
    "stage_10c_coating_temperature_limit_": "DIAGNOSTIC_ONLY",
    "phase_10c6_": "DIAGNOSTIC_ONLY",
    "stage_10c_bond_coat_": "DIAGNOSTIC_ONLY",
    "phase_10c7_": "DIAGNOSTIC_ONLY",
    "stage_10c_coating_integration_": "DIAGNOSTIC_ONLY",
    "phase_10c8_": "DIAGNOSTIC_ONLY",
    "stage_10c_coating_integration_": "DIAGNOSTIC_ONLY",
    "phase_10d_verification_": "DIAGNOSTIC_ONLY",
    "phase_10d1_": "DIAGNOSTIC_ONLY",
    "stage_10d_temperature_": "DIAGNOSTIC_ONLY",
    "phase_10d2_": "DIAGNOSTIC_ONLY",
    "stage_10d_material_conductivity_": "DIAGNOSTIC_ONLY",
    "phase_10d3_": "DIAGNOSTIC_ONLY",
    "stage_10d_specific_heat_": "DIAGNOSTIC_ONLY",
    "phase_10d4_": "DIAGNOSTIC_ONLY",
    "stage_10d_density_coolant_property_": "DIAGNOSTIC_ONLY",
    "phase_10d5_": "DIAGNOSTIC_ONLY",
    "stage_10d_coating_thermal_": "DIAGNOSTIC_ONLY",
    "phase_10d6_": "DIAGNOSTIC_ONLY",
    "stage_10d_bond_coat_": "DIAGNOSTIC_ONLY",
    "phase_10d7_": "DIAGNOSTIC_ONLY",
    "stage_10d_temperature_dependent_solver_": "DIAGNOSTIC_ONLY",
    "phase_11a1_": "DIAGNOSTIC_ONLY",
    "stage_11a_regen_geometry_constraint_discovery_": "DIAGNOSTIC_ONLY",
    "phase_11a2_": "DIAGNOSTIC_ONLY",
    "stage_11a_regen_geometry_constraint_validation_": "DIAGNOSTIC_ONLY",
    "stage_11a_regen_geometry_constraint_engineering_": "DIAGNOSTIC_ONLY",
    "phase_11a3_": "DIAGNOSTIC_ONLY",
    "stage_11a_regen_geometry_failure_explanation_": "DIAGNOSTIC_ONLY",
    "phase_11a4_": "DIAGNOSTIC_ONLY",
    "stage_11a_regen_geometry_recommendation_": "DIAGNOSTIC_ONLY",
    "stage_11a_regen_geometry_recommendation_engineering_": "DIAGNOSTIC_ONLY",
    "phase_11a5_": "DIAGNOSTIC_ONLY",
    "stage_11a_regen_geometry_apply_recommendation_": "DIAGNOSTIC_ONLY",
    "phase_11a6_": "DIAGNOSTIC_ONLY",
    "stage_11a_regen_geometry_output_architecture_": "DIAGNOSTIC_ONLY",
    "phase_11a8_": "DIAGNOSTIC_ONLY",
    "stage_11a_regen_geometry_candidate_acceptance_": "DIAGNOSTIC_ONLY",
    "foundation_save_load_": "DIAGNOSTIC_ONLY",
    "foundation_ui_launch_": "DIAGNOSTIC_ONLY",
    "foundation_final_signoff_": "DIAGNOSTIC_ONLY",
    "foundation_completion_handover_": "DIAGNOSTIC_ONLY",
    "low_confidence_public_benchmark_blocks_stage_w": "DIAGNOSTIC_ONLY",
    "out_of_band_public_benchmark_blocks_stage_w": "DIAGNOSTIC_ONLY",

    # Phase 11C.1 autonomous regen optimisation input-audit keys.
    "regen_autonomous_optimisation_input_": "DIAGNOSTIC_ONLY",
    "regen_autonomous_optimisation_runtime_": "DIAGNOSTIC_ONLY",
    "regen_autonomous_optimisation_solver_": "DIAGNOSTIC_ONLY",
    "regen_autonomous_optimisation_live_": "DIAGNOSTIC_ONLY",
    "regen_autonomous_optimisation_candidate_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_session_owner_": "DIAGNOSTIC_ONLY",
    "phase_11c_1_": "DIAGNOSTIC_ONLY",
    "phase_11c_2_": "DIAGNOSTIC_ONLY",
    "phase_11c_3_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_session_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_runtime_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_generation_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_mutation_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_candidate_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_live_": "DIAGNOSTIC_ONLY",
    "regen_optimisation_report_owner_": "DIAGNOSTIC_ONLY",
}


EXPECTED_SUFFIX_VISIBILITY = {
    "_attachment_status": "DIAGNOSTIC_ONLY",
    "_attachment_message": "DIAGNOSTIC_ONLY",
    "_attachment_error_type": "DIAGNOSTIC_ONLY",
    "_attachment_traceback": "DIAGNOSTIC_ONLY",
}


KNOWN_DEVELOPMENT_KEYS = {
    "regen_recommendation_viewer_",
    "regen_recommendation_feed_repair_",
    "regen_ranking_owner_source_repair_",
    "phase_16j3e_",
    "phase_16j3f_",
    "regen_ranking_input_feed_bridge_",
    "phase_16j3d_",
    "phase_16j3e_",
    "regen_candidate_base_geometry_population_repair_",
    "phase_16j3c_",
    "phase_16j3d_",
    "regen_candidate_generator_data_source_repair_",
    "phase_16j3a_",
    "phase_16j3b_",
    "regen_coolant_flow_activation_layer_",
    "phase_16j2a_",
    "phase_16j2b_",
    "regen_candidate_ranking_payload_bridge_",
    "phase_16j1_",
    "phase_16k_",
    "regen_candidate_ranking_inspector_",
    "phase_16j_",
    "phase_16k_",
    "coolant_mass_flow_fraction",
    "regen_architecture_visibility_audit_",
    "phase_16i_",
    "phase_16j_",
    "regen_candidate_population_inspector_",
    "regen_coolant_property_resolution_repair_",
    "recommended_geometry_status_previous",
    "regen_input_mapping_repair_",
    "regen_workflow_",
    "phase_16f_",
    "regen_completion_",
    "regen_system_",
    "leaf_regen_",
    "phase_16e_",
    "phase_16f_",
    "regen_system_signoff_",
    "phase_16d_",
    "phase_16e_",
    "regen_unified_validation_",
    "unified_regen_validation_",
    "phase_16c_",
    "phase_16d_",
    "regen_unified_report_",
    "unified_regen_report_",
    "phase_16b_",
    "phase_16c_",
    "regen_unified_viewer_",
    "unified_regen_viewer_",
    "phase_16a_",
    "phase_16b_",
    "regen_unified_",
    "unified_regen_",
    "optimisation_report_backend_payload",
    "optimisation_report_backend_report",
    "optimisation_report_backend_source_count",
    "optimisation_report_backend_summary",
    "optimisation_report_history",
    "optimisation_report_html_exported",
    "optimisation_report_metrics",
    "optimisation_report_pdf_exported",
    "optimisation_report_qt_window_created",
    "optimisation_report_section_count",
    "optimisation_report_sections",
    "phase_16_unified_regen_ecosystem_allowed",
    "optimisation_report_backend_",
    "optimisation_report_",
    "phase_16_",
    "phase_15d_",
    "phase_16_",
    "regen_optimisation_report_",
    "optimisation_report_",
    "phase_15c_",
    "phase_15d_",
    "regen_evolution_tree_",
    "evolution_tree_",
    "phase_15b_",
    "phase_15c_",
    "regen_candidate_comparison_",
    "candidate_comparison_",
    "phase_15a_",
    "phase_15b_",
    "regen_optimisation_viewer_",
    "regen_generation_viewer_",
    "regen_candidate_viewer_",
    "regen_improvement_viewer_",
    "optimisation_viewer_",
    "phase_14f_",
    "phase_14_runtime_backend_",
    "phase_15a_",
    "regen_runtime_optimisation_completion_",
    "regen_runtime_optimisation_backend_",
    "regen_runtime_final_",
    "runtime_optimisation_",
    "regen_runtime_optimisation_complete",
    "phase_14e_",
    "regen_runtime_convergence_",
    "regen_runtime_improvement_",
    "regen_runtime_stagnation_",
    "regen_runtime_stop_condition_",
    "runtime_current_best_",
    "runtime_previous_best_",
    "runtime_generation_improvement",
    "runtime_improvement_",
    "runtime_stagnated_",
    "runtime_stagnation_",
    "runtime_convergence_",
    "runtime_max_generation_",
    "runtime_stop_",
    "runtime_baseline_best_",
    "runtime_previous_stagnation_",
    "runtime_max_generations",
    "regen_runtime_parent_lineage",
    "regen_runtime_parent_lineage_count",
    "runtime_next_generation_number",
    "regen_runtime_parent_lineage",
    "runtime_next_generation_",
    "phase_14d_",
    "regen_runtime_evolution_",
    "regen_runtime_generation_",
    "regen_runtime_population_",
    "runtime_generation_",
    "runtime_parent_lineage",
    "phase_14c_",
    "regen_runtime_selection_",
    "regen_runtime_parent_pool",
    "runtime_selection_",
    "runtime_candidate_",
    "phase_14b_",
    "regen_runtime_candidate_evaluation_",
    "regen_runtime_candidate_solver_",
    "regen_runtime_candidate_acceptance_",
    "regen_runtime_candidate_generation_",
    "regen_runtime_candidate_live_",
    "phase_14_runtime_optimisation_allowed",
    "regen_evolution_engine_execution_allowed",
    "regen_generation_advance_execution_allowed",

    "phase_13k_",
    "phase_13l_",
    "phase_14a_",
    "phase_14b_",
    "phase_14c_",
    "phase_14d_",
    "phase_14e_",
    "phase_14f_",
    "selection_",
    "selected_for_parent_pool",
    "survives_generation",
    "regen_optimisation_selection_",
    "regen_optimisation_parent_pool",
    "regen_optimisation_parent_pool_",
    "regen_optimisation_foundation_",
    "optimisation_foundation_",
    "regen_runtime_mutation_",
    "regen_runtime_candidate_",

    "calculation_history",
    "foundation_input_coerced",
    "foundation_input_type",
    "foundation_pipeline_input_coerced",
    "foundation_pipeline_input_type",
    "foundation_attachment_pipeline_started",
    "foundation_attachment_pipeline_completed",
    "foundation_attachment_pipeline_started_at",
    "foundation_attachment_pipeline_completed_at",
    "foundation_attachment_pipeline_status",
    "foundation_attachment_benchmark_case",
    "foundation_attachment_summary",
    "foundation_attachment_audit",
    "loaded_project_startup_health_snapshot",
    "loaded_project_startup_health_snapshot_preserved",
    "live_startup_health_used_after_load",
    "stage_t_recommendation_ownership_complete",
    "stage_u_regen_validation_complete",
    "foundation_layer_verified",
}


def audit_result_keys(results):
    results = results if isinstance(results, dict) else {}

    registered_keys = []
    unregistered_keys = []
    known_development_keys = []
    visibility_counts = {}

    possible_pollution = []
    wrong_prefix_visibility = []

    for key in sorted(results.keys()):
        value = results.get(key)

        if value is None:
            continue

        registered = key in VARIABLES
        known_development = _is_known_development_key(key)

        expected_visibility = _expected_visibility_from_key(key)

        if registered:
            registered_keys.append(key)
            visibility = get_output_visibility(key)
        elif known_development:
            known_development_keys.append(key)
            visibility = "DIAGNOSTIC_ONLY"
        elif expected_visibility:
            known_development_keys.append(key)
            visibility = expected_visibility
        else:
            dynamic_seed = None
            if classify_dynamic_key is not None:
                dynamic_seed = classify_dynamic_key(key, value)

            if dynamic_seed is not None:
                known_development_keys.append(key)
                visibility_counts[dynamic_seed.visibility] = (
                    visibility_counts.get(dynamic_seed.visibility, 0) + 1
                )
            else:
                unregistered_keys.append(key)
            visibility = "UNREGISTERED"

        visibility_counts[visibility] = visibility_counts.get(visibility, 0) + 1

        if visibility == "SCALAR_OUTPUT":
            if _looks_like_report_or_diagnostic_key(key, value):
                possible_pollution.append(key)

        if expected_visibility:
            if visibility not in (expected_visibility, "DIAGNOSTIC_ONLY"):
                wrong_prefix_visibility.append({
                    "key": key,
                    "expected_visibility": expected_visibility,
                    "actual_visibility": visibility,
                })

    status = "PASS"

    if unregistered_keys:
        status = "WARN_UNREGISTERED_KEYS"

    if wrong_prefix_visibility:
        status = "FAIL_WRONG_VISIBILITY"

    if possible_pollution:
        status = "FAIL_MAIN_OUTPUT_POLLUTION"

    text = build_result_key_audit_text(
        status=status,
        registered_keys=registered_keys,
        unregistered_keys=unregistered_keys,
        known_development_keys=known_development_keys,
        visibility_counts=visibility_counts,
        possible_pollution=possible_pollution,
        wrong_prefix_visibility=wrong_prefix_visibility,
    )

    return {
        "foundation_result_key_audit_status": status,
        "foundation_result_key_audit_registered_count": len(registered_keys),
        "foundation_result_key_audit_unregistered_count": len(unregistered_keys),
        "foundation_result_key_audit_known_development_count": len(known_development_keys),
        "foundation_result_key_audit_visibility_counts": visibility_counts,
        "foundation_result_key_audit_possible_pollution": possible_pollution,
        "foundation_result_key_audit_wrong_visibility": wrong_prefix_visibility,
        "foundation_result_key_audit_known_development_keys": known_development_keys,
        "foundation_result_key_audit_text": text,
    }


def attach_foundation_result_key_audit(results):
    if results is None:
        return results

    audit = audit_result_keys(results)

    for key, value in audit.items():
        results[key] = value

    return results


def _is_known_development_key(key):
    key_l = str(key).lower()

    phase_13_to_14_prefixes = (
        "phase_13k_",
        "phase_13l_",
        "phase_14a_",
        "phase_14b_",
        "phase_14c_",
        "phase_14d_",
        "phase_14e_",
        "phase_14f_",
        "selection_",
        "regen_optimisation_selection_",
        "regen_optimisation_parent_pool",
        "regen_optimisation_foundation_",
        "optimisation_foundation_",
        "regen_runtime_mutation_",
        "regen_runtime_candidate_",
    )

    if key_l.startswith(phase_13_to_14_prefixes):
        return True

    if key_l in {
        "selected_for_parent_pool",
        "survives_generation",
        "selection_rank",
        "selection_score",
    }:
        return True


    if key_l in KNOWN_DEVELOPMENT_KEYS:
        return True


    # Phase 11C.5 completion audit and 11D readiness keys.
    # These are architecture/sign-off keys, not scalar outputs.
    if key_l in {
        "phase_11c_complete",
        "regen_optimisation_architecture_complete",
        "regen_optimisation_completion_audit",
    }:
        return True


    # Phase 11D.1 runtime optimisation input-gate architecture keys.
    # These are runtime architecture gate keys, not scalar outputs.
    if key_l == "regen_runtime_optimisation_input_gate":
        return True

    if key_l.startswith((
        "phase_11d_1_",
        "phase_11d_2_",
        "regen_runtime_optimisation_input_gate_",
        "regen_runtime_optimisation_runtime_owner_",
        "regen_runtime_optimisation_architecture_gate_",
    )):
        return True

    if key_l.startswith((
        "phase_11c_5_",
        "phase_11d_",
        "regen_runtime_optimisation_architecture_",
        "regen_optimisation_completion_audit_",
        "regen_optimisation_architecture_",
    )):
        return True


    # Phase 11C.2 exact optimisation session object key.
    # This key stores the session dictionary itself.
    if key_l == "regen_optimisation_session":
        return True


    # Phase 11C.3 optimisation report-owner architecture keys.
    # These are report/diagnostic ownership keys, not scalar outputs.
    if key_l == "regen_optimisation_report_bundle":
        return True


    # Phase 11C.4 optimisation registration-owner architecture keys.
    # These are registry/report/session ownership keys, not scalar outputs.
    if key_l == "regen_optimisation_registry":
        return True

    if key_l.startswith((
        "phase_11c_5_",
        "regen_optimisation_registration_owner_",
        "regen_optimisation_completion_audit_",
    )):
        return True

    if key_l.startswith((
        "phase_11c_4_",
        "regen_optimisation_report_owner_",
        "regen_optimisation_registration_owner_",
    )):
        return True


    # Phase 11C autonomous optimisation/session architecture keys.
    # These are diagnostic/report/session ownership keys, not scalar outputs.
    if key_l.startswith((
        "phase_11c_1_",
        "phase_11c_2_",
        "phase_11c_3_",
        "regen_autonomous_optimisation_input_",
        "regen_autonomous_optimisation_runtime_",
        "regen_autonomous_optimisation_solver_",
        "regen_autonomous_optimisation_live_",
        "regen_autonomous_optimisation_candidate_",
        "regen_optimisation_session_",
        "regen_optimisation_session_owner_",
        "regen_optimisation_runtime_",
        "regen_optimisation_generation_",
        "regen_optimisation_mutation_",
        "regen_optimisation_candidate_",
        "regen_optimisation_live_",
        "regen_optimisation_report_owner_",
    )):
        return True

    if key_l.startswith("foundation_attachment_"):
        return True

    if key_l.startswith("foundation_result_key_audit_"):
        return True

    if key_l.startswith("foundation_verification_"):
        return True

    # Stage V regen scalability architecture keys.
    # These are structural/report/diagnostic keys, not scalar engineering outputs.
    if key_l.startswith("regen_scalability_"):
        return True

    if key_l.startswith("stage_v"):
        return True

    # Stage W real-engine benchmark architecture keys.
    if key_l.startswith("real_engine_benchmark_"):
        return True

    if key_l.startswith("stage_w"):
        return True

    # Phase 8A regen optimisation profile foundation keys.
    if key_l.startswith("regen_optimisation_profile_"):
        return True

    if key_l.startswith("phase_8a_"):
        return True

    # Phase 8B regen optimisation candidate generator foundation keys.
    if key_l.startswith("regen_optimisation_candidate_generator_"):
        return True

    if key_l.startswith("phase_8b_"):
        return True

    # Phase 8C regen optimisation scoring owner keys.
    if key_l.startswith("regen_optimisation_scoring_"):
        return True

    if key_l.startswith("regen_optimisation_score_"):
        return True

    if key_l.startswith("regen_optimisation_scored_"):
        return True

    if key_l.startswith("phase_8c_"):
        return True

    # Phase 8D regen optimisation failure owner keys.
    if key_l.startswith("regen_optimisation_failure_"):
        return True

    if key_l.startswith("regen_optimisation_blocking_"):
        return True

    if key_l.startswith("phase_8d_"):
        return True

    # Phase 8E regen optimisation report owner keys.
    if key_l.startswith("regen_optimisation_report_"):
        return True

    if key_l.startswith("phase_8e_"):
        return True

    # Phase 8F regen optimisation recommendation owner keys.
    if key_l.startswith("regen_optimisation_recommendation_"):
        return True

    if key_l.startswith("phase_8f_"):
        return True

    # Phase 8G regen optimisation master gate keys.
    if key_l.startswith("regen_optimisation_master_gate_"):
        return True

    if key_l.startswith("phase_8g_"):
        return True

    # Phase 8H regen optimisation completion audit keys.
    if key_l.startswith("regen_optimisation_completion_audit_"):
        return True

    if key_l.startswith("phase_8h_"):
        return True

    if key_l.startswith("stage_8_regen_optimisation_"):
        return True

    # Phase 9A material property interpolation owner keys.
    if key_l.startswith("material_property_interpolation_"):
        return True

    if key_l.startswith("phase_9a_"):
        return True

    # Phase 9B material source / provenance owner keys.
    if key_l.startswith("material_source_provenance_"):
        return True

    # PFQ-2E correlation source / provenance owner keys.
    if key_l.startswith("correlation_source_provenance_"):
        return True

    if key_l.startswith("phase_9b_"):
        return True

    # Phase 9C material source quality ranking owner keys.
    if key_l.startswith("material_source_quality_ranking_"):
        return True

    if key_l.startswith("phase_9c_"):
        return True

    # Phase 9D material validation owner keys.
    if key_l.startswith("material_validation_"):
        return True

    if key_l.startswith("phase_9d_"):
        return True

    # Phase 9E material completion audit keys.
    if key_l.startswith("material_completion_audit_"):
        return True

    if key_l.startswith("phase_9e_"):
        return True

    if key_l.startswith("stage_9_material_foundation_"):
        return True

    # Phase 9F coating source / provenance owner keys.
    if key_l.startswith("coating_source_provenance_"):
        return True

    if key_l.startswith("phase_9f_"):
        return True

    # Phase 9G coating validation owner keys.
    if key_l.startswith("coating_validation_"):
        return True

    if key_l.startswith("phase_9g_"):
        return True

    # Phase 9H material & coating foundation audit keys.
    if key_l.startswith("material_and_coating_foundation_audit_"):
        return True

    if key_l.startswith("phase_9h_"):
        return True

    if key_l.startswith("stage_9_material_and_coating_foundation_"):
        return True

    # Phase 10A sourced material/coating solver integration planning keys.
    if key_l.startswith("phase_10a_"):
        return True

    if key_l.startswith("stage_10_solver_integration_"):
        return True

    # Phase 10B.1 material property consumption audit keys.
    if key_l.startswith("phase_10b1_"):
        return True

    if key_l.startswith("stage_10b_material_property_"):
        return True

    # Phase 10B.2 material thermal conductivity integration keys.
    if key_l.startswith("phase_10b2_"):
        return True

    if key_l.startswith("stage_10b_material_thermal_conductivity_"):
        return True

    if key_l in (
        "sourced_wall_thermal_conductivity",
        "wall_thermal_conductivity_source",
        "material_thermal_conductivity",
    ):
        return True

    # Phase 10B.3 material specific heat integration keys.
    if key_l.startswith("phase_10b3_"):
        return True

    if key_l.startswith("stage_10b_material_specific_heat_"):
        return True

    if key_l in (
        "material_specific_heat_cp",
        "sourced_material_specific_heat_cp",
        "material_specific_heat_cp_source",
    ):
        return True

    # Phase 10B.4 material density integration keys.
    if key_l.startswith("phase_10b4_"):
        return True

    if key_l.startswith("stage_10b_material_density_"):
        return True

    if key_l in (
        "material_density",
        "sourced_material_density",
        "material_density_source",
    ):
        return True

    # Phase 10B.5 material temperature limit integration keys.
    if key_l.startswith("phase_10b5_"):
        return True

    if key_l.startswith("stage_10b_material_temperature_limit_"):
        return True

    if key_l in (
        "effective_material_temperature_limit",
        "material_temperature_limit_source",
        "material_temperature_limit_margin",
        "material_temperature_limit_pass",
    ):
        return True

    # Phase 10B.6 material strength limit integration keys.
    if key_l.startswith("phase_10b6_"):
        return True

    if key_l.startswith("stage_10b_material_strength_limit_"):
        return True

    if key_l in (
        "effective_material_yield_strength",
        "material_strength_limit_source",
        "material_allowable_wall_stress",
        "material_structural_margin",
        "material_structural_pass",
    ):
        return True

    # Phase 10B.7 material integration validation keys.
    if key_l.startswith("phase_10b7_"):
        return True

    if key_l.startswith("stage_10b_material_integration_validation_"):
        return True

    # Phase 10B.8 material integration completion audit keys.
    if key_l.startswith("phase_10b8_"):
        return True

    if key_l.startswith("stage_10b_material_integration_"):
        return True

    # Phase 10C.1 coating property consumption audit keys.
    if key_l.startswith("phase_10c1_"):
        return True

    if key_l.startswith("stage_10c_coating_property_"):
        return True

    # Phase 10C.2 coating thermal conductivity integration keys.
    if key_l.startswith("phase_10c2_"):
        return True

    if key_l.startswith("stage_10c_coating_thermal_conductivity_"):
        return True

    if key_l in (
        "coating_thermal_conductivity",
        "sourced_coating_thermal_conductivity",
        "coating_thermal_conductivity_source",
    ):
        return True

    # Phase 10C.3 coating thickness integration keys.
    if key_l.startswith("phase_10c3_"):
        return True

    if key_l.startswith("stage_10c_coating_thickness_"):
        return True

    if key_l in (
        "effective_coating_thickness",
        "sourced_coating_thickness",
        "coating_thickness_source",
    ):
        return True

    # Phase 10C.4 coating thermal resistance integration keys.
    if key_l.startswith("phase_10c4_"):
        return True

    if key_l.startswith("stage_10c_coating_thermal_resistance_"):
        return True

    if key_l in (
        "coating_thermal_resistance",
        "effective_coating_thermal_resistance",
        "sourced_coating_thermal_resistance",
        "coating_thermal_resistance_source",
    ):
        return True

    # Phase 10C.5 coating temperature limit integration keys.
    if key_l.startswith("phase_10c5_"):
        return True

    if key_l.startswith("stage_10c_coating_temperature_limit_"):
        return True

    if key_l in (
        "effective_coating_temperature_limit",
        "coating_max_temperature",
        "sourced_coating_temperature_limit",
        "coating_temperature_limit_source",
        "coating_temperature_limit_margin",
        "coating_temperature_limit_pass",
    ):
        return True

    # Phase 10C.6 bond coat integration keys.
    if key_l.startswith("phase_10c6_"):
        return True

    if key_l.startswith("stage_10c_bond_coat_"):
        return True

    if key_l in (
        "bond_coat_thermal_conductivity",
        "bond_coat_thickness",
        "bond_coat_thermal_resistance",
        "effective_bond_coat_thermal_resistance",
        "bond_coat_thermal_resistance_source",
        "bond_coat_temperature_limit",
        "effective_bond_coat_temperature_limit",
        "bond_coat_temperature_limit_source",
        "bond_coat_temperature_limit_margin",
        "bond_coat_temperature_limit_pass",
        "bond_coat_integration_active",
    ):
        return True

    # Phase 10C.7 coating integration validation keys.
    if key_l.startswith("phase_10c7_"):
        return True

    if key_l.startswith("stage_10c_coating_integration_"):
        return True

    # Phase 10C.8 coating integration completion audit keys.
    if key_l.startswith("phase_10c8_"):
        return True

    if key_l.startswith("stage_10c_coating_integration_"):
        return True

    # Phase 10D shared verification evidence keys.
    if key_l.startswith("phase_10d_verification_"):
        return True

    # Phase 10D.1 temperature dependency discovery audit keys.
    if key_l.startswith("phase_10d1_"):
        return True

    if key_l.startswith("stage_10d_temperature_"):
        return True

    # Phase 10D.2 material conductivity consumption audit keys.
    if key_l.startswith("phase_10d2_"):
        return True

    if key_l.startswith("stage_10d_material_conductivity_"):
        return True

    # Phase 10D.3 specific heat consumption audit keys.
    if key_l.startswith("phase_10d3_"):
        return True

    if key_l.startswith("stage_10d_specific_heat_"):
        return True

    # Phase 10D.4 density and coolant property consumption audit keys.
    if key_l.startswith("phase_10d4_"):
        return True

    if key_l.startswith("stage_10d_density_coolant_property_"):
        return True

    # Phase 10D.5 coating thermal consumption audit keys.
    if key_l.startswith("phase_10d5_"):
        return True

    if key_l.startswith("stage_10d_coating_thermal_"):
        return True

    # Phase 10D.6 bond-coat consumption audit keys.
    if key_l.startswith("phase_10d6_"):
        return True

    if key_l.startswith("stage_10d_bond_coat_"):
        return True

    # Phase 10D.7 temperature-dependent solver completion audit keys.
    if key_l.startswith("phase_10d7_"):
        return True

    if key_l.startswith("stage_10d_temperature_dependent_solver_"):
        return True

    # Phase 11A.1 regen geometry constraint discovery audit keys.
    if key_l.startswith("phase_11a1_"):
        return True

    if key_l.startswith("stage_11a_regen_geometry_constraint_discovery_"):
        return True

    # Phase 11A.2 regen geometry constraint validation keys.
    if key_l.startswith("phase_11a2_"):
        return True

    if key_l.startswith("stage_11a_regen_geometry_constraint_validation_"):
        return True

    if key_l.startswith("stage_11a_regen_geometry_constraint_engineering_"):
        return True

    # Phase 11A.3 regen geometry failure explanation keys.
    if key_l.startswith("phase_11a3_"):
        return True

    if key_l.startswith("stage_11a_regen_geometry_failure_explanation_"):
        return True

    # Phase 11A.4 regen geometry recommendation engine keys.
    if key_l.startswith("phase_11a4_"):
        return True

    if key_l.startswith("stage_11a_regen_geometry_recommendation_"):
        return True

    if key_l.startswith("stage_11a_regen_geometry_recommendation_engineering_"):
        return True

    # Phase 11A.5 apply recommended geometry keys.
    if key_l.startswith("phase_11a5_"):
        return True

    if key_l.startswith("stage_11a_regen_geometry_apply_recommendation_"):
        return True

    # Phase 11A.6 regen geometry output architecture keys.
    if key_l.startswith("phase_11a6_"):
        return True

    if key_l.startswith("stage_11a_regen_geometry_output_architecture_"):
        return True

    # Phase 11A.8 regen geometry candidate acceptance keys.
    if key_l.startswith("phase_11a8_"):
        return True

    if key_l.startswith("stage_11a_regen_geometry_candidate_acceptance_"):
        return True

    # Stage W public benchmark source-owner compatibility keys.
    if key_l.startswith("public_benchmark_source_"):
        return True

    if key_l.startswith("real_engine_benchmark_source_"):
        return True

    if key_l.startswith("stage_w1_real_engine_benchmark_source_owner_"):
        return True

    if key_l.startswith("stage_w2_public_benchmark_source_"):
        return True

    # Stage W numeric benchmark band-owner compatibility keys.
    if key_l.startswith("numeric_benchmark_band_"):
        return True

    if key_l.startswith("real_engine_benchmark_band_"):
        return True

    if key_l.startswith("stage_w3_numeric_benchmark_band_"):
        return True

    # Phase 11C.1 autonomous regen optimisation input-audit keys.
    # These are architecture/report/safety-gating keys, not scalar outputs.
    if key_l.startswith("regen_autonomous_optimisation_input_"):
        return True

    if key_l.startswith("regen_autonomous_optimisation_runtime_"):
        return True

    if key_l.startswith("regen_autonomous_optimisation_solver_"):
        return True

    if key_l.startswith("regen_autonomous_optimisation_live_"):
        return True

    if key_l.startswith("regen_autonomous_optimisation_candidate_"):
        return True

    if key_l.startswith("regen_optimisation_session_owner_"):
        return True

    if key_l.startswith("phase_11c_1_"):
        return True

    if key_l.startswith("phase_11c_2_"):
        return True

    if key_l.startswith("phase_11c_3_"):
        return True

    if key_l.startswith("regen_optimisation_session_"):
        return True

    if key_l.startswith("regen_optimisation_runtime_"):
        return True

    if key_l.startswith("regen_optimisation_generation_"):
        return True

    if key_l.startswith("regen_optimisation_mutation_"):
        return True

    if key_l.startswith("regen_optimisation_candidate_"):
        return True

    if key_l.startswith("regen_optimisation_live_"):
        return True

    if key_l.startswith("regen_optimisation_report_owner_"):
        return True

    # Foundation verification benchmark case flags.
    if key_l in {
        "low_confidence_public_benchmark_blocks_stage_w",
        "out_of_band_public_benchmark_blocks_stage_w",
    }:
        return True

    if key_l.startswith("foundation_verification_"):
        return True

    if key_l.startswith("real_engine_benchmark_reference_"):
        return True

    # Foundation verification diagnostic case controls.
    if key_l.startswith("foundation_verification_"):
        return True

    # Public benchmark diagnostic inputs used by Stage W verification cases.
    if key_l.startswith("public_benchmark_"):
        return True

    if key_l.startswith("benchmark_reference_"):
        return True

    if key_l.startswith("real_engine_benchmark_source_"):
        return True

    if key_l.startswith("real_engine_benchmark_reference_"):
        return True

    if key_l.startswith("real_engine_benchmark_tolerance_"):
        return True

    for suffix in EXPECTED_SUFFIX_VISIBILITY:
        if key_l.endswith(suffix):
            return True

    # Phase 11D.5 restored runtime optimisation architecture completion-audit keys.
    # These are architecture/sign-off keys, not scalar outputs.
    if key_l in {
        "phase_11e_runtime_execution_architecture_allowed",
        "regen_runtime_execution_architecture_allowed",
        "regen_runtime_optimisation_completion_audit_ready",
        "regen_runtime_optimisation_completion_audit_status",
    }:
        return True

    return False

def _expected_visibility_from_key(key):
    key_l = str(key).lower()

    phase_13_to_14_prefixes = (
        "phase_13k_",
        "phase_13l_",
        "phase_14a_",
        "phase_14b_",
        "phase_14c_",
        "phase_14d_",
        "phase_14e_",
        "phase_14f_",
        "selection_",
        "regen_optimisation_selection_",
        "regen_optimisation_parent_pool",
        "regen_optimisation_foundation_",
        "optimisation_foundation_",
        "regen_runtime_mutation_",
        "regen_runtime_candidate_",
    )

    if key_l.startswith(phase_13_to_14_prefixes):
        return True

    if key_l in {
        "selected_for_parent_pool",
        "survives_generation",
        "selection_rank",
        "selection_score",
    }:
        return True


    for prefix, visibility in EXPECTED_PREFIX_VISIBILITY.items():
        if key_l.startswith(prefix):
            return visibility

    for suffix, visibility in EXPECTED_SUFFIX_VISIBILITY.items():
        if key_l.endswith(suffix):
            return visibility

    return None


def _looks_like_report_or_diagnostic_key(key, value):
    key_l = str(key).lower()

    phase_13_to_14_prefixes = (
        "phase_13k_",
        "phase_13l_",
        "phase_14a_",
        "phase_14b_",
        "phase_14c_",
        "phase_14d_",
        "phase_14e_",
        "phase_14f_",
        "selection_",
        "regen_optimisation_selection_",
        "regen_optimisation_parent_pool",
        "regen_optimisation_foundation_",
        "optimisation_foundation_",
        "regen_runtime_mutation_",
        "regen_runtime_candidate_",
    )

    if key_l.startswith(phase_13_to_14_prefixes):
        return True

    if key_l in {
        "selected_for_parent_pool",
        "survives_generation",
        "selection_rank",
        "selection_score",
    }:
        return True


    suspicious_fragments = [
        "status",
        "reason",
        "report",
        "diagnostic",
        "validation",
        "proof",
        "root_cause",
        "recommendation",
        "benchmark",
        "startup_health",
        "attachment",
        "failure",
        "warning",
        "error",
        "text",
        "rows",
        "items",
        "audit",
        "summary",
        "traceback",
    ]

    if any(fragment in key_l for fragment in suspicious_fragments):
        return True

    if isinstance(value, (dict, list, tuple)):
        return True

    if isinstance(value, str) and len(value) > 80:
        return True

    return False


def build_result_key_audit_text(
        status,
        registered_keys,
        unregistered_keys,
        known_development_keys,
        visibility_counts,
        possible_pollution,
        wrong_prefix_visibility,
):
    lines = []
    lines.append("LEAF FOUNDATION RESULT KEY AUDIT")
    lines.append("================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Registered non-empty keys: {len(registered_keys)}")
    lines.append(f"Known development/evidence keys: {len(known_development_keys)}")
    lines.append(f"Unregistered non-empty keys: {len(unregistered_keys)}")
    lines.append("")

    lines.append("Visibility counts:")
    if visibility_counts:
        for visibility, count in sorted(visibility_counts.items()):
            lines.append(f"- {visibility}: {count}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("Possible Main Output pollution:")
    if possible_pollution:
        for key in possible_pollution:
            lines.append(f"- {key}")
    else:
        lines.append("- None detected.")
    lines.append("")

    lines.append("Wrong prefix/suffix visibility:")
    if wrong_prefix_visibility:
        for item in wrong_prefix_visibility:
            lines.append(
                f"- {item['key']}: expected {item['expected_visibility']}, "
                f"actual {item['actual_visibility']}"
            )
    else:
        lines.append("- None detected.")
    lines.append("")

    lines.append("Known development/evidence keys:")
    if known_development_keys:
        for key in known_development_keys:
            lines.append(f"- {key}")
    else:
        lines.append("- None detected.")
    lines.append("")

    lines.append("Unregistered keys requiring review:")
    if unregistered_keys:
        for key in unregistered_keys:
            lines.append(f"- {key}")
    else:
        lines.append("- None detected.")
    lines.append("")

    lines.append("Interpretation:")
    lines.append("- Registered keys are declared in the variable registry.")
    lines.append("- Known development/evidence keys are intentional structural/reporting keys.")
    lines.append("- Unregistered keys may still be valid during development, but should be reviewed.")
    lines.append("- Report/diagnostic/recommendation keys should not appear as SCALAR_OUTPUT.")
    lines.append("- This audit checks ownership hygiene, not physical correctness.")

    return "\n".join(lines)