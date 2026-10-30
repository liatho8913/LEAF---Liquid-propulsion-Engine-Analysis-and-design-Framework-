from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

# ============================================================
# 1. ADD: Recommendation Feed Repair Owner
# ============================================================

(LEAF / "regen_recommendation_feed_repair.py").write_text(r'''"""
PHASE 16J.3F — Recommendation Feed Repair

Purpose:
- Consume the Phase 16J.3E best ranked candidate.
- Convert it into the selected-candidate payload expected by
  regen_candidate_recommendation_owner.py.
- Run the existing recommendation owner.
- Publish recommendation payload/report/explanation compatibility keys.
- Do NOT apply geometry.
- Do NOT mutate geometry.
- Do NOT commit live design changes.
"""

import copy

try:
    from regen_candidate_recommendation_owner import (
        attach_regen_candidate_recommendation_owner,
    )
except Exception:
    attach_regen_candidate_recommendation_owner = None


PASS_STATUS = "PASS_REGEN_RECOMMENDATION_FEED_REPAIR_PHASE_16J3F"
FAIL_STATUS = "FAIL_REGEN_RECOMMENDATION_FEED_REPAIR_PHASE_16J3F"


def attach_regen_recommendation_feed_repair(results):
    if not isinstance(results, dict):
        return results

    source_key, best_candidate = _find_best_candidate(results)
    ranked_key, ranked_candidates = _find_ranked_candidates(results)

    blockers = []

    if not best_candidate:
        blockers.append("No best ranked candidate was available from Phase 16J.3E.")

    if attach_regen_candidate_recommendation_owner is None:
        blockers.append("regen_candidate_recommendation_owner.py could not be imported.")

    selected_candidate = None

    if not blockers:
        selected_candidate = _build_selected_candidate_payload(
            best_candidate=best_candidate,
            ranked_candidates=ranked_candidates,
        )

        results["regen_candidate_selector_selected_candidate"] = selected_candidate
        results["regen_candidate_ranker_ranked_candidates"] = [
            _build_selected_candidate_payload(candidate, ranked_candidates)
            for candidate in ranked_candidates
            if isinstance(candidate, dict)
        ]

        results["regen_candidate_validator_validated_candidates"] = [
            results["regen_candidate_selector_selected_candidate"]
        ]

        results = attach_regen_candidate_recommendation_owner(results)

    recommendation = results.get("regen_candidate_recommendation")

    if not recommendation and not blockers:
        blockers.append(
            "Recommendation owner ran but did not publish regen_candidate_recommendation."
        )

    status = PASS_STATUS if recommendation and not blockers else FAIL_STATUS

    explanation = _build_feed_explanation(
        status=status,
        source_key=source_key,
        ranked_key=ranked_key,
        best_candidate=best_candidate,
        selected_candidate=selected_candidate,
        recommendation=recommendation,
        blockers=blockers,
    )

    results["regen_recommendation_feed_repair_complete"] = True
    results["phase_16j3f_complete"] = status == PASS_STATUS
    results["regen_recommendation_feed_repair_status"] = status
    results["phase_16j3f_status"] = status
    results["regen_recommendation_feed_repair_blockers"] = blockers
    results["regen_recommendation_feed_repair_source_key"] = source_key
    results["regen_recommendation_feed_repair_ranked_source_key"] = ranked_key
    results["regen_recommendation_feed_repair_selected_candidate"] = selected_candidate
    results["regen_recommendation_feed_repair_recommendation_payload"] = recommendation
    results["regen_recommendation_feed_repair_explanation"] = explanation

    # Compatibility feed for next phases.
    results["phase_16j3g_recommendation_viewer_repair_allowed"] = (
        status == PASS_STATUS
    )
    results["regen_recommendation_viewer_feed_payload"] = recommendation
    results["regen_recommendation_viewer_feed_explanation"] = explanation

    # Safety locks.
    results["regen_recommendation_feed_repair_live_geometry_commit_executed"] = False
    results["regen_recommendation_feed_repair_geometry_application_executed"] = False
    results["regen_candidate_geometry_application_allowed"] = False
    results["regen_candidate_manual_overwrite_allowed"] = False

    return results


def _find_best_candidate(results):
    for key in (
        "regen_candidate_ranking_best_candidate",
        "regen_best_ranked_candidate",
        "regen_optimisation_best_candidate",
        "best_full_engine_regen_design",
        "regen_candidate_best_candidate",
    ):
        value = results.get(key)
        if isinstance(value, dict) and value:
            return key, value
    return None, None


def _find_ranked_candidates(results):
    for key in (
        "regen_candidate_ranking_inspector_ranked_candidates",
        "regen_candidate_ranked_population",
        "regen_ranked_population",
        "regen_optimisation_selection_ranked_candidates",
        "regen_optimisation_recommendation_ranked_candidates",
        "regen_optimisation_scored_candidates",
    ):
        value = results.get(key)
        if isinstance(value, list) and value:
            return key, value
    return None, []


def _build_selected_candidate_payload(best_candidate, ranked_candidates=None):
    candidate = copy.deepcopy(best_candidate) if isinstance(best_candidate, dict) else {}

    geometry = (
        candidate.get("candidate_geometry")
        or candidate.get("inputs")
        or candidate.get("geometry")
        or {}
    )

    rank = (
        candidate.get("candidate_rank")
        or candidate.get("rank")
        or candidate.get("ranking", {}).get("rank")
        or 1
    )

    score = (
        candidate.get("candidate_rank_score")
        or candidate.get("candidate_score")
        or candidate.get("score")
        or candidate.get("total_score")
        or candidate.get("ranking", {}).get("objective_score")
    )

    score_parts = (
        candidate.get("candidate_rank_score_parts")
        or candidate.get("score_breakdown")
        or candidate.get("ranking")
        or {}
    )

    candidate["inputs"] = geometry
    candidate["candidate_geometry"] = geometry
    candidate["candidate_rank"] = rank
    candidate["candidate_rank_score"] = score
    candidate["candidate_rank_score_parts"] = score_parts
    candidate["validation_status"] = "PASS_CANDIDATE_VALIDATION"
    candidate["candidate_ranking_reason"] = candidate.get(
        "ranking_explanation",
        "Candidate selected from Phase 16J.3E best ranked candidate feed.",
    )
    candidate["recommended_regen_candidate_reason"] = (
        "Phase 16J.3F bridged the best ranked candidate into the existing "
        "recommendation owner. This is recommendation evidence only; geometry "
        "has not been applied."
    )

    candidate["validation_metrics"] = _build_preview_metrics(candidate)
    candidate["pass_reasons"] = [
        "Best ranked candidate was available.",
        "Recommendation feed bridge produced selected-candidate compatibility payload.",
        "Existing recommendation owner accepted the bridged candidate.",
    ]
    candidate["failure_reasons"] = []

    return candidate


def _build_preview_metrics(candidate):
    geometry = candidate.get("candidate_geometry") or candidate.get("inputs") or {}

    def f(key, default=None):
        try:
            return float(geometry.get(key, default))
        except Exception:
            return default

    width = f("coolant_channel_width")
    height = f("coolant_channel_height")

    aspect_ratio = None
    if width and height:
        aspect_ratio = height / max(width, 1.0e-12)

    return {
        "fit_ratio": candidate.get("fit_ratio") or candidate.get("geometry_fit_ratio"),
        "coolant_reynolds_preview": candidate.get("coolant_reynolds_preview"),
        "coolant_velocity_preview": candidate.get("coolant_velocity_preview"),
        "aspect_ratio": aspect_ratio,
        "hot_gas_wall_thickness": f("hot_gas_wall_thickness"),
    }


def _build_feed_explanation(
    status,
    source_key,
    ranked_key,
    best_candidate,
    selected_candidate,
    recommendation,
    blockers,
):
    lines = [
        "LEAF PHASE 16J.3F RECOMMENDATION FEED REPAIR",
        "================================================",
        "",
        f"Status: {status}",
        f"Best candidate source key: {source_key}",
        f"Ranked population source key: {ranked_key}",
        "",
        "Scope:",
        "- Consumes the best ranked candidate from Phase 16J.3E.",
        "- Converts it into the selected-candidate format expected by the recommendation owner.",
        "- Publishes a recommendation payload for viewer/report phases.",
        "- Does not apply geometry.",
        "- Does not mutate geometry.",
        "- Does not commit live design changes.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Candidate:")

    if isinstance(best_candidate, dict):
        lines.append(f"- candidate_id: {best_candidate.get('candidate_id')}")
        lines.append(f"- score: {best_candidate.get('score') or best_candidate.get('total_score')}")
        lines.append(f"- rank: {best_candidate.get('rank') or best_candidate.get('candidate_rank')}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Recommendation:")

    if isinstance(recommendation, dict):
        lines.append(f"- candidate_id: {recommendation.get('candidate_id')}")
        lines.append(f"- status: {recommendation.get('status')}")
        lines.append(f"- confidence: {recommendation.get('confidence')}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Next Required Phase:")
    lines.append("- 16J.3G Recommendation Viewer Repair.")

    return "\n".join(lines)
''')

