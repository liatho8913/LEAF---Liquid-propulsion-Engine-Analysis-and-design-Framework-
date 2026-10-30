OWNER_NAME = "REGEN_OPTIMISATION_REPORT_BACKEND_REPORT_OWNER"
PHASE = "15D"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_REPORT_OWNER_PHASE_15D"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_REPORT_BACKEND_REPORT_OWNER_PHASE_15D"


def attach_regen_optimisation_report_backend_report_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if not isinstance(results.get("optimisation_report_history"), dict):
        blockers.append("Optimisation report history is missing.")

    sections = results.get("optimisation_report_sections", [])
    metrics = results.get("optimisation_report_metrics", {})

    if not isinstance(sections, list) or not sections:
        blockers.append("Optimisation report sections are missing.")

    if not isinstance(metrics, dict):
        blockers.append("Optimisation report metrics are missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(status, sections, metrics, results)

    results.update({
        "regen_optimisation_report_backend_report_owner_complete": True,
        "phase_15d_optimisation_report_backend_report_owner_complete": True,
        "regen_optimisation_report_backend_report_owner_ready": ready,
        "regen_optimisation_report_backend_report_owner_status": status,
        "regen_optimisation_report_backend_report_owner_blockers": blockers,

        "optimisation_report_backend_report": report,
        "optimisation_report_backend_summary": _summary(results) if ready else {},
    })

    return results


def _ready_report(status, sections, metrics, results):
    lines = [
        "PHASE 15D OPTIMISATION REPORT BACKEND",
        f"Status: {status}",
        "",
        "Report Sections:",
    ]

    for section in sections:
        lines.append(f"- {section.get('title')}")

    lines.extend([
        "",
        "Key Metrics:",
        f"- Final best score: {metrics.get('final_best_score')}",
        f"- Final generation: {metrics.get('final_generation')}",
        f"- Candidate count: {metrics.get('candidate_count')}",
        f"- Evolution-tree generations: {metrics.get('evolution_tree_generation_count')}",
        "",
        "Execution Locks:",
        "- Qt report window: LOCKED",
        "- PDF export: LOCKED",
        "- HTML export: LOCKED",
        "",
        "Next phase: 16 Unified Regen Ecosystem Integration.",
    ])

    return "\n".join(lines)


def _blocked_report(blockers):
    lines = [
        "PHASE 15D OPTIMISATION REPORT BACKEND",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines)


def _summary(results):
    return {
        "section_count": results.get("optimisation_report_section_count"),
        "source_count": results.get("optimisation_report_backend_source_count"),
        "final_best_score": results.get("runtime_optimisation_final_best_score"),
        "final_generation": results.get("runtime_optimisation_final_generation"),
        "ready_for_phase_16": True,
    }
