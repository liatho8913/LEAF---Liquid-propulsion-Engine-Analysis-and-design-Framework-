from leaf_qt.status_presentation import status_severity

try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:


    class LegacyCompatibilityProducer:
        """
        Phase 16U shared presentation compatibility fallback.

        This local fallback is only used when leaf_qt.status_presentation
        cannot be imported. Normal production execution should use the shared
        status_presentation implementation.
        """

        @staticmethod
        def marker_from_bool(value, pass_marker="PASS", fail_marker="FAIL"):
            return pass_marker if bool(value) else fail_marker

        @staticmethod
        def marker_from_status(value):
            severity = status_severity(value)
            if severity == "FAIL":
                return "FAIL"
            if severity == "WARN":
                return "WARN"
            if severity == "PASS":
                return "PASS"
            return "UNKNOWN"

        @staticmethod
        def status_severity(value):
            return status_severity(value)

def _leaf_16u71_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u71_is_fail_like(text) or _leaf_16u71_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u71_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u71_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u71_is_fail_like(value):
    return _leaf_16u71_status_severity(value) == "FAIL"


def _leaf_16u71_is_warn_like(value):
    return _leaf_16u71_status_severity(value) == "WARN"


def _leaf_16u71_is_pass_like(value):
    return _leaf_16u71_status_severity(value) == "PASS"


OWNER_NAME = "REGEN_SYSTEM_SIGNOFF_VALIDATION_OWNER"
PHASE = "16E"

PASS_STATUS = "PASS_REGEN_SYSTEM_SIGNOFF_VALIDATION_OWNER_PHASE_16E"

# ---------------------------------------------------------------------------
# PHASE 16T.3W.3 — REGEN SYSTEM SIGNOFF VALIDATION OWNER STATUS ADAPTER
# ---------------------------------------------------------------------------
# Additive reporting wrapper only.
# Does not alter Phase 16E signoff checks or legacy PASS/FAIL outputs.

def _leaf_16t3w3_make_finding(message, category, owner, evidence=None):
    return {
        "message": message,
        "category": category,
        "owner": owner,
        "evidence": evidence or {},
    }


def _leaf_16t3w3_classify(findings):
    categories = {
        str(finding.get("category", "")).upper()
        for finding in findings
        if isinstance(finding, dict)
    }

    if "VALIDATION_FAILURE" in categories:
        status = "FAIL"
    elif _leaf_16u71_is_fail_like(categories):
        status = "BLOCKED"
    elif "MANUAL_REVIEW_REQUIRED" in categories:
        status = "REVIEW_REQUIRED"
    else:
        status = "PASS"

    return {
        "status": status,
        "finding_count": len(findings),
        "findings": findings,
        "production_gate": True,
    }


def _leaf_16t3w3_build_findings(results):
    owner = "Regen System Signoff Validation Owner"
    legacy_status = results.get("regen_system_signoff_validation_owner_status")
    passed = bool(results.get("regen_system_signoff_validation_passed"))
    blockers = results.get("regen_system_signoff_validation_blockers", [])

    if legacy_status == PASS_STATUS and passed:
        return [
            _leaf_16t3w3_make_finding(
                message="Regen system signoff validation owner passed with legacy status preserved.",
                category="COMPLETE",
                owner=owner,
                evidence={
                    "legacy_status": legacy_status,
                    "passed": passed,
                    "blocker_count": len(blockers),
                },
            )
        ]

    return [
        _leaf_16t3w3_make_finding(
            message="Regen system signoff validation owner is blocked or failed.",
            category="VALIDATION_FAILURE",
            owner=owner,
            evidence={
                "legacy_status": legacy_status,
                "passed": passed,
                "blockers": blockers,
            },
        )
    ]


def _leaf_16t3w3_build_adapter_report(findings, payload, legacy_status):
    lines = [
        "LEAF PHASE 16T.3W.3",
        "REGEN SYSTEM SIGNOFF VALIDATION OWNER STATUS ADAPTER",
        "====================================================",
        "",
        f"Legacy Status: {legacy_status}",
        f"Canonical Global Status: {payload.get('status')}",
        f"Structured Findings: {len(findings)}",
        "",
        "Adapter Scope:",
        "- Preserve Phase 16E signoff checks.",
        "- Preserve legacy PASS/FAIL status strings.",
        "- Add structured findings.",
        "- Add canonical global status payload.",
        "",
        "Findings:",
    ]

    for finding in findings:
        lines.append(f"- [{finding.get('category')}] {finding.get('message')}")

    return "\n".join(lines)


def _leaf_16t3w3_apply_status_adapter(results):
    if not isinstance(results, dict):
        return results

    legacy_status = results.get("regen_system_signoff_validation_owner_status")
    findings = _leaf_16t3w3_build_findings(results)
    payload = _leaf_16t3w3_classify(findings)
    report = _leaf_16t3w3_build_adapter_report(findings, payload, legacy_status)

    results.update({
        "phase_16t3w3_status_adapter_complete": True,
        "phase_16t3w3_regen_system_signoff_validation_owner_status_adapter_complete": True,
        "regen_system_signoff_validation_owner_status_adapter_complete": True,
        "regen_system_signoff_validation_owner_structured_findings": findings,
        "regen_system_signoff_validation_owner_global_status": payload.get("status"),
        "regen_system_signoff_validation_owner_global_status_payload": payload,
        "regen_system_signoff_validation_owner_adapter_report": report,
        "regen_system_signoff_validation_owner_legacy_status": legacy_status,
        "structured_findings": findings,
        "global_status": payload.get("status"),
        "global_status_payload": payload,
        "adapter_report": report,
    })

    return results


