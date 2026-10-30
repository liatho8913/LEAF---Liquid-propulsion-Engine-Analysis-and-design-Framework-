

















try:
    from regen_candidate_creation_completion_audit import (
        attach_regen_candidate_creation_completion_audit,
    )
except Exception:
    attach_regen_candidate_creation_completion_audit = None

try:
    from regen_candidate_creation_registration_owner import (
        attach_regen_candidate_creation_registration_owner,
    )
except Exception:
    attach_regen_candidate_creation_registration_owner = None

try:
    from regen_candidate_creation_report_owner import (
        attach_regen_candidate_creation_report_owner,
    )
except Exception:
    attach_regen_candidate_creation_report_owner = None

try:
    from regen_candidate_creation_session_owner import (
        attach_regen_candidate_creation_session_owner,
    )
except Exception:
    attach_regen_candidate_creation_session_owner = None

try:
    from regen_candidate_creation_input_audit import (
        attach_regen_candidate_creation_input_audit,
    )
except Exception:
    attach_regen_candidate_creation_input_audit = None

try:
    from regen_candidate_generation_completion_audit import (
        attach_regen_candidate_generation_completion_audit,
    )
except Exception:
    attach_regen_candidate_generation_completion_audit = None

try:
    from regen_candidate_generation_registration_owner import (
        attach_regen_candidate_generation_registration_owner,
    )
except Exception:
    attach_regen_candidate_generation_registration_owner = None

try:
    from regen_candidate_generation_report_owner import (
        attach_regen_candidate_generation_report_owner,
    )
except Exception:
    attach_regen_candidate_generation_report_owner = None

try:
    from regen_candidate_generation_session_owner import (
        attach_regen_candidate_generation_session_owner,
    )
except Exception:
    attach_regen_candidate_generation_session_owner = None

try:
    from regen_candidate_generation_input_gate import (
        attach_regen_candidate_generation_input_gate,
    )
except Exception:
    attach_regen_candidate_generation_input_gate = None

try:
    from regen_runtime_execution_completion_audit import (
        attach_regen_runtime_execution_completion_audit,
    )
except Exception:
    attach_regen_runtime_execution_completion_audit = None

try:
    from regen_runtime_execution_registration_owner import (
        attach_regen_runtime_execution_registration_owner,
    )
except Exception:
    attach_regen_runtime_execution_registration_owner = None

try:
    from regen_runtime_execution_report_owner import (
        attach_regen_runtime_execution_report_owner,
    )
except Exception:
    attach_regen_runtime_execution_report_owner = None

try:
    from regen_runtime_execution_session_owner import (
        attach_regen_runtime_execution_session_owner,
    )
except Exception:
    attach_regen_runtime_execution_session_owner = None

try:
    from regen_runtime_execution_input_gate import (
        attach_regen_runtime_execution_input_gate,
    )
except Exception:
    attach_regen_runtime_execution_input_gate = None

try:
    from regen_runtime_optimisation_completion_audit import (
        attach_regen_runtime_optimisation_completion_audit,
    )
except Exception:
    attach_regen_runtime_optimisation_completion_audit = None

try:
    from regen_runtime_optimisation_registration_owner import (
        attach_regen_runtime_optimisation_registration_owner,
    )
except Exception:
    attach_regen_runtime_optimisation_registration_owner = None

try:
    from regen_runtime_optimisation_report_owner import (
        attach_regen_runtime_optimisation_report_owner,
    )
except Exception:
    attach_regen_runtime_optimisation_report_owner = None


try:
    from regen_runtime_optimisation_input_gate import (
        attach_regen_runtime_optimisation_input_gate,
    )
except Exception:
    attach_regen_runtime_optimisation_input_gate = None

# Phase 11C.4 forced registration-owner import
try:
    from regen_optimisation_registration_owner import (
        attach_regen_optimisation_registration_owner,
    )
except Exception:
    attach_regen_optimisation_registration_owner = None


try:
    from optimisation.regen_optimisation_selection_ranking_engine import (
        attach_regen_optimisation_selection_ranking_engine,
    )
except Exception:
    attach_regen_optimisation_selection_ranking_engine = None

try:
    from regen_optimisation_selection_registry import (
        attach_regen_optimisation_selection_registry,
    )
except Exception:
    attach_regen_optimisation_selection_registry = None

try:
    from regen_optimisation_selection_validation_owner import (
        attach_regen_optimisation_selection_validation_owner,
    )
except Exception:
    attach_regen_optimisation_selection_validation_owner = None

try:
    from regen_optimisation_selection_parent_pool_builder import (
        attach_regen_optimisation_selection_parent_pool_builder,
    )
except Exception:
    attach_regen_optimisation_selection_parent_pool_builder = None

try:
    from regen_optimisation_selection_state_owner import (
        attach_regen_optimisation_selection_state_owner,
    )
except Exception:
    attach_regen_optimisation_selection_state_owner = None

try:
    from regen_optimisation_selection_history_owner import (
        attach_regen_optimisation_selection_history_owner,
    )
except Exception:
    attach_regen_optimisation_selection_history_owner = None

try:
    from regen_optimisation_selection_report_owner import (
        attach_regen_optimisation_selection_report_owner,
    )
except Exception:
    attach_regen_optimisation_selection_report_owner = None

try:
    from regen_optimisation_selection_completion_audit import (
        attach_regen_optimisation_selection_completion_audit,
    )
except Exception:
    attach_regen_optimisation_selection_completion_audit = None

try:
    from regen_optimisation_selection_master_gate import (
        attach_regen_optimisation_selection_master_gate,
    )
except Exception:
    attach_regen_optimisation_selection_master_gate = None


try:
    from regen_optimisation_foundation_registry import (
        attach_regen_optimisation_foundation_registry,
    )
except Exception:
    attach_regen_optimisation_foundation_registry = None

try:
    from regen_optimisation_foundation_validation_owner import (
        attach_regen_optimisation_foundation_validation_owner,
    )
except Exception:
    attach_regen_optimisation_foundation_validation_owner = None

try:
    from regen_optimisation_foundation_history_owner import (
        attach_regen_optimisation_foundation_history_owner,
    )
except Exception:
    attach_regen_optimisation_foundation_history_owner = None

try:
    from regen_optimisation_foundation_report_owner import (
        attach_regen_optimisation_foundation_report_owner,
    )
except Exception:
    attach_regen_optimisation_foundation_report_owner = None

try:
    from regen_optimisation_foundation_completion_audit import (
        attach_regen_optimisation_foundation_completion_audit,
    )
except Exception:
    attach_regen_optimisation_foundation_completion_audit = None

try:
    from regen_optimisation_foundation_master_gate import (
        attach_regen_optimisation_foundation_master_gate,
    )
except Exception:
    attach_regen_optimisation_foundation_master_gate = None


try:
    from regen_runtime_mutation_execution_registry import (
        attach_regen_runtime_mutation_execution_registry,
    )
except Exception:
    attach_regen_runtime_mutation_execution_registry = None

try:
    from regen_runtime_mutation_execution_engine import (
        attach_regen_runtime_mutation_execution_engine,
    )
except Exception:
    attach_regen_runtime_mutation_execution_engine = None

try:
    from regen_runtime_mutation_execution_validation_owner import (
        attach_regen_runtime_mutation_execution_validation_owner,
    )
except Exception:
    attach_regen_runtime_mutation_execution_validation_owner = None

try:
    from regen_runtime_mutation_execution_history_owner import (
        attach_regen_runtime_mutation_execution_history_owner,
    )
except Exception:
    attach_regen_runtime_mutation_execution_history_owner = None

try:
    from regen_runtime_mutation_execution_report_owner import (
        attach_regen_runtime_mutation_execution_report_owner,
    )
except Exception:
    attach_regen_runtime_mutation_execution_report_owner = None

try:
    from regen_runtime_mutation_execution_completion_audit import (
        attach_regen_runtime_mutation_execution_completion_audit,
    )
except Exception:
    attach_regen_runtime_mutation_execution_completion_audit = None

try:
    from regen_runtime_mutation_execution_master_gate import (
        attach_regen_runtime_mutation_execution_master_gate,
    )
except Exception:
    attach_regen_runtime_mutation_execution_master_gate = None


try:
    from regen_runtime_candidate_evaluation_registry import (
        attach_regen_runtime_candidate_evaluation_registry,
    )
except Exception:
    attach_regen_runtime_candidate_evaluation_registry = None

try:
    from regen_runtime_candidate_evaluation_engine import (
        attach_regen_runtime_candidate_evaluation_engine,
    )
except Exception:
    attach_regen_runtime_candidate_evaluation_engine = None

try:
    from regen_runtime_candidate_evaluation_validation_owner import (
        attach_regen_runtime_candidate_evaluation_validation_owner,
    )
except Exception:
    attach_regen_runtime_candidate_evaluation_validation_owner = None

try:
    from regen_runtime_candidate_evaluation_history_owner import (
        attach_regen_runtime_candidate_evaluation_history_owner,
    )
except Exception:
    attach_regen_runtime_candidate_evaluation_history_owner = None

