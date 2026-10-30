from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_failure_root_cause_system.py").write_text(r'''"""
PHASE 16J.6 — Failure Root Cause System

Purpose:
- Collect blockers, regressions, risks, and failed phase statuses.
- Classify likely root causes.
- Produce actionable repair guidance.
- Does not modify geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_FAILURE_ROOT_CAUSE_SYSTEM_PHASE_16J6"
FAIL_STATUS = "FAIL_REGEN_FAILURE_ROOT_CAUSE_SYSTEM_PHASE_16J6"


def attach_regen_failure_root_cause_system(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16j5_complete") is not True:
        blockers.append("Phase 16J.5 recommendation explanation engine has not passed.")

    raw_items = []
    raw_items.extend(_collect_blockers(results))
    raw_items.extend(_collect_regressions(results))
    raw_items.extend(_collect_risks(results))
    raw_items.extend(_collect_failed_phase_statuses(results))

    root_causes = [_classify_item(item) for item in raw_items]
    summary = _summarise(root_causes)

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "visibility": "REPORT_ONLY",
            "source_phase": "16J.6",
            "root_cause_count": len(root_causes),
            "summary": summary,
            "root_causes": root_causes,
            "next_actions": _next_actions(root_causes),
        }

    report = _build_report(status, blockers, payload)

    results["regen_failure_root_cause_system_complete"] = True
    results["phase_16j6_complete"] = status == PASS_STATUS
    results["regen_failure_root_cause_system_status"] = status
    results["phase_16j6_status"] = status
    results["regen_failure_root_cause_system_blockers"] = blockers
    results["regen_failure_root_cause_payload"] = payload
    results["regen_failure_root_cause_report"] = report
    results["regen_failure_root_cause_visibility"] = "REPORT_ONLY"

    results["phase_16j7_optimisation_proof_system_allowed"] = status == PASS_STATUS

    return results


def _collect_blockers(results):
    items = []
    for key, value in results.items():
        if key.endswith("_blockers") and isinstance(value, list):
            for blocker in value:
                if blocker:
                    items.append({
                        "source": key,
                        "type": "BLOCKER",
                        "message": str(blocker),
                    })
    return items


def _collect_regressions(results):
    items = []
    changes = results.get("regen_before_after_solver_comparison_classified_changes")
    if isinstance(changes, list):
        for change in changes:
            if isinstance(change, dict) and change.get("classification") == "REGRESSED":
                items.append({
                    "source": "regen_before_after_solver_comparison_classified_changes",
                    "type": "REGRESSION",
                    "message": f"{change.get('key')} regressed from {change.get('before')} to {change.get('after')}",
                    "key": change.get("key"),
                    "before": change.get("before"),
                    "after": change.get("after"),
                })
    return items


def _collect_risks(results):
    items = []
    explanation = results.get("regen_recommendation_explanation_payload")
    if isinstance(explanation, dict):
        for risk in explanation.get("remaining_risks", []) or []:
            items.append({
                "source": "regen_recommendation_explanation_payload.remaining_risks",
                "type": "RISK",
                "message": str(risk),
            })
    return items


def _collect_failed_phase_statuses(results):
    items = []
    for key, value in results.items():
        if key.endswith("_status") and isinstance(value, str) and value.startswith("FAIL_"):
            items.append({
                "source": key,
                "type": "FAILED_STATUS",
                "message": value,
            })
    return items


def _classify_item(item):
    message = item.get("message", "")
    lower = message.lower()

    category = "GENERAL"
    severity = "LOW"
    action = "Review the source report and add a more specific diagnostic rule if this repeats."

    if "missing" in lower or "not available" in lower:
        category = "MISSING_DATA"
        severity = "HIGH"
        action = "Trace the upstream owner that should publish this payload/key."

    elif "regressed" in lower:
        category = "PERFORMANCE_REGRESSION"
        severity = "HIGH"
        action = "Compare the accepted geometry change against the regressed solver output and add optimisation constraints."

    elif "geometry" in lower and ("invalid" in lower or "fit" in lower or "commit" in lower):
        category = "GEOMETRY_PIPELINE"
        severity = "HIGH"
        action = "Inspect geometry validation, commit readiness, and live geometry audit records."

    elif "solver" in lower or "callable" in lower:
        category = "SOLVER_REGENERATION"
        severity = "HIGH"
        action = "Verify a real solver regeneration callable is connected before accepting solver PASS."

    elif "risk" in lower or "review" in lower:
        category = "REVIEW_REQUIRED"
        severity = "MEDIUM"
        action = "Keep the result report-only until the risk has a domain-specific validation rule."

    return {
        "source": item.get("source"),
        "input_type": item.get("type"),
        "message": message,
        "category": category,
        "severity": severity,
        "recommended_action": action,
    }


