OWNER_NAME = "REGEN_CANDIDATE_COMPARISON_METRICS_OWNER"
PHASE = "15B"

PASS_STATUS = "PASS_REGEN_CANDIDATE_COMPARISON_METRICS_OWNER_PHASE_15B"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_COMPARISON_METRICS_OWNER_PHASE_15B"


def attach_regen_candidate_comparison_metrics_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_candidate_comparison_best_owner_ready") is not True:
        blockers.append("Candidate comparison best owner is not ready.")

    baseline = results.get("candidate_comparison_baseline")
    current = results.get("candidate_comparison_current")
    best = results.get("candidate_comparison_best")

    if not isinstance(baseline, dict) or not baseline:
        blockers.append("Baseline candidate is missing.")

    if not isinstance(current, dict) or not current:
        blockers.append("Current candidate is missing.")

    if not isinstance(best, dict) or not best:
        blockers.append("Best candidate is missing.")

    deltas = {}
    improvements = {}

    if not blockers:
        deltas = {
            "current_vs_baseline": _delta(current, baseline),
            "best_vs_baseline": _delta(best, baseline),
            "best_vs_current": _delta(best, current),
        }

        improvements = {
            "current_improves_over_baseline": deltas["current_vs_baseline"]["score_delta"] > 0.0,
            "best_improves_over_baseline": deltas["best_vs_baseline"]["score_delta"] > 0.0,
            "best_improves_over_current": deltas["best_vs_current"]["score_delta"] > 0.0,
        }

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    summary = {
        "baseline_id": baseline.get("runtime_candidate_id") if isinstance(baseline, dict) else None,
        "current_id": current.get("runtime_candidate_id") if isinstance(current, dict) else None,
        "best_id": best.get("runtime_candidate_id") if isinstance(best, dict) else None,
        "best_score": _score(best) if isinstance(best, dict) else None,
        "current_score": _score(current) if isinstance(current, dict) else None,
        "baseline_score": _score(baseline) if isinstance(baseline, dict) else None,
    } if ready else {}

    results.update({
        "regen_candidate_comparison_metrics_owner_complete": True,
        "phase_15b_candidate_comparison_metrics_owner_complete": True,
        "regen_candidate_comparison_metrics_owner_ready": ready,
        "regen_candidate_comparison_metrics_owner_status": status,
        "regen_candidate_comparison_metrics_owner_blockers": blockers,

        "candidate_comparison_deltas": deltas if ready else {},
        "candidate_comparison_improvements": improvements if ready else {},
        "candidate_comparison_summary": summary,
    })

    return results


def _score(candidate):
    try:
        return float(candidate.get("score", 0.0))
    except Exception:
        return 0.0


def _delta(left, right):
    left_score = _score(left)
    right_score = _score(right)

    return {
        "left_id": left.get("runtime_candidate_id"),
        "right_id": right.get("runtime_candidate_id"),
        "left_score": left_score,
        "right_score": right_score,
        "score_delta": left_score - right_score,
        "rank_delta": _rank(left) - _rank(right),
    }


def _rank(candidate):
    try:
        return int(candidate.get("rank", 0) or 0)
    except Exception:
        return 0
