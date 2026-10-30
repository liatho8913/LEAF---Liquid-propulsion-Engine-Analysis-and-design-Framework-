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


OWNER_NAME = "REGEN_COMPLETION_GATE_VALIDATION_OWNER"
PHASE = "16F"

PASS_STATUS = "PASS_REGEN_COMPLETION_GATE_VALIDATION_OWNER_PHASE_16F"

# ---------------------------------------------------------------------------
# PHASE 16T.3W.4 — REGEN COMPLETION GATE VALIDATION OWNER STATUS ADAPTER
# ---------------------------------------------------------------------------
# Additive reporting wrapper only.
# Does not alter Phase 16F completion gate checks or legacy PASS/FAIL outputs.

def _leaf_16t3w4_make_finding(message, category, owner, evidence=None):
    return {
        "message": message,
        "category": category,
        "owner": owner,
        "evidence": evidence or {},
    }


def _leaf_16t3w4_classify(findings):
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


def _leaf_16t3w4_build_findings(results):
    owner = "Regen Completion Gate Validation Owner"
    legacy_status = results.get("regen_completion_gate_validation_owner_status")
    passed = bool(results.get("regen_completion_gate_validation_passed"))
    blockers = results.get("regen_completion_gate_validation_blockers", [])

    if legacy_status == PASS_STATUS and passed:
        return [
            _leaf_16t3w4_make_finding(
                message="Regen completion gate validation owner passed with legacy status preserved.",
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
        _leaf_16t3w4_make_finding(
            message="Regen completion gate validation owner is blocked or failed.",
            category="VALIDATION_FAILURE",
            owner=owner,
            evidence={
                "legacy_status": legacy_status,
                "passed": passed,
                "blockers": blockers,
            },
        )
    ]


def _leaf_16t3w4_build_adapter_report(findings, payload, legacy_status):
    lines = [
        "LEAF PHASE 16T.3W.4",
        "REGEN COMPLETION GATE VALIDATION OWNER STATUS ADAPTER",
        "=====================================================",
        "",
        f"Legacy Status: {legacy_status}",
        f"Canonical Global Status: {payload.get('status')}",
        f"Structured Findings: {len(findings)}",
        "",
        "Adapter Scope:",
        "- Preserve Phase 16F completion gate checks.",
        "- Preserve legacy PASS/FAIL status strings.",
        "- Add structured findings.",
        "- Add canonical global status payload.",
        "",
        "Findings:",
    ]

    for finding in findings:
        lines.append(f"- [{finding.get('category')}] {finding.get('message')}")

    return "\n".join(lines)


def _leaf_16t3w4_apply_status_adapter(results):
    if not isinstance(results, dict):
        return results

    legacy_status = results.get("regen_completion_gate_validation_owner_status")
    findings = _leaf_16t3w4_build_findings(results)
    payload = _leaf_16t3w4_classify(findings)
    report = _leaf_16t3w4_build_adapter_report(findings, payload, legacy_status)

    results.update({
        "phase_16t3w4_status_adapter_complete": True,
        "phase_16t3w4_regen_completion_gate_validation_owner_status_adapter_complete": True,
        "regen_completion_gate_validation_owner_status_adapter_complete": True,
        "regen_completion_gate_validation_owner_structured_findings": findings,
        "regen_completion_gate_validation_owner_global_status": payload.get("status"),
        "regen_completion_gate_validation_owner_global_status_payload": payload,
        "regen_completion_gate_validation_owner_adapter_report": report,
        "regen_completion_gate_validation_owner_legacy_status": legacy_status,
        "structured_findings": findings,
        "global_status": payload.get("status"),
        "global_status_payload": payload,
        "adapter_report": report,
    })

    return results


FAIL_STATUS = "FAIL_REGEN_COMPLETION_GATE_VALIDATION_OWNER_PHASE_16F"


def attach_regen_completion_gate_validation_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_completion_gate_registry_ready") is not True:
        blockers.append("Regen completion gate registry is not ready.")

    required_statuses = {
        "phase_16e_status": "PASS_REGEN_SYSTEM_SIGNOFF_AUDIT_PHASE_16E",
        "regen_system_signoff_master_gate_status": "PASS_REGEN_SYSTEM_SIGNOFF_MASTER_GATE_PHASE_16E",
        "regen_system_signoff_completion_audit_status": "PASS_REGEN_SYSTEM_SIGNOFF_AUDIT_PHASE_16E",
        "regen_unified_validation_integration_master_gate_status": "PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_MASTER_GATE_PHASE_16D",
        "regen_unified_report_integration_master_gate_status": "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_MASTER_GATE_PHASE_16C",
        "regen_unified_viewer_integration_master_gate_status": "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_MASTER_GATE_PHASE_16B",
        "regen_unified_ecosystem_master_gate_status": "PASS_REGEN_UNIFIED_ECOSYSTEM_MASTER_GATE_PHASE_16A",
        "regen_optimisation_report_backend_master_gate_status": "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_MASTER_GATE_PHASE_15D",
        "regen_evolution_tree_master_gate_status": "PASS_REGEN_EVOLUTION_TREE_MASTER_GATE_PHASE_15C",
        "regen_candidate_comparison_master_gate_status": "PASS_REGEN_CANDIDATE_COMPARISON_MASTER_GATE_PHASE_15B",
        "regen_optimisation_viewer_master_gate_status": "PASS_REGEN_OPTIMISATION_VIEWER_MASTER_GATE_PHASE_15A",
        "regen_runtime_optimisation_completion_master_gate_status": "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_MASTER_GATE_PHASE_14F",
    }

    checks = []

    for key, expected in required_statuses.items():
        actual = results.get(key)
        passed = actual == expected
        checks.append({
            "check_id": f"REGEN_COMPLETION_STATUS_{key.upper()}",
            "key": key,
            "expected": expected,
            "actual": actual,
            "passed": passed,
        })
        if not passed:
            blockers.append(f"{key} is not at expected PASS status.")

    required_true = {
        "phase_13k_complete": "Phase 13K is not complete.",
        "phase_13l_complete": "Phase 13L is not complete.",
        "phase_14a_complete": "Phase 14A is not complete.",
        "phase_14b_complete": "Phase 14B is not complete.",
        "phase_14c_complete": "Phase 14C is not complete.",
        "phase_14d_complete": "Phase 14D is not complete.",
        "phase_14e_complete": "Phase 14E is not complete.",
        "phase_14f_complete": "Phase 14F is not complete.",
        "phase_15a_complete": "Phase 15A is not complete.",
        "phase_15b_complete": "Phase 15B is not complete.",
        "phase_15c_complete": "Phase 15C is not complete.",
        "phase_15d_complete": "Phase 15D is not complete.",
        "phase_16a_complete": "Phase 16A is not complete.",
        "phase_16b_complete": "Phase 16B is not complete.",
        "phase_16c_complete": "Phase 16C is not complete.",
        "phase_16d_complete": "Phase 16D is not complete.",
        "phase_16e_complete": "Phase 16E is not complete.",
        "regen_system_signoff_validation_passed": "Regen system signoff validation did not pass.",
        "unified_regen_ecosystem_integrated": "Unified regen ecosystem is not integrated.",
        "unified_regen_viewer_integration_ready": "Unified viewer integration is not ready.",
        "unified_regen_report_integration_ready": "Unified report integration is not ready.",
        "unified_regen_validation_integration_ready": "Unified validation integration is not ready.",
    }

    for key, message in required_true.items():
        passed = results.get(key) is True
        checks.append({
            "check_id": f"REGEN_COMPLETION_TRUE_{key.upper()}",
            "key": key,
            "expected": True,
            "actual": results.get(key),
            "passed": passed,
        })
        if not passed:
            blockers.append(message)

    forbidden_true = {
        "regen_runtime_final_live_geometry_committed": "Live geometry was committed before final completion.",
        "unified_regen_qt_windows_created": "Unified Qt windows were created before final completion.",
        "unified_regen_rendering_performed": "Unified rendering was performed before final completion.",
        "unified_regen_report_export_performed": "Unified report export was performed before final completion.",
        "unified_regen_validation_view_created": "Unified validation view was created before final completion.",
    }

    for key, message in forbidden_true.items():
        if results.get(key) not in (False, None):
            blockers.append(message)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_completion_gate_validation_owner_complete": True,
        "phase_16f_regen_completion_gate_validation_owner_complete": True,
        "regen_completion_gate_validation_owner_ready": ready,
        "regen_completion_gate_validation_owner_status": status,
        "regen_completion_gate_validation_owner_blockers": blockers,

        "regen_completion_gate_validation_checks": checks,
        "regen_completion_gate_validation_check_count": len(checks),
        "regen_completion_gate_validation_passed": ready,
    })

    return _leaf_16t3w4_apply_status_adapter(results)
