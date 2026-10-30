from leaf_qt.status_presentation import status_severity
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

from leaf_qt.structured_status_access import findings_highest_severity, highest_severity as gate_highest_severity, is_pass
"""
PHASE 11B.4F
Candidate Ranking Master Gate

Final sign-off authority for the full candidate ranking architecture.

Verifies:
- 11B.4A Ranking Input Audit
- 11B.4B Ranking Owner
- 11B.4C Ranking Report Owner
- 11B.4D Ranking Registration Owner
- 11B.4E Ranking Completion Audit

Does NOT:
- mutate candidates
- evolve generations
- solve candidates
- commit geometry
- accept candidates
"""


OWNER_NAME = "REGEN_CANDIDATE_RANKING_MASTER_GATE"
PHASE = "11B.4F"

PASS_STATUS = "PASS_REGEN_CANDIDATE_RANKING_MASTER_GATE_PHASE_11B4F"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_RANKING_MASTER_GATE_PHASE_11B4F"


PHASE_16T3Q3_STATUS_ADAPTER_COMPLETE = True
PHASE_16T3Q3_STATUS_ADAPTER_STATUS = "PASS_REGEN_CANDIDATE_RANKING_STATUS_ADAPTER_PHASE_16T3Q3"


def _leaf_16t3q3_make_finding(code, severity, message, evidence=None):
    return {
        "code": str(code),
        "severity": str(severity).upper(),
        "message": str(message),
        "evidence": evidence or {},
        "phase": "16T.3Q.3",
        "owner": OWNER_NAME,
    }


def _leaf_16t3q3_canonical_status_from_findings(findings, ready):
    severities = {str(f.get("severity", "")).upper() for f in findings}

    if gate_highest_severity(severities) == "FAIL":
        return "FAIL"

    if "BLOCKED" in severities:
        return "BLOCKED"

    if "REVIEW_REQUIRED" in severities:
        return "REVIEW_REQUIRED"

    if ready is True:
        return "PASS"

    return "FAIL"


def _leaf_16t3q3_classify_ranking_findings(results, checks, failed, ready, status):
    findings = []

    ranked = results.get("regen_candidate_ranked_population")
    best = results.get("regen_candidate_best_candidate")
    stats = results.get("regen_candidate_ranking_statistics")
    report_bundle = results.get("regen_candidate_ranking_report_bundle")

    if not isinstance(ranked, list) or len(ranked) == 0:
        findings.append(
            _leaf_16t3q3_make_finding(
                "RANKED_POPULATION_EMPTY",
                "FAIL",
                "Ranked candidate population is missing or empty.",
                {"ranked_population_type": type(ranked).__name__},
            )
        )
    else:
        findings.append(
            _leaf_16t3q3_make_finding(
                "RANKED_POPULATION_PRESENT",
                "INFO",
                "Ranked candidate population is present.",
                {"ranked_population_count": len(ranked)},
            )
        )

    invalid_scores = []
    for index, candidate in enumerate(ranked if isinstance(ranked, list) else []):
        score = candidate.get("score") if isinstance(candidate, dict) else None
        try:
            score_value = float(score)
        except Exception:
            invalid_scores.append({"index": index, "score": score})
            continue

        if score_value < 0:
            invalid_scores.append({"index": index, "score": score})

    if invalid_scores:
        findings.append(
            _leaf_16t3q3_make_finding(
                "INVALID_RANKING_SCORE",
                "FAIL",
                "One or more ranked candidates have invalid ranking scores.",
                {"invalid_scores": invalid_scores[:10]},
            )
        )

    winner_like = []
    if isinstance(ranked, list):
        for index, candidate in enumerate(ranked):
            if not isinstance(candidate, dict):
                continue
            if (
                candidate.get("winner") is True
                or candidate.get("selected") is True
                or candidate.get("is_winner") is True
                or candidate.get("is_selected") is True
            ):
                winner_like.append(index)

    if not isinstance(best, dict) or not best.get("candidate_id"):
        findings.append(
            _leaf_16t3q3_make_finding(
                "BEST_CANDIDATE_MISSING",
                "FAIL",
                "Best ranked candidate is missing.",
                {"best_candidate_type": type(best).__name__},
            )
        )

    if len(winner_like) > 1:
        findings.append(
            _leaf_16t3q3_make_finding(
                "DUPLICATE_WINNER_CANDIDATES",
                "FAIL",
                "More than one candidate is marked as winner or selected.",
                {"winner_indexes": winner_like},
            )
        )

    if isinstance(stats, dict) and stats:
        findings.append(
            _leaf_16t3q3_make_finding(
                "RANKING_STATISTICS_PRESENT",
                "INFO",
                "Ranking statistics payload is present.",
                {"statistics_keys": sorted(stats.keys())[:20]},
            )
        )
    else:
        findings.append(
            _leaf_16t3q3_make_finding(
                "RANKING_STATISTICS_MISSING",
                "REVIEW_REQUIRED",
                "Ranking statistics payload is missing.",
                {},
            )
        )

    if not isinstance(report_bundle, dict) or report_bundle.get("ready") is not True:
        findings.append(
            _leaf_16t3q3_make_finding(
                "RANKING_REPORT_BUNDLE_NOT_READY",
                "FAIL",
                "Ranking report bundle is missing or not ready.",
                {"report_bundle_type": type(report_bundle).__name__},
            )
        )

    for check in failed:
        findings.append(
            _leaf_16t3q3_make_finding(
                f"FAILED_CHECK_{check.get('name', 'UNKNOWN')}",
                "FAIL",
                check.get("fail_message", "Ranking master gate check failed."),
                {"check": check},
            )
        )

    if ready is True and findings_highest_severity(findings) == "INFO":
        findings.append(
            _leaf_16t3q3_make_finding(
                "RANKING_MASTER_GATE_READY",
                "INFO",
                "Candidate ranking master gate is ready.",
                {"legacy_status": status},
            )
        )

    return findings


