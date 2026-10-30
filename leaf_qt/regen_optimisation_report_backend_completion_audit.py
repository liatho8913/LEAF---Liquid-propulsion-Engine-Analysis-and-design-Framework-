OWNER_NAME = "REGEN_OPTIMISATION_REPORT_BACKEND_COMPLETION_AUDIT"
PHASE = "15D"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_PHASE_15D"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_REPORT_BACKEND_PHASE_15D"


def attach_regen_optimisation_report_backend_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_optimisation_report_backend_registry_ready": "Report backend registry is not ready.",
        "regen_optimisation_report_backend_data_owner_ready": "Report backend data owner is not ready.",
        "regen_optimisation_report_section_owner_ready": "Report section owner is not ready.",
        "regen_optimisation_report_metrics_owner_ready": "Report metrics owner is not ready.",
        "regen_optimisation_report_history_owner_ready": "Report history owner is not ready.",
        "regen_optimisation_report_backend_report_owner_ready": "Report owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("optimisation_report_qt_window_created") is not False:
        blockers.append("Qt report window was illegally created in 15D.")

    if results.get("optimisation_report_pdf_exported") is not False:
        blockers.append("PDF export was illegally performed in 15D.")

    if results.get("optimisation_report_html_exported") is not False:
        blockers.append("HTML export was illegally performed in 15D.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_optimisation_report_backend_completion_audit_complete": True,
        "phase_15d_optimisation_report_backend_completion_audit_complete": True,
        "regen_optimisation_report_backend_completion_audit_ready": ready,
        "regen_optimisation_report_backend_completion_audit_status": status,
        "regen_optimisation_report_backend_completion_audit_blockers": blockers,

        "phase_15d_complete": ready,
        "phase_15d_status": status,
        "phase_16_unified_regen_ecosystem_allowed": ready,
    })

    return results