try:
    from regen_runtime_candidate_evaluation_report_owner import (
        attach_regen_runtime_candidate_evaluation_report_owner,
    )
except Exception:
    attach_regen_runtime_candidate_evaluation_report_owner = None

try:
    from regen_runtime_candidate_evaluation_completion_audit import (
        attach_regen_runtime_candidate_evaluation_completion_audit,
    )
except Exception:
    attach_regen_runtime_candidate_evaluation_completion_audit = None

try:
    from regen_runtime_candidate_evaluation_master_gate import (
        attach_regen_runtime_candidate_evaluation_master_gate,
    )
except Exception:
    attach_regen_runtime_candidate_evaluation_master_gate = None


try:
    from regen_runtime_selection_registry import attach_regen_runtime_selection_registry
except Exception:
    attach_regen_runtime_selection_registry = None

try:
    from regen_runtime_selection_ranking_engine import attach_regen_runtime_selection_ranking_engine
except Exception:
    attach_regen_runtime_selection_ranking_engine = None

try:
    from regen_runtime_selection_parent_pool_builder import attach_regen_runtime_selection_parent_pool_builder
except Exception:
    attach_regen_runtime_selection_parent_pool_builder = None

try:
    from regen_runtime_selection_validation_owner import attach_regen_runtime_selection_validation_owner
except Exception:
    attach_regen_runtime_selection_validation_owner = None

try:
    from regen_runtime_selection_history_owner import attach_regen_runtime_selection_history_owner
except Exception:
    attach_regen_runtime_selection_history_owner = None

try:
    from regen_runtime_selection_report_owner import attach_regen_runtime_selection_report_owner
except Exception:
    attach_regen_runtime_selection_report_owner = None

try:
    from regen_runtime_selection_completion_audit import attach_regen_runtime_selection_completion_audit
except Exception:
    attach_regen_runtime_selection_completion_audit = None

try:
    from regen_runtime_selection_master_gate import attach_regen_runtime_selection_master_gate
except Exception:
    attach_regen_runtime_selection_master_gate = None


try:
    from regen_runtime_evolution_registry import attach_regen_runtime_evolution_registry
except Exception:
    attach_regen_runtime_evolution_registry = None

try:
    from regen_runtime_generation_advance_engine import attach_regen_runtime_generation_advance_engine
except Exception:
    attach_regen_runtime_generation_advance_engine = None

try:
    from regen_runtime_generation_creation_engine import attach_regen_runtime_generation_creation_engine
except Exception:
    attach_regen_runtime_generation_creation_engine = None

try:
    from regen_runtime_population_carryover_engine import attach_regen_runtime_population_carryover_engine
except Exception:
    attach_regen_runtime_population_carryover_engine = None

try:
    from regen_runtime_evolution_validation_owner import attach_regen_runtime_evolution_validation_owner
except Exception:
    attach_regen_runtime_evolution_validation_owner = None

try:
    from regen_runtime_evolution_history_owner import attach_regen_runtime_evolution_history_owner
except Exception:
    attach_regen_runtime_evolution_history_owner = None

try:
    from regen_runtime_evolution_report_owner import attach_regen_runtime_evolution_report_owner
except Exception:
    attach_regen_runtime_evolution_report_owner = None

try:
    from regen_runtime_evolution_completion_audit import attach_regen_runtime_evolution_completion_audit
except Exception:
    attach_regen_runtime_evolution_completion_audit = None

try:
    from regen_runtime_evolution_master_gate import attach_regen_runtime_evolution_master_gate
except Exception:
    attach_regen_runtime_evolution_master_gate = None


try:
    from regen_runtime_convergence_registry import attach_regen_runtime_convergence_registry
except Exception:
    attach_regen_runtime_convergence_registry = None

try:
    from regen_runtime_improvement_tracking_engine import attach_regen_runtime_improvement_tracking_engine
except Exception:
    attach_regen_runtime_improvement_tracking_engine = None

try:
    from regen_runtime_stagnation_detection_engine import attach_regen_runtime_stagnation_detection_engine
except Exception:
    attach_regen_runtime_stagnation_detection_engine = None

try:
    from regen_runtime_convergence_detection_engine import attach_regen_runtime_convergence_detection_engine
except Exception:
    attach_regen_runtime_convergence_detection_engine = None

try:
    from regen_runtime_stop_condition_engine import attach_regen_runtime_stop_condition_engine
except Exception:
    attach_regen_runtime_stop_condition_engine = None

try:
    from regen_runtime_convergence_validation_owner import attach_regen_runtime_convergence_validation_owner
except Exception:
    attach_regen_runtime_convergence_validation_owner = None

try:
    from regen_runtime_convergence_history_owner import attach_regen_runtime_convergence_history_owner
except Exception:
    attach_regen_runtime_convergence_history_owner = None

try:
    from regen_runtime_convergence_report_owner import attach_regen_runtime_convergence_report_owner
except Exception:
    attach_regen_runtime_convergence_report_owner = None

try:
    from regen_runtime_convergence_completion_audit import attach_regen_runtime_convergence_completion_audit
except Exception:
    attach_regen_runtime_convergence_completion_audit = None

try:
    from regen_runtime_convergence_master_gate import attach_regen_runtime_convergence_master_gate
except Exception:
    attach_regen_runtime_convergence_master_gate = None


try:
    from regen_runtime_optimisation_completion_registry import attach_regen_runtime_optimisation_completion_registry
except Exception:
    attach_regen_runtime_optimisation_completion_registry = None

try:
    from regen_runtime_optimisation_completion_audit import attach_regen_runtime_optimisation_completion_audit
except Exception:
    attach_regen_runtime_optimisation_completion_audit = None

try:
    from regen_runtime_optimisation_completion_validation_owner import attach_regen_runtime_optimisation_completion_validation_owner
except Exception:
    attach_regen_runtime_optimisation_completion_validation_owner = None

try:
    from regen_runtime_optimisation_completion_history_owner import attach_regen_runtime_optimisation_completion_history_owner
except Exception:
    attach_regen_runtime_optimisation_completion_history_owner = None

try:
    from regen_runtime_optimisation_completion_report_owner import attach_regen_runtime_optimisation_completion_report_owner
except Exception:
    attach_regen_runtime_optimisation_completion_report_owner = None

try:
    from regen_runtime_optimisation_completion_master_gate import attach_regen_runtime_optimisation_completion_master_gate
except Exception:
    attach_regen_runtime_optimisation_completion_master_gate = None


try:
    from regen_optimisation_viewer_registry import attach_regen_optimisation_viewer_registry
except Exception:
    attach_regen_optimisation_viewer_registry = None

try:
    from regen_optimisation_viewer_data_owner import attach_regen_optimisation_viewer_data_owner
except Exception:
    attach_regen_optimisation_viewer_data_owner = None

try:
    from regen_generation_viewer_data_owner import attach_regen_generation_viewer_data_owner
except Exception:
    attach_regen_generation_viewer_data_owner = None

try:
    from regen_candidate_viewer_data_owner import attach_regen_candidate_viewer_data_owner
except Exception:
    attach_regen_candidate_viewer_data_owner = None

try:
    from regen_improvement_viewer_data_owner import attach_regen_improvement_viewer_data_owner
except Exception:
    attach_regen_improvement_viewer_data_owner = None

try:
    from regen_optimisation_viewer_history_owner import attach_regen_optimisation_viewer_history_owner
except Exception:
    attach_regen_optimisation_viewer_history_owner = None

try:
    from regen_optimisation_viewer_report_owner import attach_regen_optimisation_viewer_report_owner
except Exception:
    attach_regen_optimisation_viewer_report_owner = None

try:
    from regen_optimisation_viewer_completion_audit import attach_regen_optimisation_viewer_completion_audit
except Exception:
    attach_regen_optimisation_viewer_completion_audit = None

try:
    from regen_optimisation_viewer_master_gate import attach_regen_optimisation_viewer_master_gate
except Exception:
    attach_regen_optimisation_viewer_master_gate = None


try:
    from regen_candidate_comparison_registry import attach_regen_candidate_comparison_registry
except Exception:
    attach_regen_candidate_comparison_registry = None

try:
    from regen_candidate_comparison_baseline_owner import attach_regen_candidate_comparison_baseline_owner
except Exception:
    attach_regen_candidate_comparison_baseline_owner = None

try:
    from regen_candidate_comparison_current_owner import attach_regen_candidate_comparison_current_owner
except Exception:
    attach_regen_candidate_comparison_current_owner = None

try:
    from regen_candidate_comparison_best_owner import attach_regen_candidate_comparison_best_owner
except Exception:
    attach_regen_candidate_comparison_best_owner = None

try:
    from regen_candidate_comparison_metrics_owner import attach_regen_candidate_comparison_metrics_owner
except Exception:
    attach_regen_candidate_comparison_metrics_owner = None

try:
    from regen_candidate_comparison_history_owner import attach_regen_candidate_comparison_history_owner
except Exception:
    attach_regen_candidate_comparison_history_owner = None

try:
    from regen_candidate_comparison_report_owner import attach_regen_candidate_comparison_report_owner
except Exception:
    attach_regen_candidate_comparison_report_owner = None

