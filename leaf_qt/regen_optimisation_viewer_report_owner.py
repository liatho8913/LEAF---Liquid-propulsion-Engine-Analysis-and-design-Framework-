OWNER_NAME = "REGEN_OPTIMISATION_VIEWER_REPORT_OWNER"
PHASE = "15A"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_VIEWER_REPORT_OWNER_PHASE_15A"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_VIEWER_REPORT_OWNER_PHASE_15A"


def attach_regen_optimisation_viewer_report_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if not isinstance(results.get("optimisation_viewer_history"), dict):
        blockers.append("Optimisation viewer history is missing.")

    if not isinstance(results.get("optimisation_viewer_generations"), list):
        blockers.append("Optimisation viewer generations are missing.")

    if not isinstance(results.get("optimisation_viewer_candidates"), list):
        blockers.append("Optimisation viewer candidates are missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(status, results)

    results.update({
        "regen_optimisation_viewer_report_owner_complete": True,
        "phase_15a_optimisation_viewer_report_owner_complete": True,
        "regen_optimisation_viewer_report_owner_ready": ready,
        "regen_optimisation_viewer_report_owner_status": status,
        "regen_optimisation_viewer_report_owner_blockers": blockers,

        "optimisation_viewer_backend_report": report,
    })

    return results


def _ready_report(status, results):
    return "\n".join([
        "PHASE 15A OPTIMISATION VIEWER BACKEND",
        f"Status: {status}",
        "",
        "Backend Data:",
        f"- Generations: {results.get('optimisation_viewer_generation_count')}",
        f"- Candidates: {results.get('optimisation_viewer_candidate_count')}",
        f"- Improvements: {results.get('optimisation_viewer_improvement_count')}",
        f"- Best score: {results.get('optimisation_viewer_best_score')}",
        f"- Current generation: {results.get('optimisation_viewer_current_generation')}",
        "",
        "Execution Locks:",
        "- Qt window creation: LOCKED",
        "- Plot rendering: LOCKED",
        "- UI widget creation: LOCKED",
        "",
        "Next phase: 15B Candidate Comparison Viewer Backend.",
    ])


def _blocked_report(blockers):
    lines = [
        "PHASE 15A OPTIMISATION VIEWER BACKEND",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines)
