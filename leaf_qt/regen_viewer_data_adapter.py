"""
PHASE 16K.1 — Regen Viewer Data Integration Adapter

Purpose:
- Collect completed optimisation/recommendation/acceptance outputs.
- Convert them into one UI-safe regen viewer payload.
- Preserve report-only visibility.
- Does not alter geometry.
- Does not rerun solver.
- Does not change Qt layout yet.
"""

PASS_STATUS = "PASS_REGEN_VIEWER_DATA_ADAPTER_PHASE_16K1"
FAIL_STATUS = "FAIL_REGEN_VIEWER_DATA_ADAPTER_PHASE_16K1"


def attach_regen_viewer_data_adapter(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16j8_complete") is not True:
        blockers.append("Phase 16J.8 optimisation completion gate has not passed.")

    required_sections = {
        "completion_gate": "regen_optimisation_completion_gate_payload",
        "recommendation": "regen_recommendation_viewer_payload",
        "explanation": "regen_recommendation_explanation_payload",
        "root_cause": "regen_failure_root_cause_payload",
        "proof": "regen_optimisation_proof_payload",
        "history": "regen_design_iteration_history_event",
        "comparison": "regen_before_after_solver_comparison_report_payload",
    }

    sections = {}

    for section_name, key in required_sections.items():
        payload = results.get(key)
        if not isinstance(payload, dict) or not payload:
            blockers.append(f"Missing viewer section: {section_name} from {key}")
        else:
            sections[section_name] = payload

    candidate_id = _resolve_candidate_id(sections)

    if not candidate_id:
        blockers.append("Viewer adapter could not resolve candidate ID.")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    viewer_payload = None

    if status == PASS_STATUS:
        viewer_payload = {
            "status": status,
            "source_phase": "16K.1",
            "visibility": "UI_REPORT_VIEW",
            "candidate_id": candidate_id,
            "title": f"Regen Optimisation Result — Candidate {candidate_id}",
            "sections": {
                "summary": _summary_section(sections),
                "recommendation": _recommendation_section(sections),
                "comparison": _comparison_section(sections),
                "explanation": _explanation_section(sections),
                "root_cause": _root_cause_section(sections),
                "proof": _proof_section(sections),
                "history": _history_section(sections),
            },
            "ui_state": {
                "geometry_applied": True,
                "solver_regenerated": True,
                "report_only": True,
                "editable": False,
            },
        }

    report = _build_report(status, blockers, viewer_payload)

    results["regen_viewer_data_adapter_complete"] = True
    results["phase_16k1_complete"] = status == PASS_STATUS
    results["regen_viewer_data_adapter_status"] = status
    results["phase_16k1_status"] = status
    results["regen_viewer_data_adapter_blockers"] = blockers
    results["regen_viewer_payload"] = viewer_payload
    results["regen_viewer_data_adapter_report"] = report
    results["regen_viewer_visibility"] = "UI_REPORT_VIEW"

    results["phase_16k2_regen_viewer_report_renderer_allowed"] = status == PASS_STATUS

    return results


def _resolve_candidate_id(sections):
    for payload in sections.values():
        if isinstance(payload, dict) and payload.get("candidate_id"):
            return payload.get("candidate_id")
    return None


def _summary_section(sections):
    completion = sections["completion_gate"]
    proof = sections["proof"]
    return {
        "heading": "Optimisation Summary",
        "candidate_id": completion.get("candidate_id"),
        "completion_state": completion.get("completion_state"),
        "trust_score": proof.get("trust_score"),
        "status": completion.get("status"),
    }


def _recommendation_section(sections):
    recommendation = sections["recommendation"]
    return {
        "heading": "Recommended Candidate",
        "candidate_id": recommendation.get("candidate_id"),
        "rank": recommendation.get("rank"),
        "score": recommendation.get("score"),
        "reasoning": recommendation.get("reasoning"),
        "advantages": recommendation.get("advantages"),
        "penalties": recommendation.get("penalties"),
    }


def _comparison_section(sections):
    comparison = sections["comparison"]
    return {
        "heading": "Before / After Solver Comparison",
        "summary": comparison.get("summary"),
        "classified_changes": comparison.get("classified_changes"),
    }


def _explanation_section(sections):
    explanation = sections["explanation"]
    return {
        "heading": "Recommendation Explanation",
        "headline": explanation.get("headline"),
        "why_chosen": explanation.get("why_chosen"),
        "trust_assessment": explanation.get("trust_assessment"),
        "remaining_risks": explanation.get("remaining_risks"),
        "next_actions": explanation.get("next_actions"),
    }


def _root_cause_section(sections):
    root = sections["root_cause"]
    return {
        "heading": "Failure / Risk Root Cause",
        "summary": root.get("summary"),
        "root_causes": root.get("root_causes"),
        "next_actions": root.get("next_actions"),
    }


def _proof_section(sections):
    proof = sections["proof"]
    return {
        "heading": "Optimisation Proof",
        "proof_state": proof.get("proof_state"),
        "trust_score": proof.get("trust_score"),
        "proof_ledger": proof.get("proof_ledger"),
    }


def _history_section(sections):
    history = sections["history"]
    return {
        "heading": "Design Iteration History",
        "event_type": history.get("event_type"),
        "phase": history.get("phase"),
        "timestamp_utc": history.get("timestamp_utc"),
        "chain": history.get("chain"),
        "comparison_summary": history.get("comparison_summary"),
    }


def _build_report(status, blockers, viewer_payload):
    lines = [
        "LEAF PHASE 16K.1 REGEN VIEWER DATA ADAPTER",
        "============================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Collects completed optimisation outputs.",
        "- Builds one UI-safe regen viewer payload.",
        "- Preserves report-only visibility.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "- Does not change Qt layout yet.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Viewer Payload:",
        f"- Created: {bool(viewer_payload)}",
        f"- Candidate ID: {(viewer_payload or {}).get('candidate_id')}",
        f"- Visibility: {(viewer_payload or {}).get('visibility')}",
        "",
        "Next Required Phase:",
        "- 16K.2 Regen Viewer Report Renderer.",
    ])

    return "\n".join(lines)