try:
    from regen_candidate_comparison_completion_audit import attach_regen_candidate_comparison_completion_audit
except Exception:
    attach_regen_candidate_comparison_completion_audit = None

try:
    from regen_candidate_comparison_master_gate import attach_regen_candidate_comparison_master_gate
except Exception:
    attach_regen_candidate_comparison_master_gate = None


try:
    from regen_evolution_tree_registry import attach_regen_evolution_tree_registry
except Exception:
    attach_regen_evolution_tree_registry = None

try:
    from regen_evolution_tree_generation_lineage_owner import attach_regen_evolution_tree_generation_lineage_owner
except Exception:
    attach_regen_evolution_tree_generation_lineage_owner = None

try:
    from regen_evolution_tree_parent_relationship_owner import attach_regen_evolution_tree_parent_relationship_owner
except Exception:
    attach_regen_evolution_tree_parent_relationship_owner = None

try:
    from regen_evolution_tree_mutation_lineage_owner import attach_regen_evolution_tree_mutation_lineage_owner
except Exception:
    attach_regen_evolution_tree_mutation_lineage_owner = None

try:
    from regen_evolution_tree_path_owner import attach_regen_evolution_tree_path_owner
except Exception:
    attach_regen_evolution_tree_path_owner = None

try:
    from regen_evolution_tree_history_owner import attach_regen_evolution_tree_history_owner
except Exception:
    attach_regen_evolution_tree_history_owner = None

try:
    from regen_evolution_tree_report_owner import attach_regen_evolution_tree_report_owner
except Exception:
    attach_regen_evolution_tree_report_owner = None

try:
    from regen_evolution_tree_completion_audit import attach_regen_evolution_tree_completion_audit
except Exception:
    attach_regen_evolution_tree_completion_audit = None

try:
    from regen_evolution_tree_master_gate import attach_regen_evolution_tree_master_gate
except Exception:
    attach_regen_evolution_tree_master_gate = None


try:
    from regen_optimisation_report_backend_registry import attach_regen_optimisation_report_backend_registry
except Exception:
    attach_regen_optimisation_report_backend_registry = None

try:
    from regen_optimisation_report_backend_data_owner import attach_regen_optimisation_report_backend_data_owner
except Exception:
    attach_regen_optimisation_report_backend_data_owner = None

try:
    from regen_optimisation_report_section_owner import attach_regen_optimisation_report_section_owner
except Exception:
    attach_regen_optimisation_report_section_owner = None

try:
    from regen_optimisation_report_metrics_owner import attach_regen_optimisation_report_metrics_owner
except Exception:
    attach_regen_optimisation_report_metrics_owner = None

try:
    from regen_optimisation_report_history_owner import attach_regen_optimisation_report_history_owner
except Exception:
    attach_regen_optimisation_report_history_owner = None

try:
    from regen_optimisation_report_backend_report_owner import attach_regen_optimisation_report_backend_report_owner
except Exception:
    attach_regen_optimisation_report_backend_report_owner = None

try:
    from regen_optimisation_report_backend_completion_audit import attach_regen_optimisation_report_backend_completion_audit
except Exception:
    attach_regen_optimisation_report_backend_completion_audit = None

try:
    from regen_optimisation_report_backend_master_gate import attach_regen_optimisation_report_backend_master_gate
except Exception:
    attach_regen_optimisation_report_backend_master_gate = None


try:
    from regen_unified_ecosystem_registry import attach_regen_unified_ecosystem_registry
except Exception:
    attach_regen_unified_ecosystem_registry = None

try:
    from regen_unified_viewer_registration_owner import attach_regen_unified_viewer_registration_owner
except Exception:
    attach_regen_unified_viewer_registration_owner = None

try:
    from regen_unified_report_registration_owner import attach_regen_unified_report_registration_owner
except Exception:
    attach_regen_unified_report_registration_owner = None

try:
    from regen_unified_validation_registration_owner import attach_regen_unified_validation_registration_owner
except Exception:
    attach_regen_unified_validation_registration_owner = None

try:
    from regen_unified_ecosystem_state_owner import attach_regen_unified_ecosystem_state_owner
except Exception:
    attach_regen_unified_ecosystem_state_owner = None

try:
    from regen_unified_ecosystem_completion_audit import attach_regen_unified_ecosystem_completion_audit
except Exception:
    attach_regen_unified_ecosystem_completion_audit = None

try:
    from regen_unified_ecosystem_master_gate import attach_regen_unified_ecosystem_master_gate
except Exception:
    attach_regen_unified_ecosystem_master_gate = None


try:
    from regen_unified_viewer_integration_registry import attach_regen_unified_viewer_integration_registry
except Exception:
    attach_regen_unified_viewer_integration_registry = None

try:
    from regen_unified_viewer_routing_owner import attach_regen_unified_viewer_routing_owner
except Exception:
    attach_regen_unified_viewer_routing_owner = None

try:
    from regen_unified_viewer_synchronisation_owner import attach_regen_unified_viewer_synchronisation_owner
except Exception:
    attach_regen_unified_viewer_synchronisation_owner = None

try:
    from regen_unified_viewer_session_owner import attach_regen_unified_viewer_session_owner
except Exception:
    attach_regen_unified_viewer_session_owner = None

try:
    from regen_unified_viewer_state_owner import attach_regen_unified_viewer_state_owner
except Exception:
    attach_regen_unified_viewer_state_owner = None

try:
    from regen_unified_viewer_integration_completion_audit import attach_regen_unified_viewer_integration_completion_audit
except Exception:
    attach_regen_unified_viewer_integration_completion_audit = None

try:
    from regen_unified_viewer_integration_master_gate import attach_regen_unified_viewer_integration_master_gate
except Exception:
    attach_regen_unified_viewer_integration_master_gate = None


try:
    from regen_unified_report_integration_registry import attach_regen_unified_report_integration_registry
except Exception:
    attach_regen_unified_report_integration_registry = None

try:
    from regen_unified_report_routing_owner import attach_regen_unified_report_routing_owner
except Exception:
    attach_regen_unified_report_routing_owner = None

try:
    from regen_unified_report_synchronisation_owner import attach_regen_unified_report_synchronisation_owner
except Exception:
    attach_regen_unified_report_synchronisation_owner = None

try:
    from regen_unified_report_session_owner import attach_regen_unified_report_session_owner
except Exception:
    attach_regen_unified_report_session_owner = None

try:
    from regen_unified_report_state_owner import attach_regen_unified_report_state_owner
except Exception:
    attach_regen_unified_report_state_owner = None

try:
    from regen_unified_report_integration_completion_audit import attach_regen_unified_report_integration_completion_audit
except Exception:
    attach_regen_unified_report_integration_completion_audit = None

try:
    from regen_unified_report_integration_master_gate import attach_regen_unified_report_integration_master_gate
except Exception:
    attach_regen_unified_report_integration_master_gate = None


try:
    from regen_unified_validation_integration_registry import attach_regen_unified_validation_integration_registry
except Exception:
    attach_regen_unified_validation_integration_registry = None

try:
    from regen_unified_validation_routing_owner import attach_regen_unified_validation_routing_owner
except Exception:
    attach_regen_unified_validation_routing_owner = None

try:
    from regen_unified_validation_synchronisation_owner import attach_regen_unified_validation_synchronisation_owner
except Exception:
    attach_regen_unified_validation_synchronisation_owner = None

try:
    from regen_unified_validation_session_owner import attach_regen_unified_validation_session_owner
except Exception:
    attach_regen_unified_validation_session_owner = None

try:
    from regen_unified_validation_state_owner import attach_regen_unified_validation_state_owner
except Exception:
    attach_regen_unified_validation_state_owner = None

try:
    from regen_unified_validation_integration_completion_audit import attach_regen_unified_validation_integration_completion_audit
except Exception:
    attach_regen_unified_validation_integration_completion_audit = None

try:
    from regen_unified_validation_integration_master_gate import attach_regen_unified_validation_integration_master_gate
except Exception:
    attach_regen_unified_validation_integration_master_gate = None


try:
    from regen_system_signoff_registry import attach_regen_system_signoff_registry
except Exception:
    attach_regen_system_signoff_registry = None

try:
    from regen_system_signoff_validation_owner import attach_regen_system_signoff_validation_owner
except Exception:
    attach_regen_system_signoff_validation_owner = None

try:
    from regen_system_signoff_report_owner import attach_regen_system_signoff_report_owner
except Exception:
    attach_regen_system_signoff_report_owner = None

try:
    from regen_system_signoff_history_owner import attach_regen_system_signoff_history_owner
except Exception:
    attach_regen_system_signoff_history_owner = None

try:
    from regen_system_signoff_completion_audit import attach_regen_system_signoff_completion_audit
except Exception:
    attach_regen_system_signoff_completion_audit = None

try:
    from regen_system_signoff_master_gate import attach_regen_system_signoff_master_gate
except Exception:
    attach_regen_system_signoff_master_gate = None


try:
    from regen_completion_gate_registry import attach_regen_completion_gate_registry
except Exception:
    attach_regen_completion_gate_registry = None

