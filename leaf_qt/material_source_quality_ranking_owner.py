"""
LEAF Material Source Quality Ranking Owner
==========================================

REGEN PHASE 9C

Owns source quality ranking for material provenance records.

This module does NOT:
- approve material validation
- replace solver constants
- override material interpolation
"""

SOURCE_TYPE_BASE_SCORES = {
    "manufacturer_datasheet": 1.00,
    "peer_reviewed_paper": 0.95,
    "standards_handbook": 0.90,
    "agency_report": 0.85,
    "textbook": 0.75,
    "engineering_database": 0.70,
    "internal_test_data": 0.65,
    "unknown": 0.30,
    "engineering_placeholder": 0.10,
}


def attach_material_source_quality_ranking_owner(results):
    if not isinstance(results, dict):
        return results

    ranking = build_material_source_quality_ranking_owner(results)
    results.update(ranking)
    return results


def build_material_source_quality_ranking_owner(results):
    results = results if isinstance(results, dict) else {}

    material_name = results.get(
        "material_source_provenance_material",
        results.get("selected_material", "GRCop-42"),
    )

    sources = results.get("material_source_provenance_sources", [])
    if not isinstance(sources, list):
        sources = []

    provenance_complete = bool(
        results.get("phase_9b_material_source_provenance_owner_complete", False)
    )

    ranked_sources = rank_material_sources(sources)

    top_source = ranked_sources[0] if ranked_sources else None

    placeholder_count = sum(
        1 for source in ranked_sources
        if source.get("is_placeholder") is True
    )

    average_rank_score = (
        round(sum(source["source_rank_score"] for source in ranked_sources) / len(ranked_sources), 6)
        if ranked_sources
        else 0.0
    )

    blockers = []

    if not provenance_complete:
        blockers.append(
            "Phase 9B material source/provenance owner is not complete."
        )

    if not ranked_sources:
        blockers.append(
            "No material sources are available for ranking."
        )

    conservative_pass_allowed = (
        provenance_complete
        and bool(ranked_sources)
        and placeholder_count == 0
        and average_rank_score >= 0.75
        and top_source is not None
        and top_source.get("source_rank_score", 0.0) >= 0.75
    )

    complete = not blockers

    status = (
        "PASS_MATERIAL_SOURCE_QUALITY_RANKING_OWNER"
        if complete
        else "FAIL_MATERIAL_SOURCE_QUALITY_RANKING_OWNER"
    )

    text = build_material_source_quality_ranking_text(
        status=status,
        material_name=material_name,
        provenance_complete=provenance_complete,
        ranked_sources=ranked_sources,
        top_source=top_source,
        placeholder_count=placeholder_count,
        average_rank_score=average_rank_score,
        conservative_pass_allowed=conservative_pass_allowed,
        blockers=blockers,
    )

    return {
        "material_source_quality_ranking_owner_status": status,
        "material_source_quality_ranking_owner_complete": complete,
        "material_source_quality_ranking_material": material_name,
        "material_source_quality_ranking_provenance_complete": provenance_complete,
        "material_source_quality_ranking_sources": ranked_sources,
        "material_source_quality_ranking_source_count": len(ranked_sources),
        "material_source_quality_ranking_top_source": top_source,
        "material_source_quality_ranking_placeholder_count": placeholder_count,
        "material_source_quality_ranking_average_score": average_rank_score,
        "material_source_quality_ranking_blockers": blockers,
        "material_source_quality_ranking_conservative_pass_allowed": conservative_pass_allowed,
        "material_source_quality_ranking_text": text,
        "phase_9c_material_source_quality_ranking_owner_complete": complete,
    }


