from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_pending_geometry_commit_validation.py").write_text(r'''"""
PHASE 16J.4B — Pending Geometry Commit Validation

Validates that the accepted pending geometry application payload is complete,
safe, traceable, and ready for a later explicit live commit phase.

This phase does NOT overwrite live geometry.
"""

PASS_STATUS = "PASS_REGEN_PENDING_GEOMETRY_COMMIT_VALIDATION_PHASE_16J4B"
FAIL_STATUS = "FAIL_REGEN_PENDING_GEOMETRY_COMMIT_VALIDATION_PHASE_16J4B"

REQUIRED_GEOMETRY_KEYS = (
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
)


def attach_regen_pending_geometry_commit_validation(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    payload = results.get("regen_candidate_acceptance_pending_application_payload")

    if results.get("phase_16j4_complete") is not True:
        blockers.append("Phase 16J.4 candidate acceptance has not passed.")

    if not isinstance(payload, dict) or not payload:
        blockers.append("Pending geometry application payload is missing.")

    accepted_geometry = {}
    previous_geometry = {}

    if isinstance(payload, dict):
        accepted_geometry = payload.get("accepted_geometry") or {}
        previous_geometry = payload.get("previous_geometry") or {}

        if payload.get("commit_state") != "NOT_COMMITTED":
            blockers.append("Pending payload is not in NOT_COMMITTED state.")

        if payload.get("application_mode") != "PENDING_REVIEW":
            blockers.append("Pending payload is not in PENDING_REVIEW mode.")

    if not isinstance(accepted_geometry, dict) or not accepted_geometry:
        blockers.append("Accepted geometry is missing.")

    if isinstance(accepted_geometry, dict):
        for key in REQUIRED_GEOMETRY_KEYS:
            if key not in accepted_geometry:
                blockers.append(f"Accepted geometry is missing required key: {key}")

        for key, value in accepted_geometry.items():
            if key == "number_of_coolant_channels":
                try:
                    if int(value) <= 0:
                        blockers.append("number_of_coolant_channels must be positive.")
                except Exception:
                    blockers.append("number_of_coolant_channels must be numeric.")
            elif isinstance(value, (int, float)):
                if value <= 0:
                    blockers.append(f"{key} must be positive.")

    approval_payload = None

    if not blockers:
        approval_payload = {
            "candidate_id": payload.get("candidate_id"),
            "previous_geometry": previous_geometry,
            "accepted_geometry": accepted_geometry,
            "commit_readiness": "READY_FOR_EXPLICIT_COMMIT",
            "commit_permission": "VALIDATED_PENDING_USER_OR_UI_TRIGGER",
            "live_commit_executed": False,
            "manual_overwrite_executed": False,
            "required_next_phase": "16J.4C",
            "source": "PHASE_16J4B_PENDING_GEOMETRY_COMMIT_VALIDATION",
        }

    status = PASS_STATUS if not blockers else FAIL_STATUS

    results["regen_pending_geometry_commit_validation_complete"] = True
    results["phase_16j4b_complete"] = status == PASS_STATUS
    results["regen_pending_geometry_commit_validation_status"] = status
    results["phase_16j4b_status"] = status
    results["regen_pending_geometry_commit_validation_blockers"] = blockers
    results["regen_pending_geometry_commit_approval_payload"] = approval_payload
    results["regen_pending_geometry_commit_validation_report"] = _build_report(
        status, blockers, approval_payload, accepted_geometry
    )

    results["regen_candidate_geometry_application_allowed"] = status == PASS_STATUS
    results["regen_candidate_manual_overwrite_allowed"] = False
    results["regen_candidate_live_geometry_commit_executed"] = False
    results["phase_16j4c_live_geometry_commit_allowed"] = status == PASS_STATUS

    return results


def _build_report(status, blockers, approval_payload, accepted_geometry):
    lines = [
        "LEAF PHASE 16J.4B PENDING GEOMETRY COMMIT VALIDATION",
        "=======================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Validates pending geometry application payload.",
        "- Checks accepted geometry completeness.",
        "- Checks commit state remains safe.",
        "- Produces explicit commit approval payload.",
        "- Does not overwrite live geometry.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Accepted Geometry:")

    if isinstance(accepted_geometry, dict) and accepted_geometry:
        for key in sorted(accepted_geometry.keys()):
            lines.append(f"- {key}: {accepted_geometry[key]}")
    else:
        lines.append("- Not available.")

    lines.extend([
        "",
        "Safety State:",
        "- Commit approval payload: CREATED" if approval_payload else "- Commit approval payload: NOT CREATED",
        "- Live geometry commit: NOT EXECUTED",
        "- Manual overwrite: LOCKED",
        "",
        "Next Required Phase:",
        "- 16J.4C Live Geometry Commit Execution.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_pending_geometry_commit_validation_phase_16j4b.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation


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

    assert results["phase_16j4b_complete"] is True
    assert results["phase_16j4b_status"] == "PASS_REGEN_PENDING_GEOMETRY_COMMIT_VALIDATION_PHASE_16J4B"

    approval = results["regen_pending_geometry_commit_approval_payload"]
    assert approval["candidate_id"] == "CANDIDATE_A"
    assert approval["commit_readiness"] == "READY_FOR_EXPLICIT_COMMIT"
    assert approval["live_commit_executed"] is False

    assert results["phase_16j4c_live_geometry_commit_allowed"] is True
    assert results["regen_candidate_manual_overwrite_allowed"] is False
    assert results["regen_candidate_live_geometry_commit_executed"] is False

    report = results["regen_pending_geometry_commit_validation_report"]
    assert "Pending Geometry Commit Validation" in report
    assert "Live geometry commit: NOT EXECUTED" in report

    print("PASS_REGEN_PENDING_GEOMETRY_COMMIT_VALIDATION_PHASE_16J4B")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation" not in text:
    anchor = (
        "try:\n"
        "    from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration\n"
        "except Exception:\n"
        "    attach_regen_candidate_acceptance_integration = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation\n"
        "except Exception:\n"
        "    attach_regen_pending_geometry_commit_validation = None\n"
    )

if "attach_regen_pending_geometry_commit_validation=attach_regen_pending_geometry_commit_validation" not in text:
    text = text.replace(
        "attach_regen_candidate_acceptance_integration=attach_regen_candidate_acceptance_integration,\n",
        "attach_regen_candidate_acceptance_integration=attach_regen_candidate_acceptance_integration,\n\n"
        "            attach_regen_pending_geometry_commit_validation=attach_regen_pending_geometry_commit_validation,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_pending_geometry_commit_validation=None" not in text:
    text = text.replace(
        "attach_regen_candidate_acceptance_integration=None,\n",
        "attach_regen_candidate_acceptance_integration=None,\n\n"
        "        attach_regen_pending_geometry_commit_validation=None,\n",
    )

if '"regen_pending_geometry_commit_validation"' not in text:
    text = text.replace(
        '(\n            "regen_candidate_acceptance_integration",\n            attach_regen_candidate_acceptance_integration,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_candidate_acceptance_integration",\n            attach_regen_candidate_acceptance_integration,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_pending_geometry_commit_validation",\n            attach_regen_pending_geometry_commit_validation,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16J4B_PENDING_GEOMETRY_COMMIT_VALIDATION_INTEGRATED")
