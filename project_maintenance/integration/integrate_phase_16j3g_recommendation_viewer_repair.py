from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

# ============================================================
# 1. ADD: Recommendation Viewer Repair Owner
# ============================================================

(LEAF / "regen_recommendation_viewer_repair.py").write_text(r'''"""
PHASE 16J.3G — Recommendation Viewer Repair

Purpose:
- Consume the Phase 16J.3F recommendation viewer feed.
- Produce a stable, readable recommendation viewer payload.
- Display candidate ID, score, rank, advantages, penalties, and reasoning.
- Do NOT apply geometry.
- Do NOT mutate live solver inputs.
"""

PASS_STATUS = "PASS_REGEN_RECOMMENDATION_VIEWER_REPAIR_PHASE_16J3G"
FAIL_STATUS = "FAIL_REGEN_RECOMMENDATION_VIEWER_REPAIR_PHASE_16J3G"


def attach_regen_recommendation_viewer_repair(results):
    if not isinstance(results, dict):
        return results

    recommendation = (
        results.get("regen_recommendation_viewer_feed_payload")
        or results.get("regen_candidate_recommendation")
        or results.get("regen_recommendation_feed_repair_recommendation_payload")
    )

    explanation = (
        results.get("regen_recommendation_viewer_feed_explanation")
        or results.get("regen_recommendation_feed_repair_explanation")
        or ""
    )

    blockers = []

    if not isinstance(recommendation, dict) or not recommendation:
        blockers.append("No recommendation payload was available for the viewer.")

    viewer_payload = None

    if not blockers:
        viewer_payload = _build_viewer_payload(recommendation, explanation)

    status = PASS_STATUS if viewer_payload and not blockers else FAIL_STATUS

    results["regen_recommendation_viewer_repair_complete"] = True
    results["phase_16j3g_complete"] = status == PASS_STATUS
    results["regen_recommendation_viewer_repair_status"] = status
    results["phase_16j3g_status"] = status
    results["regen_recommendation_viewer_repair_blockers"] = blockers
    results["regen_recommendation_viewer_payload"] = viewer_payload
    results["regen_recommendation_viewer_report"] = (
        _build_viewer_report(viewer_payload, blockers, status)
    )

    # Compatibility keys for UI/report systems.
    results["regen_recommendation_display_candidate_id"] = (
        viewer_payload or {}
    ).get("candidate_id")
    results["regen_recommendation_display_rank"] = (
        viewer_payload or {}
    ).get("rank")
    results["regen_recommendation_display_score"] = (
        viewer_payload or {}
    ).get("score")
    results["regen_recommendation_display_reasoning"] = (
        viewer_payload or {}
    ).get("reasoning")
    results["regen_recommendation_display_advantages"] = (
        viewer_payload or {}
    ).get("advantages", [])
    results["regen_recommendation_display_penalties"] = (
        viewer_payload or {}
    ).get("penalties", [])

    # Safety locks remain active.
    results["regen_recommendation_viewer_live_geometry_commit_executed"] = False
    results["regen_recommendation_viewer_geometry_application_executed"] = False
    results["regen_candidate_geometry_application_allowed"] = False
    results["regen_candidate_manual_overwrite_allowed"] = False

    # Next phase permission.
    results["phase_16j3h_end_to_end_selection_validation_allowed"] = (
        status == PASS_STATUS
    )

    return results


def _build_viewer_payload(recommendation, explanation):
    candidate = (
        recommendation.get("candidate")
        or recommendation.get("selected_candidate")
        or recommendation
    )

    score = (
        recommendation.get("score")
        or recommendation.get("candidate_rank_score")
        or candidate.get("candidate_rank_score")
        or candidate.get("score")
        or candidate.get("total_score")
    )

    rank = (
        recommendation.get("rank")
        or recommendation.get("candidate_rank")
        or candidate.get("candidate_rank")
        or candidate.get("rank")
        or 1
    )

    reasoning = (
        recommendation.get("reasoning")
        or recommendation.get("recommendation_reason")
        or candidate.get("recommended_regen_candidate_reason")
        or candidate.get("candidate_ranking_reason")
        or "Candidate recommended from ranked regen candidate feed."
    )

    advantages = _normalise_list(
        recommendation.get("advantages")
        or recommendation.get("pass_reasons")
        or candidate.get("pass_reasons")
        or []
    )

    penalties = _normalise_list(
        recommendation.get("penalties")
        or recommendation.get("failure_reasons")
        or candidate.get("failure_reasons")
        or []
    )

    geometry = (
        candidate.get("candidate_geometry")
        or candidate.get("inputs")
        or recommendation.get("candidate_geometry")
        or {}
    )

    return {
        "candidate_id": (
            recommendation.get("candidate_id")
            or candidate.get("candidate_id")
            or "UNKNOWN_CANDIDATE"
        ),
        "rank": rank,
        "score": score,
        "status": recommendation.get("status"),
        "confidence": recommendation.get("confidence"),
        "reasoning": reasoning,
        "advantages": advantages,
        "penalties": penalties,
        "geometry": geometry,
        "source": "PHASE_16J3G_RECOMMENDATION_VIEWER_REPAIR",
        "upstream_explanation": explanation,
        "geometry_application_state": "LOCKED_NOT_APPLIED",
    }


def _normalise_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, tuple):
        return [str(v) for v in value]
    return [str(value)]


def _build_viewer_report(viewer_payload, blockers, status):
    lines = [
        "LEAF PHASE 16J.3G RECOMMENDATION VIEWER REPAIR",
        "==================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Receives recommendation payload from Phase 16J.3F.",
        "- Converts recommendation into viewer-readable display data.",
        "- Shows candidate ID, score, rank, advantages, penalties, and reasoning.",
        "- Does not apply geometry.",
        "- Does not mutate live inputs.",
        "",
    ]

    if blockers:
        lines.append("Blocking Reasons:")
        for blocker in blockers:
            lines.append(f"- {blocker}")
        return "\n".join(lines)

    lines.extend([
        "Recommendation Display:",
        f"- Candidate ID: {viewer_payload.get('candidate_id')}",
        f"- Rank: {viewer_payload.get('rank')}",
        f"- Score: {viewer_payload.get('score')}",
        f"- Status: {viewer_payload.get('status')}",
        f"- Confidence: {viewer_payload.get('confidence')}",
        "",
        "Reasoning:",
        f"{viewer_payload.get('reasoning')}",
        "",
        "Advantages:",
    ])

    advantages = viewer_payload.get("advantages") or []
    if advantages:
        for item in advantages:
            lines.append(f"- {item}")
    else:
        lines.append("- None provided.")

    lines.append("")
    lines.append("Penalties:")

    penalties = viewer_payload.get("penalties") or []
    if penalties:
        for item in penalties:
            lines.append(f"- {item}")
    else:
        lines.append("- None provided.")

    lines.extend([
        "",
        "Safety State:",
        "- Geometry application: LOCKED",
        "- Live commit: NOT EXECUTED",
        "",
        "Next Required Phase:",
        "- 16J.3H End-to-End Candidate Selection Validation.",
    ])

    return "\n".join(lines)
''')

