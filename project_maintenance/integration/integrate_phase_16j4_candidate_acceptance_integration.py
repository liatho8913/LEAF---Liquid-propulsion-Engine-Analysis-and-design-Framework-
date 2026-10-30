from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

# ============================================================
# 1. ADD: Candidate Acceptance Integration Owner
# ============================================================

(LEAF / "regen_candidate_acceptance_integration.py").write_text(r'''"""
PHASE 16J.4 — Candidate Acceptance Integration

Purpose:
- Accept the validated recommendation viewer payload.
- Produce a pending geometry application payload.
- Produce before/after preview data.
- Record an acceptance history event.
- Do NOT directly overwrite live geometry in this phase.
"""

import copy
from datetime import datetime, timezone

PASS_STATUS = "PASS_REGEN_CANDIDATE_ACCEPTANCE_INTEGRATION_PHASE_16J4"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_ACCEPTANCE_INTEGRATION_PHASE_16J4"


GEOMETRY_KEYS = (
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


def attach_regen_candidate_acceptance_integration(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    viewer_payload = results.get("regen_recommendation_viewer_payload")
    validation_ok = results.get("phase_16j3h_complete") is True

    if not validation_ok:
        blockers.append("Phase 16J.3H end-to-end selection validation has not passed.")

    if not isinstance(viewer_payload, dict) or not viewer_payload:
        blockers.append("Recommendation viewer payload is missing.")

    geometry = {}
    if isinstance(viewer_payload, dict):
        geometry = viewer_payload.get("geometry") or {}

    if not isinstance(geometry, dict) or not geometry:
        blockers.append("Accepted candidate geometry is missing from viewer payload.")

    candidate_id = None
    if isinstance(viewer_payload, dict):
        candidate_id = viewer_payload.get("candidate_id")

    if not candidate_id:
        blockers.append("Accepted candidate ID is missing.")

    pending_payload = None
    preview = None
    history_event = None

    if not blockers:
        live_geometry = _extract_current_live_geometry(results)
        accepted_geometry = _normalise_geometry(geometry)

        pending_payload = {
            "candidate_id": candidate_id,
            "accepted_geometry": accepted_geometry,
            "previous_geometry": live_geometry,
            "application_mode": "PENDING_REVIEW",
            "commit_state": "NOT_COMMITTED",
            "requires_explicit_commit_phase": "16J.4B",
            "source": "PHASE_16J4_CANDIDATE_ACCEPTANCE_INTEGRATION",
        }

        preview = _build_before_after_preview(
            previous_geometry=live_geometry,
            accepted_geometry=accepted_geometry,
        )

        history_event = {
            "event_type": "REGEN_CANDIDATE_ACCEPTED_PENDING_APPLICATION",
            "phase": "16J.4",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "candidate_id": candidate_id,
            "commit_state": "NOT_COMMITTED",
            "summary": (
                "Candidate accepted into pending geometry application state. "
                "Live geometry was not overwritten."
            ),
            "preview": preview,
        }

    status = PASS_STATUS if not blockers else FAIL_STATUS

    report = _build_report(
        status=status,
        blockers=blockers,
        candidate_id=candidate_id,
        pending_payload=pending_payload,
        preview=preview,
        history_event=history_event,
    )

    results["regen_candidate_acceptance_integration_complete"] = True
    results["phase_16j4_complete"] = status == PASS_STATUS
    results["regen_candidate_acceptance_integration_status"] = status
    results["phase_16j4_status"] = status
    results["regen_candidate_acceptance_integration_blockers"] = blockers

    results["regen_candidate_acceptance_pending_application_payload"] = pending_payload
    results["regen_candidate_acceptance_before_after_preview"] = preview
    results["regen_candidate_acceptance_history_event"] = history_event
    results["regen_candidate_acceptance_report"] = report

    # Safe state: accepted but not committed.
    results["regen_candidate_accepted_for_pending_application"] = status == PASS_STATUS
    results["regen_candidate_pending_application_candidate_id"] = candidate_id
    results["regen_candidate_geometry_application_allowed"] = status == PASS_STATUS
    results["regen_candidate_manual_overwrite_allowed"] = False
    results["regen_candidate_live_geometry_commit_executed"] = False

    # Next phase permission.
    results["phase_16j4b_pending_geometry_commit_validation_allowed"] = (
        status == PASS_STATUS
    )

    return results


def _extract_current_live_geometry(results):
    live = {}

    possible_sources = [
        results.get("manual_regen_geometry"),
        results.get("regen_manual_geometry"),
        results.get("regen_geometry_inputs"),
        results.get("inputs"),
        results,
    ]

    for source in possible_sources:
        if not isinstance(source, dict):
            continue

        for key in GEOMETRY_KEYS:
            if key in source and key not in live:
                live[key] = source[key]

    return live


def _normalise_geometry(geometry):
    out = {}
    for key, value in geometry.items():
        out[key] = copy.deepcopy(value)
    return out


def _build_before_after_preview(previous_geometry, accepted_geometry):
    all_keys = sorted(set(previous_geometry.keys()) | set(accepted_geometry.keys()))
    changes = []

    for key in all_keys:
        before = previous_geometry.get(key)
        after = accepted_geometry.get(key)

        if before != after:
            changes.append({
                "key": key,
                "before": before,
                "after": after,
                "changed": True,
            })

    return {
        "change_count": len(changes),
        "changes": changes,
        "previous_geometry": previous_geometry,
        "accepted_geometry": accepted_geometry,
    }


def _build_report(status, blockers, candidate_id, pending_payload, preview, history_event):
    lines = [
        "LEAF PHASE 16J.4 CANDIDATE ACCEPTANCE INTEGRATION",
        "====================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Accepts the validated recommended candidate.",
        "- Creates a pending geometry application payload.",
        "- Creates before/after preview data.",
        "- Records a history event.",
        "- Does not overwrite live geometry.",
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

    if preview:
        lines.append("Before/After Preview:")
        lines.append(f"- Change count: {preview.get('change_count')}")
        for change in preview.get("changes", [])[:20]:
            lines.append(
                f"- {change.get('key')}: {change.get('before')} -> {change.get('after')}"
            )
    else:
        lines.append("Before/After Preview:")
        lines.append("- Not available.")

    lines.extend([
        "",
        "Safety State:",
        "- Accepted candidate: YES" if pending_payload else "- Accepted candidate: NO",
        "- Pending application payload: CREATED" if pending_payload else "- Pending application payload: NOT CREATED",
        "- Live geometry commit: NOT EXECUTED",
        "- Manual overwrite: LOCKED",
        "",
        "Next Required Phase:",
        "- 16J.4B Pending Geometry Commit Validation.",
    ])

    if history_event:
        lines.extend([
            "",
            "History Event:",
            f"- Type: {history_event.get('event_type')}",
            f"- Commit state: {history_event.get('commit_state')}",
        ])

    return "\n".join(lines)
''')