try:
    from regen_completion_gate_validation_owner import attach_regen_completion_gate_validation_owner
except Exception:
    attach_regen_completion_gate_validation_owner = None

try:
    from regen_completion_gate_report_owner import attach_regen_completion_gate_report_owner
except Exception:
    attach_regen_completion_gate_report_owner = None

try:
    from regen_completion_gate_history_owner import attach_regen_completion_gate_history_owner
except Exception:
    attach_regen_completion_gate_history_owner = None

try:
    from regen_completion_gate_completion_audit import attach_regen_completion_gate_completion_audit
except Exception:
    attach_regen_completion_gate_completion_audit = None

try:
    from regen_completion_master_gate import attach_regen_completion_master_gate
except Exception:
    attach_regen_completion_master_gate = None


try:
    from regen_input_mapping_repair import attach_regen_input_mapping_repair
except Exception:
    attach_regen_input_mapping_repair = None


try:
    from regen_coolant_property_resolution_repair import attach_regen_coolant_property_resolution_repair
except Exception:
    attach_regen_coolant_property_resolution_repair = None


try:
    from regen_architecture_visibility_audit import attach_regen_architecture_visibility_audit
except Exception:
    attach_regen_architecture_visibility_audit = None


try:
    from leaf_qt.optimisation.regen_candidate_ranking_payload_bridge import attach_regen_candidate_ranking_payload_bridge
except Exception:
    attach_regen_candidate_ranking_payload_bridge = None


try:
    from regen_coolant_flow_activation_layer import attach_regen_coolant_flow_activation_layer
except Exception:
    attach_regen_coolant_flow_activation_layer = None


try:
    from regen_candidate_generator_data_source_repair import attach_regen_candidate_generator_data_source_repair
except Exception:
    attach_regen_candidate_generator_data_source_repair = None


try:
    from regen_candidate_base_geometry_population_repair import attach_regen_candidate_base_geometry_population_repair
except Exception:
    attach_regen_candidate_base_geometry_population_repair = None


try:
    from regen_ranking_input_feed_bridge import attach_regen_ranking_input_feed_bridge
except Exception:
    attach_regen_ranking_input_feed_bridge = None


try:
    from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
except Exception:
    attach_regen_ranking_owner_source_repair = None

try:
    from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
except Exception:
    attach_regen_recommendation_feed_repair = None

try:
    from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
except Exception:
    attach_regen_recommendation_viewer_repair = None

try:
    from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
except Exception:
    attach_regen_end_to_end_candidate_selection_validation = None

try:
    from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
except Exception:
    attach_regen_candidate_acceptance_integration = None

try:
    from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation
except Exception:
    attach_regen_pending_geometry_commit_validation = None

try:
    from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution
except Exception:
    attach_regen_live_geometry_commit_execution = None

try:
    from regen_solver_regeneration_after_commit import attach_regen_solver_regeneration_after_commit
except Exception:
    attach_regen_solver_regeneration_after_commit = None

try:
    from regen_before_after_solver_comparison_report_owner import attach_regen_before_after_solver_comparison_report_owner
except Exception:
    attach_regen_before_after_solver_comparison_report_owner = None

try:
    from history.regen_design_iteration_history_link import attach_regen_design_iteration_history_link
except Exception:
    attach_regen_design_iteration_history_link = None

try:
    from regen_candidate_acceptance_completion_gate import attach_regen_candidate_acceptance_completion_gate
except Exception:
    attach_regen_candidate_acceptance_completion_gate = None

try:
    from regen_failure_root_cause_system import attach_regen_failure_root_cause_system
except Exception:
    attach_regen_failure_root_cause_system = None

try:
    from regen_optimisation_completion_gate import attach_regen_optimisation_completion_gate
except Exception:
    attach_regen_optimisation_completion_gate = None

try:
    from regen_viewer_data_adapter import attach_regen_viewer_data_adapter
except Exception:
    attach_regen_viewer_data_adapter = None

try:
    from regen_viewer_report_renderer import attach_regen_viewer_report_renderer
except Exception:
    attach_regen_viewer_report_renderer = None

try:
    from regen_viewer_navigation_system import attach_regen_viewer_navigation_system
except Exception:
    attach_regen_viewer_navigation_system = None

try:
    from regen_viewer_ownership_architecture import attach_regen_viewer_ownership_architecture
except Exception:
    attach_regen_viewer_ownership_architecture = None

try:
    from regen_cross_section_viewer_integration import attach_regen_cross_section_viewer_integration
except Exception:
    attach_regen_cross_section_viewer_integration = None

try:
    from regen_station_viewer_integration import attach_regen_station_viewer_integration
except Exception:
    attach_regen_station_viewer_integration = None

try:
    from regen_viewer_completion_gate import attach_regen_viewer_completion_gate
except Exception:
    attach_regen_viewer_completion_gate = None

try:
    from regen_acceptance_criteria_owner import attach_regen_acceptance_criteria_owner
except Exception:
    attach_regen_acceptance_criteria_owner = None

try:
    from regen_engineering_acceptance_report import attach_regen_engineering_acceptance_report
except Exception:
    attach_regen_engineering_acceptance_report = None

try:
    from regen_acceptance_audit import attach_regen_acceptance_audit
except Exception:
    attach_regen_acceptance_audit = None

try:
    from regen_acceptance_master_gate import attach_regen_acceptance_master_gate
except Exception:
    attach_regen_acceptance_master_gate = None

try:
    from regen_final_completion_audit import attach_regen_final_completion_audit
except Exception:
    attach_regen_final_completion_audit = None

try:
    from regen_final_verification_audit import attach_regen_final_verification_audit
except Exception:
    attach_regen_final_verification_audit = None

try:
    from regen_final_signoff_report import attach_regen_final_signoff_report
except Exception:
    attach_regen_final_signoff_report = None

try:
    from regen_final_master_gate import attach_regen_final_master_gate
except Exception:
    attach_regen_final_master_gate = None

try:
    from foundation_verification_harness import run_foundation_verification_harness
except Exception:
    run_foundation_verification_harness = None

try:
    from report_ownership import build_report_viewer_bundle, get_main_output_results
except Exception:
    build_report_viewer_bundle = None
    get_main_output_results = None

try:
    from history.design_iteration_narrative import attach_regen_design_iteration_narrative
except Exception:
    attach_regen_design_iteration_narrative = None

try:
    from optimisation_proof import attach_regen_optimisation_proof
except Exception:
    attach_regen_optimisation_proof = None

try:
    from failure_root_cause import attach_regen_failure_root_cause
except Exception:
    attach_regen_failure_root_cause = None

try:
    from recommendation_explanation import attach_recommendation_explanation
except Exception:
    attach_recommendation_explanation = None

try:
    from recommendation_ownership_final_audit import attach_recommendation_ownership_final_audit
except Exception:
    attach_recommendation_ownership_final_audit = None

try:
    from before_after_comparison import attach_before_after_comparison
except Exception:
    attach_before_after_comparison = None

try:
    from report_dashboard import attach_report_dashboard
except Exception:
    attach_report_dashboard = None

try:
    from foundation_regression_tests import attach_foundation_regression_tests
except Exception:
    attach_foundation_regression_tests = None

try:
    from foundation_result_key_audit import attach_foundation_result_key_audit
except Exception:
    attach_foundation_result_key_audit = None

try:
    from regen_source_validation_gate import attach_regen_source_validation_gate
except Exception:
    attach_regen_source_validation_gate = None

try:
    from benchmark_evaluator import attach_benchmark_evaluation
except Exception:
    attach_benchmark_evaluation = None

try:
    from engine_reproduction_validation import attach_engine_reproduction_validation
except Exception:
    attach_engine_reproduction_validation = None

try:
    from output_ownership_audit import attach_output_ownership_audit
except Exception:
    attach_output_ownership_audit = None

try:
    from output_visibility_architecture import attach_output_visibility_architecture
except Exception:
    attach_output_visibility_architecture = None

try:
    from regen_provenance_report_owner import attach_regen_provenance_report
except Exception:
    attach_regen_provenance_report = None

try:
    from regen_property_table_owner import attach_regen_property_table_owner
except Exception:
    attach_regen_property_table_owner = None

try:
    from regen_validation_master_gate import attach_regen_validation_master_gate
except Exception:
    attach_regen_validation_master_gate = None

try:
    from regen_completion_audit import attach_regen_completion_audit
except Exception:
    attach_regen_completion_audit = None

try:
    from regen_scalability_framework import attach_regen_scalability_framework
except Exception:
    attach_regen_scalability_framework = None

try:
    from regen_scalability_report_owner import attach_regen_scalability_report_owner
except Exception:
    attach_regen_scalability_report_owner = None

try:
    from regen_scalability_failure_owner import attach_regen_scalability_failure_owner
except Exception:
    attach_regen_scalability_failure_owner = None

try:
    from regen_scalability_master_gate import attach_regen_scalability_master_gate
except Exception:
    attach_regen_scalability_master_gate = None

try:
    from regen_scalability_completion_audit import attach_regen_scalability_completion_audit
except Exception:
    attach_regen_scalability_completion_audit = None

