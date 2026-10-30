"""
LEAF Regen Optimisation Failure Owner
=====================================

REGEN PHASE 8D

Owns failure explanations for regen optimisation.

This module explains:
- why candidate generation was blocked
- why candidate scoring was blocked
- why candidates are not yet selectable
- what corrective action is recommended

It does NOT:
- score candidates
- rank candidates
- select geometry
- apply geometry
- approve recommendations
- replace validation gates
"""


def attach_regen_optimisation_failure_owner(results):
    if not isinstance(results, dict):
        return results

    failure = build_regen_optimisation_failure_owner(results)
    results.update(failure)
    return results


def build_regen_optimisation_failure_owner(results):
    results = results if isinstance(results, dict) else {}

    generation_blocking = _normalise_reasons(
        results.get("regen_optimisation_candidate_generator_blocking_reasons", [])
    )

    scoring_blocking = _normalise_reasons(
        results.get("regen_optimisation_scoring_blocking_reasons", [])
    )

    profile_blocking = _normalise_reasons(
        results.get("regen_optimisation_profile_blocking_reasons", [])
    )

    scored_candidates = results.get("regen_optimisation_scored_candidates", [])
    if not isinstance(scored_candidates, list):
        scored_candidates = []

    failure_items = []

    failure_items.extend(
        _build_failure_items(
            source="profile",
            phase="8A",
            reasons=profile_blocking,
        )
    )

    failure_items.extend(
        _build_failure_items(
            source="candidate_generator",
            phase="8B",
            reasons=generation_blocking,
        )
    )

    failure_items.extend(
        _build_failure_items(
            source="scoring_owner",
            phase="8C",
            reasons=scoring_blocking,
        )
    )

    if scored_candidates:
        failure_items.extend(
            _build_candidate_selection_lock_items(scored_candidates)
        )

    if not failure_items:
        failure_items.append({
            "failure_id": "REGEN-OPT-8D-INFO-0001",
            "severity": "INFO",
            "source": "regen_optimisation_failure_owner",
            "phase": "8D",
            "reason": "No active optimisation failures were detected.",
            "root_cause": "Previous optimisation foundation stages are structurally complete and currently not reporting blocking reasons.",
            "recommended_action": "Continue to Phase 8E report ownership before introducing any master gate or automatic selection.",
            "blocks_recommendation": False,
            "blocks_selection": True,
            "blocks_geometry_application": True,
        })

    blocking_failure_count = sum(
        1 for item in failure_items
        if item.get("blocks_recommendation")
    )

    selection_locked = True
    geometry_application_locked = True
    recommendation_approval_locked = True

    status = "PASS_REGEN_OPTIMISATION_FAILURE_OWNER"

    text = build_regen_optimisation_failure_text(
        status=status,
        failure_items=failure_items,
        blocking_failure_count=blocking_failure_count,
        selection_locked=selection_locked,
        geometry_application_locked=geometry_application_locked,
        recommendation_approval_locked=recommendation_approval_locked,
    )

    return {
        "regen_optimisation_failure_owner_status": status,
        "regen_optimisation_failure_owner_complete": True,
        "regen_optimisation_failure_items": failure_items,
        "regen_optimisation_failure_count": len(failure_items),
        "regen_optimisation_blocking_failure_count": blocking_failure_count,
        "regen_optimisation_failure_selection_locked": selection_locked,
        "regen_optimisation_failure_geometry_application_locked": geometry_application_locked,
        "regen_optimisation_failure_recommendation_approval_locked": recommendation_approval_locked,
        "regen_optimisation_failure_text": text,
        "phase_8d_regen_optimisation_failure_owner_complete": True,
    }


def build_regen_optimisation_failure_text(
        status,
        failure_items,
        blocking_failure_count,
        selection_locked,
        geometry_application_locked,
        recommendation_approval_locked,
):
    lines = [
        "LEAF REGEN PHASE 8D OPTIMISATION FAILURE OWNER",
        "================================================",
        "",
        f"Status: {status}",
        f"Failure item count: {len(failure_items)}",
        f"Blocking failure count: {blocking_failure_count}",
        "",
        "Owned By:",
        "- regen_optimisation_failure_owner.py",
        "",
        "Scope:",
        "- Owns optimisation failure explanations.",
        "- Owns blocking reason translation.",
        "- Owns corrective action text.",
        "- Owns selection/application locks.",
        "- Does not score candidates.",
        "- Does not rank candidates.",
        "- Does not select geometry.",
        "- Does not apply geometry.",
        "- Does not approve recommendations.",
        "",
        "Phase Locks:",
        f"- Selection locked: {selection_locked}",
        f"- Geometry application locked: {geometry_application_locked}",
        f"- Recommendation approval locked: {recommendation_approval_locked}",
        "",
        "Failure Items:",
    ]

    for item in failure_items:
        lines.append("")
        lines.append(f"- Failure ID: {item.get('failure_id')}")
        lines.append(f"  Severity: {item.get('severity')}")
        lines.append(f"  Source: {item.get('source')}")
        lines.append(f"  Phase: {item.get('phase')}")
        lines.append(f"  Reason: {item.get('reason')}")
        lines.append(f"  Root Cause: {item.get('root_cause')}")
        lines.append(f"  Recommended Action: {item.get('recommended_action')}")
        lines.append(f"  Blocks Recommendation: {item.get('blocks_recommendation')}")
        lines.append(f"  Blocks Selection: {item.get('blocks_selection')}")
        lines.append(f"  Blocks Geometry Application: {item.get('blocks_geometry_application')}")

    lines.append("")
    lines.append("Next Required Action:")
    lines.append(
        "- After Phase 8D is verified, build Phase 8E report ownership before introducing any master gate."
    )

    return "\n".join(lines)


