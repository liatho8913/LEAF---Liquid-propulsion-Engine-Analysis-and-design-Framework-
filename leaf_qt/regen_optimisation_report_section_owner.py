OWNER_NAME = "REGEN_OPTIMISATION_REPORT_SECTION_OWNER"
PHASE = "15D"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_REPORT_SECTION_OWNER_PHASE_15D"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_REPORT_SECTION_OWNER_PHASE_15D"


def attach_regen_optimisation_report_section_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_optimisation_report_backend_data_owner_ready") is not True:
        blockers.append("Optimisation report backend data owner is not ready.")

    payload = results.get("optimisation_report_backend_payload", {})
    if not isinstance(payload, dict) or not payload:
        blockers.append("Optimisation report backend payload is missing.")

    sections = []

    if not blockers:
        sections = [
            _section(
                "OPTIMISATION_REPORT_SECTION_15D_EXECUTIVE_SUMMARY",
                "Executive Summary",
                payload.get("optimisation_summary", {}),
            ),
            _section(
                "OPTIMISATION_REPORT_SECTION_15D_VIEWER_BACKEND",
                "Optimisation Viewer Backend",
                payload.get("viewer_summary", {}),
            ),
            _section(
                "OPTIMISATION_REPORT_SECTION_15D_CANDIDATE_COMPARISON",
                "Candidate Comparison",
                payload.get("comparison_summary", {}),
            ),
            _section(
                "OPTIMISATION_REPORT_SECTION_15D_EVOLUTION_TREE",
                "Evolution Tree",
                payload.get("evolution_tree_summary", {}),
            ),
            _section(
                "OPTIMISATION_REPORT_SECTION_15D_SOURCE_REPORTS",
                "Source Reports",
                payload.get("source_reports", {}),
            ),
        ]

    ready = len(blockers) == 0 and len(sections) >= 5
    if not ready and not blockers:
        blockers.append("Required optimisation report sections were not assembled.")

    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_optimisation_report_section_owner_complete": True,
        "phase_15d_optimisation_report_section_owner_complete": True,
        "regen_optimisation_report_section_owner_ready": ready,
        "regen_optimisation_report_section_owner_status": status,
        "regen_optimisation_report_section_owner_blockers": blockers,

        "optimisation_report_sections": sections if ready else [],
        "optimisation_report_section_count": len(sections) if ready else 0,
    })

    return results


def _section(section_id, title, data):
    return {
        "section_id": section_id,
        "title": title,
        "data": data,
        "backend_only": True,
        "rendered": False,
    }