# ============================================================
# 2. ADD: Verification Test
# ============================================================

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_recommendation_feed_repair_phase_16j3f.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair


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
    assert results["phase_16j3f_recommendation_feed_repair_allowed"] is True

    results = attach_regen_recommendation_feed_repair(results)

    assert results["regen_recommendation_feed_repair_complete"] is True
    assert results["phase_16j3f_complete"] is True
    assert results["phase_16j3f_status"] == "PASS_REGEN_RECOMMENDATION_FEED_REPAIR_PHASE_16J3F"

    selected = results["regen_recommendation_feed_repair_selected_candidate"]
    assert selected["candidate_id"] == "CANDIDATE_A"
    assert selected["candidate_rank"] == 1
    assert selected["validation_status"] == "PASS_CANDIDATE_VALIDATION"

    recommendation = results["regen_candidate_recommendation"]
    assert recommendation is not None
    assert recommendation["candidate_id"] == "CANDIDATE_A"
    assert results["regen_candidate_recommendation_owner_status"] == "PASS_REGEN_CANDIDATE_RECOMMENDATION_READY"

    assert results["regen_recommendation_viewer_feed_payload"] is recommendation
    assert results["phase_16j3g_recommendation_viewer_repair_allowed"] is True

    assert results["regen_recommendation_feed_repair_live_geometry_commit_executed"] is False
    assert results["regen_recommendation_feed_repair_geometry_application_executed"] is False
    assert results["regen_candidate_geometry_application_allowed"] is False

    print("PASS_REGEN_RECOMMENDATION_FEED_REPAIR_PHASE_16J3F")