def _leaf_16t3q3_build_global_status_payload(status, legacy_status, findings, ready):
    severity_counts = {}
    for finding in findings:
        severity = str(finding.get("severity", "UNKNOWN")).upper()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    return {
        "owner": OWNER_NAME,
        "phase": "16T.3Q.3",
        "canonical_status": status,
        "global_status": status,
        "legacy_status": legacy_status,
        "ready": bool(ready),
        "finding_count": len(findings),
        "severity_counts": severity_counts,
        "findings": findings,
        "adapter": "wave_2_status_adapter",
        "adapter_phase": "16T.3Q.3",
    }


def _leaf_16t3q3_build_adapter_report(global_status, legacy_status, findings):
    lines = [
        "LEAF PHASE 16T.3Q.3 STATUS ADAPTER",
        "====================================",
        "",
        f"Owner: {OWNER_NAME}",
        "Target: Regen Candidate Ranking Master Gate",
        f"Canonical Status: {global_status}",
        f"Legacy Status: {legacy_status}",
        f"Structured Findings: {len(findings)}",
        "",
        "Findings:",
    ]

    if findings:
        for finding in findings:
            lines.append(
                f"- [{finding.get('severity')}] {finding.get('code')}: {finding.get('message')}"
            )
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "Compatibility:",
            "- Existing PASS/FAIL status strings are preserved.",
            "- Existing public payload fields are preserved.",
            "- Structured findings are additive only.",
        ]
    )

    return "\n".join(lines)


def _leaf_16t3q3_apply_status_adapter(results, checks, failed, ready, legacy_status):
    findings = _leaf_16t3q3_classify_ranking_findings(
        results=results,
        checks=checks,
        failed=failed,
        ready=ready,
        status=legacy_status,
    )

    global_status = _leaf_16t3q3_canonical_status_from_findings(findings, ready)

    payload = _leaf_16t3q3_build_global_status_payload(
        status=global_status,
        legacy_status=legacy_status,
        findings=findings,
        ready=ready,
    )

    report = _leaf_16t3q3_build_adapter_report(
        global_status=global_status,
        legacy_status=legacy_status,
        findings=findings,
    )

    return findings, global_status, payload, report



