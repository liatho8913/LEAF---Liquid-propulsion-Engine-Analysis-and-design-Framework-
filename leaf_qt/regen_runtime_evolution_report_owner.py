OWNER_NAME = "REGEN_RUNTIME_EVOLUTION_REPORT_OWNER"
PHASE = "14D"

PASS_STATUS = "PASS_REGEN_RUNTIME_EVOLUTION_REPORT_OWNER_PHASE_14D"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_EVOLUTION_REPORT_OWNER_PHASE_14D"


def attach_regen_runtime_evolution_report_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    history = results.get("regen_runtime_evolution_history")
    generation = results.get("regen_runtime_generation")
    lineage = results.get("regen_runtime_parent_lineage", [])

    if not isinstance(history, dict):
        blockers.append("Runtime evolution history is missing.")

    if not isinstance(generation, dict):
        blockers.append("Runtime generation record is missing.")

    if not isinstance(lineage, list) or not lineage:
        blockers.append("Runtime parent lineage is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(status, generation, lineage)

    results.update({
        "regen_runtime_evolution_report_owner_complete": True,
        "phase_14d_runtime_evolution_report_owner_complete": True,
        "regen_runtime_evolution_report_owner_ready": ready,
        "regen_runtime_evolution_report_owner_status": status,
        "regen_runtime_evolution_report_owner_blockers": blockers,
        "regen_runtime_evolution_report": report,
    })

    return results


def _ready_report(status, generation, lineage):
    lines = [
        "PHASE 14D RUNTIME EVOLUTION ENGINE",
        f"Status: {status}",
        "",
        "Generation Advancement:",
        f"- New generation: {generation.get('runtime_generation_number')}",
        f"- Population size: {generation.get('population_size')}",
        "",
        "Parent Lineage:",
    ]

    for item in lineage[:20]:
        lines.append(
            f"- {item.get('parent_runtime_candidate_id')} -> "
            f"{item.get('child_runtime_generation_candidate_id')}"
        )

    lines.extend([
        "",
        "Execution Locks:",
        "- Convergence detection: LOCKED UNTIL 14E",
        "- Termination logic: LOCKED UNTIL 14E/14F",
        "- Live geometry commit: LOCKED",
        "- Full runtime optimisation loop: LOCKED",
    ])

    return "\n".join(lines)


def _blocked_report(blockers):
    lines = [
        "PHASE 14D RUNTIME EVOLUTION ENGINE",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines)