try:
    from real_engine_benchmarking_framework import attach_real_engine_benchmarking_framework
except Exception:
    attach_real_engine_benchmarking_framework = None

try:
    from real_engine_benchmark_source_owner import attach_real_engine_benchmark_source_owner
except Exception:
    attach_real_engine_benchmark_source_owner = None

try:
    from real_engine_benchmark_band_owner import attach_real_engine_benchmark_band_owner
except Exception:
    attach_real_engine_benchmark_band_owner = None

try:
    from real_engine_benchmark_failure_owner import attach_real_engine_benchmark_failure_owner
except Exception:
    attach_real_engine_benchmark_failure_owner = None

try:
    from real_engine_benchmark_master_gate import attach_real_engine_benchmark_master_gate
except Exception:
    attach_real_engine_benchmark_master_gate = None

try:
    from real_engine_benchmark_completion_audit import attach_real_engine_benchmark_completion_audit
except Exception:
    attach_real_engine_benchmark_completion_audit = None

from foundation_attachment_pipeline import (
    attach_foundation_layers,
    finalize_foundation_regression as _finalize_foundation_regression,
)

from regen_scalability_profile import attach_regen_scalability_profile

try:
    from regen_optimisation_profile import attach_regen_optimisation_profile
except Exception:
    attach_regen_optimisation_profile = None

try:
    from optimisation.regen_optimisation_candidate_generator import attach_regen_optimisation_candidate_generator
except Exception:
    attach_regen_optimisation_candidate_generator = None

try:
    from regen_optimisation_scoring_owner import attach_regen_optimisation_scoring_owner
except Exception:
    attach_regen_optimisation_scoring_owner = None

try:
    from regen_optimisation_failure_owner import attach_regen_optimisation_failure_owner
except Exception:
    attach_regen_optimisation_failure_owner = None

try:
    from regen_optimisation_report_owner import attach_regen_optimisation_report_owner
except Exception:
    attach_regen_optimisation_report_owner = None

try:
    from regen_optimisation_recommendation_owner import attach_regen_optimisation_recommendation_owner
except Exception:
    attach_regen_optimisation_recommendation_owner = None

try:
    from regen_optimisation_master_gate import attach_regen_optimisation_master_gate
except Exception:
    attach_regen_optimisation_master_gate = None

try:
    from regen_optimisation_completion_audit import attach_regen_optimisation_completion_audit
except Exception:
    attach_regen_optimisation_completion_audit = None



try:
    from regen_optimisation_session_owner import (
        attach_regen_optimisation_session_owner,
    )
except Exception:
    attach_regen_optimisation_session_owner = None

try:
    from regen_autonomous_optimisation_input_audit import (
        attach_regen_autonomous_optimisation_input_audit,
    )
except Exception:
    attach_regen_autonomous_optimisation_input_audit = None

try:
    from material_property_interpolation_owner import attach_material_property_interpolation_owner
except Exception:
    attach_material_property_interpolation_owner = None

try:
    from material_source_provenance_owner import attach_material_source_provenance_owner
except Exception:
    attach_material_source_provenance_owner = None

try:
    from correlation_source_provenance_owner import attach_correlation_source_provenance_owner
except Exception:
    attach_correlation_source_provenance_owner = None

try:
    from material_source_quality_ranking_owner import attach_material_source_quality_ranking_owner
except Exception:
    attach_material_source_quality_ranking_owner = None

try:
    from material_validation_owner import attach_material_validation_owner
except Exception:
    attach_material_validation_owner = None

try:
    from material_completion_audit import attach_material_completion_audit
except Exception:
    attach_material_completion_audit = None

try:
    from coating_source_provenance_owner import attach_coating_source_provenance_owner
except Exception:
    attach_coating_source_provenance_owner = None

try:
    from coating_validation_owner import attach_coating_validation_owner
except Exception:
    attach_coating_validation_owner = None

try:
    from materials.validation.material_and_coating_foundation_audit import attach_material_and_coating_foundation_audit
except Exception:
    attach_material_and_coating_foundation_audit = None

try:
    from materials.solver.material_coating_solver_integration_planning_owner import (
        attach_material_coating_solver_integration_planning_owner,
    )
except Exception:
    attach_material_coating_solver_integration_planning_owner = None

try:
    from material_property_consumption_audit_owner import (
        attach_material_property_consumption_audit_owner,
    )
except Exception:
    attach_material_property_consumption_audit_owner = None

try:
    from materials.owner.material_thermal_conductivity_integration_owner import (
        attach_material_thermal_conductivity_integration_owner,
    )
except Exception:
    attach_material_thermal_conductivity_integration_owner = None

try:
    from material_specific_heat_integration_owner import (
        attach_material_specific_heat_integration_owner,
    )
except Exception:
    attach_material_specific_heat_integration_owner = None

try:
    from material_density_integration_owner import (
        attach_material_density_integration_owner,
    )
except Exception:
    attach_material_density_integration_owner = None

try:
    from material_temperature_limit_integration_owner import (
        attach_material_temperature_limit_integration_owner,
        attach_material_temperature_limit_precheck,
    )
except Exception:
    attach_material_temperature_limit_integration_owner = None
    attach_material_temperature_limit_precheck = None

try:
    from material_strength_limit_integration_owner import (
        attach_material_strength_limit_integration_owner,
    )
except Exception:
    attach_material_strength_limit_integration_owner = None

try:
    from material_integration_validation_owner import (
        attach_material_integration_validation_owner,
    )
except Exception:
    attach_material_integration_validation_owner = None

try:
    from material_integration_completion_audit import (
        attach_material_integration_completion_audit,
    )
except Exception:
    attach_material_integration_completion_audit = None

try:
    from coating_property_consumption_audit_owner import (
        attach_coating_property_consumption_audit_owner,
    )
except Exception:
    attach_coating_property_consumption_audit_owner = None

try:
    from materials.owner.coating_thermal_conductivity_integration_owner import (
        attach_coating_thermal_conductivity_integration_owner,
    )
except Exception:
    attach_coating_thermal_conductivity_integration_owner = None

try:
    from coating_thickness_integration_owner import (
        attach_coating_thickness_integration_owner,
    )
except Exception:
    attach_coating_thickness_integration_owner = None

try:
    from coating_thermal_resistance_integration_owner import (
        attach_coating_thermal_resistance_integration_owner,
    )
except Exception:
    attach_coating_thermal_resistance_integration_owner = None

try:
    from coating_temperature_limit_integration_owner import (
        attach_coating_temperature_limit_integration_owner,
    )
except Exception:
    attach_coating_temperature_limit_integration_owner = None

try:
    from bond_coat_integration_owner import (
        attach_bond_coat_integration_owner,
    )
except Exception:
    attach_bond_coat_integration_owner = None

try:
    from coating_integration_validation_owner import (
        attach_coating_integration_validation_owner,
    )
except Exception:
    attach_coating_integration_validation_owner = None

try:
    from coating_integration_completion_audit import (
        attach_coating_integration_completion_audit,
    )
except Exception:
    attach_coating_integration_completion_audit = None

try:
    from temperature_dependency_discovery_audit_owner import (
        attach_temperature_dependency_discovery_audit_owner,
    )
except Exception:
    attach_temperature_dependency_discovery_audit_owner = None

try:
    from materials.validation.material_conductivity_consumption_audit_owner import (
        attach_material_conductivity_consumption_audit_owner,
    )
except Exception:
    attach_material_conductivity_consumption_audit_owner = None

try:
    from specific_heat_consumption_audit_owner import (
        attach_specific_heat_consumption_audit_owner,
    )
except Exception:
    attach_specific_heat_consumption_audit_owner = None

try:
    from density_coolant_property_consumption_audit_owner import (
        attach_density_coolant_property_consumption_audit_owner,
    )
except Exception:
    attach_density_coolant_property_consumption_audit_owner = None

try:
    from coating_thermal_consumption_audit_owner import (
        attach_coating_thermal_consumption_audit_owner,
    )
except Exception:
    attach_coating_thermal_consumption_audit_owner = None

try:
    from bond_coat_consumption_audit_owner import (
        attach_bond_coat_consumption_audit_owner,
    )
except Exception:
    attach_bond_coat_consumption_audit_owner = None

try:
    from temperature_dependent_solver_completion_audit_owner import (
        attach_temperature_dependent_solver_completion_audit_owner,
    )
except Exception:
    attach_temperature_dependent_solver_completion_audit_owner = None

try:
    from regen_geometry_constraint_discovery_audit_owner import (
        attach_regen_geometry_constraint_discovery_audit_owner,
    )
except Exception:
    attach_regen_geometry_constraint_discovery_audit_owner = None

try:
    from regen_geometry_constraint_validation_owner import (
        attach_regen_geometry_constraint_validation_owner,
    )
except Exception:
    attach_regen_geometry_constraint_validation_owner = None

try:
    from regen_geometry_failure_explanation_owner import (
        attach_regen_geometry_failure_explanation_owner,
    )
except Exception:
    attach_regen_geometry_failure_explanation_owner = None

try:
    from regen_geometry_recommendation_engine_owner import (
        attach_regen_geometry_recommendation_engine_owner,
    )