def _build_failure_items(source, phase, reasons):
    items = []

    for index, reason in enumerate(reasons, start=1):
        failure_id = f"REGEN-OPT-{phase}-FAIL-{index:04d}"

        items.append({
            "failure_id": failure_id,
            "severity": _severity_for_reason(reason),
            "source": source,
            "phase": phase,
            "reason": reason,
            "root_cause": _root_cause_for_reason(reason),
            "recommended_action": _recommended_action_for_reason(reason),
            "blocks_recommendation": True,
            "blocks_selection": True,
            "blocks_geometry_application": True,
        })

    return items


def _build_candidate_selection_lock_items(scored_candidates):
    items = []

    for index, candidate in enumerate(scored_candidates, start=1):
        if not isinstance(candidate, dict):
            continue

        candidate_id = candidate.get("candidate_id", f"UNKNOWN-{index:04d}")

        if candidate.get("selection_allowed") is True:
            continue

        items.append({
            "failure_id": f"REGEN-OPT-8D-LOCK-{index:04d}",
            "severity": "INFO",
            "source": "scored_candidate_selection_lock",
            "phase": "8D",
            "candidate_id": candidate_id,
            "reason": f"Candidate {candidate_id} is scored but not selectable in Phase 8D.",
            "root_cause": "Candidate scoring evidence exists, but report ownership, master gate approval, and recommendation ownership have not yet been implemented.",
            "recommended_action": "Continue to Phase 8E report ownership, then build later gate/recommendation stages before selection is permitted.",
            "blocks_recommendation": False,
            "blocks_selection": True,
            "blocks_geometry_application": True,
        })

    return items


def _severity_for_reason(reason):
    text = str(reason).lower()

    if "automatic" in text or "apply" in text or "selection" in text:
        return "BLOCKED_BY_PHASE_LOCK"

    if "not complete" in text or "missing" in text:
        return "BLOCKED_BY_DEPENDENCY"

    if "disabled" in text:
        return "BLOCKED_BY_CONFIGURATION"

    if "no generated candidates" in text:
        return "BLOCKED_BY_MISSING_CANDIDATES"

    return "BLOCKED"


def _root_cause_for_reason(reason):
    text = str(reason).lower()

    if "phase 8a" in text:
        return "The optimisation profile foundation must complete before downstream optimisation systems are trusted."

    if "phase 8b" in text:
        return "The candidate generator foundation must complete before candidate scoring can be trusted."

    if "phase 8c" in text:
        return "The scoring owner must exist before scored recommendation evidence can be trusted."

    if "disabled" in text:
        return "The relevant optimisation stage is intentionally disabled by default to prevent accidental automatic optimisation."

    if "automatic" in text or "selection" in text:
        return "Automatic selection is intentionally locked until later report, failure, master gate, and recommendation owners exist."

    if "apply" in text or "application" in text:
        return "Geometry application is intentionally locked until recommendation approval and master gate ownership exist."

    if "no generated candidates" in text:
        return "No candidate set is available for scoring or recommendation."

    return "The optimisation pipeline reported a blocking condition that must be resolved before progression."


def _recommended_action_for_reason(reason):
    text = str(reason).lower()

    if "phase 8a" in text:
        return "Complete and verify Phase 8A before enabling candidate generation."

    if "phase 8b" in text:
        return "Complete and verify Phase 8B before enabling scoring."

    if "phase 8c" in text:
        return "Complete and verify Phase 8C before building reports or recommendations."

    if "disabled" in text:
        return "Enable the relevant stage only when deliberately testing that stage."

    if "automatic" in text or "selection" in text:
        return "Keep automatic selection disabled until the optimisation master gate and recommendation approval stages are complete."

    if "apply" in text or "application" in text:
        return "Keep geometry application disabled until recommendation approval and application safety checks are implemented."

    if "no generated candidates" in text:
        return "Enable Phase 8B candidate generation and confirm generated candidates exist before scoring."

    return "Inspect the upstream optimisation stage and resolve the blocking condition."


def _normalise_reasons(value):
    if value is None:
        return []

    if isinstance(value, str):
        value = value.strip()
        return [value] if value else []

    if isinstance(value, (list, tuple, set)):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    return [str(value).strip()] if str(value).strip() else []