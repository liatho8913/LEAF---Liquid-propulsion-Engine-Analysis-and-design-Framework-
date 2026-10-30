OWNER_NAME = "REGEN_OPTIMISATION_REPORT_HISTORY_OWNER"
PHASE = "15D"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_REPORT_HISTORY_OWNER_PHASE_15D"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_REPORT_HISTORY_OWNER_PHASE_15D"


def attach_regen_optimisation_report_history_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_optimisation_report_metrics_owner_ready") is not True:
        blockers.append("Optimisation report metrics owner is not ready.")

    sections = results.get("optimisation_report_sections", [])
    if not isinstance(sections, list) or not sections:
        blockers.append("Optimisation report sections are missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None

    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "OPTIMISATION_REPORT_BACKEND_ASSEMBLED",
            "entries": [
                {
                    "entry_id": "OPTIMISATION_REPORT_HISTORY_15D_SECTIONS",
                    "event": "REPORT_SECTIONS_ASSEMBLED",
                    "section_count": len(sections),
                },
                {
                    "entry_id": "OPTIMISATION_REPORT_HISTORY_15D_METRICS",
                    "event": "REPORT_METRICS_ASSEMBLED",
                    "metric_count": len(results.get("optimisation_report_metrics", {})),
                },
            ],
            "qt_report_window_count": 0,
            "pdf_export_count": 0,
            "html_export_count": 0,
        }

    results.update({
        "regen_optimisation_report_history_owner_complete": True,
        "phase_15d_optimisation_report_history_owner_complete": True,
        "regen_optimisation_report_history_owner_ready": ready,
        "regen_optimisation_report_history_owner_status": status,
        "regen_optimisation_report_history_owner_blockers": blockers,

        "optimisation_report_history": history if ready else {},
    })

    return results