except Exception:
    attach_regen_geometry_recommendation_engine_owner = None

try:
    from regen_geometry_apply_recommendation_owner import (
        attach_regen_geometry_apply_recommendation_owner,
    )
except Exception:
    attach_regen_geometry_apply_recommendation_owner = None

try:
    from regen_geometry_output_architecture_owner import (
        attach_regen_geometry_output_architecture_owner,
    )
except Exception:
    attach_regen_geometry_output_architecture_owner = None

try:
    from regen_geometry_candidate_acceptance_owner import (
        attach_regen_geometry_candidate_acceptance_owner,
    )
except Exception:
    attach_regen_geometry_candidate_acceptance_owner = None

class FoundationLayerController:
    """
    Owns optional foundation/report/benchmark attachment layers.

    This controller prevents main_window.py and calculation_controller.py
    from knowing about every individual report/evidence/benchmark module.
    """

    def __init__(
            self,
            get_benchmark_case_callback,
            get_startup_health_callback,
    ):
        self.get_benchmark_case = get_benchmark_case_callback
        self.get_startup_health = get_startup_health_callback

    def apply_foundation_layers(self, solved):
        if not isinstance(solved, dict):
            solved = {
                "foundation_input_coerced": True,
                "foundation_input_type": type(solved).__name__,
            }

        self._attach_startup_health(solved)

        return attach_foundation_layers(
            solved,
            benchmark_case=self.get_benchmark_case(),
            attach_regen_design_iteration_narrative=attach_regen_design_iteration_narrative,
            attach_regen_optimisation_proof=attach_regen_optimisation_proof,
            attach_regen_failure_root_cause=attach_regen_failure_root_cause,
            attach_regen_provenance_report=attach_regen_provenance_report,
            attach_regen_property_table_owner=attach_regen_property_table_owner,
            attach_material_temperature_limit_precheck=attach_material_temperature_limit_precheck,
            attach_regen_validation_master_gate=attach_regen_validation_master_gate,
            attach_regen_completion_audit=attach_regen_completion_audit,
            attach_recommendation_explanation=attach_recommendation_explanation,
            attach_before_after_comparison=attach_before_after_comparison,
            attach_report_dashboard=attach_report_dashboard,
            attach_foundation_result_key_audit=attach_foundation_result_key_audit,
            attach_benchmark_evaluation=attach_benchmark_evaluation,
            attach_engine_reproduction_validation=attach_engine_reproduction_validation,
            attach_regen_source_validation_gate=attach_regen_source_validation_gate,
            attach_output_ownership_audit=attach_output_ownership_audit,
            attach_recommendation_ownership_final_audit=attach_recommendation_ownership_final_audit,
            attach_output_visibility_architecture=attach_output_visibility_architecture,
            attach_regen_scalability_profile=attach_regen_scalability_profile,
            attach_regen_scalability_framework=attach_regen_scalability_framework,
            attach_regen_scalability_report_owner=attach_regen_scalability_report_owner,
            attach_regen_scalability_failure_owner=attach_regen_scalability_failure_owner,
            attach_regen_scalability_master_gate=attach_regen_scalability_master_gate,
            attach_regen_scalability_completion_audit=attach_regen_scalability_completion_audit,
            attach_real_engine_benchmarking_framework=attach_real_engine_benchmarking_framework,
            attach_real_engine_benchmark_source_owner=attach_real_engine_benchmark_source_owner,
            attach_real_engine_benchmark_band_owner=attach_real_engine_benchmark_band_owner,
            attach_real_engine_benchmark_failure_owner=attach_real_engine_benchmark_failure_owner,
            attach_real_engine_benchmark_master_gate=attach_real_engine_benchmark_master_gate,
            attach_real_engine_benchmark_completion_audit=attach_real_engine_benchmark_completion_audit,
            attach_regen_optimisation_profile=attach_regen_optimisation_profile,
            attach_regen_optimisation_candidate_generator=attach_regen_optimisation_candidate_generator,
            attach_regen_optimisation_scoring_owner=attach_regen_optimisation_scoring_owner,
            attach_regen_optimisation_failure_owner=attach_regen_optimisation_failure_owner,
            attach_regen_optimisation_report_owner=attach_regen_optimisation_report_owner,
            attach_regen_optimisation_registration_owner=attach_regen_optimisation_registration_owner,
            attach_regen_optimisation_recommendation_owner=attach_regen_optimisation_recommendation_owner,
            attach_regen_optimisation_master_gate=attach_regen_optimisation_master_gate,
            attach_regen_optimisation_completion_audit=attach_regen_optimisation_completion_audit,
            attach_regen_runtime_optimisation_input_gate=attach_regen_runtime_optimisation_input_gate,
            attach_regen_autonomous_optimisation_input_audit=attach_regen_autonomous_optimisation_input_audit,
            attach_regen_optimisation_session_owner=attach_regen_optimisation_session_owner,

            attach_regen_optimisation_selection_ranking_engine=attach_regen_optimisation_selection_ranking_engine,
            attach_regen_optimisation_selection_registry=attach_regen_optimisation_selection_registry,
            attach_regen_optimisation_selection_validation_owner=attach_regen_optimisation_selection_validation_owner,
            attach_regen_optimisation_selection_parent_pool_builder=attach_regen_optimisation_selection_parent_pool_builder,
            attach_regen_optimisation_selection_state_owner=attach_regen_optimisation_selection_state_owner,
            attach_regen_optimisation_selection_history_owner=attach_regen_optimisation_selection_history_owner,
            attach_regen_optimisation_selection_report_owner=attach_regen_optimisation_selection_report_owner,
            attach_regen_optimisation_selection_completion_audit=attach_regen_optimisation_selection_completion_audit,
            attach_regen_optimisation_selection_master_gate=attach_regen_optimisation_selection_master_gate,

            attach_regen_optimisation_foundation_registry=attach_regen_optimisation_foundation_registry,
            attach_regen_optimisation_foundation_validation_owner=attach_regen_optimisation_foundation_validation_owner,
            attach_regen_optimisation_foundation_history_owner=attach_regen_optimisation_foundation_history_owner,
            attach_regen_optimisation_foundation_report_owner=attach_regen_optimisation_foundation_report_owner,
            attach_regen_optimisation_foundation_completion_audit=attach_regen_optimisation_foundation_completion_audit,
            attach_regen_optimisation_foundation_master_gate=attach_regen_optimisation_foundation_master_gate,

            attach_regen_runtime_mutation_execution_registry=attach_regen_runtime_mutation_execution_registry,
            attach_regen_runtime_mutation_execution_engine=attach_regen_runtime_mutation_execution_engine,
            attach_regen_runtime_mutation_execution_validation_owner=attach_regen_runtime_mutation_execution_validation_owner,
            attach_regen_runtime_mutation_execution_history_owner=attach_regen_runtime_mutation_execution_history_owner,
            attach_regen_runtime_mutation_execution_report_owner=attach_regen_runtime_mutation_execution_report_owner,
            attach_regen_runtime_mutation_execution_completion_audit=attach_regen_runtime_mutation_execution_completion_audit,
            attach_regen_runtime_mutation_execution_master_gate=attach_regen_runtime_mutation_execution_master_gate,

            attach_regen_runtime_candidate_evaluation_registry=attach_regen_runtime_candidate_evaluation_registry,
            attach_regen_runtime_candidate_evaluation_engine=attach_regen_runtime_candidate_evaluation_engine,
            attach_regen_runtime_candidate_evaluation_validation_owner=attach_regen_runtime_candidate_evaluation_validation_owner,
            attach_regen_runtime_candidate_evaluation_history_owner=attach_regen_runtime_candidate_evaluation_history_owner,
            attach_regen_runtime_candidate_evaluation_report_owner=attach_regen_runtime_candidate_evaluation_report_owner,
            attach_regen_runtime_candidate_evaluation_completion_audit=attach_regen_runtime_candidate_evaluation_completion_audit,
            attach_regen_runtime_candidate_evaluation_master_gate=attach_regen_runtime_candidate_evaluation_master_gate,

            attach_regen_runtime_selection_registry=attach_regen_runtime_selection_registry,
            attach_regen_runtime_selection_ranking_engine=attach_regen_runtime_selection_ranking_engine,
            attach_regen_runtime_selection_parent_pool_builder=attach_regen_runtime_selection_parent_pool_builder,
            attach_regen_runtime_selection_validation_owner=attach_regen_runtime_selection_validation_owner,
            attach_regen_runtime_selection_history_owner=attach_regen_runtime_selection_history_owner,
            attach_regen_runtime_selection_report_owner=attach_regen_runtime_selection_report_owner,
            attach_regen_runtime_selection_completion_audit=attach_regen_runtime_selection_completion_audit,
            attach_regen_runtime_selection_master_gate=attach_regen_runtime_selection_master_gate,

            attach_regen_runtime_evolution_registry=attach_regen_runtime_evolution_registry,
            attach_regen_runtime_generation_advance_engine=attach_regen_runtime_generation_advance_engine,
            attach_regen_runtime_generation_creation_engine=attach_regen_runtime_generation_creation_engine,
            attach_regen_runtime_population_carryover_engine=attach_regen_runtime_population_carryover_engine,
            attach_regen_runtime_evolution_validation_owner=attach_regen_runtime_evolution_validation_owner,
            attach_regen_runtime_evolution_history_owner=attach_regen_runtime_evolution_history_owner,
            attach_regen_runtime_evolution_report_owner=attach_regen_runtime_evolution_report_owner,
            attach_regen_runtime_evolution_completion_audit=attach_regen_runtime_evolution_completion_audit,
            attach_regen_runtime_evolution_master_gate=attach_regen_runtime_evolution_master_gate,

            attach_regen_runtime_convergence_registry=attach_regen_runtime_convergence_registry,
            attach_regen_runtime_improvement_tracking_engine=attach_regen_runtime_improvement_tracking_engine,
            attach_regen_runtime_stagnation_detection_engine=attach_regen_runtime_stagnation_detection_engine,
            attach_regen_runtime_convergence_detection_engine=attach_regen_runtime_convergence_detection_engine,
            attach_regen_runtime_stop_condition_engine=attach_regen_runtime_stop_condition_engine,
            attach_regen_runtime_convergence_validation_owner=attach_regen_runtime_convergence_validation_owner,
            attach_regen_runtime_convergence_history_owner=attach_regen_runtime_convergence_history_owner,
            attach_regen_runtime_convergence_report_owner=attach_regen_runtime_convergence_report_owner,
            attach_regen_runtime_convergence_completion_audit=attach_regen_runtime_convergence_completion_audit,
            attach_regen_runtime_convergence_master_gate=attach_regen_runtime_convergence_master_gate,

            attach_regen_runtime_optimisation_completion_registry=attach_regen_runtime_optimisation_completion_registry,
            attach_regen_runtime_optimisation_completion_audit=attach_regen_runtime_optimisation_completion_audit,
            attach_regen_runtime_optimisation_completion_validation_owner=attach_regen_runtime_optimisation_completion_validation_owner,
            attach_regen_runtime_optimisation_completion_history_owner=attach_regen_runtime_optimisation_completion_history_owner,
            attach_regen_runtime_optimisation_completion_report_owner=attach_regen_runtime_optimisation_completion_report_owner,
            attach_regen_runtime_optimisation_completion_master_gate=attach_regen_runtime_optimisation_completion_master_gate,

            attach_regen_optimisation_viewer_registry=attach_regen_optimisation_viewer_registry,
            attach_regen_optimisation_viewer_data_owner=attach_regen_optimisation_viewer_data_owner,
            attach_regen_generation_viewer_data_owner=attach_regen_generation_viewer_data_owner,
            attach_regen_candidate_viewer_data_owner=attach_regen_candidate_viewer_data_owner,
            attach_regen_improvement_viewer_data_owner=attach_regen_improvement_viewer_data_owner,
            attach_regen_optimisation_viewer_history_owner=attach_regen_optimisation_viewer_history_owner,
            attach_regen_optimisation_viewer_report_owner=attach_regen_optimisation_viewer_report_owner,
            attach_regen_optimisation_viewer_completion_audit=attach_regen_optimisation_viewer_completion_audit,
            attach_regen_optimisation_viewer_master_gate=attach_regen_optimisation_viewer_master_gate,

            attach_regen_candidate_comparison_registry=attach_regen_candidate_comparison_registry,
            attach_regen_candidate_comparison_baseline_owner=attach_regen_candidate_comparison_baseline_owner,
            attach_regen_candidate_comparison_current_owner=attach_regen_candidate_comparison_current_owner,
            attach_regen_candidate_comparison_best_owner=attach_regen_candidate_comparison_best_owner,
            attach_regen_candidate_comparison_metrics_owner=attach_regen_candidate_comparison_metrics_owner,
            attach_regen_candidate_comparison_history_owner=attach_regen_candidate_comparison_history_owner,
            attach_regen_candidate_comparison_report_owner=attach_regen_candidate_comparison_report_owner,
            attach_regen_candidate_comparison_completion_audit=attach_regen_candidate_comparison_completion_audit,
            attach_regen_candidate_comparison_master_gate=attach_regen_candidate_comparison_master_gate,

            attach_regen_evolution_tree_registry=attach_regen_evolution_tree_registry,
            attach_regen_evolution_tree_generation_lineage_owner=attach_regen_evolution_tree_generation_lineage_owner,
            attach_regen_evolution_tree_parent_relationship_owner=attach_regen_evolution_tree_parent_relationship_owner,
            attach_regen_evolution_tree_mutation_lineage_owner=attach_regen_evolution_tree_mutation_lineage_owner,
            attach_regen_evolution_tree_path_owner=attach_regen_evolution_tree_path_owner,
            attach_regen_evolution_tree_history_owner=attach_regen_evolution_tree_history_owner,
            attach_regen_evolution_tree_report_owner=attach_regen_evolution_tree_report_owner,
            attach_regen_evolution_tree_completion_audit=attach_regen_evolution_tree_completion_audit,
            attach_regen_evolution_tree_master_gate=attach_regen_evolution_tree_master_gate,

            attach_regen_optimisation_report_backend_registry=attach_regen_optimisation_report_backend_registry,
            attach_regen_optimisation_report_backend_data_owner=attach_regen_optimisation_report_backend_data_owner,
            attach_regen_optimisation_report_section_owner=attach_regen_optimisation_report_section_owner,
            attach_regen_optimisation_report_metrics_owner=attach_regen_optimisation_report_metrics_owner,
            attach_regen_optimisation_report_history_owner=attach_regen_optimisation_report_history_owner,
            attach_regen_optimisation_report_backend_report_owner=attach_regen_optimisation_report_backend_report_owner,
            attach_regen_optimisation_report_backend_completion_audit=attach_regen_optimisation_report_backend_completion_audit,
            attach_regen_optimisation_report_backend_master_gate=attach_regen_optimisation_report_backend_master_gate,

            attach_regen_unified_ecosystem_registry=attach_regen_unified_ecosystem_registry,
            attach_regen_unified_viewer_registration_owner=attach_regen_unified_viewer_registration_owner,
            attach_regen_unified_report_registration_owner=attach_regen_unified_report_registration_owner,
            attach_regen_unified_validation_registration_owner=attach_regen_unified_validation_registration_owner,
            attach_regen_unified_ecosystem_state_owner=attach_regen_unified_ecosystem_state_owner,
            attach_regen_unified_ecosystem_completion_audit=attach_regen_unified_ecosystem_completion_audit,
            attach_regen_unified_ecosystem_master_gate=attach_regen_unified_ecosystem_master_gate,

            attach_regen_unified_viewer_integration_registry=attach_regen_unified_viewer_integration_registry,
            attach_regen_unified_viewer_routing_owner=attach_regen_unified_viewer_routing_owner,
            attach_regen_unified_viewer_synchronisation_owner=attach_regen_unified_viewer_synchronisation_owner,
            attach_regen_unified_viewer_session_owner=attach_regen_unified_viewer_session_owner,
            attach_regen_unified_viewer_state_owner=attach_regen_unified_viewer_state_owner,
            attach_regen_unified_viewer_integration_completion_audit=attach_regen_unified_viewer_integration_completion_audit,
            attach_regen_unified_viewer_integration_master_gate=attach_regen_unified_viewer_integration_master_gate,

            attach_regen_unified_report_integration_registry=attach_regen_unified_report_integration_registry,
            attach_regen_unified_report_routing_owner=attach_regen_unified_report_routing_owner,
            attach_regen_unified_report_synchronisation_owner=attach_regen_unified_report_synchronisation_owner,
            attach_regen_unified_report_session_owner=attach_regen_unified_report_session_owner,
            attach_regen_unified_report_state_owner=attach_regen_unified_report_state_owner,
            attach_regen_unified_report_integration_completion_audit=attach_regen_unified_report_integration_completion_audit,
            attach_regen_unified_report_integration_master_gate=attach_regen_unified_report_integration_master_gate,

            attach_regen_unified_validation_integration_registry=attach_regen_unified_validation_integration_registry,
            attach_regen_unified_validation_routing_owner=attach_regen_unified_validation_routing_owner,
            attach_regen_unified_validation_synchronisation_owner=attach_regen_unified_validation_synchronisation_owner,
            attach_regen_unified_validation_session_owner=attach_regen_unified_validation_session_owner,
            attach_regen_unified_validation_state_owner=attach_regen_unified_validation_state_owner,
            attach_regen_unified_validation_integration_completion_audit=attach_regen_unified_validation_integration_completion_audit,
            attach_regen_unified_validation_integration_master_gate=attach_regen_unified_validation_integration_master_gate,

            attach_regen_system_signoff_registry=attach_regen_system_signoff_registry,
            attach_regen_system_signoff_validation_owner=attach_regen_system_signoff_validation_owner,
            attach_regen_system_signoff_report_owner=attach_regen_system_signoff_report_owner,
            attach_regen_system_signoff_history_owner=attach_regen_system_signoff_history_owner,
            attach_regen_system_signoff_completion_audit=attach_regen_system_signoff_completion_audit,
            attach_regen_system_signoff_master_gate=attach_regen_system_signoff_master_gate,

            attach_regen_completion_gate_registry=attach_regen_completion_gate_registry,
            attach_regen_completion_gate_validation_owner=attach_regen_completion_gate_validation_owner,
            attach_regen_completion_gate_report_owner=attach_regen_completion_gate_report_owner,
            attach_regen_completion_gate_history_owner=attach_regen_completion_gate_history_owner,
            attach_regen_completion_gate_completion_audit=attach_regen_completion_gate_completion_audit,
            attach_regen_completion_master_gate=attach_regen_completion_master_gate,



            attach_regen_coolant_flow_activation_layer=attach_regen_coolant_flow_activation_layer,

            attach_regen_candidate_generator_data_source_repair=attach_regen_candidate_generator_data_source_repair,

            attach_regen_candidate_base_geometry_population_repair=attach_regen_candidate_base_geometry_population_repair,

            attach_regen_ranking_input_feed_bridge=attach_regen_ranking_input_feed_bridge,

            attach_regen_ranking_owner_source_repair=attach_regen_ranking_owner_source_repair,

            attach_regen_recommendation_feed_repair=attach_regen_recommendation_feed_repair,

            attach_regen_recommendation_viewer_repair=attach_regen_recommendation_viewer_repair,

            attach_regen_end_to_end_candidate_selection_validation=attach_regen_end_to_end_candidate_selection_validation,

            attach_regen_candidate_acceptance_integration=attach_regen_candidate_acceptance_integration,

            attach_regen_pending_geometry_commit_validation=attach_regen_pending_geometry_commit_validation,

            attach_regen_live_geometry_commit_execution=attach_regen_live_geometry_commit_execution,

            attach_regen_solver_regeneration_after_commit=attach_regen_solver_regeneration_after_commit,

            attach_regen_before_after_solver_comparison_report_owner=attach_regen_before_after_solver_comparison_report_owner,

            attach_regen_design_iteration_history_link=attach_regen_design_iteration_history_link,

            attach_regen_candidate_acceptance_completion_gate=attach_regen_candidate_acceptance_completion_gate,


            attach_regen_failure_root_cause_system=attach_regen_failure_root_cause_system,


            attach_regen_optimisation_completion_gate=attach_regen_optimisation_completion_gate,

            attach_regen_viewer_data_adapter=attach_regen_viewer_data_adapter,

            attach_regen_viewer_report_renderer=attach_regen_viewer_report_renderer,

            attach_regen_viewer_navigation_system=attach_regen_viewer_navigation_system,

            attach_regen_viewer_ownership_architecture=attach_regen_viewer_ownership_architecture,

            attach_regen_cross_section_viewer_integration=attach_regen_cross_section_viewer_integration,

            attach_regen_station_viewer_integration=attach_regen_station_viewer_integration,

            attach_regen_viewer_completion_gate=attach_regen_viewer_completion_gate,

            attach_regen_acceptance_criteria_owner=attach_regen_acceptance_criteria_owner,

            attach_regen_engineering_acceptance_report=attach_regen_engineering_acceptance_report,

            attach_regen_acceptance_audit=attach_regen_acceptance_audit,

            attach_regen_acceptance_master_gate=attach_regen_acceptance_master_gate,

            attach_regen_final_completion_audit=attach_regen_final_completion_audit,

            attach_regen_final_verification_audit=attach_regen_final_verification_audit,

            attach_regen_final_signoff_report=attach_regen_final_signoff_report,

            attach_regen_final_master_gate=attach_regen_final_master_gate,




            attach_regen_coolant_property_resolution_repair=attach_regen_coolant_property_resolution_repair,

            attach_regen_architecture_visibility_audit=attach_regen_architecture_visibility_audit,

            attach_regen_candidate_ranking_payload_bridge=attach_regen_candidate_ranking_payload_bridge,


            attach_regen_input_mapping_repair=attach_regen_input_mapping_repair,



















            attach_material_property_interpolation_owner=attach_material_property_interpolation_owner,
            attach_material_source_provenance_owner=attach_material_source_provenance_owner,
            attach_correlation_source_provenance_owner=attach_correlation_source_provenance_owner,
            attach_material_source_quality_ranking_owner=attach_material_source_quality_ranking_owner,
            attach_material_validation_owner=attach_material_validation_owner,
            attach_material_completion_audit=attach_material_completion_audit,
            attach_coating_source_provenance_owner=attach_coating_source_provenance_owner,
            attach_coating_validation_owner=attach_coating_validation_owner,
            attach_material_and_coating_foundation_audit=attach_material_and_coating_foundation_audit,
            attach_material_coating_solver_integration_planning_owner=attach_material_coating_solver_integration_planning_owner,
            attach_material_property_consumption_audit_owner=attach_material_property_consumption_audit_owner,
            attach_material_thermal_conductivity_integration_owner=attach_material_thermal_conductivity_integration_owner,
            attach_material_specific_heat_integration_owner=attach_material_specific_heat_integration_owner,
            attach_material_density_integration_owner=attach_material_density_integration_owner,
            attach_material_temperature_limit_integration_owner=attach_material_temperature_limit_integration_owner,
            attach_material_strength_limit_integration_owner=attach_material_strength_limit_integration_owner,
            attach_material_integration_validation_owner=attach_material_integration_validation_owner,
            attach_material_integration_completion_audit=attach_material_integration_completion_audit,
            attach_coating_property_consumption_audit_owner=attach_coating_property_consumption_audit_owner,
            attach_coating_thermal_conductivity_integration_owner=attach_coating_thermal_conductivity_integration_owner,
            attach_coating_thickness_integration_owner=attach_coating_thickness_integration_owner,
            attach_coating_thermal_resistance_integration_owner=attach_coating_thermal_resistance_integration_owner,
            attach_coating_temperature_limit_integration_owner=attach_coating_temperature_limit_integration_owner,
            attach_bond_coat_integration_owner=attach_bond_coat_integration_owner,
            attach_coating_integration_validation_owner=attach_coating_integration_validation_owner,
            attach_coating_integration_completion_audit=attach_coating_integration_completion_audit,
            attach_temperature_dependency_discovery_audit_owner=attach_temperature_dependency_discovery_audit_owner,
            attach_material_conductivity_consumption_audit_owner=attach_material_conductivity_consumption_audit_owner,
            attach_specific_heat_consumption_audit_owner=attach_specific_heat_consumption_audit_owner,
            attach_density_coolant_property_consumption_audit_owner=attach_density_coolant_property_consumption_audit_owner,
            attach_coating_thermal_consumption_audit_owner=attach_coating_thermal_consumption_audit_owner,
            attach_bond_coat_consumption_audit_owner=attach_bond_coat_consumption_audit_owner,
            attach_temperature_dependent_solver_completion_audit_owner=attach_temperature_dependent_solver_completion_audit_owner,
            attach_regen_geometry_constraint_discovery_audit_owner=attach_regen_geometry_constraint_discovery_audit_owner,
            attach_regen_geometry_constraint_validation_owner=attach_regen_geometry_constraint_validation_owner,
            attach_regen_geometry_failure_explanation_owner=attach_regen_geometry_failure_explanation_owner,
            attach_regen_geometry_recommendation_engine_owner=attach_regen_geometry_recommendation_engine_owner,
            attach_regen_geometry_apply_recommendation_owner=attach_regen_geometry_apply_recommendation_owner,
            attach_regen_geometry_output_architecture_owner=attach_regen_geometry_output_architecture_owner,
            attach_regen_geometry_candidate_acceptance_owner=attach_regen_geometry_candidate_acceptance_owner,
        )

    def finalize_foundation_regression(
            self,
            solved,
    ):
        return _finalize_foundation_regression(
            solved,
            attach_foundation_regression_tests,
        )

    def _attach_startup_health(self, solved):
        startup_health = self.get_startup_health() or {}

        solved["startup_health_status"] = startup_health.get("startup_health_status")
        solved["startup_health_text"] = startup_health.get("startup_health_text")
        solved["startup_health_required_failure_count"] = startup_health.get(
            "startup_health_required_failure_count"
        )
        solved["startup_health_optional_warning_count"] = startup_health.get(
            "startup_health_optional_warning_count"
        )

        solved["startup_health_attached_to_results"] = True

    def run_foundation_verification(self):
        if run_foundation_verification_harness is None:
            return {
                "foundation_verification_status": "FAIL_HARNESS_UNAVAILABLE",
                "foundation_layer_verified": False,
                "foundation_verification_text": (
                    "Foundation verification harness could not be imported."
                ),
            }

        if build_report_viewer_bundle is None or get_main_output_results is None:
            return {
                "foundation_verification_status": "FAIL_REPORT_CALLBACKS_UNAVAILABLE",
                "foundation_layer_verified": False,
                "foundation_verification_text": (
                    "Report ownership callbacks could not be imported."
                ),
            }

        return run_foundation_verification_harness(
            apply_foundation_layers_callback=self.apply_foundation_layers,
            build_report_viewer_bundle_callback=build_report_viewer_bundle,
            get_main_output_results_callback=get_main_output_results,
        )