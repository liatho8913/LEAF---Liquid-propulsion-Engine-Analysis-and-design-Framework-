"""
PHASE 16I — Regen Architecture Visibility Audit

Purpose:
- Explain the regen optimisation architecture as a readable chain.
- Show complete / blocked / locked / allowed status for each subsystem.
- Does not mutate geometry.
- Does not run optimisation.
- Does not accept/reject candidates.
"""
from leaf_qt.status_presentation import status_severity

CHAIN = [
    {
        "name": "Manual Regen Geometry",
        "complete_keys": [
            "regen_input_mapping_repair_base_geometry_complete",
            "regen_workflow_manual_complete",
        ],
        "status_keys": [
            "regen_input_mapping_repair_status",
            "regen_workflow_status_text",
        ],
        "meaning": "Manual geometry and mapped base values required before candidate generation.",
    },
    {
        "name": "Coolant Property Resolution",
        "complete_keys": [
            "regen_coolant_property_resolution_repair_complete",
        ],
        "status_keys": [
            "regen_coolant_property_resolution_repair_status",
        ],
        "meaning": "Coolant mass flow and properties must exist before recommended/candidate geometry can run.",
    },
    {
        "name": "Candidate Generation",
        "complete_keys": [
            "regen_optimisation_candidate_generator_complete",
            "phase_8b_regen_optimisation_candidate_generator_complete",
        ],
        "status_keys": [
            "regen_optimisation_candidate_generator_status",
        ],
        "count_keys": [
            "regen_optimisation_candidate_generator_candidate_count",
        ],
        "meaning": "Creates candidate geometry options from the current/base regen design.",
    },
    {
        "name": "Candidate Population",
        "complete_keys": [
            "regen_candidate_population_master_gate_ready",
            "regen_population_master_gate_ready",
            "phase_11b_3e_regen_candidate_population_master_gate_complete",
        ],
        "status_keys": [
            "regen_candidate_population_master_gate_status",
            "regen_population_master_gate_status",
        ],
        "count_keys": [
            "regen_candidate_population_count",
            "regen_optimisation_candidate_generator_candidate_count",
        ],
        "meaning": "Stores and registers a population of candidate designs.",
    },
    {
        "name": "Candidate Ranking",
        "complete_keys": [
            "regen_candidate_ranking_master_gate_ready",
            "phase_11b_4_candidate_ranking_architecture_allowed",
        ],
        "status_keys": [
            "regen_candidate_ranking_master_gate_status",
            "regen_candidate_ranking_owner_status",
        ],
        "count_keys": [
            "regen_optimisation_scored_candidate_count",
            "regen_optimisation_recommendation_ranked_candidate_count",
        ],
        "meaning": "Scores candidates and orders them by engineering objectives.",
    },
    {
        "name": "Selection Framework",
        "complete_keys": [
            "phase_13k_complete",
            "regen_optimisation_selection_framework_complete",
        ],
        "status_keys": [
            "phase_13k_status",
            "regen_optimisation_selection_master_gate_status",
        ],
        "meaning": "Builds parent pools and selects candidates for later generations.",
    },
    {
        "name": "Runtime Mutation",
        "complete_keys": [
            "phase_14a_complete",
        ],
        "status_keys": [
            "phase_14a_status",
            "regen_runtime_mutation_execution_master_gate_status",
        ],
        "locked_keys": [
            "regen_runtime_mutation_live_geometry_committed",
            "regen_runtime_mutation_solver_executed",
        ],
        "meaning": "Runtime mutation architecture exists, but live solving/commit remains locked unless explicitly enabled.",
    },
    {
        "name": "Runtime Candidate Evaluation",
        "complete_keys": [
            "phase_14b_complete",
        ],
        "status_keys": [
            "phase_14b_status",
            "regen_runtime_candidate_evaluation_master_gate_status",
        ],
        "count_keys": [
            "regen_runtime_candidate_evaluation_count",
            "regen_runtime_candidate_evaluation_record_count",
        ],
        "meaning": "Evaluates runtime candidates in a controlled, auditable layer.",
    },
    {
        "name": "Runtime Selection",
        "complete_keys": [
            "phase_14c_complete",
        ],
        "status_keys": [
            "phase_14c_status",
            "regen_runtime_selection_master_gate_status",
        ],
        "meaning": "Selects runtime candidates without automatically committing live geometry.",
    },
    {
        "name": "Runtime Evolution",
        "complete_keys": [
            "phase_14d_complete",
        ],
        "status_keys": [
            "phase_14d_status",
            "regen_runtime_evolution_master_gate_status",
        ],
        "count_keys": [
            "regen_runtime_generation_population_count",
            "regen_runtime_parent_lineage_count",
        ],
        "meaning": "Creates generation-to-generation evolution records.",
    },
    {
        "name": "Runtime Convergence",
        "complete_keys": [
            "phase_14e_complete",
        ],
        "status_keys": [
            "phase_14e_status",
            "regen_runtime_convergence_master_gate_status",
        ],
        "meaning": "Checks improvement, stagnation, and stop conditions.",
    },
    {
        "name": "Runtime Optimisation Completion",
        "complete_keys": [
            "phase_14f_complete",
        ],
        "status_keys": [
            "phase_14f_status",
            "regen_runtime_optimisation_completion_master_gate_status",
        ],
        "meaning": "Audits runtime optimisation completion without pretending autonomous optimisation is live.",
    },
    {
        "name": "Unified Regen Ecosystem",
        "complete_keys": [
            "phase_16a_complete",
            "phase_16b_complete",
            "phase_16c_complete",
            "phase_16d_complete",
            "phase_16e_complete",
            "phase_16f_complete",
        ],
        "status_keys": [
            "phase_16a_status",
            "phase_16b_status",
            "phase_16c_status",
            "phase_16d_status",
            "phase_16e_status",
            "phase_16f_status",
        ],
        "meaning": "Connects viewer/report/validation/signoff/completion layers.",
    },
]