# ============================================================
# 2. ADD: Verification Test
# ============================================================

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_recommendation_viewer_repair_phase_16j3g.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair


def main():
    results = {
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
        ]
    }

    results = attach_regen_ranking_owner_source_repair(results)
    results = attach_regen_recommendation_feed_repair(results)
    results = attach_regen_recommendation_viewer_repair(results)

    assert results["phase_16j3g_complete"] is True
    assert results["phase_16j3g_status"] == "PASS_REGEN_RECOMMENDATION_VIEWER_REPAIR_PHASE_16J3G"

    payload = results["regen_recommendation_viewer_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["rank"] == 1
    assert payload["geometry_application_state"] == "LOCKED_NOT_APPLIED"

    report = results["regen_recommendation_viewer_report"]
    assert "Recommendation Display" in report
    assert "Candidate ID: CANDIDATE_A" in report
    assert "Geometry application: LOCKED" in report

    assert results["regen_recommendation_display_candidate_id"] == "CANDIDATE_A"
    assert results["regen_candidate_geometry_application_allowed"] is False
    assert results["regen_recommendation_viewer_live_geometry_commit_executed"] is False
    assert results["phase_16j3h_end_to_end_selection_validation_allowed"] is True

    print("PASS_REGEN_RECOMMENDATION_VIEWER_REPAIR_PHASE_16J3G")


if __name__ == "__main__":
    main()
''')

# ============================================================
# 3. PATCH: Foundation Layer Controller
# ============================================================

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair" not in text:
    anchor = (
        "try:\n"
        "    from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair\n"
        "except Exception:\n"
        "    attach_regen_recommendation_feed_repair = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair\n"
        "except Exception:\n"
        "    attach_regen_recommendation_viewer_repair = None\n"
    )

if "attach_regen_recommendation_viewer_repair=attach_regen_recommendation_viewer_repair" not in text:
    text = text.replace(
        "attach_regen_recommendation_feed_repair=attach_regen_recommendation_feed_repair,\n",
        "attach_regen_recommendation_feed_repair=attach_regen_recommendation_feed_repair,\n\n"
        "            attach_regen_recommendation_viewer_repair=attach_regen_recommendation_viewer_repair,\n",
    )

controller.write_text(text)

# ============================================================
# 4. PATCH: Foundation Attachment Pipeline
# ============================================================

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_recommendation_viewer_repair=None" not in text:
    text = text.replace(
        "attach_regen_recommendation_feed_repair=None,\n",
        "attach_regen_recommendation_feed_repair=None,\n\n"
        "        attach_regen_recommendation_viewer_repair=None,\n",
    )

if '"regen_recommendation_viewer_repair"' not in text:
    text = text.replace(
        '(\n            "regen_recommendation_feed_repair",\n            attach_regen_recommendation_feed_repair,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_recommendation_feed_repair",\n            attach_regen_recommendation_feed_repair,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_recommendation_viewer_repair",\n            attach_regen_recommendation_viewer_repair,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

# ============================================================
# 5. REGISTER RESULT KEY PREFIXES
# ============================================================

for path in [
    LEAF / "foundation_result_key_audit.py",
    LEAF / "variable_registry.py",
]:
    if not path.exists():
        continue

    text = path.read_text()

    if "EXPECTED_PREFIX_VISIBILITY = {" in text and '"regen_recommendation_viewer_": "REPORT_ONLY",' not in text:
        text = text.replace(
            "EXPECTED_PREFIX_VISIBILITY = {",
            'EXPECTED_PREFIX_VISIBILITY = {\n'
            '    "regen_recommendation_viewer_": "REPORT_ONLY",'
        )

    if "KNOWN_DEVELOPMENT_KEYS = {" in text and '"regen_recommendation_viewer_",' not in text:
        text = text.replace(
            "KNOWN_DEVELOPMENT_KEYS = {",
            'KNOWN_DEVELOPMENT_KEYS = {\n'
            '    "regen_recommendation_viewer_",'
        )

    path.write_text(text)

print("PHASE_16J3G_RECOMMENDATION_VIEWER_REPAIR_INTEGRATED")