# ============================================================
# 2. ADD: Verification Test
# ============================================================

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_candidate_acceptance_integration_phase_16j4.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import (
    attach_regen_end_to_end_candidate_selection_validation,
)
from regen_candidate_acceptance_integration import (
    attach_regen_candidate_acceptance_integration,
)


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
            },
            {
                "candidate_id": "CANDIDATE_B",
                "candidate_geometry": {
                    "number_of_coolant_channels": 100,
                    "coolant_channel_width": 0.0012,
                    "coolant_channel_height": 0.0025,
                    "rib_width": 0.0008,
                    "hot_gas_wall_thickness": 0.0012,
                },
            },
        ],
    }

    results = attach_regen_ranking_owner_source_repair(results)
    results = attach_regen_recommendation_feed_repair(results)
    results = attach_regen_recommendation_viewer_repair(results)
    results = attach_regen_end_to_end_candidate_selection_validation(results)
    results = attach_regen_candidate_acceptance_integration(results)

    assert results["phase_16j4_complete"] is True
    assert (
        results["phase_16j4_status"]
        == "PASS_REGEN_CANDIDATE_ACCEPTANCE_INTEGRATION_PHASE_16J4"
    )

    payload = results["regen_candidate_acceptance_pending_application_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["commit_state"] == "NOT_COMMITTED"
    assert payload["application_mode"] == "PENDING_REVIEW"

    preview = results["regen_candidate_acceptance_before_after_preview"]
    assert preview["change_count"] >= 1

    history = results["regen_candidate_acceptance_history_event"]
    assert history["event_type"] == "REGEN_CANDIDATE_ACCEPTED_PENDING_APPLICATION"
    assert history["commit_state"] == "NOT_COMMITTED"

    assert results["regen_candidate_accepted_for_pending_application"] is True
    assert results["regen_candidate_geometry_application_allowed"] is True
    assert results["regen_candidate_manual_overwrite_allowed"] is False
    assert results["regen_candidate_live_geometry_commit_executed"] is False
    assert results["phase_16j4b_pending_geometry_commit_validation_allowed"] is True

    report = results["regen_candidate_acceptance_report"]
    assert "Pending Geometry Commit Validation" in report
    assert "Live geometry commit: NOT EXECUTED" in report

    print("PASS_REGEN_CANDIDATE_ACCEPTANCE_INTEGRATION_PHASE_16J4")


if __name__ == "__main__":
    main()
''')

# ============================================================
# 3. PATCH: Foundation Layer Controller
# ============================================================

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration" not in text:
    anchor = (
        "try:\n"
        "    from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation\n"
        "except Exception:\n"
        "    attach_regen_end_to_end_candidate_selection_validation = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration\n"
        "except Exception:\n"
        "    attach_regen_candidate_acceptance_integration = None\n"
    )

if "attach_regen_candidate_acceptance_integration=attach_regen_candidate_acceptance_integration" not in text:
    text = text.replace(
        "attach_regen_end_to_end_candidate_selection_validation=attach_regen_end_to_end_candidate_selection_validation,\n",
        "attach_regen_end_to_end_candidate_selection_validation=attach_regen_end_to_end_candidate_selection_validation,\n\n"
        "            attach_regen_candidate_acceptance_integration=attach_regen_candidate_acceptance_integration,\n",
    )

controller.write_text(text)

# ============================================================
# 4. PATCH: Foundation Attachment Pipeline
# ============================================================

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_candidate_acceptance_integration=None" not in text:
    text = text.replace(
        "attach_regen_end_to_end_candidate_selection_validation=None,\n",
        "attach_regen_end_to_end_candidate_selection_validation=None,\n\n"
        "        attach_regen_candidate_acceptance_integration=None,\n",
    )

if '"regen_candidate_acceptance_integration"' not in text:
    text = text.replace(
        '(\n            "regen_end_to_end_candidate_selection_validation",\n            attach_regen_end_to_end_candidate_selection_validation,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_end_to_end_candidate_selection_validation",\n            attach_regen_end_to_end_candidate_selection_validation,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_candidate_acceptance_integration",\n            attach_regen_candidate_acceptance_integration,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16J4_CANDIDATE_ACCEPTANCE_INTEGRATION_INTEGRATED")
