from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_live_geometry_commit_execution.py").write_text(r'''"""
PHASE 16J.4C — Live Geometry Commit Execution

Purpose:
- Consume the 16J.4B commit approval payload.
- Apply accepted geometry into the active results/input dictionary.
- Record before/after commit audit.
- Mark live geometry commit as executed.

This is the first controlled live-geometry commit phase.
"""

import copy
from datetime import datetime, timezone

PASS_STATUS = "PASS_REGEN_LIVE_GEOMETRY_COMMIT_EXECUTION_PHASE_16J4C"
FAIL_STATUS = "FAIL_REGEN_LIVE_GEOMETRY_COMMIT_EXECUTION_PHASE_16J4C"

COMMITTABLE_GEOMETRY_KEYS = (
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
    "outer_wall_thickness",
    "coating_thickness",
    "bond_coat_thickness",
    "coolant_channel_aspect_ratio",
)


def attach_regen_live_geometry_commit_execution(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    approval = results.get("regen_pending_geometry_commit_approval_payload")

    if results.get("phase_16j4b_complete") is not True:
        blockers.append("Phase 16J.4B pending geometry commit validation has not passed.")

    if not isinstance(approval, dict) or not approval:
        blockers.append("Commit approval payload is missing.")

    accepted_geometry = {}
    previous_geometry = {}

    if isinstance(approval, dict):
        if approval.get("commit_readiness") != "READY_FOR_EXPLICIT_COMMIT":
            blockers.append("Commit approval payload is not READY_FOR_EXPLICIT_COMMIT.")

        if approval.get("live_commit_executed") is not False:
            blockers.append("Commit approval payload already indicates a live commit.")

        accepted_geometry = approval.get("accepted_geometry") or {}
        previous_geometry = approval.get("previous_geometry") or {}

    if not isinstance(accepted_geometry, dict) or not accepted_geometry:
        blockers.append("Accepted geometry is missing from commit approval payload.")

    committed_keys = []
    before_after = []

    if not blockers:
        for key in COMMITTABLE_GEOMETRY_KEYS:
            if key not in accepted_geometry:
                continue

            before = copy.deepcopy(results.get(key))
            after = copy.deepcopy(accepted_geometry[key])

            results[key] = after
            committed_keys.append(key)

            before_after.append({
                "key": key,
                "before": before,
                "after": after,
                "changed": before != after,
            })

        results["regen_geometry_active_source"] = "ACCEPTED_RECOMMENDED_CANDIDATE"
        results["regen_geometry_active_candidate_id"] = approval.get("candidate_id")
        results["regen_geometry_last_commit_phase"] = "16J.4C"

    status = PASS_STATUS if not blockers else FAIL_STATUS

    audit_record = None
    if status == PASS_STATUS:
        audit_record = {
            "event_type": "REGEN_LIVE_GEOMETRY_COMMIT_EXECUTED",
            "phase": "16J.4C",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "candidate_id": approval.get("candidate_id"),
            "committed_keys": committed_keys,
            "before_after": before_after,
            "previous_geometry_snapshot": previous_geometry,
            "accepted_geometry_snapshot": accepted_geometry,
        }

    report = _build_report(status, blockers, approval, committed_keys, before_after)

    results["regen_live_geometry_commit_execution_complete"] = True
    results["phase_16j4c_complete"] = status == PASS_STATUS
    results["regen_live_geometry_commit_execution_status"] = status
    results["phase_16j4c_status"] = status
    results["regen_live_geometry_commit_execution_blockers"] = blockers
    results["regen_live_geometry_commit_audit_record"] = audit_record
    results["regen_live_geometry_commit_report"] = report

    results["regen_candidate_live_geometry_commit_executed"] = status == PASS_STATUS
    results["regen_candidate_manual_overwrite_allowed"] = False
    results["regen_candidate_geometry_application_allowed"] = status == PASS_STATUS

    results["phase_16j4d_solver_regeneration_after_commit_allowed"] = status == PASS_STATUS

    return results


def _build_report(status, blockers, approval, committed_keys, before_after):
    candidate_id = approval.get("candidate_id") if isinstance(approval, dict) else None

    lines = [
        "LEAF PHASE 16J.4C LIVE GEOMETRY COMMIT EXECUTION",
        "===================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Applies validated accepted candidate geometry into active geometry keys.",
        "- Records before/after commit audit.",
        "- Marks live geometry commit as executed.",
        "- Does not regenerate solver outputs yet.",
        "",
        f"Candidate ID: {candidate_id}",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Committed Keys:")

    if committed_keys:
        for key in committed_keys:
            lines.append(f"- {key}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Before/After:")

    if before_after:
        for change in before_after:
            lines.append(
                f"- {change['key']}: {change['before']} -> {change['after']}"
            )
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Safety State:",
        "- Live geometry commit: EXECUTED" if committed_keys and not blockers else "- Live geometry commit: NOT EXECUTED",
        "- Manual overwrite: LOCKED",
        "",
        "Next Required Phase:",
        "- 16J.4D Solver Regeneration After Commit.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_live_geometry_commit_execution_phase_16j4c.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation
from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution


def main():
    results = {
        "number_of_coolant_channels": 60,
        "coolant_channel_width": 0.0010,
        "coolant_channel_height": 0.0015,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0008,
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

    assert results["phase_16j4c_complete"] is True
    assert results["phase_16j4c_status"] == "PASS_REGEN_LIVE_GEOMETRY_COMMIT_EXECUTION_PHASE_16J4C"

    assert results["number_of_coolant_channels"] == 80
    assert results["coolant_channel_width"] == 0.0015
    assert results["coolant_channel_height"] == 0.0020
    assert results["hot_gas_wall_thickness"] == 0.0010

    audit = results["regen_live_geometry_commit_audit_record"]
    assert audit["event_type"] == "REGEN_LIVE_GEOMETRY_COMMIT_EXECUTED"
    assert audit["candidate_id"] == "CANDIDATE_A"
    assert "coolant_channel_width" in audit["committed_keys"]

    assert results["regen_candidate_live_geometry_commit_executed"] is True
    assert results["regen_candidate_manual_overwrite_allowed"] is False
    assert results["phase_16j4d_solver_regeneration_after_commit_allowed"] is True

    report = results["regen_live_geometry_commit_report"]
    assert "LIVE GEOMETRY COMMIT EXECUTION" in report
    assert "Live geometry commit: EXECUTED" in report

    print("PASS_REGEN_LIVE_GEOMETRY_COMMIT_EXECUTION_PHASE_16J4C")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution" not in text:
    anchor = (
        "try:\n"
        "    from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation\n"
        "except Exception:\n"
        "    attach_regen_pending_geometry_commit_validation = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution\n"
        "except Exception:\n"
        "    attach_regen_live_geometry_commit_execution = None\n"
    )

if "attach_regen_live_geometry_commit_execution=attach_regen_live_geometry_commit_execution" not in text:
    text = text.replace(
        "attach_regen_pending_geometry_commit_validation=attach_regen_pending_geometry_commit_validation,\n",
        "attach_regen_pending_geometry_commit_validation=attach_regen_pending_geometry_commit_validation,\n\n"
        "            attach_regen_live_geometry_commit_execution=attach_regen_live_geometry_commit_execution,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_live_geometry_commit_execution=None" not in text:
    text = text.replace(
        "attach_regen_pending_geometry_commit_validation=None,\n",
        "attach_regen_pending_geometry_commit_validation=None,\n\n"
        "        attach_regen_live_geometry_commit_execution=None,\n",
    )

if '"regen_live_geometry_commit_execution"' not in text:
    text = text.replace(
        '(\n            "regen_pending_geometry_commit_validation",\n            attach_regen_pending_geometry_commit_validation,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_pending_geometry_commit_validation",\n            attach_regen_pending_geometry_commit_validation,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_live_geometry_commit_execution",\n            attach_regen_live_geometry_commit_execution,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16J4C_LIVE_GEOMETRY_COMMIT_EXECUTION_INTEGRATED")
