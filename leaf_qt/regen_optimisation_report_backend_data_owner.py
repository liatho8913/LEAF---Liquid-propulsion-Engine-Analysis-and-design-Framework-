OWNER_NAME = "REGEN_OPTIMISATION_REPORT_BACKEND_DATA_OWNER"
PHASE = "15D"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_DATA_OWNER_PHASE_15D"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_REPORT_BACKEND_DATA_OWNER_PHASE_15D"


def attach_regen_optimisation_report_backend_data_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_optimisation_report_backend_registry_ready") is not True:
        blockers.append("Optimisation report backend registry is not ready.")

    required_sections = {
        "optimisation_viewer_backend_report": "Optimisation viewer backend report missing.",
        "candidate_comparison_backend_report": "Candidate comparison backend report missing.",
        "evolution_tree_report": "Evolution tree report missing.",
    }

    for key, message in required_sections.items():
        if not results.get(key):
            blockers.append(message)

    payload = {
        "optimisation_summary": {
            "runtime_backend_complete": results.get("phase_14_runtime_backend_complete"),
            "optimisation_complete": results.get("regen_runtime_optimisation_complete"),
            "continue_required": results.get("runtime_optimisation_continue_required"),
            "completion_reason": results.get("runtime_optimisation_completion_reason"),
            "final_generation": results.get("runtime_optimisation_final_generation"),
            "final_best_score": results.get("runtime_optimisation_final_best_score"),
        },
        "viewer_summary": {
            "generation_count": results.get("optimisation_viewer_generation_count"),
            "candidate_count": results.get("optimisation_viewer_candidate_count"),
            "improvement_count": results.get("optimisation_viewer_improvement_count"),
        },
        "comparison_summary": results.get("candidate_comparison_summary", {}),
        "evolution_tree_summary": results.get("evolution_tree_summary", {}),
        "source_reports": {
            "optimisation_viewer": results.get("optimisation_viewer_backend_report"),
            "candidate_comparison": results.get("candidate_comparison_backend_report"),
            "evolution_tree": results.get("evolution_tree_report"),
        },
    }

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_optimisation_report_backend_data_owner_complete": True,
        "phase_15d_optimisation_report_backend_data_owner_complete": True,
        "regen_optimisation_report_backend_data_owner_ready": ready,
        "regen_optimisation_report_backend_data_owner_status": status,
        "regen_optimisation_report_backend_data_owner_blockers": blockers,

        "optimisation_report_backend_payload": payload if ready else {},
        "optimisation_report_backend_source_count": len(payload["source_reports"]) if ready else 0,

        "optimisation_report_qt_window_created": False,
        "optimisation_report_pdf_exported": False,
        "optimisation_report_html_exported": False,
    })

    return results