def attach_regen_candidate_ranking_master_gate(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_ranking_master_gate(results)
    results.update(payload)
    return results


def build_regen_candidate_ranking_master_gate(results):
    checks = []

    checks.extend(master_gate_phase_checks(results))
    checks.extend(master_gate_ranking_output_checks(results))
    checks.extend(master_gate_report_registration_checks(results))
    checks.extend(master_gate_completion_audit_checks(results))
    checks.extend(master_gate_safety_checks(results))

    failed = [check for check in checks if not check["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = build_master_gate_report(
        status=status,
        ready=ready,
        checks=checks,
        failed=failed,
        results=results,
    )

    structured_findings, global_status, global_status_payload, adapter_report = (
        _leaf_16t3q3_apply_status_adapter(
            results=results,
            checks=checks,
            failed=failed,
            ready=ready,
            legacy_status=status,
        )
    )

    return {
        "regen_candidate_ranking_master_gate_complete": True,
        "phase_11b_4f_regen_candidate_ranking_master_gate_complete": True,
        "regen_candidate_ranking_master_gate_ready": ready,
        "regen_candidate_ranking_master_gate_status": status,
        "regen_candidate_ranking_master_gate_checks": checks,
        "regen_candidate_ranking_master_gate_failed_checks": failed,
        "regen_candidate_ranking_master_gate_report": report,

        # Phase 16T.3Q.3 Wave 2 Status Adapter payload.
        "phase_16t3q3_status_adapter_complete": True,
        "phase_16t3q3_regen_candidate_ranking_status_adapter_complete": True,
        "regen_candidate_ranking_status_adapter_complete": True,
        "regen_candidate_ranking_status_adapter_status": PHASE_16T3Q3_STATUS_ADAPTER_STATUS,
        "regen_candidate_ranking_master_gate_structured_findings": structured_findings,
        "regen_candidate_ranking_master_gate_global_status": global_status,
        "regen_candidate_ranking_master_gate_global_status_payload": global_status_payload,
        "regen_candidate_ranking_master_gate_adapter_report": adapter_report,
        "regen_candidate_ranking_master_gate_legacy_status": status,
        "structured_findings": structured_findings,
        "global_status": global_status,
        "global_status_payload": global_status_payload,
        "adapter_report": adapter_report,

        # Architecture completion aliases.
        "regen_candidate_ranking_architecture_complete": ready,
        "phase_11b_4_candidate_ranking_architecture_complete": ready,
        "regen_ranking_master_gate_complete": True,
        "regen_ranking_master_gate_ready": ready,
        "regen_ranking_master_gate_status": status,
        "regen_ranking_master_gate_report": report,

        # This authorises beginning mutation architecture only.
        # It does not allow runtime mutation execution yet.
        "regen_candidate_mutation_architecture_allowed": ready,
        "phase_11b_5_candidate_mutation_architecture_allowed": ready,

        # Runtime safety remains locked.
        "regen_candidate_runtime_mutation_allowed": False,
        "regen_candidate_runtime_evolution_allowed": False,
        "regen_candidate_runtime_solver_allowed": False,
        "regen_candidate_runtime_live_commit_allowed": False,
        "regen_candidate_runtime_acceptance_allowed": False,

        # Explicit no-execution flags.
        "regen_candidate_ranking_master_gate_mutation_executed": False,
        "regen_candidate_ranking_master_gate_evolution_executed": False,
        "regen_candidate_ranking_master_gate_solver_executed": False,
        "regen_candidate_ranking_master_gate_live_commit_executed": False,
        "regen_candidate_ranking_master_gate_candidate_acceptance_executed": False,
    }


def master_gate_phase_checks(results):
    return [
        _check(
            "phase_11b_4a_ranking_input_audit_complete",
            results.get("phase_11b_4a_regen_candidate_ranking_input_audit_complete") is True,
            "11B.4A ranking input audit is complete.",
            "11B.4A ranking input audit is missing.",
        ),
        _check(
            "phase_11b_4b_ranking_owner_complete",
            results.get("phase_11b_4b_regen_candidate_ranking_owner_complete") is True,
            "11B.4B ranking owner is complete.",
            "11B.4B ranking owner is missing.",
        ),
        _check(
            "phase_11b_4c_ranking_report_owner_complete",
            results.get("phase_11b_4c_regen_candidate_ranking_report_owner_complete") is True,
            "11B.4C ranking report owner is complete.",
            "11B.4C ranking report owner is missing.",
        ),
        _check(
            "phase_11b_4d_ranking_registration_owner_complete",
            results.get("phase_11b_4d_regen_candidate_ranking_registration_owner_complete") is True,
            "11B.4D ranking registration owner is complete.",
            "11B.4D ranking registration owner is missing.",
        ),
        _check(
            "phase_11b_4e_ranking_completion_audit_complete",
            results.get("phase_11b_4e_regen_candidate_ranking_completion_audit_complete") is True,
            "11B.4E ranking completion audit is complete.",
            "11B.4E ranking completion audit is missing.",
        ),
    ]


def master_gate_ranking_output_checks(results):
    ranked = results.get("regen_candidate_ranked_population")
    best = results.get("regen_candidate_best_candidate")
    stats = results.get("regen_candidate_ranking_statistics")

    return [
        _check(
            "ranked_population_exists",
            isinstance(ranked, list) and len(ranked) > 0,
            "Ranked population exists.",
            "Ranked population is missing or empty.",
        ),
        _check(
            "ranked_population_count_valid",
            isinstance(ranked, list)
            and int(results.get("regen_candidate_ranked_population_count") or 0) == len(ranked)
            and len(ranked) > 0,
            "Ranked population count is valid.",
            "Ranked population count is invalid.",
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


def master_gate_report_registration_checks(results):
    report_bundle = results.get("regen_candidate_ranking_report_bundle")
    export_bundle = results.get("regen_candidate_ranking_export_bundle")
    registry_entry = results.get("regen_candidate_ranking_registry_entry")
    report_registry = results.get("regen_candidate_ranking_report_registry")
    viewer_registry = results.get("regen_candidate_ranking_viewer_registry")
    export_registry = results.get("regen_candidate_ranking_export_registry")

    return [
        _check(
            "ranking_report_bundle_exists",
            isinstance(report_bundle, dict) and report_bundle.get("ready") is True,
            "Ranking report bundle exists and is ready.",
            "Ranking report bundle is missing or not ready.",
        ),
        _check(
            "ranking_export_bundle_exists",
            isinstance(export_bundle, dict) and bool(export_bundle),
            "Ranking export bundle exists.",
            "Ranking export bundle is missing.",
        ),
        _check(
            "ranking_registry_entry_registered",
            isinstance(registry_entry, dict) and registry_entry.get("registered") is True,
            "Ranking registry entry is registered.",
            "Ranking registry entry is missing or not registered.",
        ),
        _check(
            "ranking_report_registry_contains_key",
            isinstance(report_registry, dict)
            and "regen_candidate_ranking_report" in (report_registry.get("registered_report_keys") or []),
            "Ranking report registry contains ranking report key.",
            "Ranking report registry does not contain ranking report key.",
        ),
        _check(
            "ranking_viewer_registry_contains_key",
            isinstance(viewer_registry, dict)
            and "regen_candidate_ranking_report" in (viewer_registry.get("viewer_report_keys") or []),
            "Ranking viewer registry contains ranking report key.",
            "Ranking viewer registry does not contain ranking report key.",
        ),
        _check(
            "ranking_export_registry_contains_key",
            isinstance(export_registry, dict)
            and "regen_candidate_ranking_report" in (export_registry.get("export_report_keys") or []),
            "Ranking export registry contains ranking report key.",
            "Ranking export registry does not contain ranking report key.",
        ),
    ]


def master_gate_completion_audit_checks(results):
    return [
        _check(
            "completion_audit_ready",
            results.get("regen_candidate_ranking_completion_audit_ready") is True,
            "Ranking completion audit is ready.",
            "Ranking completion audit is not ready.",
        ),
        _check(
            "completion_audit_status_pass",
            results.get("regen_candidate_ranking_completion_audit_status")
            == "PASS_REGEN_CANDIDATE_RANKING_COMPLETION_AUDIT_PHASE_11B4E",
            "Ranking completion audit status is PASS.",
            "Ranking completion audit status is not PASS.",
        ),
        _check(
            "completion_audit_failed_checks_empty",
            results.get("regen_candidate_ranking_completion_audit_failed_checks") == [],
            "Ranking completion audit has no failed checks.",
            "Ranking completion audit has failed checks.",
        ),
        _check(
            "completion_audit_report_exists",
            isinstance(results.get("regen_candidate_ranking_completion_audit_report"), str)
            and bool(results.get("regen_candidate_ranking_completion_audit_report").strip()),
            "Ranking completion audit report exists.",
            "Ranking completion audit report is missing.",
        ),
    ]


def master_gate_safety_checks(results):
    expected_false = [
        "regen_candidate_ranking_completion_audit_mutation_executed",
        "regen_candidate_ranking_completion_audit_evolution_executed",
        "regen_candidate_ranking_completion_audit_solver_executed",
        "regen_candidate_ranking_completion_audit_live_commit_executed",
        "regen_candidate_ranking_completion_audit_candidate_acceptance_executed",
        "regen_candidate_runtime_mutation_allowed",
        "regen_candidate_runtime_evolution_allowed",
        "regen_candidate_runtime_solver_allowed",
        "regen_candidate_runtime_live_commit_allowed",
        "regen_candidate_runtime_acceptance_allowed",
    ]

    return [
        _check(
            f"safety_lock_{key}",
            results.get(key, False) is False,
            f"Safety lock '{key}' is active.",
            f"Safety lock '{key}' is not active.",
        )
        for key in expected_false
    ]


def build_master_gate_report(status, ready, checks, failed, results):
    lines = [
        "LEAF PHASE 11B.4F CANDIDATE RANKING MASTER GATE",
        "================================================",
        "",
        f"Owner: {OWNER_NAME}",
        f"Phase: {PHASE}",
        f"Status: {status}",
        f"Master gate ready: {ready}",
        f"Total checks: {len(checks)}",
        f"Failed checks: {len(failed)}",
        "",
        "Purpose:",
        "- Final sign-off for the full candidate ranking architecture.",
        "- Confirms ranking input audit, ranking owner, report owner, registration owner, and completion audit.",
        "- Allows progression into mutation architecture.",
        "- Does not execute mutation, evolution, solving, geometry commit, or candidate acceptance.",
        "",
        "Architecture Completion:",
        f"- Ranking architecture complete: {ready}",
        f"- Mutation architecture may begin: {ready}",
        "- Runtime mutation allowed: False",
        "- Runtime evolution allowed: False",
        "- Runtime solver allowed: False",
        "- Runtime live commit allowed: False",
        "- Runtime candidate acceptance allowed: False",
        "",
        "Summary:",
        f"- Ranked population count: {results.get('regen_candidate_ranked_population_count')}",
        f"- Best candidate id: {(results.get('regen_candidate_best_candidate') or {}).get('candidate_id') if isinstance(results.get('regen_candidate_best_candidate'), dict) else None}",
        f"- Ranking status: {results.get('regen_candidate_ranking_status')}",
        f"- Completion audit status: {results.get('regen_candidate_ranking_completion_audit_status')}",
        "",
        "Failed Checks:",
    ]

    if failed:
        for check in failed:
            lines.append(f"- {check['name']}: {check['fail_message']}")
    else:
        lines.append("- None.")

    lines.extend(["", "Master Gate Checks:"])

    for check in checks:
        label = LegacyCompatibilityProducer.marker_from_bool(check["passed"])
        message = check["pass_message"] if check["passed"] else check["fail_message"]
        lines.append(f"[{label}] {check['name']} — {message}")

    lines.extend([
        "",
        "Completion Meaning:",
        "- 11B.4F formally completes the Candidate Ranking Architecture.",
        "- 11B.5 Mutation Engine Architecture may now begin.",
        "- No mutation has been executed by this gate.",
    ])

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