def rank_material_sources(sources):
    ranked = []

    if not isinstance(sources, list):
        return ranked

    for source in sources:
        if not isinstance(source, dict):
            continue

        source_type = str(source.get("source_type", "unknown")).strip().lower()
        confidence = _clamp01(source.get("confidence", 0.0))
        is_placeholder = _bool_value(source.get("is_placeholder"), default=False)

        base_score = SOURCE_TYPE_BASE_SCORES.get(source_type, SOURCE_TYPE_BASE_SCORES["unknown"])

        property_coverage = source.get("properties_covered", [])
        if isinstance(property_coverage, (list, tuple, set)):
            coverage_score = min(len(property_coverage) / 4.0, 1.0)
        else:
            coverage_score = 0.0

        placeholder_penalty = 0.75 if is_placeholder else 0.0

        rank_score = (
            0.45 * base_score
            + 0.35 * confidence
            + 0.20 * coverage_score
            - placeholder_penalty
        )

        rank_score = round(max(0.0, min(1.0, rank_score)), 6)

        ranked_source = dict(source)
        ranked_source.update({
            "source_rank_score": rank_score,
            "source_rank_basis": {
                "base_source_type_score": base_score,
                "confidence_score": confidence,
                "coverage_score": coverage_score,
                "placeholder_penalty": placeholder_penalty,
            },
            "source_quality_rank_owner": "material_source_quality_ranking_owner.py",
        })

        ranked.append(ranked_source)

    ranked.sort(
        key=lambda item: (
            item.get("source_rank_score", 0.0),
            item.get("confidence", 0.0),
            str(item.get("source_id", "")),
        ),
        reverse=True,
    )

    for index, source in enumerate(ranked, start=1):
        source["source_quality_rank"] = index

    return ranked


def build_material_source_quality_ranking_text(
        status,
        material_name,
        provenance_complete,
        ranked_sources,
        top_source,
        placeholder_count,
        average_rank_score,
        conservative_pass_allowed,
        blockers,
):
    lines = [
        "LEAF REGEN PHASE 9C MATERIAL SOURCE QUALITY RANKING OWNER",
        "==========================================================",
        "",
        f"Status: {status}",
        f"Material: {material_name}",
        f"Provenance complete: {provenance_complete}",
        f"Ranked source count: {len(ranked_sources)}",
        f"Placeholder source count: {placeholder_count}",
        f"Average rank score: {average_rank_score}",
        f"Conservative pass allowed: {conservative_pass_allowed}",
        "",
        "Owned By:",
        "- material_source_quality_ranking_owner.py",
        "",
        "Scope:",
        "- Owns material source quality ranking.",
        "- Owns source-type weighting.",
        "- Owns placeholder penalties.",
        "- Owns ranking evidence.",
        "- Does not approve material validation by itself.",
        "",
        "Top Source:",
    ]

    if top_source:
        lines.append(f"- Source ID: {top_source.get('source_id')}")
        lines.append(f"- Rank Score: {top_source.get('source_rank_score')}")
        lines.append(f"- Source Type: {top_source.get('source_type')}")
        lines.append(f"- Confidence: {top_source.get('confidence')}")
        lines.append(f"- Placeholder: {top_source.get('is_placeholder')}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Ranked Sources:")

    if ranked_sources:
        for source in ranked_sources:
            lines.append(
                f"- rank={source.get('source_quality_rank')}, "
                f"id={source.get('source_id')}, "
                f"score={source.get('source_rank_score')}, "
                f"type={source.get('source_type')}, "
                f"placeholder={source.get('is_placeholder')}"
            )
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Blockers:")

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Next Required Action:")
    lines.append(
        "- After Phase 9C is verified, build Phase 9D material validation owner."
    )

    return "\n".join(lines)


def _clamp01(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0

    return max(0.0, min(1.0, value))


def _bool_value(value, default=False):
    if value is None:
        return bool(default)

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value_l = value.strip().lower()
        if value_l in {"true", "1", "yes", "y", "enabled", "on"}:
            return True
        if value_l in {"false", "0", "no", "n", "disabled", "off"}:
            return False

    return bool(value)