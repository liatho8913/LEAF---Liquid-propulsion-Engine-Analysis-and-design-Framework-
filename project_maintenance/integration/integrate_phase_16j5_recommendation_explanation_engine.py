from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_recommendation_explanation_engine.py").write_text(r'''"""
PHASE 16J.5 — Recommendation Explanation Engine

Purpose:
- Explain why the accepted/recommended candidate was chosen.
- Explain what changed.
- Explain what improved, regressed, or stayed neutral.
- Explain remaining risks and next actions.
- Does not modify geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_RECOMMENDATION_EXPLANATION_ENGINE_PHASE_16J5"
FAIL_STATUS = "FAIL_REGEN_RECOMMENDATION_EXPLANATION_ENGINE_PHASE_16J5"


def attach_regen_recommendation_explanation_engine(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16j4g_complete") is not True:
        blockers.append("Phase 16J.4G candidate acceptance completion gate has not passed.")

    gate = results.get("regen_candidate_acceptance_completion_gate_payload")
    recommendation = results.get("regen_recommendation_viewer_payload")
    comparison = results.get("regen_before_after_solver_comparison_report_payload")
    history_event = results.get("regen_design_iteration_history_event")
    summary = results.get("regen_before_after_solver_comparison_summary")

    required = {
        "completion gate payload": gate,
        "recommendation viewer payload": recommendation,
        "before/after comparison report payload": comparison,
        "design iteration history event": history_event,
        "comparison summary": summary,
    }

    for name, payload in required.items():
        if not isinstance(payload, dict) or not payload:
            blockers.append(f"Missing {name}.")

    candidate_id = _candidate_id(gate, recommendation, comparison, history_event)

    if not candidate_id:
        blockers.append("Candidate ID could not be resolved for recommendation explanation.")

    explanation_payload = None

    if not blockers:
        classified_changes = comparison.get("classified_changes") or []

        explanation_payload = {
            "status": PASS_STATUS,
            "candidate_id": candidate_id,
            "visibility": "REPORT_ONLY",
            "source_phase": "16J.5",
            "headline": _headline(candidate_id, summary),
            "why_chosen": _why_chosen(recommendation, comparison, summary),
            "trade_offs": _trade_offs(classified_changes),
            "improvements": _changes_by_class(classified_changes, "IMPROVED"),
            "regressions": _changes_by_class(classified_changes, "REGRESSED"),
            "neutral_changes": [
                c for c in classified_changes
                if c.get("classification") in {"CHANGED_NEUTRAL", "CHANGED_NON_NUMERIC"}
            ],
            "trust_assessment": _trust_assessment(summary),
            "remaining_risks": _remaining_risks(summary, classified_changes),
            "next_actions": _next_actions(summary, classified_changes),
            "history_chain": history_event.get("chain"),
        }

    status = PASS_STATUS if not blockers else FAIL_STATUS

    report = _build_report(status, blockers, explanation_payload)

    results["regen_recommendation_explanation_engine_complete"] = True
    results["phase_16j5_complete"] = status == PASS_STATUS
    results["regen_recommendation_explanation_engine_status"] = status
    results["phase_16j5_status"] = status
    results["regen_recommendation_explanation_engine_blockers"] = blockers
    results["regen_recommendation_explanation_payload"] = explanation_payload
    results["regen_recommendation_explanation_report"] = report
    results["regen_recommendation_explanation_visibility"] = "REPORT_ONLY"

    results["phase_16j6_failure_root_cause_system_allowed"] = status == PASS_STATUS

    return results


def _candidate_id(*payloads):
    for payload in payloads:
        if isinstance(payload, dict):
            value = payload.get("candidate_id")
            if value:
                return value
    return None


def _headline(candidate_id, summary):
    improved = summary.get("improved", 0)
    regressed = summary.get("regressed", 0)

    if improved > 0 and regressed == 0:
        return f"Candidate {candidate_id} was accepted because it improved solver outputs without recorded regressions."
    if improved > 0 and regressed > 0:
        return f"Candidate {candidate_id} was accepted with trade-offs: {improved} improvements and {regressed} regressions."
    return f"Candidate {candidate_id} was accepted, but no clear solver-output improvement was recorded."


def _why_chosen(recommendation, comparison, summary):
    reasons = []

    reasoning = recommendation.get("reasoning")
    if reasoning:
        reasons.append(reasoning)

    if summary.get("improved", 0) > 0:
        reasons.append(
            f"Post-commit solver comparison recorded {summary.get('improved')} improved output(s)."
        )

    if summary.get("regressed", 0) == 0:
        reasons.append("No regressed solver outputs were recorded in the comparison report.")
    else:
        reasons.append(
            f"{summary.get('regressed')} regressed solver output(s) were recorded and must be reviewed."
        )

    if comparison.get("visibility") == "REPORT_ONLY":
        reasons.append("The comparison is owned as a report-only payload, preserving output visibility rules.")

    return reasons


def _changes_by_class(changes, class_name):
    return [c for c in changes if c.get("classification") == class_name]


def _trade_offs(changes):
    tradeoffs = []

    for change in changes:
        if not change.get("changed"):
            continue

        tradeoffs.append({
            "key": change.get("key"),
            "before": change.get("before"),
            "after": change.get("after"),
            "classification": change.get("classification"),
            "explanation": _change_sentence(change),
        })

    return tradeoffs


def _change_sentence(change):
    key = change.get("key")
    before = change.get("before")
    after = change.get("after")
    classification = change.get("classification")

    if classification == "IMPROVED":
        return f"{key} improved from {before} to {after}."
    if classification == "REGRESSED":
        return f"{key} regressed from {before} to {after}."
    if classification == "UNCHANGED":
        return f"{key} stayed unchanged at {after}."
    return f"{key} changed from {before} to {after}; this is treated as neutral until a domain rule is added."


def _trust_assessment(summary):
    improved = summary.get("improved", 0)
    regressed = summary.get("regressed", 0)

    if improved > 0 and regressed == 0:
        return {
            "level": "HIGH",
            "reason": "At least one output improved and no regressions were recorded.",
        }

    if improved > 0 and regressed > 0:
        return {
            "level": "MEDIUM",
            "reason": "The candidate improved some outputs but also introduced regressions.",
        }

    return {
        "level": "LOW",
        "reason": "No clear solver-output improvement was recorded.",
    }


def _remaining_risks(summary, changes):
    risks = []

    if summary.get("regressed", 0) > 0:
        risks.append("One or more solver outputs regressed and require review before automatic optimisation is trusted.")

    if summary.get("neutral_changed", 0) > 0:
        risks.append("Some changed outputs are not yet classified by domain-specific improvement rules.")

    if not changes:
        risks.append("No classified solver changes were available.")

    if not risks:
        risks.append("No immediate recommendation-level risks were detected by this explanation engine.")

    return risks


def _next_actions(summary, changes):
    actions = [
        "Review the report-only recommendation explanation in the UI/report viewer.",
        "Use the next phase to add failure root-cause explanation for any blocked or regressed paths.",
    ]

    if summary.get("regressed", 0) > 0:
        actions.append("Investigate regressed outputs before allowing automatic repeated optimisation.")

    if summary.get("neutral_changed", 0) > 0:
        actions.append("Add domain classification rules for neutral changed outputs.")

    return actions


def _build_report(status, blockers, explanation):
    lines = [
        "LEAF PHASE 16J.5 RECOMMENDATION EXPLANATION ENGINE",
        "====================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Explains why the accepted candidate was recommended.",
        "- Explains solver-output improvements, regressions, and neutral changes.",
        "- Produces trust assessment, risks, and next actions.",
        "- Does not modify geometry.",
        "- Does not rerun solver.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
        return "\n".join(lines)

    lines.extend([
        "- None.",
        "",
        "Headline:",
        explanation.get("headline"),
        "",
        "Why Chosen:",
    ])

    for reason in explanation.get("why_chosen", []):
        lines.append(f"- {reason}")

    lines.extend([
        "",
        "Trust Assessment:",
        f"- Level: {explanation.get('trust_assessment', {}).get('level')}",
        f"- Reason: {explanation.get('trust_assessment', {}).get('reason')}",
        "",
        "Improvements:",
    ])

    for change in explanation.get("improvements", []):
        lines.append(f"- {change.get('key')}: {change.get('before')} -> {change.get('after')}")

    if not explanation.get("improvements"):
        lines.append("- None.")

    lines.append("")
    lines.append("Regressions:")

    for change in explanation.get("regressions", []):
        lines.append(f"- {change.get('key')}: {change.get('before')} -> {change.get('after')}")

    if not explanation.get("regressions"):
        lines.append("- None.")

    lines.append("")
    lines.append("Remaining Risks:")

    for risk in explanation.get("remaining_risks", []):
        lines.append(f"- {risk}")

    lines.append("")
    lines.append("Next Actions:")

    for action in explanation.get("next_actions", []):
        lines.append(f"- {action}")

    lines.extend([
        "",
        "Visibility:",
        "- REPORT_ONLY",
        "",
        "Next Required Phase:",
        "- 16J.6 Failure Root Cause System.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_recommendation_explanation_engine_phase_16j5.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation
from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution
from regen_solver_regeneration_after_commit import attach_regen_solver_regeneration_after_commit
from regen_before_after_solver_comparison_report_owner import attach_regen_before_after_solver_comparison_report_owner
from regen_design_iteration_history_link import attach_regen_design_iteration_history_link
from regen_candidate_acceptance_completion_gate import attach_regen_candidate_acceptance_completion_gate
from regen_recommendation_explanation_engine import attach_regen_recommendation_explanation_engine


def fake_solver(payload):
    out = dict(payload)
    out["corrected_thrust"] = 3500.0
    out["isp_vac"] = 315.0
    out["coolant_pressure_drop"] = 900.0
    out["regen_validation_status"] = "PASS_REGENERATED_SOLVER_PAYLOAD"
    return out


def main():
    results = {
        "number_of_coolant_channels": 60,
        "coolant_channel_width": 0.0010,
        "coolant_channel_height": 0.0015,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0008,
        "corrected_thrust": 3300.0,
        "isp_vac": 300.0,
        "coolant_pressure_drop": 1200.0,
        "regen_solver_regeneration_callable": fake_solver,
        "regen_candidate_ranking_input_population": [
            {
                "candidate_id": "CANDIDATE_A",
                "candidate_geometry": {
                    "number_of_coolant_channels": 80,
                    "coolant_channel_width": 0.0015,
                    "coolant_channel_height": 0.0020,
                    "rib_width": 0.0010,
                    "hot_gas_wall_thickness": 0.0010,
                },
            }
        ],
    }

    for fn in (
        attach_regen_ranking_owner_source_repair,
        attach_regen_recommendation_feed_repair,
        attach_regen_recommendation_viewer_repair,
        attach_regen_end_to_end_candidate_selection_validation,
        attach_regen_candidate_acceptance_integration,
        attach_regen_pending_geometry_commit_validation,
        attach_regen_live_geometry_commit_execution,
        attach_regen_solver_regeneration_after_commit,
        attach_regen_before_after_solver_comparison_report_owner,
        attach_regen_design_iteration_history_link,
        attach_regen_candidate_acceptance_completion_gate,
        attach_regen_recommendation_explanation_engine,
    ):
        results = fn(results)

    assert results["phase_16j5_complete"] is True
    assert results["phase_16j5_status"] == "PASS_REGEN_RECOMMENDATION_EXPLANATION_ENGINE_PHASE_16J5"

    payload = results["regen_recommendation_explanation_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["visibility"] == "REPORT_ONLY"
    assert payload["trust_assessment"]["level"] == "HIGH"
    assert len(payload["improvements"]) >= 3
    assert len(payload["why_chosen"]) >= 2

    report = results["regen_recommendation_explanation_report"]
    assert "RECOMMENDATION EXPLANATION ENGINE" in report
    assert "Trust Assessment" in report
    assert "Next Actions" in report

    assert results["phase_16j6_failure_root_cause_system_allowed"] is True

    print("PASS_REGEN_RECOMMENDATION_EXPLANATION_ENGINE_PHASE_16J5")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_recommendation_explanation_engine import attach_regen_recommendation_explanation_engine" not in text:
    anchor = (
        "try:\n"
        "    from regen_candidate_acceptance_completion_gate import attach_regen_candidate_acceptance_completion_gate\n"
        "except Exception:\n"
        "    attach_regen_candidate_acceptance_completion_gate = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_recommendation_explanation_engine import attach_regen_recommendation_explanation_engine\n"
        "except Exception:\n"
        "    attach_regen_recommendation_explanation_engine = None\n"
    )

if "attach_regen_recommendation_explanation_engine=attach_regen_recommendation_explanation_engine" not in text:
    text = text.replace(
        "attach_regen_candidate_acceptance_completion_gate=attach_regen_candidate_acceptance_completion_gate,\n",
        "attach_regen_candidate_acceptance_completion_gate=attach_regen_candidate_acceptance_completion_gate,\n\n"
        "            attach_regen_recommendation_explanation_engine=attach_regen_recommendation_explanation_engine,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_recommendation_explanation_engine=None" not in text:
    text = text.replace(
        "attach_regen_candidate_acceptance_completion_gate=None,\n",
        "attach_regen_candidate_acceptance_completion_gate=None,\n\n"
        "        attach_regen_recommendation_explanation_engine=None,\n",
    )

if '"regen_recommendation_explanation_engine"' not in text:
    text = text.replace(
        '(\n            "regen_candidate_acceptance_completion_gate",\n            attach_regen_candidate_acceptance_completion_gate,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_candidate_acceptance_completion_gate",\n            attach_regen_candidate_acceptance_completion_gate,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_recommendation_explanation_engine",\n            attach_regen_recommendation_explanation_engine,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16J5_RECOMMENDATION_EXPLANATION_ENGINE_INTEGRATED")
