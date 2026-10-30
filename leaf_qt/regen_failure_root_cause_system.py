"""
PHASE 16J.6 — Failure Root Cause System

Purpose:
- Collect blockers, regressions, risks, and failed phase statuses.
- Classify likely root causes.
- Produce actionable repair guidance.
- Does not modify geometry.
- Does not rerun solver.
"""
from leaf_qt.status_presentation import status_severity

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
        if key.endswith("_status") and isinstance(value, str) and status_severity(value) == "FAIL":
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
