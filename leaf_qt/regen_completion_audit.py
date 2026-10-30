REQUIRED_STAGE_U_KEYS = (
    "regen_source_validation_gate_status",
    "regen_source_validation_pass_allowed",
    "regen_provenance_report_status",
    "regen_property_table_owner_status",
    "regen_property_table_owner_pass_allowed",
    "regen_validation_master_gate_status",
    "regen_validation_master_gate_pass_allowed",
)


def attach_regen_completion_audit(results):
    if not isinstance(results, dict):
        return results

    audit = audit_regen_completion(results)
    results.update(audit)
    return results


def audit_regen_completion(results):
    missing = []
    failures = []
    warnings = []

    for key in REQUIRED_STAGE_U_KEYS:
        if key not in results:
            missing.append(key)

    source_status = str(results.get("regen_source_validation_gate_status", "")).upper()
    property_status = str(results.get("regen_property_table_owner_status", "")).upper()
    master_status = str(results.get("regen_validation_master_gate_status", "")).upper()

    if missing:
        failures.append("Missing required Stage U keys: " + ", ".join(missing))

    if "PLACEHOLDER" in source_status and results.get("regen_source_validation_pass_allowed"):
        failures.append("Placeholder source data is allowing PASS, which is forbidden.")

    if "PARTIAL" in source_status and results.get("regen_source_validation_pass_allowed"):
        failures.append("Partial source data is allowing final PASS, which is forbidden.")

    if not results.get("regen_property_table_owner_pass_allowed"):
        warnings.append("Property table owner does not currently allow PASS.")

    if not results.get("regen_validation_master_gate_pass_allowed"):
        warnings.append("Regen validation master gate does not currently allow final PASS.")

    if _bad_status(source_status):
        failures.append(f"Source validation gate is failing: {source_status}")

    if _bad_status(property_status):
        failures.append(f"Property table owner is failing: {property_status}")

    if _bad_status(master_status):
        failures.append(f"Master regen gate is failing: {master_status}")

    if failures:
        status = "FAIL_STAGE_U_INCOMPLETE"
        complete = False
    elif warnings:
        status = "WARN_STAGE_U_REVIEW_REQUIRED"
        complete = False
    else:
        status = "PASS_STAGE_U_COMPLETE"
        complete = True

    text = build_regen_completion_audit_report(
        status=status,
        complete=complete,
        missing=missing,
        failures=failures,
        warnings=warnings,
        results=results,
    )

    return {
        "regen_completion_audit_status": status,
        "regen_completion_audit_complete": complete,
        "regen_completion_audit_missing_keys": missing,
        "regen_completion_audit_failures": failures,
        "regen_completion_audit_warnings": warnings,
        "regen_completion_audit_text": text,
        "stage_u_regen_validation_complete": complete,
    }


def _bad_status(status):
    return (
        "FAIL" in status
        or "BLOCKED" in status
        or "INVALID" in status
        or "ERROR" in status
    )


def build_regen_completion_audit_report(status, complete, missing, failures, warnings, results):
    lines = [
        "LEAF STAGE U REGEN COMPLETION AUDIT",
        "===================================",
        "",
        f"Status: {status}",
        f"Stage U complete: {complete}",
        "",
        "Required Systems:",
        f"- Source validation gate: {results.get('regen_source_validation_gate_status', 'MISSING')}",
        f"- Provenance report: {results.get('regen_provenance_report_status', 'MISSING')}",
        f"- Property table owner: {results.get('regen_property_table_owner_status', 'MISSING')}",
        f"- Master validation gate: {results.get('regen_validation_master_gate_status', 'MISSING')}",
        "",
        "Missing Keys:",
    ]

    lines.extend([f"- {item}" for item in missing] or ["- None."])

    lines.append("")
    lines.append("Failures:")
    lines.extend([f"- {item}" for item in failures] or ["- None."])

    lines.append("")
    lines.append("Warnings:")
    lines.extend([f"- {item}" for item in warnings] or ["- None."])

    lines.append("")
    lines.append("Completion Rule:")
    lines.append("- Stage U is complete only when source validation, provenance, property tables, and master gate all support final regen validation.")
    lines.append("- Placeholder data can never pass.")
    lines.append("- Partial source data can never produce final PASS.")

    return "\n".join(lines)