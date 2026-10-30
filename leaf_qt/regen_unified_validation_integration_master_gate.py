OWNER_NAME = "REGEN_UNIFIED_VALIDATION_INTEGRATION_MASTER_GATE"
PHASE = "16D"

PASS_STATUS = "PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_MASTER_GATE_PHASE_16D"

# ---------------------------------------------------------------------------
# PHASE 16T.3W.7 — REGEN UNIFIED VALIDATION INTEGRATION MASTER GATE ADAPTER
# ---------------------------------------------------------------------------
# Additive reporting wrapper only.
# Does not alter Phase 16D unified validation integration gate logic.

def _leaf_16t3w7_make_finding(message, category, owner, evidence=None):
    return {
        "message": message,
        "category": category,
        "owner": owner,
        "evidence": evidence or {},
    }


def _leaf_16t3w7_classify(findings):
    categories = {
        str(finding.get("category", "")).upper()
        for finding in findings
        if isinstance(finding, dict)
    }

    if "VALIDATION_FAILURE" in categories:
        status = "FAIL"
    elif "BLOCKED" in categories:
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


def _leaf_16t3w7_build_findings(results):
    owner = "Regen Unified Validation Integration Master Gate"
    legacy_status = results.get("regen_unified_validation_integration_master_gate_status")
    passed = bool(results.get("regen_unified_validation_integration_master_gate_passed"))
    blockers = results.get("regen_unified_validation_integration_master_gate_blockers", [])

    if legacy_status == PASS_STATUS and passed:
        return [
            _leaf_16t3w7_make_finding(
                message="Unified validation integration master gate passed with legacy status preserved.",
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
        _leaf_16t3w7_make_finding(
            message="Unified validation integration master gate is blocked or failed.",
            category="VALIDATION_FAILURE",
            owner=owner,
            evidence={
                "legacy_status": legacy_status,
                "passed": passed,
                "blockers": blockers,
            },
        )
    ]


def _leaf_16t3w7_build_adapter_report(findings, payload, legacy_status):
    lines = [
        "LEAF PHASE 16T.3W.7",
        "REGEN UNIFIED VALIDATION INTEGRATION MASTER GATE STATUS ADAPTER",
        "================================================================",
        "",
        f"Legacy Status: {legacy_status}",
        f"Canonical Global Status: {payload.get('status')}",
        f"Structured Findings: {len(findings)}",
        "",
        "Adapter Scope:",
        "- Preserve Phase 16D unified validation integration gate logic.",
        "- Preserve legacy PASS/FAIL status strings.",
        "- Add structured findings.",
        "- Add canonical global status payload.",
        "",
        "Findings:",
    ]

    for finding in findings:
        lines.append(f"- [{finding.get('category')}] {finding.get('message')}")

    return "\n".join(lines)


def _leaf_16t3w7_apply_status_adapter(results):
    if not isinstance(results, dict):
        return results

    legacy_status = results.get("regen_unified_validation_integration_master_gate_status")
    findings = _leaf_16t3w7_build_findings(results)
    payload = _leaf_16t3w7_classify(findings)
    report = _leaf_16t3w7_build_adapter_report(findings, payload, legacy_status)

    results.update({
        "phase_16t3w7_status_adapter_complete": True,
        "phase_16t3w7_regen_unified_validation_integration_master_gate_status_adapter_complete": True,
        "regen_unified_validation_integration_master_gate_status_adapter_complete": True,
        "regen_unified_validation_integration_master_gate_structured_findings": findings,
        "regen_unified_validation_integration_master_gate_global_status": payload.get("status"),
        "regen_unified_validation_integration_master_gate_global_status_payload": payload,
        "regen_unified_validation_integration_master_gate_adapter_report": report,
        "regen_unified_validation_integration_master_gate_legacy_status": legacy_status,
        "structured_findings": findings,
        "global_status": payload.get("status"),
        "global_status_payload": payload,
        "adapter_report": report,
    })

    return results


FAIL_STATUS = "FAIL_REGEN_UNIFIED_VALIDATION_INTEGRATION_MASTER_GATE_PHASE_16D"


def attach_regen_unified_validation_integration_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_validation_integration_completion_audit_ready") is not True:
        blockers.append("16D unified validation integration completion audit is not ready.")

    if results.get("regen_unified_validation_integration_completion_audit_status") != "PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_PHASE_16D":
        blockers.append("16D unified validation integration completion audit has not passed.")

    if results.get("phase_16e_regen_signoff_allowed") is not True:
        blockers.append("Phase 16E regen signoff was not unlocked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_validation_integration_master_gate_complete": True,
        "phase_16d_unified_validation_integration_master_gate_complete": True,
        "regen_unified_validation_integration_master_gate_passed": ready,
        "regen_unified_validation_integration_master_gate_status": status,
        "regen_unified_validation_integration_master_gate_blockers": blockers,

        "phase_16d_complete": ready,
        "phase_16d_status": (
            "PASS_REGEN_UNIFIED_VALIDATION_INTEGRATION_PHASE_16D"
            if ready else
            "FAIL_REGEN_UNIFIED_VALIDATION_INTEGRATION_PHASE_16D"
        ),

        "phase_16e_regen_signoff_allowed": ready,
    })

    return _leaf_16t3w7_apply_status_adapter(results)
