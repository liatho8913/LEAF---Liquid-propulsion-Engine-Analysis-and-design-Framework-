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
PHASE 11B.3E
Candidate Population Master Gate

Responsibilities:
- Final sign-off for the complete 11B.3 population architecture.
- Verify generation, report, registration, and completion audit readiness.
- Verify safety locks remain active.
- Authorise progression to 11B.4 ranking architecture.
- Do NOT perform ranking.
- Do NOT perform mutation.
- Do NOT solve candidates.
- Do NOT commit live geometry.
"""


OWNER_NAME = "REGEN_CANDIDATE_POPULATION_MASTER_GATE"
PHASE = "11B.3E"

PASS_STATUS = "PASS_REGEN_CANDIDATE_POPULATION_MASTER_GATE_PHASE_11B3E"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_POPULATION_MASTER_GATE_PHASE_11B3E"


def attach_regen_candidate_population_master_gate(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_population_master_gate(results)
    results.update(payload)
    return results


def build_regen_candidate_population_master_gate(results):
    checks = []

    checks.extend(master_gate_phase_checks(results))
    checks.extend(master_gate_population_checks(results))
    checks.extend(master_gate_audit_checks(results))
    checks.extend(master_gate_registration_checks(results))
    checks.extend(master_gate_safety_checks(results))

    failed_checks = [check for check in checks if not check["passed"]]
    ready = len(failed_checks) == 0

    status = PASS_STATUS if ready else FAIL_STATUS

    report = build_master_gate_report(
        status=status,
        ready=ready,
        checks=checks,
        failed_checks=failed_checks,
    )

    return {
        "regen_candidate_population_master_gate_complete": True,
        "phase_11b_3e_regen_candidate_population_master_gate_complete": True,
        "regen_candidate_population_master_gate_ready": ready,
        "regen_candidate_population_master_gate_status": status,
        "regen_candidate_population_master_gate_checks": checks,
        "regen_candidate_population_master_gate_failed_checks": failed_checks,
        "regen_candidate_population_master_gate_report": report,

        # Compatibility aliases.
        "regen_population_master_gate_complete": True,
        "regen_population_master_gate_ready": ready,
        "regen_population_master_gate_status": status,
        "regen_population_master_gate_report": report,

        # This is the only forward permission granted by the master gate.
        # It permits architecture development of ranking, not ranking execution.
        "regen_candidate_ranking_architecture_allowed": ready,
        "phase_11b_4_candidate_ranking_architecture_allowed": ready,

        # Safety locks remain active.
        "regen_candidate_population_master_gate_ranking_executed": False,
        "regen_candidate_population_master_gate_mutation_executed": False,
        "regen_candidate_population_master_gate_solver_executed": False,
        "regen_candidate_population_master_gate_live_commit_executed": False,

        # Explicitly keep these false until future phases implement them.
        "regen_candidate_population_runtime_ranking_allowed": False,
        "regen_candidate_population_runtime_mutation_allowed": False,
        "regen_candidate_population_runtime_solver_allowed": False,
        "regen_candidate_population_runtime_live_commit_allowed": False,
    }


def master_gate_phase_checks(results):
    return [
        _check(
            "phase_11b_3a_generation_owner_complete",
            results.get("phase_11b_3a_regen_candidate_population_generation_owner_complete") is True,
            "11B.3A population generation owner is complete.",
            "11B.3A population generation owner is not complete.",
        ),
        _check(
            "phase_11b_3b_report_owner_complete",
            results.get("phase_11b_3b_regen_candidate_population_report_owner_complete") is True,
            "11B.3B population report owner is complete.",
            "11B.3B population report owner is not complete.",
        ),
        _check(
            "phase_11b_3c_registration_owner_complete",
            results.get("phase_11b_3c_regen_candidate_population_registration_owner_complete") is True,
            "11B.3C population registration owner is complete.",
            "11B.3C population registration owner is not complete.",
        ),
        _check(
            "phase_11b_3d_completion_audit_complete",
            results.get("phase_11b_3d_regen_candidate_population_completion_audit_complete") is True,
            "11B.3D population completion audit is complete.",
            "11B.3D population completion audit is not complete.",
        ),
    ]


def master_gate_population_checks(results):
    population = results.get("regen_candidate_population")
    population_count = results.get("regen_candidate_population_count")
    seed = results.get("regen_candidate_population_seed")

    return [
        _check(
            "population_payload_exists",
            isinstance(population, list) and len(population) > 0,
            "Population payload exists and is non-empty.",
            "Population payload is missing or empty.",
        ),
        _check(
            "population_count_valid",
            isinstance(population, list)
            and int(population_count or 0) == len(population)
            and int(population_count or 0) > 0,
            "Population count is valid.",
            "Population count is invalid.",
        ),
        _check(
            "seed_candidate_exists",
            isinstance(seed, dict) and bool(seed.get("seed_candidate_id")),
            "Seed candidate exists.",
            "Seed candidate is missing.",
        ),
        _check(
            "population_statistics_exists",
            isinstance(results.get("regen_candidate_population_statistics"), dict)
            and bool(results.get("regen_candidate_population_statistics")),
            "Population statistics exist.",
            "Population statistics are missing.",
        ),
    ]


def master_gate_audit_checks(results):
    return [
        _check(
            "completion_audit_ready",
            results.get("regen_candidate_population_completion_audit_ready") is True,
            "Population completion audit is ready.",
            "Population completion audit is not ready.",
        ),
        _check(
            "completion_audit_status_pass",
            results.get("regen_candidate_population_completion_audit_status")
            == "PASS_REGEN_CANDIDATE_POPULATION_COMPLETION_AUDIT_PHASE_11B3D",
            "Population completion audit status is PASS.",
            "Population completion audit status is not PASS.",
        ),
        _check(
            "completion_audit_failed_checks_empty",
            results.get("regen_candidate_population_completion_audit_failed_checks") == [],
            "Population completion audit has no failed checks.",
            "Population completion audit has failed checks.",
        ),
        _check(
            "completion_audit_report_exists",
            isinstance(results.get("regen_candidate_population_completion_audit_report"), str)
            and bool(results.get("regen_candidate_population_completion_audit_report").strip()),
            "Population completion audit report exists.",
            "Population completion audit report is missing.",
        ),
    ]


def master_gate_registration_checks(results):
    report_registry = results.get("regen_candidate_population_report_registry")
    viewer_registry = results.get("regen_candidate_population_viewer_registry")
    export_registry = results.get("regen_candidate_population_export_registry")

    return [
        _check(
            "registration_ready",
            results.get("regen_candidate_population_registration_ready") is True,
            "Population registration is ready.",
            "Population registration is not ready.",
        ),
        _check(
            "report_registry_registered",
            isinstance(report_registry, dict)
            and "regen_candidate_population_report"
            in (report_registry.get("registered_report_keys") or []),
            "Population report is registered in report registry.",
            "Population report is not registered in report registry.",
        ),
        _check(
            "viewer_registry_registered",
            isinstance(viewer_registry, dict)
            and "regen_candidate_population_report"
            in (viewer_registry.get("viewer_report_keys") or []),
            "Population report is registered in viewer registry.",
            "Population report is not registered in viewer registry.",
        ),
        _check(
            "export_registry_registered",
            isinstance(export_registry, dict)
            and "regen_candidate_population_report"
            in (export_registry.get("export_report_keys") or []),
            "Population report is registered in export registry.",
            "Population report is not registered in export registry.",
        ),
    ]


def master_gate_safety_checks(results):
    expected_false_keys = [
        "regen_candidate_population_solver_executed",
        "regen_candidate_population_live_geometry_modified",
        "regen_candidate_population_candidate_committed",
        "regen_candidate_population_ranking_executed",
        "regen_candidate_population_mutation_executed",
        "regen_candidate_population_report_ranking_allowed",
        "regen_candidate_population_report_mutation_allowed",
        "regen_candidate_population_report_solver_allowed",
        "regen_candidate_population_report_live_commit_allowed",
        "regen_candidate_population_registration_ranking_allowed",
        "regen_candidate_population_registration_mutation_allowed",
        "regen_candidate_population_registration_solver_allowed",
        "regen_candidate_population_registration_live_commit_allowed",
        "regen_candidate_population_completion_audit_ranking_allowed",
        "regen_candidate_population_completion_audit_mutation_allowed",
        "regen_candidate_population_completion_audit_solver_allowed",
        "regen_candidate_population_completion_audit_live_commit_allowed",
    ]

    checks = []

    for key in expected_false_keys:
        checks.append(
            _check(
                f"safety_lock_{key}",
                results.get(key) is False,
                f"Safety lock '{key}' is active.",
                f"Safety lock '{key}' is not active.",
            )
        )

    return checks


def build_master_gate_report(status, ready, checks, failed_checks):
    lines = [
        "LEAF PHASE 11B.3E CANDIDATE POPULATION MASTER GATE",
        "==================================================",
        "",
        f"Owner: {OWNER_NAME}",
        f"Phase: {PHASE}",
        f"Status: {status}",
        f"Master gate ready: {ready}",
        f"Total checks: {len(checks)}",
        f"Failed checks: {len(failed_checks)}",
        "",
        "Purpose:",
        "- Final sign-off for the 11B.3 population generation architecture.",
        "- Confirms generation, report ownership, registration, and audit have all passed.",
        "- Allows progression into 11B.4 candidate ranking architecture.",
        "- Does not execute ranking, mutation, candidate solving, or live geometry commit.",
        "",
        "Progression Decision:",
        f"- 11B.4 Candidate Ranking Architecture allowed: {ready}",
        "- Runtime candidate ranking allowed: False",
        "- Runtime mutation allowed: False",
        "- Runtime candidate solving allowed: False",
        "- Runtime live geometry commit allowed: False",
        "",
        "Failed Checks:",
    ]

    if failed_checks:
        for check in failed_checks:
            lines.append(f"- {check['name']}: {check['fail_message']}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Master Gate Checks:",
    ])

    for check in checks:
        label = LegacyCompatibilityProducer.marker_from_bool(check["passed"])
        message = check["pass_message"] if check["passed"] else check["fail_message"]
        lines.append(f"[{label}] {check['name']} — {message}")

    lines.extend([
        "",
        "Completion Meaning:",
        "- 11B.3E completes the population generation architecture foundation.",
        "- 11B.4 may now build candidate ranking architecture on top of this verified stack.",
        "- No ranking has been executed by this gate.",
    ])

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }


# ============================================================
# PHASE 16T.3Q.2 — REGEN CANDIDATE POPULATION MASTER GATE STATUS ADAPTER
# ============================================================

from typing import Any as _LeafAny_16t3q2

from leaf_qt.global_status_classification_engine import (
    classify_status as _leaf_16t3q2_classify_status,
    make_finding as _leaf_16t3q2_make_finding,
)


_REGEN_CANDIDATE_POPULATION_MASTER_GATE_OWNER_16T3Q2 = "Regen Candidate Population Master Gate"


def _leaf_16t3q2_first_present(results: dict, keys: tuple[str, ...]):
    for key in keys:
        if key in results:
            return results.get(key)
    return None


def _leaf_16t3q2_int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _leaf_16t3q2_list_length(value):
    if isinstance(value, (list, tuple)):
        return len(value)
    return None


def _leaf_16t3q2_population_findings(results: dict) -> list[dict[str, _LeafAny_16t3q2]]:
    findings: list[dict[str, _LeafAny_16t3q2]] = []

    population = _leaf_16t3q2_first_present(
        results,
        ("regen_candidate_population", "candidate_population", "regen_candidates", "candidates"),
    )

    candidate_count = _leaf_16t3q2_int_or_none(
        _leaf_16t3q2_first_present(
            results,
            ("regen_candidate_population_count", "candidate_population_count", "candidate_count", "regen_candidate_count"),
        )
    )

    if candidate_count is None:
        candidate_count = _leaf_16t3q2_list_length(population)

    survivor_count = _leaf_16t3q2_int_or_none(
        _leaf_16t3q2_first_present(
            results,
            ("regen_candidate_survivor_count", "candidate_survivor_count", "survivor_count"),
        )
    )

    status_values = {
        key: results.get(key)
        for key in (
            "regen_candidate_population_master_gate_status",
            "regen_candidate_population_status",
            "candidate_population_status",
            "regen_optimisation_population_status",
            "regen_overall_status",
        )
        if key in results
    }

    evidence = {
        "candidate_count": candidate_count,
        "survivor_count": survivor_count,
        "has_population_payload": population is not None,
        "status_values": status_values,
    }

    for key, value in status_values.items():
        text = str(value).upper()

        if "FAIL" in text or "INVALID" in text or "ERROR" in text:
            findings.append(
                _leaf_16t3q2_make_finding(
                    message=f"{key} reports failing candidate-population state: {value}",
                    category="VALIDATION_FAILURE",
                    owner=_REGEN_CANDIDATE_POPULATION_MASTER_GATE_OWNER_16T3Q2,
                    evidence={"key": key, "value": value},
                )
            )
        elif "WARN" in text or "REVIEW" in text or "PLACEHOLDER" in text:
            findings.append(
                _leaf_16t3q2_make_finding(
                    message=f"{key} requires candidate-population review: {value}",
                    category="MANUAL_REVIEW_REQUIRED",
                    owner=_REGEN_CANDIDATE_POPULATION_MASTER_GATE_OWNER_16T3Q2,
                    evidence={"key": key, "value": value},
                )
            )

    if candidate_count is None:
        findings.append(
            _leaf_16t3q2_make_finding(
                message="Candidate population count is missing.",
                category="VALIDATION_INCOMPLETE",
                owner=_REGEN_CANDIDATE_POPULATION_MASTER_GATE_OWNER_16T3Q2,
                evidence=evidence,
            )
        )
    elif candidate_count <= 0:
        findings.append(
            _leaf_16t3q2_make_finding(
                message=f"Candidate population is empty; candidate_count={candidate_count}.",
                category="VALIDATION_FAILURE",
                owner=_REGEN_CANDIDATE_POPULATION_MASTER_GATE_OWNER_16T3Q2,
                evidence=evidence,
            )
        )

    if survivor_count is not None:
        if survivor_count < 0:
            findings.append(
                _leaf_16t3q2_make_finding(
                    message=f"Survivor count cannot be negative; survivor_count={survivor_count}.",
                    category="VALIDATION_FAILURE",
                    owner=_REGEN_CANDIDATE_POPULATION_MASTER_GATE_OWNER_16T3Q2,
                    evidence=evidence,
                )
            )
        elif candidate_count is not None and survivor_count > candidate_count:
            findings.append(
                _leaf_16t3q2_make_finding(
                    message=f"Survivor count exceeds candidate count; survivor_count={survivor_count}, candidate_count={candidate_count}.",
                    category="VALIDATION_FAILURE",
                    owner=_REGEN_CANDIDATE_POPULATION_MASTER_GATE_OWNER_16T3Q2,
                    evidence=evidence,
                )
            )
        elif survivor_count == 0:
            findings.append(
                _leaf_16t3q2_make_finding(
                    message="Candidate population has zero survivors and requires review.",
                    category="MANUAL_REVIEW_REQUIRED",
                    owner=_REGEN_CANDIDATE_POPULATION_MASTER_GATE_OWNER_16T3Q2,
                    evidence=evidence,
                )
            )

    if not findings:
        findings.append(
            _leaf_16t3q2_make_finding(
                message="Regen candidate population master gate status-adapter checks passed.",
                category="COMPLETE",
                owner=_REGEN_CANDIDATE_POPULATION_MASTER_GATE_OWNER_16T3Q2,
                evidence=evidence,
            )
        )

    return findings


def build_regen_candidate_population_master_gate_status_adapter_report(
    results: dict,
    global_status_payload: dict,
) -> str:
    return "\n".join([
        "LEAF PHASE 16T.3Q.2 — REGEN CANDIDATE POPULATION MASTER GATE STATUS ADAPTER",
        "==============================================================================",
        "",
        f"canonical_status: {global_status_payload.get('status')}",
        f"passed: {global_status_payload.get('passed')}",
        f"blocked: {global_status_payload.get('blocked')}",
        f"failed: {global_status_payload.get('failed')}",
        f"finding_count: {global_status_payload.get('finding_count')}",
        "",
        "Rule:",
        "- The existing population master gate still owns candidate generation decisions.",
        "- This adapter classifies whether the resulting candidate pool is usable.",
        "- Empty or invalid populations fail.",
        "- Zero-survivor populations block production sign-off until reviewed.",
        "- Legacy status strings remain available.",
    ])


def attach_regen_candidate_population_master_gate_status_adapter(results):
    if not isinstance(results, dict):
        return results

    findings = _leaf_16t3q2_population_findings(results)

    global_status_payload = _leaf_16t3q2_classify_status(
        findings,
        production_gate=True,
    )

    canonical = global_status_payload.get("status")

    if is_pass(canonical):
        legacy_status = "PASS_REGEN_CANDIDATE_POPULATION_MASTER_GATE_STATUS_ADAPTER"
    elif canonical in {"BLOCKED", "REVIEW_REQUIRED"}:
        legacy_status = "WARN_REGEN_CANDIDATE_POPULATION_MASTER_GATE_STATUS_ADAPTER_REVIEW_REQUIRED"
    else:
        legacy_status = "FAIL_REGEN_CANDIDATE_POPULATION_MASTER_GATE_STATUS_ADAPTER"

    results["regen_candidate_population_master_gate_status_adapter_status"] = legacy_status
    results["regen_candidate_population_master_gate_structured_findings"] = findings
    results["regen_candidate_population_master_gate_global_status"] = canonical
    results["regen_candidate_population_master_gate_global_status_payload"] = global_status_payload
    results["regen_candidate_population_master_gate_status_adapter_report"] = (
        build_regen_candidate_population_master_gate_status_adapter_report(
            results,
            global_status_payload,
        )
    )
    results["phase_16t3q2_status_adapter_complete"] = True

    return results
