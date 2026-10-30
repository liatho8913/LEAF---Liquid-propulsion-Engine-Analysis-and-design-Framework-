from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_before_after_solver_comparison_report_owner.py").write_text(r'''"""
PHASE 16J.4E — Before/After Solver Comparison Report Ownership

Purpose:
- Own the before/after solver comparison produced by 16J.4D.
- Classify changed solver outputs.
- Produce a report-only payload for UI/report viewers.
- Preserve traceability from candidate acceptance to regeneration.
"""

PASS_STATUS = "PASS_REGEN_BEFORE_AFTER_SOLVER_COMPARISON_REPORT_PHASE_16J4E"
FAIL_STATUS = "FAIL_REGEN_BEFORE_AFTER_SOLVER_COMPARISON_REPORT_PHASE_16J4E"

HIGHER_IS_BETTER = {
    "thrust",
    "corrected_thrust",
    "specific_impulse",
    "isp",
    "isp_vac",
}

LOWER_IS_BETTER = {
    "coolant_pressure_drop",
    "regen_max_hot_wall_temperature",
    "regen_max_coolant_wall_temperature",
}


def attach_regen_before_after_solver_comparison_report_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16j4d_complete") is not True:
        blockers.append("Phase 16J.4D solver regeneration has not passed.")

    comparison = results.get("regen_solver_regeneration_before_after_comparison")
    audit = results.get("regen_solver_regeneration_audit_record")
    payload = results.get("regen_solver_regeneration_result_payload")

    if not isinstance(comparison, dict) or not comparison:
        blockers.append("Solver before/after comparison payload is missing.")

    if not isinstance(audit, dict) or not audit:
        blockers.append("Solver regeneration audit record is missing.")

    if not isinstance(payload, dict) or not payload:
        blockers.append("Post-commit solver result payload is missing.")

    owned_changes = []

    if isinstance(comparison, dict):
        for change in comparison.get("changes", []):
            if isinstance(change, dict):
                owned_changes.append(_classify_change(change))

    summary = _summarise_changes(owned_changes)

    status = PASS_STATUS if not blockers else FAIL_STATUS

    report_payload = None
    if status == PASS_STATUS:
        report_payload = {
            "status": status,
            "candidate_id": audit.get("candidate_id"),
            "source_phase": "16J.4E",
            "upstream_phase": "16J.4D",
            "visibility": "REPORT_ONLY",
            "summary": summary,
            "classified_changes": owned_changes,
            "solver_callback_key": results.get("regen_solver_regeneration_callback_key"),
            "geometry_snapshot": results.get("regen_solver_regeneration_committed_geometry_snapshot"),
            "audit_record": audit,
        }

    report = _build_report(status, blockers, report_payload, owned_changes, summary)

    results["regen_before_after_solver_comparison_report_owner_complete"] = True
    results["phase_16j4e_complete"] = status == PASS_STATUS
    results["regen_before_after_solver_comparison_report_status"] = status
    results["phase_16j4e_status"] = status
    results["regen_before_after_solver_comparison_report_blockers"] = blockers
    results["regen_before_after_solver_comparison_report_payload"] = report_payload
    results["regen_before_after_solver_comparison_classified_changes"] = owned_changes
    results["regen_before_after_solver_comparison_summary"] = summary
    results["regen_before_after_solver_comparison_report"] = report

    results["regen_before_after_solver_comparison_visibility"] = "REPORT_ONLY"
    results["phase_16j4f_design_iteration_history_link_allowed"] = status == PASS_STATUS

    return results


def _classify_change(change):
    key = change.get("key")
    before = change.get("before")
    after = change.get("after")
    changed = bool(change.get("changed"))

    classification = "UNCHANGED"
    delta = None

    if changed:
        try:
            delta = float(after) - float(before)
        except Exception:
            delta = None

        if delta is None:
            classification = "CHANGED_NON_NUMERIC"
        elif key in HIGHER_IS_BETTER:
            classification = "IMPROVED" if delta > 0 else "REGRESSED"
        elif key in LOWER_IS_BETTER:
            classification = "IMPROVED" if delta < 0 else "REGRESSED"
        else:
            classification = "CHANGED_NEUTRAL"

    return {
        "key": key,
        "before": before,
        "after": after,
        "changed": changed,
        "delta": delta,
        "classification": classification,
    }


def _summarise_changes(changes):
    return {
        "total_compared": len(changes),
        "changed": sum(1 for c in changes if c.get("changed")),
        "improved": sum(1 for c in changes if c.get("classification") == "IMPROVED"),
        "regressed": sum(1 for c in changes if c.get("classification") == "REGRESSED"),
        "neutral_changed": sum(1 for c in changes if c.get("classification") in {"CHANGED_NEUTRAL", "CHANGED_NON_NUMERIC"}),
        "unchanged": sum(1 for c in changes if c.get("classification") == "UNCHANGED"),
    }


def _build_report(status, blockers, report_payload, changes, summary):
    lines = [
        "LEAF PHASE 16J.4E BEFORE/AFTER SOLVER COMPARISON REPORT OWNERSHIP",
        "====================================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Owns the before/after solver comparison from Phase 16J.4D.",
        "- Classifies changed outputs as improved, regressed, neutral, or unchanged.",
        "- Publishes report-only payload for viewer/report systems.",
        "- Does not rerun the solver.",
        "- Does not alter committed geometry.",
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
        "Summary:",
        f"- Compared outputs: {summary.get('total_compared')}",
        f"- Changed outputs: {summary.get('changed')}",
        f"- Improved: {summary.get('improved')}",
        f"- Regressed: {summary.get('regressed')}",
        f"- Neutral changed: {summary.get('neutral_changed')}",
        f"- Unchanged: {summary.get('unchanged')}",
        "",
        "Classified Changes:",
    ])

    if changes:
        for change in changes:
            lines.append(
                f"- {change.get('key')}: {change.get('before')} -> {change.get('after')} "
                f"[{change.get('classification')}]"
            )
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Visibility:",
        "- REPORT_ONLY",
        "",
        "Next Required Phase:",
        "- 16J.4F Design Iteration History Link.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_before_after_solver_comparison_report_phase_16j4e.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation
from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution
from regen_solver_regeneration_after_commit import attach_regen_solver_regeneration_after_commit
from regen_before_after_solver_comparison_report_owner import attach_regen_before_after_solver_comparison_report_owner


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

    results = attach_regen_ranking_owner_source_repair(results)
    results = attach_regen_recommendation_feed_repair(results)
    results = attach_regen_recommendation_viewer_repair(results)
    results = attach_regen_end_to_end_candidate_selection_validation(results)
    results = attach_regen_candidate_acceptance_integration(results)
    results = attach_regen_pending_geometry_commit_validation(results)
    results = attach_regen_live_geometry_commit_execution(results)
    results = attach_regen_solver_regeneration_after_commit(results)
    results = attach_regen_before_after_solver_comparison_report_owner(results)

    assert results["phase_16j4e_complete"] is True
    assert results["phase_16j4e_status"] == "PASS_REGEN_BEFORE_AFTER_SOLVER_COMPARISON_REPORT_PHASE_16J4E"

    payload = results["regen_before_after_solver_comparison_report_payload"]
    assert payload["visibility"] == "REPORT_ONLY"
    assert payload["candidate_id"] == "CANDIDATE_A"

    summary = results["regen_before_after_solver_comparison_summary"]
    assert summary["changed"] >= 3
    assert summary["improved"] >= 3

    changes = results["regen_before_after_solver_comparison_classified_changes"]
    assert any(c["key"] == "corrected_thrust" and c["classification"] == "IMPROVED" for c in changes)
    assert any(c["key"] == "coolant_pressure_drop" and c["classification"] == "IMPROVED" for c in changes)

    report = results["regen_before_after_solver_comparison_report"]
    assert "BEFORE/AFTER SOLVER COMPARISON REPORT OWNERSHIP" in report
    assert "REPORT_ONLY" in report

    assert results["phase_16j4f_design_iteration_history_link_allowed"] is True

    print("PASS_REGEN_BEFORE_AFTER_SOLVER_COMPARISON_REPORT_PHASE_16J4E")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_before_after_solver_comparison_report_owner import attach_regen_before_after_solver_comparison_report_owner" not in text:
    anchor = (
        "try:\n"
        "    from regen_solver_regeneration_after_commit import attach_regen_solver_regeneration_after_commit\n"
        "except Exception:\n"
        "    attach_regen_solver_regeneration_after_commit = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_before_after_solver_comparison_report_owner import attach_regen_before_after_solver_comparison_report_owner\n"
        "except Exception:\n"
        "    attach_regen_before_after_solver_comparison_report_owner = None\n"
    )

if "attach_regen_before_after_solver_comparison_report_owner=attach_regen_before_after_solver_comparison_report_owner" not in text:
    text = text.replace(
        "attach_regen_solver_regeneration_after_commit=attach_regen_solver_regeneration_after_commit,\n",
        "attach_regen_solver_regeneration_after_commit=attach_regen_solver_regeneration_after_commit,\n\n"
        "            attach_regen_before_after_solver_comparison_report_owner=attach_regen_before_after_solver_comparison_report_owner,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_before_after_solver_comparison_report_owner=None" not in text:
    text = text.replace(
        "attach_regen_solver_regeneration_after_commit=None,\n",
        "attach_regen_solver_regeneration_after_commit=None,\n\n"
        "        attach_regen_before_after_solver_comparison_report_owner=None,\n",
    )

if '"regen_before_after_solver_comparison_report_owner"' not in text:
    text = text.replace(
        '(\n            "regen_solver_regeneration_after_commit",\n            attach_regen_solver_regeneration_after_commit,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_solver_regeneration_after_commit",\n            attach_regen_solver_regeneration_after_commit,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_before_after_solver_comparison_report_owner",\n            attach_regen_before_after_solver_comparison_report_owner,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16J4E_BEFORE_AFTER_SOLVER_COMPARISON_REPORT_INTEGRATED")
