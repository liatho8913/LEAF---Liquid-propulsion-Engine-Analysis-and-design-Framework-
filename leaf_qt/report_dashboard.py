def _value(results, key, default="UNKNOWN"):
    value = results.get(key)

    if value in (None, "", "N/A", "None"):
        return default

    return value


def build_report_dashboard(results):
    results = results if isinstance(results, dict) else {}

    dashboard = {
        "Overall Regen Status": _value(
            results,
            "best_full_engine_regen_status",
            _value(results, "full_engine_regen_geometry_status"),
        ),
        "Proof Status": _value(results, "regen_optimisation_proof_status"),
        "Failure Type": _value(results, "regen_optimisation_proof_failure_type"),
        "Root Cause Status": _value(results, "failure_root_cause_status"),
        "Root Cause Count": _value(results, "failure_root_cause_count", 0),
        "Recommendation Count": _value(
            results,
            "recommendation_owner_count",
            _value(results, "recommendation_explanation_count", 0),
        ),
        "Recommendation Evidence Status": _value(
            results,
            "recommendation_owner_evidence_status",
            "N/A",
        ),
        "Rejected Recommendation Count": _value(
            results,
            "recommendation_owner_rejected_count",
            0,
        ),
        "Recommendation Ownership Audit": _value(
            results,
            "recommendation_ownership_final_audit_status",
            "N/A",
        ),
        "Stage T Complete": _value(
            results,
            "stage_t_recommendation_ownership_complete",
            False,
        ),
        "Regen Source Validation": _value(
            results,
            "regen_source_validation_gate_status",
            "N/A",
        ),
        "Regen PASS Allowed": _value(
            results,
            "regen_source_validation_pass_allowed",
            False,
        ),
        "Conservative Regen Gate": _value(
            results,
            "regen_conservative_validation_gate_status",
            "N/A",
        ),
        "Regen Provenance": _value(
            results,
            "regen_provenance_report_status",
            "N/A",
        ),
        "Material Source Mode": _value(
            results,
            "regen_provenance_material_mode",
            "UNKNOWN",
        ),
        "Coating Source Mode": _value(
            results,
            "regen_provenance_coating_mode",
            "NONE",
        ),
        "Regen Property Tables": _value(
            results,
            "regen_property_table_owner_status",
            "N/A",
        ),
        "Property Table PASS Allowed": _value(
            results,
            "regen_property_table_owner_pass_allowed",
            False,
        ),
        "Regen Master Gate": _value(
            results,
            "regen_validation_master_gate_status",
            "N/A",
        ),
        "Final Regen PASS Allowed": _value(
            results,
            "regen_validation_master_gate_pass_allowed",
            False,
        ),
        "Stage U Regen Complete": _value(
            results,
            "stage_u_regen_validation_complete",
            False,
        ),
        "Regen Completion Audit": _value(
            results,
            "regen_completion_audit_status",
            "N/A",
        ),
        "Benchmark Status": _value(results, "benchmark_status"),
        "Benchmark Major Deviations": _value(results, "benchmark_major_failed_count", 0),
        "Benchmark Minor Deviations": _value(results, "benchmark_minor_failed_count", 0),
        "Engine Reproduction Status": _value(results, "engine_reproduction_status"),
        "Engine Reproduction Confidence": _value(results, "engine_reproduction_confidence"),
        "Engine Reproduction Score": _value(results, "engine_reproduction_score"),
        "Before / After Status": _value(results, "before_after_comparison_status"),
        "Design Attempts": _value(results, "design_iteration_attempt_count", 0),
        "Next Step": _value(results, "regen_optimisation_proof_next_step"),
    }

    return dashboard


def build_report_dashboard_text(results):
    dashboard = build_report_dashboard(results)

    lines = []
    lines.append("LEAF REPORT DASHBOARD")
    lines.append("====================")
    lines.append("")

    for key, value in dashboard.items():
        lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("Interpretation:")
    lines.append("- Use this dashboard as the first-pass report summary.")
    lines.append("- Use the detailed reports below it for evidence and reasoning.")
    lines.append("- A best-available status is not a validated pass unless the proof status confirms it.")

    return "\n".join(lines)


def attach_report_dashboard(results):
    if results is None:
        return results

    results["report_dashboard_status"] = "RECORDED"
    results["report_dashboard_text"] = build_report_dashboard_text(results)
    results["report_dashboard_items"] = build_report_dashboard(results)

    return results