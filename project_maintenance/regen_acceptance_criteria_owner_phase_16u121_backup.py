"""
PHASE 16L.1 — Regen Acceptance Criteria Owner

Purpose:
- Define and evaluate regen acceptance criteria.
- Start the Regen Acceptance Framework.
- Does not alter geometry.
- Does not rerun solver.
"""

try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    def status_severity(value):
        text = str(value or "").upper()
        if "FAIL" in text or "BLOCKED" in text or "ERROR" in text:
            return "FAIL"
        if "WARN" in text or "PARTIAL" in text or "DEGRADED" in text:
            return "WARN"
        if "PASS" in text or "OK" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"

    class LegacyCompatibilityProducer:
        @staticmethod
        def marker_from_bool(value, pass_marker="PASS", fail_marker="FAIL"):
            return pass_marker if bool(value) else fail_marker

        @staticmethod
        def marker_from_status(value):
            severity = status_severity(value)
            if severity in {"PASS", "WARN", "FAIL"}:
                return severity
            return "UNKNOWN"

        @staticmethod
        def status_severity(value):
            return status_severity(value)

PASS_STATUS = "PASS_REGEN_ACCEPTANCE_CRITERIA_OWNER_PHASE_16L1"
FAIL_STATUS = "FAIL_REGEN_ACCEPTANCE_CRITERIA_OWNER_PHASE_16L1"


def attach_regen_acceptance_criteria_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16k7_complete") is not True:
        blockers.append("Phase 16K.7 viewer completion gate has not passed.")

    criteria = _build_criteria(results)
    evaluations = [_evaluate_criterion(c, results) for c in criteria]

    failed = [e for e in evaluations if e.get("passed") is not True]

    status = PASS_STATUS if not blockers and not failed else FAIL_STATUS

    if failed:
        for item in failed:
            blockers.append(f"Acceptance criterion failed: {item.get('name')}")

    payload = {
        "status": status,
        "source_phase": "16L.1",
        "visibility": "REPORT_ONLY",
        "criteria_count": len(criteria),
        "passed_count": sum(1 for e in evaluations if e.get("passed") is True),
        "failed_count": len(failed),
        "criteria": criteria,
        "evaluations": evaluations,
    }

    report = _build_report(status, blockers, payload)

    results["regen_acceptance_criteria_owner_complete"] = True
    results["phase_16l1_complete"] = status == PASS_STATUS
    results["regen_acceptance_criteria_owner_status"] = status
    results["phase_16l1_status"] = status
    results["regen_acceptance_criteria_owner_blockers"] = blockers
    results["regen_acceptance_criteria_payload"] = payload
    results["regen_acceptance_criteria_report"] = report

    results["phase_16l2_engineering_acceptance_report_allowed"] = status == PASS_STATUS

    return results


def _build_criteria(results):
    return [
        {
            "name": "viewer_system_complete",
            "description": "The regen viewer system must be complete.",
            "required_key": "regen_viewer_system_complete",
            "required_value": True,
            "severity": "HIGH",
        },
        {
            "name": "optimisation_pipeline_complete",
            "description": "The optimisation pipeline must be complete.",
            "required_key": "regen_optimisation_pipeline_complete",
            "required_value": True,
            "severity": "HIGH",
        },
        {
            "name": "candidate_acceptance_pipeline_complete",
            "description": "The candidate acceptance pipeline must be complete.",
            "required_key": "regen_candidate_acceptance_pipeline_complete",
            "required_value": True,
            "severity": "HIGH",
        },
        {
            "name": "solver_regenerated_after_commit",
            "description": "The solver must have regenerated after committed geometry.",
            "required_key": "regen_solver_regenerated_after_commit",
            "required_value": True,
            "severity": "HIGH",
        },
        {
            "name": "viewer_payload_exists",
            "description": "The unified regen viewer payload must exist.",
            "required_key": "regen_viewer_payload",
            "required_type": "dict",
            "severity": "MEDIUM",
        },
        {
            "name": "station_viewer_payload_exists",
            "description": "The station viewer payload must exist.",
            "required_key": "regen_station_viewer_payload",
            "required_type": "dict",
            "severity": "MEDIUM",
        },
        {
            "name": "cross_section_viewer_payload_exists",
            "description": "The cross-section viewer payload must exist.",
            "required_key": "regen_cross_section_viewer_payload",
            "required_type": "dict",
            "severity": "MEDIUM",
        },
    ]


def _evaluate_criterion(criterion, results):
    key = criterion.get("required_key")
    value = results.get(key)

    passed = False

    if "required_value" in criterion:
        passed = value == criterion.get("required_value")
    elif criterion.get("required_type") == "dict":
        passed = isinstance(value, dict) and bool(value)
    elif criterion.get("required_type") == "list":
        passed = isinstance(value, list) and bool(value)

    return {
        "name": criterion.get("name"),
        "key": key,
        "passed": passed,
        "severity": criterion.get("severity"),
        "observed_type": type(value).__name__ if value is not None else None,
        "observed_value": value if isinstance(value, (str, int, float, bool)) else None,
    }


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16L.1 REGEN ACCEPTANCE CRITERIA OWNER",
        "==================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Defines regen acceptance criteria.",
        "- Evaluates current regen system against those criteria.",
        "- Produces acceptance criteria payload.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for b in blockers:
            lines.append(f"- {b}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Criteria Summary:",
        f"- Criteria count: {payload.get('criteria_count')}",
        f"- Passed: {payload.get('passed_count')}",
        f"- Failed: {payload.get('failed_count')}",
        "",
        "Evaluations:",
    ])

    for item in payload.get("evaluations", []):
        lines.append(
            f"- {item.get('name')}: {LegacyCompatibilityProducer.marker_from_bool(item.get('passed'))}"
        )

    lines.extend([
        "",
        "Next Required Phase:",
        "- 16L.2 Engineering Acceptance Report.",
    ])

    return "\n".join(lines)