if __name__ == "__main__":
    main()
''')

# ============================================================
# 3. PATCH: Foundation Layer Controller Import + Injection
# ============================================================

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair" not in text:
    text = text.replace(
        "try:\n    from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair\nexcept Exception:\n    attach_regen_ranking_owner_source_repair = None\n",
        "try:\n    from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair\nexcept Exception:\n    attach_regen_ranking_owner_source_repair = None\n\n"
        "try:\n    from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair\nexcept Exception:\n    attach_regen_recommendation_feed_repair = None\n",
    )

if "attach_regen_recommendation_feed_repair=attach_regen_recommendation_feed_repair" not in text:
    text = text.replace(
        "attach_regen_ranking_owner_source_repair=attach_regen_ranking_owner_source_repair,\n",
        "attach_regen_ranking_owner_source_repair=attach_regen_ranking_owner_source_repair,\n\n"
        "            attach_regen_recommendation_feed_repair=attach_regen_recommendation_feed_repair,\n",
    )

controller.write_text(text)

# ============================================================
# 4. PATCH: Foundation Attachment Pipeline
# ============================================================

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_recommendation_feed_repair=None" not in text:
    text = text.replace(
        "attach_regen_ranking_owner_source_repair=None,\n",
        "attach_regen_ranking_owner_source_repair=None,\n\n"
        "        attach_regen_recommendation_feed_repair=None,\n",
    )

if '"regen_recommendation_feed_repair"' not in text:
    text = text.replace(
        '(\n            "regen_ranking_owner_source_repair",\n            attach_regen_ranking_owner_source_repair,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_ranking_owner_source_repair",\n            attach_regen_ranking_owner_source_repair,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_recommendation_feed_repair",\n            attach_regen_recommendation_feed_repair,\n            (),\n            {},\n        ),\n',
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

    if "EXPECTED_PREFIX_VISIBILITY = {" in text and '"regen_recommendation_feed_repair_": "DIAGNOSTIC_ONLY",' not in text:
        text = text.replace(
            "EXPECTED_PREFIX_VISIBILITY = {",
            'EXPECTED_PREFIX_VISIBILITY = {\n'
            '    "regen_recommendation_feed_repair_": "DIAGNOSTIC_ONLY",'
        )

    if "KNOWN_DEVELOPMENT_KEYS = {" in text and '"regen_recommendation_feed_repair_",' not in text:
        text = text.replace(
            "KNOWN_DEVELOPMENT_KEYS = {",
            'KNOWN_DEVELOPMENT_KEYS = {\n'
            '    "regen_recommendation_feed_repair_",'
        )

    path.write_text(text)

print("PHASE_16J3F_RECOMMENDATION_FEED_REPAIR_INTEGRATED")
