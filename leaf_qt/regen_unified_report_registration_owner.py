OWNER_NAME = "REGEN_UNIFIED_REPORT_REGISTRATION_OWNER"
PHASE = "16A"

PASS_STATUS = "PASS_REGEN_UNIFIED_REPORT_REGISTRATION_OWNER_PHASE_16A"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_REPORT_REGISTRATION_OWNER_PHASE_16A"


def attach_regen_unified_report_registration_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_viewer_registration_owner_ready") is not True:
        blockers.append("Unified viewer registration owner is not ready.")

    reports = [
        ("optimisation_viewer_backend_report", "OPTIMISATION_VIEWER_REPORT"),
        ("candidate_comparison_backend_report", "CANDIDATE_COMPARISON_REPORT"),
        ("evolution_tree_report", "EVOLUTION_TREE_REPORT"),
        ("optimisation_report_backend_report", "OPTIMISATION_REPORT_BACKEND_REPORT"),
        ("regen_runtime_optimisation_completion_report", "RUNTIME_OPTIMISATION_COMPLETION_REPORT"),
        ("regen_runtime_convergence_report", "RUNTIME_CONVERGENCE_REPORT"),
    ]

    registered = []

    for key, report_id in reports:
        exists = results.get(key) is not None
        registered.append({
            "report_id": report_id,
            "source_key": key,
            "registered": exists,
            "rendered": False,
            "exported": False,
        })

    missing = [r["report_id"] for r in registered if r.get("registered") is not True]
    if missing:
        blockers.append("Report backend registrations missing: " + ", ".join(missing))

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_report_registration_owner_complete": True,
        "phase_16a_unified_report_registration_owner_complete": True,
        "regen_unified_report_registration_owner_ready": ready,
        "regen_unified_report_registration_owner_status": status,
        "regen_unified_report_registration_owner_blockers": blockers,

        "unified_regen_registered_reports": registered if ready else [],
        "unified_regen_registered_report_count": len(registered) if ready else 0,
        "unified_regen_report_rendering_performed": False,
        "unified_regen_report_export_performed": False,
    })

    return results