FAIL_STATUS = "FAIL_REGEN_SYSTEM_SIGNOFF_VALIDATION_OWNER_PHASE_16E"


def attach_regen_system_signoff_validation_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_system_signoff_registry_ready") is not True:
        blockers.append("Regen system signoff registry is not ready.")

    required_phase_statuses = {
        "phase_13k_status": "PASS_REGEN_OPTIMISATION_SELECTION_FRAMEWORK_PHASE_13K",
        "phase_13l_status": "PASS_REGEN_OPTIMISATION_FOUNDATION_PHASE_13L",
        "phase_14a_status": "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_PHASE_14A",
        "phase_14b_status": "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_PHASE_14B",
        "phase_14c_status": "PASS_REGEN_RUNTIME_SELECTION_PHASE_14C",
        "phase_14d_status": "PASS_REGEN_RUNTIME_EVOLUTION_PHASE_14D",
        "phase_14e_status": "PASS_REGEN_RUNTIME_CONVERGENCE_PHASE_14E",
        "phase_14f_status": "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_PHASE_14F",
        "phase_15a_status": "PASS_REGEN_OPTIMISATION_VIEWER_BACKEND_PHASE_15A",
        "phase_15b_status": "PASS_REGEN_CANDIDATE_COMPARISON_VIEWER_BACKEND_PHASE_15B",
        "phase_15c_status": "PASS_REGEN_EVOLUTION_TREE_BACKEND_PHASE_15C",
        "phase_15d_status": "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_PHASE_15D",
        "phase_16a_status": "PASS_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A",
        "phase_16b_status": "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_PHASE_16B",
        "phase_16c_status": "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_PHASE_16C",
        "phase_16d_status": "PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_PHASE_16D",
    }

    checks = []

    for key, expected in required_phase_statuses.items():
        actual = results.get(key)
        passed = actual == expected
        checks.append({
            "check_id": f"SIGNOFF_PHASE_STATUS_{key.upper()}",
            "key": key,
            "expected": expected,
            "actual": actual,
            "passed": passed,
        })
        if not passed:
            blockers.append(f"{key} did not pass expected status.")

    required_boolean_checks = {
        "phase_14_runtime_backend_complete": "Runtime optimisation backend is not complete.",
        "regen_runtime_optimisation_backend_complete": "Runtime optimisation backend flag missing.",
        "phase_15a_complete": "Optimisation viewer backend is not complete.",
        "phase_15b_complete": "Candidate comparison backend is not complete.",
        "phase_15c_complete": "Evolution tree backend is not complete.",
        "phase_15d_complete": "Optimisation report backend is not complete.",
        "phase_16a_complete": "Unified ecosystem registry is not complete.",
        "phase_16b_complete": "Unified viewer integration is not complete.",
        "phase_16c_complete": "Unified report integration is not complete.",
        "phase_16d_complete": "Unified validation integration is not complete.",
        "unified_regen_ecosystem_integrated": "Unified regen ecosystem is not integrated.",
        "unified_regen_viewer_integration_ready": "Unified viewer integration is not ready.",
        "unified_regen_report_integration_ready": "Unified report integration is not ready.",
        "unified_regen_validation_integration_ready": "Unified validation integration is not ready.",
    }

    for key, message in required_boolean_checks.items():
        passed = results.get(key) is True
        checks.append({
            "check_id": f"SIGNOFF_BOOLEAN_{key.upper()}",
            "key": key,
            "expected": True,
            "actual": results.get(key),
            "passed": passed,
        })
        if not passed:
            blockers.append(message)

    forbidden = {
        "regen_runtime_final_live_geometry_committed": "Live geometry was committed before signoff.",
        "optimisation_viewer_qt_window_created": "Optimisation viewer Qt window was created before final UI phase.",
        "candidate_comparison_qt_window_created": "Candidate comparison Qt window was created before final UI phase.",
        "evolution_tree_qt_viewer_created": "Evolution tree Qt viewer was created before final UI phase.",
        "optimisation_report_qt_window_created": "Optimisation report Qt window was created before final UI phase.",
        "unified_regen_qt_windows_created": "Unified regen Qt windows were created before signoff.",
        "unified_regen_viewer_qt_window_created": "Unified viewer Qt window was created before signoff.",
        "unified_regen_report_window_created": "Unified report window was created before signoff.",
        "unified_regen_validation_view_created": "Unified validation view was created before signoff.",
    }

    for key, message in forbidden.items():
        if results.get(key) not in (False, None):
            blockers.append(message)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_system_signoff_validation_owner_complete": True,
        "phase_16e_regen_system_signoff_validation_owner_complete": True,
        "regen_system_signoff_validation_owner_ready": ready,
        "regen_system_signoff_validation_owner_status": status,
        "regen_system_signoff_validation_owner_blockers": blockers,

        "regen_system_signoff_validation_checks": checks,
        "regen_system_signoff_validation_check_count": len(checks),
        "regen_system_signoff_validation_passed": ready,
    })

    return _leaf_16t3w3_apply_status_adapter(results)
