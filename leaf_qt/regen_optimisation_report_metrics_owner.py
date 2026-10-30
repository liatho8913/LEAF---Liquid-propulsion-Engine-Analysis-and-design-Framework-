OWNER_NAME = "REGEN_OPTIMISATION_REPORT_METRICS_OWNER"
PHASE = "15D"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_REPORT_METRICS_OWNER_PHASE_15D"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_REPORT_METRICS_OWNER_PHASE_15D"


def attach_regen_optimisation_report_metrics_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_optimisation_report_section_owner_ready") is not True:
        blockers.append("Optimisation report section owner is not ready.")

    metrics = {
        "final_best_score": results.get("runtime_optimisation_final_best_score"),
        "final_generation": results.get("runtime_optimisation_final_generation"),
        "generation_count": results.get("optimisation_viewer_generation_count"),
        "candidate_count": results.get("optimisation_viewer_candidate_count"),
        "comparison_best_score": _nested(results, "candidate_comparison_summary", "best_score"),
        "comparison_baseline_score": _nested(results, "candidate_comparison_summary", "baseline_score"),
        "evolution_tree_generation_count": _nested(results, "evolution_tree_summary", "generation_count"),
        "evolution_tree_parent_link_count": _nested(results, "evolution_tree_summary", "parent_link_count"),
        "evolution_tree_mutation_link_count": _nested(results, "evolution_tree_summary", "mutation_link_count"),
    }

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_optimisation_report_metrics_owner_complete": True,
        "phase_15d_optimisation_report_metrics_owner_complete": True,
        "regen_optimisation_report_metrics_owner_ready": ready,
        "regen_optimisation_report_metrics_owner_status": status,
        "regen_optimisation_report_metrics_owner_blockers": blockers,

        "optimisation_report_metrics": metrics if ready else {},
    })

    return results


def _nested(results, key, child):
    value = results.get(key)
    if isinstance(value, dict):
        return value.get(child)
    return None
