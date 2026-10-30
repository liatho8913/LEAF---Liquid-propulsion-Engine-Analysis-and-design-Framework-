"""
LEAF Regen Candidate Recommendation Owner
========================================

PHASE 11B.1E

Publishes the selected regen candidate as a formal recommendation.

This module DOES:
- consume selected candidate payload
- publish recommendation summary
- publish recommendation confidence
- publish recommendation metrics
- publish recommendation report text
- expose recommendation fields for report/viewer/output systems

This module DOES NOT:
- apply geometry
- overwrite manual inputs
- modify the active engine design
"""

import copy


def attach_regen_candidate_recommendation_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_recommendation_owner(results)
    results.update(payload)
    return results


def build_regen_candidate_recommendation_owner(results):
    selected = results.get("regen_candidate_selector_selected_candidate")
    ranked = (
        results.get(
            "regen_candidate_selector_ranked_candidates"
        )
        or []
    )
    validated = [
        candidate
        for candidate in ranked
        if (
            isinstance(
                candidate,
                dict,
            )
            and
            candidate.get(
                "validation_status"
            )
            ==
            "PASS_CANDIDATE_VALIDATION"
        )
    ]

    blocking_reasons = []

    if not selected:
        blocking_reasons.append("No selected regen candidate is available.")

    if selected and selected.get("validation_status") != "PASS_CANDIDATE_VALIDATION":
        blocking_reasons.append("Selected candidate did not pass validation.")

    if selected and selected.get("candidate_rank") != 1:
        blocking_reasons.append("Selected candidate is not rank 1.")

    if blocking_reasons:
        status = "FAIL_REGEN_CANDIDATE_RECOMMENDATION_BLOCKED"
        recommendation = None
    else:
        status = "PASS_REGEN_CANDIDATE_RECOMMENDATION_READY"
        recommendation = build_recommendation_payload(
            selected=selected,
            ranked=ranked,
            validated=validated,
        )

    report = build_recommendation_report(
        status=status,
        recommendation=recommendation,
        blocking_reasons=blocking_reasons,
        ranked=ranked,
        validated=validated,
    )

    return {
        "regen_candidate_recommendation_owner_complete": True,
        "phase_11b_1e_regen_candidate_recommendation_owner_complete": True,
        "regen_candidate_recommendation_owner_status": status,
        "regen_candidate_recommendation_owner_blocking_reasons": blocking_reasons,

        "regen_candidate_recommendation": recommendation,
        "regen_candidate_recommendation_id": (
            recommendation.get("candidate_id") if recommendation else None
        ),
        "regen_candidate_recommendation_inputs": (
            recommendation.get("inputs") if recommendation else None
        ),
        "regen_candidate_recommendation_summary": (
            recommendation.get("summary") if recommendation else None
        ),
        "regen_candidate_recommendation_confidence": (
            recommendation.get("confidence") if recommendation else None
        ),
        "regen_candidate_recommendation_metrics": (
            recommendation.get("metrics") if recommendation else None
        ),
        "regen_candidate_recommendation_risks": (
            recommendation.get("risks") if recommendation else []
        ),
        "regen_candidate_recommendation_benefits": (
            recommendation.get("benefits") if recommendation else []
        ),
        "regen_candidate_recommendation_report": report,

        # Compatibility aliases for output/report/viewer systems.
        "recommended_full_engine_regen_candidate": recommendation,
        "recommended_full_engine_regen_candidate_id": (
            recommendation.get("candidate_id") if recommendation else None
        ),
        "recommended_full_engine_regen_candidate_inputs": (
            recommendation.get("inputs") if recommendation else None
        ),
        "recommended_full_engine_regen_candidate_report": report,

        # Still locked until application owner exists.
        "regen_candidate_recommendation_ready_for_application": bool(recommendation),
        "regen_candidate_geometry_application_allowed": False,
        "regen_candidate_manual_overwrite_allowed": False,
    }


def build_recommendation_payload(selected, ranked, validated):
    selected = copy.deepcopy(selected)

    ranking_score = selected.get("candidate_rank_score")
    score_parts = selected.get("candidate_rank_score_parts") or {}
    inputs = selected.get("inputs") or {}
    metrics = selected.get("validation_metrics") or {}
    preview = selected.get("preview_metrics") or {}

    confidence = estimate_recommendation_confidence(
        selected=selected,
        ranked=ranked,
        validated=validated,
    )

    benefits = build_benefits(selected)
    risks = build_risks(selected)

    return {
        "candidate_id": selected.get("candidate_id"),
        "source": "regen_candidate_recommendation_owner.py",
        "phase": "PHASE_11B_1E",
        "status": "PASS_RECOMMENDED_REGEN_CANDIDATE_READY",
        "summary": build_summary(selected, confidence),
        "selection_reason": selected.get("candidate_ranking_reason"),
        "selector_reason": selected.get("recommended_regen_candidate_reason"),
        "rank": selected.get("candidate_rank"),
        "ranking_score": ranking_score,
        "score_parts": score_parts,
        "confidence": confidence,
        "inputs": inputs,
        "metrics": {
            "fit_ratio": metrics.get("fit_ratio") or preview.get("fit_ratio"),
            "coolant_reynolds": (
                metrics.get("coolant_reynolds_preview")
                or preview.get("coolant_reynolds_preview")
            ),
            "coolant_velocity": (
                metrics.get("coolant_velocity_preview")
                or preview.get("coolant_velocity_preview")
            ),
            "aspect_ratio": metrics.get("aspect_ratio") or preview.get("aspect_ratio"),
            "hot_gas_wall_thickness": (
                metrics.get("hot_gas_wall_thickness")
                or inputs.get("hot_gas_wall_thickness")
            ),
        },
        "benefits": benefits,
        "risks": risks,
        "application_status": "NOT_APPLIED_REQUIRES_APPLICATION_OWNER",
        "geometry_application_allowed": False,
        "manual_overwrite_allowed": False,
        "raw_selected_candidate": selected,
    }


