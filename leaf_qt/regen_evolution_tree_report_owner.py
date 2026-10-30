OWNER_NAME = "REGEN_EVOLUTION_TREE_REPORT_OWNER"
PHASE = "15C"

PASS_STATUS = "PASS_REGEN_EVOLUTION_TREE_REPORT_OWNER_PHASE_15C"
FAIL_STATUS = "FAIL_REGEN_EVOLUTION_TREE_REPORT_OWNER_PHASE_15C"


def attach_regen_evolution_tree_report_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if not isinstance(results.get("evolution_tree_history"), dict):
        blockers.append("Evolution tree history is missing.")

    if not isinstance(results.get("evolution_tree_summary"), dict):
        blockers.append("Evolution tree summary is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(status, results)

    results.update({
        "regen_evolution_tree_report_owner_complete": True,
        "phase_15c_evolution_tree_report_owner_complete": True,
        "regen_evolution_tree_report_owner_ready": ready,
        "regen_evolution_tree_report_owner_status": status,
        "regen_evolution_tree_report_owner_blockers": blockers,

        "evolution_tree_report": report,
    })

    return results


def _ready_report(status, results):
    summary = results.get("evolution_tree_summary", {})

    return "\n".join([
        "PHASE 15C EVOLUTION TREE BACKEND",
        f"Status: {status}",
        "",
        "Tree Backend Data:",
        f"- Generations: {summary.get('generation_count')}",
        f"- Parent links: {summary.get('parent_link_count')}",
        f"- Mutation links: {summary.get('mutation_link_count')}",
        f"- Paths: {summary.get('path_count')}",
        f"- Best candidate: {summary.get('best_candidate_id')}",
        "",
        "Execution Locks:",
        "- Qt tree viewer: LOCKED",
        "- Node graph rendering: LOCKED",
        "- UI widgets: LOCKED",
        "",
        "Next phase: 15D Optimisation Report Backend.",
    ])


def _blocked_report(blockers):
    lines = [
        "PHASE 15C EVOLUTION TREE BACKEND",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines)
