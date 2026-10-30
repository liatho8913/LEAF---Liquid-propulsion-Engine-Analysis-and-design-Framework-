"""
LEAF Regen Candidate Selector
=============================

PHASE 11B.1D

Selects the best ranked regen candidate as the official recommended candidate.

This module DOES:
- inspect ranked passing candidates
- select rank-1 candidate
- produce selection reasons
- expose recommended candidate payload

This module DOES NOT:
- apply geometry
- overwrite user inputs
- modify manual design values
"""

import copy


def attach_regen_candidate_selector(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_selector(results)
    results.update(payload)
    return results


def build_regen_candidate_selector(results):
    modern_ranking_complete = bool(
        results.get(
            "regen_candidate_ranking_owner_complete"
        )
    )

    if modern_ranking_complete:
        source_ranked = (
            results.get(
                "regen_candidate_ranked_population"
            )
            or results.get(
                "regen_ranked_population"
            )
            or []
        )

        ranked = []

        if isinstance(
            source_ranked,
            list,
        ):

            for item in source_ranked:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue


                candidate = copy.deepcopy(
                    item
                )


                geometry = (
                    candidate.get(
                        "candidate_geometry"
                    )
                    or candidate.get(
                        "inputs"
                    )
                    or candidate.get(
                        "geometry"
                    )
                    or {}
                )


                ranking = candidate.get(
                    "ranking",
                    {},
                )

                if not isinstance(
                    ranking,
                    dict,
                ):
                    ranking = {}


                candidate_rank = (
                    candidate.get(
                        "candidate_rank"
                    )
                    or candidate.get(
                        "rank"
                    )
                    or ranking.get(
                        "rank"
                    )
                    or 999999
                )


                qualification_state = str(
                    candidate.get(
                        "regen_qualification_state"
                    )
                    or ""
                ).upper()


                qualification_pass = bool(
                    candidate.get(
                        "regen_qualification_pass"
                    )
                    is True
                    or
                    qualification_state
                    ==
                    "QUALIFIED"
                )


                candidate[
                    "inputs"
                ] = geometry

                candidate[
                    "candidate_geometry"
                ] = geometry

                candidate[
                    "candidate_rank"
                ] = candidate_rank


                candidate[
                    "candidate_rank_score"
                ] = (
                    candidate.get(
                        "candidate_rank_score"
                    )
                    or candidate.get(
                        "candidate_score"
                    )
                    or candidate.get(
                        "score"
                    )
                    or candidate.get(
                        "total_score"
                    )
                    or ranking.get(
                        "objective_score"
                    )
                )


                candidate[
                    "candidate_rank_score_parts"
                ] = (
                    candidate.get(
                        "candidate_rank_score_parts"
                    )
                    or candidate.get(
                        "score_breakdown"
                    )
                    or ranking
                )


                candidate[
                    "validation_status"
                ] = (
                    "PASS_CANDIDATE_VALIDATION"
                    if qualification_pass
                    else
                    "FAIL_CANDIDATE_VALIDATION"
                )


                ranked.append(
                    candidate
                )


    else:

        ranked = (
            results.get(
                "regen_candidate_ranker_ranked_candidates"
            )
            or []
        )

        if not isinstance(
            ranked,
            list,
        ):
            ranked = []


    selected = None

    blocking_reasons = []


    if not ranked:
        blocking_reasons.append(
            "No ranked passing candidates are available."
        )


    ranked_sorted = sorted(
        ranked,
        key=lambda candidate:
            candidate.get(
                "candidate_rank",
                999999,
            ),
    )


    requested_candidate_id = results.get(
        "regen_candidate_selector_requested_candidate_id"
    )

    if requested_candidate_id is not None:
        requested_candidate_id = (
            str(requested_candidate_id).strip()
            or None
        )

    user_selected_candidate = None
    user_selection_blocking_reasons = []

    if requested_candidate_id:
        for candidate in ranked_sorted:
            candidate_id = candidate.get(
                "candidate_id"
            )

            if candidate_id is None:
                continue

            if (
                str(candidate_id).strip()
                != requested_candidate_id
            ):
                continue

            if (
                candidate.get(
                    "validation_status"
                )
                !=
                "PASS_CANDIDATE_VALIDATION"
            ):
                user_selection_blocking_reasons.append(
                    "Requested Generated Design did not pass "
                    "canonical candidate validation."
                )
            else:
                user_selected_candidate = (
                    copy.deepcopy(
                        candidate
                    )
                )

            break

        if (
            user_selected_candidate is None
            and
            not user_selection_blocking_reasons
        ):
            user_selection_blocking_reasons.append(
                "Requested Generated Design is not present in "
                "the canonical qualified ranked population: "
                f"{requested_candidate_id}"
            )

    if user_selected_candidate:
        user_selection_status = (
            "PASS_QUALIFIED_GENERATED_DESIGN_SELECTED"
        )

    elif requested_candidate_id:
        user_selection_status = (
            "FAIL_GENERATED_DESIGN_SELECTION_BLOCKED"
        )

    else:
        user_selection_status = (
            "NO_EXPLICIT_GENERATED_DESIGN_SELECTION"
        )


    if ranked_sorted:

        top = ranked_sorted[
            0
        ]


        if (
            top.get(
                "validation_status"
            )
            !=
            "PASS_CANDIDATE_VALIDATION"
        ):

            blocking_reasons.append(
                "Top ranked candidate did not pass validation."
            )


        elif (
            top.get(
                "candidate_rank"
            )
            !=
            1
        ):

            blocking_reasons.append(
                "No rank-1 candidate was found."
            )


        else:

            selected = copy.deepcopy(
                top
            )


    if selected:

        status = (
            "PASS_RECOMMENDED_CANDIDATE_SELECTED"
        )


    elif blocking_reasons:

        status = (
            "FAIL_RECOMMENDED_CANDIDATE_SELECTION_BLOCKED"
        )


    else:

        status = (
            "FAIL_RECOMMENDED_CANDIDATE_SELECTION_UNKNOWN"
        )


    text = build_regen_candidate_selector_text(
        status=status,
        selected=selected,
        blocking_reasons=blocking_reasons,
        ranked_count=len(
            ranked
        ),
    )


    return {
        "regen_candidate_selector_complete": True,
        "phase_11b_1d_regen_candidate_selector_complete": True,
        "regen_candidate_selector_status": status,
        "regen_candidate_selector_blocking_reasons": blocking_reasons,
        "regen_candidate_selector_ranked_count": len(ranked),
        "regen_candidate_selector_ranked_candidates": ranked,
        "regen_candidate_selector_selected_candidate": selected,
        "regen_candidate_selector_selected_candidate_id": (
            selected.get(
                "candidate_id"
            )
            if selected
            else None
        ),
        "regen_candidate_selector_text": text,

        # Explicit Generated Design selection is independent from
        # the canonical rank-1 recommendation below.
        "regen_candidate_selector_requested_candidate_id": (
            requested_candidate_id
        ),
        "regen_candidate_selector_user_selection_status": (
            user_selection_status
        ),
        "regen_candidate_selector_user_selection_blocking_reasons": (
            user_selection_blocking_reasons
        ),
        "regen_candidate_selector_user_selected_candidate": (
            user_selected_candidate
        ),
        "regen_candidate_selector_user_selected_candidate_id": (
            user_selected_candidate.get(
                "candidate_id"
            )
            if user_selected_candidate
            else None
        ),

        "recommended_regen_candidate": selected,
        "recommended_regen_candidate_id": (
            selected.get(
                "candidate_id"
            )
            if selected
            else None
        ),
        "recommended_regen_candidate_inputs": (
            selected.get(
                "inputs"
            )
            if selected
            else None
        ),
        "recommended_regen_candidate_reason": (
            build_selection_reason(
                selected
            )
            if selected
            else None
        ),

        "regen_candidate_geometry_application_allowed": False,
        "regen_candidate_manual_overwrite_allowed": False,
    }


def build_selection_reason(selected):
    if not selected:
        return None

    return (
        f"Candidate {selected.get('candidate_id')} was selected because it is the "
        f"highest-ranked candidate that passed validation. "
        f"Rank={selected.get('candidate_rank')}; "
        f"score={selected.get('candidate_rank_score')}."
    )


def build_regen_candidate_selector_text(
        status,
        selected,
        blocking_reasons,
        ranked_count,
):
    lines = [
        "LEAF PHASE 11B.1D REGEN CANDIDATE SELECTOR",
        "===========================================",
        "",
        f"Status: {status}",
        f"Ranked candidate count: {ranked_count}",
        f"Selected candidate ID: {selected.get('candidate_id') if selected else None}",
        "",
        "Scope:",
        "- Selects the highest-ranked validated candidate.",
        "- Creates official recommended candidate payload.",
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

    if selected:
        lines.extend([
            "",
            "Selected Candidate:",
            f"- Candidate ID: {selected.get('candidate_id')}",
            f"- Rank: {selected.get('candidate_rank')}",
            f"- Score: {selected.get('candidate_rank_score')}",
            f"- Validation Status: {selected.get('validation_status')}",
            "",
            "Selection Reason:",
            f"- {build_selection_reason(selected)}",
        ])

    return "\n".join(lines)