def estimate_recommendation_confidence(selected, ranked, validated):
    ranked_count = len(ranked or [])
    validated_count = len(validated or [])
    failures = selected.get("failure_reasons") or []
    passes = selected.get("pass_reasons") or []
    score = selected.get("candidate_rank_score")

    confidence = 0.5

    if selected.get("validation_status") == "PASS_CANDIDATE_VALIDATION":
        confidence += 0.2

    if selected.get("candidate_rank") == 1:
        confidence += 0.1

    if ranked_count >= 3:
        confidence += 0.05

    if validated_count >= 20:
        confidence += 0.05

    if passes:
        confidence += min(0.05, len(passes) * 0.01)

    if failures:
        confidence -= 0.2

    try:
        if score is not None and float(score) < 25.0:
            confidence += 0.05
    except Exception:
        pass

    return max(0.0, min(1.0, confidence))


def build_summary(selected, confidence):
    return (
        f"Candidate {selected.get('candidate_id')} is the current recommended "
        f"full-engine regen candidate. It passed validation, ranked first among "
        f"passing candidates, and is ready for report/viewer integration. "
        f"Confidence={confidence:.2f}. Geometry has not been applied."
    )


def build_benefits(selected):
    benefits = [
        "Candidate passed the conservative regen candidate validator.",
        "Candidate ranked first among passing regen candidates.",
        "Candidate can be inspected before any geometry is applied.",
    ]

    metrics = selected.get("validation_metrics") or {}
    fit_ratio = metrics.get("fit_ratio")
    reynolds = metrics.get("coolant_reynolds_preview")
    velocity = metrics.get("coolant_velocity_preview")

    if fit_ratio is not None:
        benefits.append(f"Geometry fit ratio available: {fit_ratio}.")

    if reynolds is not None:
        benefits.append(f"Coolant Reynolds preview available: {reynolds}.")

    if velocity is not None:
        benefits.append(f"Coolant velocity preview available: {velocity} m/s.")

    return benefits


def build_risks(selected):
    risks = [
        "Candidate has not yet been applied to the active engine design.",
        "Candidate still requires full application-owner checks before use.",
        "Candidate ranking uses current simplified scoring weights.",
    ]

    score_parts = selected.get("candidate_rank_score_parts") or {}

    for key, value in score_parts.items():
        try:
            if float(value) > 30.0:
                risks.append(f"High ranking penalty from {key}: {value}.")
        except Exception:
            pass

    return risks


def build_recommendation_report(
        status,
        recommendation,
        blocking_reasons,
        ranked,
        validated,
):
    lines = [
        "LEAF PHASE 11B.1E REGEN CANDIDATE RECOMMENDATION OWNER",
        "=======================================================",
        "",
        f"Status: {status}",
        f"Validated candidate count: {len(validated or [])}",
        f"Ranked candidate count: {len(ranked or [])}",
        f"Recommended candidate ID: {recommendation.get('candidate_id') if recommendation else None}",
        "",
        "Scope:",
        "- Publishes selected regen candidate as a formal recommendation.",
        "- Exposes recommendation for reports, output systems, and viewer integration.",
        "- Does not apply geometry.",
        "- Does not overwrite manual inputs.",
        "",
        "Blocking Reasons:",
    ]

    if blocking_reasons:
        for reason in blocking_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None.")

    if recommendation:
        lines.extend([
            "",
            "Recommendation Summary:",
            f"- {recommendation.get('summary')}",
            "",
            "Confidence:",
            f"- {recommendation.get('confidence')}",
            "",
            "Inputs:",
        ])

        for key, value in (recommendation.get("inputs") or {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "Metrics:",
        ])

        for key, value in (recommendation.get("metrics") or {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "Benefits:",
        ])

        for benefit in recommendation.get("benefits") or []:
            lines.append(f"- {benefit}")

        lines.extend([
            "",
            "Risks:",
        ])

        for risk in recommendation.get("risks") or []:
            lines.append(f"- {risk}")

    return "\n".join(lines)