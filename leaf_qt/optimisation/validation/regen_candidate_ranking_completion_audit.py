from leaf_qt.status_presentation import status_severity
"""
PHASE 11B.4E
Candidate Ranking Completion Audit

Verifies that the ranking stack is complete up to registration.

Does NOT:
- master-gate ranking
- mutate candidates
- evolve generations
- solve candidates
- commit geometry
"""


try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    class LegacyCompatibilityProducer:
        @staticmethod
        def marker_from_bool(value, pass_marker="PASS", fail_marker="FAIL"):
            return pass_marker if bool(value) else fail_marker

        @staticmethod
        def marker_from_status(value):
            severity = status_severity(value)
            if severity in {"PASS", "WARN", "FAIL"}:
                return severity
            return "UNKNOWN"

        @staticmethod
        def status_severity(value):
            return status_severity(value)

OWNER_NAME = "REGEN_CANDIDATE_RANKING_COMPLETION_AUDIT"
PHASE = "11B.4E"

PASS_STATUS = "PASS_REGEN_CANDIDATE_RANKING_COMPLETION_AUDIT_PHASE_11B4E"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_RANKING_COMPLETION_AUDIT_PHASE_11B4E"


def attach_regen_candidate_ranking_completion_audit(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_ranking_completion_audit(results)
    results.update(payload)
    return results


def build_regen_candidate_ranking_completion_audit(results):
    checks = []

    checks.extend(audit_phase_chain(results))
    checks.extend(audit_ranking_outputs(results))
    checks.extend(audit_report_outputs(results))
    checks.extend(audit_registration_outputs(results))
    checks.extend(audit_safety_locks(results))

    failed = [check for check in checks if not check["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = build_completion_report(status, ready, checks, failed, results)

    return {
        "regen_candidate_ranking_completion_audit_complete": True,
        "phase_11b_4e_regen_candidate_ranking_completion_audit_complete": True,
        "regen_candidate_ranking_completion_audit_ready": ready,
        "regen_candidate_ranking_completion_audit_status": status,
        "regen_candidate_ranking_completion_audit_checks": checks,
        "regen_candidate_ranking_completion_audit_failed_checks": failed,
        "regen_candidate_ranking_completion_audit_report": report,

        "regen_ranking_completion_audit_complete": True,
        "regen_ranking_completion_audit_ready": ready,
        "regen_ranking_completion_audit_status": status,
        "regen_ranking_completion_audit_report": report,

        "regen_candidate_ranking_master_gate_allowed": ready,
        "phase_11b_4f_candidate_ranking_master_gate_allowed": ready,

        "regen_candidate_ranking_completion_audit_mutation_executed": False,
        "regen_candidate_ranking_completion_audit_evolution_executed": False,
        "regen_candidate_ranking_completion_audit_solver_executed": False,
        "regen_candidate_ranking_completion_audit_live_commit_executed": False,
        "regen_candidate_ranking_completion_audit_candidate_acceptance_executed": False,

        "regen_candidate_mutation_architecture_allowed": False,
        "regen_candidate_evolution_architecture_allowed": False,
    }


def audit_phase_chain(results):
    return [
        _check(
            "ranking_input_audit_complete",
            results.get("phase_11b_4a_regen_candidate_ranking_input_audit_complete") is True,
            "11B.4A ranking input audit is complete.",
            "11B.4A ranking input audit is missing.",
        ),
        _check(
            "ranking_owner_complete",
            results.get("phase_11b_4b_regen_candidate_ranking_owner_complete") is True,
            "11B.4B ranking owner is complete.",
            "11B.4B ranking owner is missing.",
        ),
        _check(
            "ranking_report_owner_complete",
            results.get("phase_11b_4c_regen_candidate_ranking_report_owner_complete") is True,
            "11B.4C ranking report owner is complete.",
            "11B.4C ranking report owner is missing.",
        ),
        _check(
            "ranking_registration_owner_complete",
            results.get("phase_11b_4d_regen_candidate_ranking_registration_owner_complete") is True,
            "11B.4D ranking registration owner is complete.",
            "11B.4D ranking registration owner is missing.",
        ),
    ]


def audit_ranking_outputs(results):
    ranked = results.get("regen_candidate_ranked_population")
    best = results.get("regen_candidate_best_candidate")
    stats = results.get("regen_candidate_ranking_statistics")

    checks = [
        _check(
            "ranked_population_exists",
            isinstance(ranked, list) and len(ranked) > 0,
            "Ranked population exists.",
            "Ranked population is missing or empty.",
        ),
        _check(
            "best_candidate_exists",
            isinstance(best, dict) and bool(best.get("candidate_id")),
            "Best ranked candidate exists.",
            "Best ranked candidate is missing.",
        ),
        _check(
            "ranking_statistics_exist",
            isinstance(stats, dict) and bool(stats),
            "Ranking statistics exist.",
            "Ranking statistics are missing.",
        ),
        _check(
            "ranking_status_pass",
            results.get("regen_candidate_ranking_status")
            == "PASS_REGEN_CANDIDATE_RANKING_OWNER_PHASE_11B4B",
            "Ranking owner status is PASS.",
            "Ranking owner status is not PASS.",
        ),
    ]

    if isinstance(ranked, list) and ranked:
        ranks = []
        scores = []

        for candidate in ranked:
            ranking = candidate.get("ranking") if isinstance(candidate, dict) else None
            if isinstance(ranking, dict):
                ranks.append(ranking.get("rank"))
                scores.append(ranking.get("objective_score"))

        checks.append(
            _check(
                "rank_values_sequential",
                ranks == list(range(1, len(ranked) + 1)),
                "Rank values are sequential.",
                "Rank values are not sequential.",
            )
        )

        checks.append(
            _check(
                "scores_sorted_descending",
                _scores_sorted_desc(scores),
                "Objective scores are sorted descending.",
                "Objective scores are not sorted descending.",
            )
        )

    return checks


def audit_report_outputs(results):
    bundle = results.get("regen_candidate_ranking_report_bundle")
    export_bundle = results.get("regen_candidate_ranking_export_bundle")
    text = results.get("regen_candidate_ranking_report_text")
    summary = results.get("regen_candidate_ranking_summary")
    explanation = results.get("regen_candidate_ranking_explanation")

    return [
        _check(
            "ranking_report_bundle_exists",
            isinstance(bundle, dict) and bool(bundle),
            "Ranking report bundle exists.",
            "Ranking report bundle is missing.",
        ),
        _check(
            "ranking_report_bundle_ready",
            isinstance(bundle, dict) and bundle.get("ready") is True,
            "Ranking report bundle is ready.",
            "Ranking report bundle is not ready.",
        ),
        _check(
            "ranking_export_bundle_exists",
            isinstance(export_bundle, dict) and bool(export_bundle),
            "Ranking export bundle exists.",
            "Ranking export bundle is missing.",
        ),
        _check(
            "ranking_report_text_exists",
            isinstance(text, str) and bool(text.strip()),
            "Ranking report text exists.",
            "Ranking report text is missing.",
        ),
        _check(
            "ranking_summary_exists",
            isinstance(summary, dict) and bool(summary),
            "Ranking summary exists.",
            "Ranking summary is missing.",
        ),
        _check(
            "ranking_explanation_exists",
            isinstance(explanation, dict) and bool(explanation),
            "Ranking explanation exists.",
            "Ranking explanation is missing.",
        ),
    ]


def audit_registration_outputs(results):
    entry = results.get("regen_candidate_ranking_registry_entry")
    report_registry = results.get("regen_candidate_ranking_report_registry")
    viewer_registry = results.get("regen_candidate_ranking_viewer_registry")
    export_registry = results.get("regen_candidate_ranking_export_registry")
    optimisation_registry = results.get("regen_candidate_ranking_future_optimisation_registry")

    return [
        _check(
            "ranking_registration_ready",
            results.get("regen_candidate_ranking_registration_ready") is True,
            "Ranking registration is ready.",
            "Ranking registration is not ready.",
        ),
        _check(
            "ranking_registry_entry_exists",
            isinstance(entry, dict) and entry.get("registered") is True,
            "Ranking registry entry exists and is registered.",
            "Ranking registry entry is missing or not registered.",
        ),
        _check(
            "ranking_report_registry_contains_key",
            isinstance(report_registry, dict)
            and "regen_candidate_ranking_report"
            in (report_registry.get("registered_report_keys") or []),
            "Ranking report registry contains ranking report key.",
            "Ranking report registry does not contain ranking report key.",
        ),
        _check(
            "ranking_viewer_registry_contains_key",
            isinstance(viewer_registry, dict)
            and "regen_candidate_ranking_report"
            in (viewer_registry.get("viewer_report_keys") or []),
            "Ranking viewer registry contains ranking report key.",
            "Ranking viewer registry does not contain ranking report key.",
        ),
        _check(
            "ranking_export_registry_contains_key",
            isinstance(export_registry, dict)
            and "regen_candidate_ranking_report"
            in (export_registry.get("export_report_keys") or []),
            "Ranking export registry contains ranking report key.",
            "Ranking export registry does not contain ranking report key.",
        ),
        _check(
            "future_optimisation_registry_exists",
            isinstance(optimisation_registry, dict)
            and "ranked_population" in (optimisation_registry.get("optimisation_keys") or []),
            "Future optimisation registry exposes ranked population.",
            "Future optimisation registry does not expose ranked population.",
        ),
    ]


def audit_safety_locks(results):
    expected_false = [
        "regen_candidate_ranking_owner_mutation_executed",
        "regen_candidate_ranking_owner_evolution_executed",
        "regen_candidate_ranking_owner_solver_executed",
        "regen_candidate_ranking_owner_live_commit_executed",
        "regen_candidate_ranking_owner_candidate_acceptance_executed",
        "regen_candidate_ranking_report_owner_mutation_executed",
        "regen_candidate_ranking_report_owner_evolution_executed",
        "regen_candidate_ranking_report_owner_solver_executed",
        "regen_candidate_ranking_report_owner_live_commit_executed",
        "regen_candidate_ranking_report_owner_candidate_acceptance_executed",
        "regen_candidate_ranking_registration_mutation_executed",
        "regen_candidate_ranking_registration_evolution_executed",
        "regen_candidate_ranking_registration_solver_executed",
        "regen_candidate_ranking_registration_live_commit_executed",
        "regen_candidate_ranking_registration_candidate_acceptance_executed",
        "regen_candidate_mutation_architecture_allowed",
        "regen_candidate_evolution_architecture_allowed",
    ]

    return [
        _check(
            f"safety_lock_{key}",
            results.get(key) is False,
            f"Safety lock '{key}' is active.",
            f"Safety lock '{key}' is not active.",
        )
        for key in expected_false
    ]


def build_completion_report(status, ready, checks, failed, results):
    lines = [
        "LEAF PHASE 11B.4E CANDIDATE RANKING COMPLETION AUDIT",
        "=====================================================",
        "",
        f"Owner: {OWNER_NAME}",
        f"Phase: {PHASE}",
        f"Status: {status}",
        f"Audit ready: {ready}",
        f"Total checks: {len(checks)}",
        f"Failed checks: {len(failed)}",
        "",
        "Purpose:",
        "- Proves ranking architecture is complete up to registration.",
        "- Verifies ranked population, best candidate, report bundle, export bundle, and registries.",
        "- Does not master-gate ranking.",
        "- Does not permit mutation or evolution.",
        "",
        "Summary:",
        f"- Ranked population count: {results.get('regen_candidate_ranked_population_count')}",
        f"- Best candidate id: {(results.get('regen_candidate_best_candidate') or {}).get('candidate_id') if isinstance(results.get('regen_candidate_best_candidate'), dict) else None}",
        f"- Ranking status: {results.get('regen_candidate_ranking_status')}",
        f"- Registration status: {results.get('regen_candidate_ranking_registration_status')}",
        "",
        "Failed Checks:",
    ]

    if failed:
        for check in failed:
            lines.append(f"- {check['name']}: {check['fail_message']}")
    else:
        lines.append("- None.")

    lines.extend(["", "Audit Checks:"])

    for check in checks:
        label = LegacyCompatibilityProducer.marker_from_bool(check["passed"])
        message = check["pass_message"] if check["passed"] else check["fail_message"]
        lines.append(f"[{label}] {check['name']} — {message}")

    lines.extend([
        "",
        "Completion Meaning:",
        "- 11B.4E proves the ranking stack is complete up to registration.",
        "- 11B.4F must still master-gate ranking.",
        "- Mutation and evolution remain forbidden.",
    ])

    return "\n".join(lines)


def _scores_sorted_desc(scores):
    try:
        cleaned = [float(score) for score in scores]
    except Exception:
        return False

    return cleaned == sorted(cleaned, reverse=True)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