def _truthy(value):
    return value is True or value == 1 or value == "1" or status_severity(str(value).upper()) == "PASS"


def _get_first(results, keys, default=None):
    for key in keys:
        if key in results:
            return results.get(key)
    return default


def _count_value(results, keys):
    for key in keys:
        value = results.get(key)
        if value is not None:
            try:
                return int(float(value))
            except Exception:
                return value
    return None


def _step_state(results, step):
    complete_values = [(key, results.get(key)) for key in step.get("complete_keys", []) if key in results]
    status_values = [(key, results.get(key)) for key in step.get("status_keys", []) if key in results]
    locked_values = [(key, results.get(key)) for key in step.get("locked_keys", []) if key in results]
    count = _count_value(results, step.get("count_keys", []))

    complete = any(_truthy(value) for _, value in complete_values)

    blocked = any(
        "FAIL" in str(value).upper() or "BLOCKED" in str(value).upper()
        for _, value in status_values
    )

    locked = any(value is False or value == 0 or value == "0" for _, value in locked_values)

    if complete and not blocked:
        state = "COMPLETE"
    elif blocked:
        state = "BLOCKED"
    elif complete_values or status_values:
        state = "PARTIAL"
    else:
        state = "NOT_VISIBLE"

    return {
        "name": step["name"],
        "state": state,
        "complete": complete,
        "blocked": blocked,
        "locked": locked,
        "count": count,
        "complete_values": complete_values,
        "status_values": status_values,
        "locked_values": locked_values,
        "meaning": step["meaning"],
    }


def attach_regen_architecture_visibility_audit(results):
    if not isinstance(results, dict):
        return results

    states = [_step_state(results, step) for step in CHAIN]

    complete_count = sum(1 for state in states if state["state"] == "COMPLETE")
    blocked_count = sum(1 for state in states if state["state"] == "BLOCKED")
    partial_count = sum(1 for state in states if state["state"] == "PARTIAL")
    not_visible_count = sum(1 for state in states if state["state"] == "NOT_VISIBLE")

    lines = [
        "LEAF PHASE 16I — REGEN ARCHITECTURE VISIBILITY AUDIT",
        "====================================================",
        "",
        "Purpose:",
        "- Explain the regen optimisation chain.",
        "- Show what exists, what is complete, what is blocked, and what is runtime-locked.",
        "- This audit does not run optimisation or modify live geometry.",
        "",
        "Summary:",
        f"- Total subsystems checked: {len(states)}",
        f"- Complete: {complete_count}",
        f"- Blocked: {blocked_count}",
        f"- Partial: {partial_count}",
        f"- Not visible: {not_visible_count}",
        "",
        "Architecture Chain:",
    ]

    for index, state in enumerate(states, 1):
        lines.extend([
            "",
            f"{index}. {state['name']}",
            f"   State: {state['state']}",
            f"   Count: {state['count']}" if state["count"] is not None else "   Count: N/A",
            f"   Meaning: {state['meaning']}",
        ])

        if state["status_values"]:
            lines.append("   Status keys:")
            for key, value in state["status_values"]:
                lines.append(f"   - {key}: {value}")

        if state["complete_values"]:
            lines.append("   Completion keys:")
            for key, value in state["complete_values"]:
                lines.append(f"   - {key}: {value}")

        if state["locked_values"]:
            lines.append("   Runtime safety locks:")
            for key, value in state["locked_values"]:
                lines.append(f"   - {key}: {value}")

    next_actions = []

    if blocked_count:
        next_actions.append("Resolve blocked subsystems before enabling new runtime automation.")
    if not_visible_count:
        next_actions.append("Expose missing subsystem state in result/report/viewer registries.")
    if complete_count >= 8:
        next_actions.append("Proceed to candidate ranking visibility after this audit is registered.")
    else:
        next_actions.append("Do not proceed to ranking UI until the chain is visible enough to explain.")

    lines.extend([
        "",
        "Recommended Next Actions:",
    ])
    for action in next_actions:
        lines.append(f"- {action}")

    report = "\n".join(lines)

    results["regen_architecture_visibility_audit_complete"] = True
    results["phase_16i_complete"] = True
    results["phase_16i_status"] = "PASS_REGEN_ARCHITECTURE_VISIBILITY_AUDIT_PHASE_16I"
    results["regen_architecture_visibility_audit_status"] = "PASS_REGEN_ARCHITECTURE_VISIBILITY_AUDIT_PHASE_16I"
    results["regen_architecture_visibility_audit_report"] = report
    results["regen_architecture_visibility_audit_states"] = states
    results["regen_architecture_visibility_audit_summary"] = {
        "total": len(states),
        "complete": complete_count,
        "blocked": blocked_count,
        "partial": partial_count,
        "not_visible": not_visible_count,
    }
    results["regen_architecture_visibility_audit_next_actions"] = next_actions
    results["phase_16j_candidate_ranking_inspector_allowed"] = True

    return results