def _summarise(root_causes):
    return {
        "total": len(root_causes),
        "high": sum(1 for r in root_causes if r.get("severity") == "HIGH"),
        "medium": sum(1 for r in root_causes if r.get("severity") == "MEDIUM"),
        "low": sum(1 for r in root_causes if r.get("severity") == "LOW"),
        "categories": sorted(set(r.get("category") for r in root_causes)),
    }


def _next_actions(root_causes):
    if not root_causes:
        return ["No root-cause items were detected; continue to optimisation proof ownership."]

    actions = []
    seen = set()
    for cause in root_causes:
        action = cause.get("recommended_action")
        if action and action not in seen:
            seen.add(action)
            actions.append(action)
    return actions


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16J.6 FAILURE ROOT CAUSE SYSTEM",
        "===========================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Collects blockers, failed statuses, regressions, and risks.",
        "- Classifies likely root causes.",
        "- Produces actionable repair guidance.",
        "- Does not modify geometry.",
        "- Does not rerun solver.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
        return "\n".join(lines)

    lines.append("- None.")
    lines.append("")

    summary = payload.get("summary", {}) if payload else {}
    lines.extend([
        "Root Cause Summary:",
        f"- Total: {summary.get('total')}",
        f"- High: {summary.get('high')}",
        f"- Medium: {summary.get('medium')}",
        f"- Low: {summary.get('low')}",
        "",
        "Root Causes:",
    ])

    causes = payload.get("root_causes", []) if payload else []
    if causes:
        for cause in causes:
            lines.append(
                f"- [{cause.get('severity')}] {cause.get('category')}: "
                f"{cause.get('message')} | Action: {cause.get('recommended_action')}"
            )
    else:
        lines.append("- None detected.")

    lines.extend([
        "",
        "Next Actions:",
    ])

    for action in payload.get("next_actions", []) if payload else []:
        lines.append(f"- {action}")

    lines.extend([
        "",
        "Visibility:",
        "- REPORT_ONLY",
        "",
        "Next Required Phase:",
        "- 16J.7 Optimisation Proof System.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_failure_root_cause_system_phase_16j6.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
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
from regen_failure_root_cause_system import attach_regen_failure_root_cause_system


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
        attach_regen_failure_root_cause_system,
    ):
        results = fn(results)

    assert results["phase_16j6_complete"] is True
    assert results["phase_16j6_status"] == "PASS_REGEN_FAILURE_ROOT_CAUSE_SYSTEM_PHASE_16J6"

    payload = results["regen_failure_root_cause_payload"]
    assert payload["visibility"] == "REPORT_ONLY"
    assert "summary" in payload
    assert "root_causes" in payload
    assert "next_actions" in payload

    report = results["regen_failure_root_cause_report"]
    assert "FAILURE ROOT CAUSE SYSTEM" in report
    assert "Root Cause Summary" in report

    assert results["phase_16j7_optimisation_proof_system_allowed"] is True

    print("PASS_REGEN_FAILURE_ROOT_CAUSE_SYSTEM_PHASE_16J6")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_failure_root_cause_system import attach_regen_failure_root_cause_system" not in text:
    anchor = (
        "try:\n"
        "    from regen_recommendation_explanation_engine import attach_regen_recommendation_explanation_engine\n"
        "except Exception:\n"
        "    attach_regen_recommendation_explanation_engine = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_failure_root_cause_system import attach_regen_failure_root_cause_system\n"
        "except Exception:\n"
        "    attach_regen_failure_root_cause_system = None\n"
    )

if "attach_regen_failure_root_cause_system=attach_regen_failure_root_cause_system" not in text:
    text = text.replace(
        "attach_regen_recommendation_explanation_engine=attach_regen_recommendation_explanation_engine,\n",
        "attach_regen_recommendation_explanation_engine=attach_regen_recommendation_explanation_engine,\n\n"
        "            attach_regen_failure_root_cause_system=attach_regen_failure_root_cause_system,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_failure_root_cause_system=None" not in text:
    text = text.replace(
        "attach_regen_recommendation_explanation_engine=None,\n",
        "attach_regen_recommendation_explanation_engine=None,\n\n"
        "        attach_regen_failure_root_cause_system=None,\n",
    )

if '"regen_failure_root_cause_system"' not in text:
    text = text.replace(
        '(\n            "regen_recommendation_explanation_engine",\n            attach_regen_recommendation_explanation_engine,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_recommendation_explanation_engine",\n            attach_regen_recommendation_explanation_engine,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_failure_root_cause_system",\n            attach_regen_failure_root_cause_system,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16J6_FAILURE_ROOT_CAUSE_SYSTEM_INTEGRATED")
