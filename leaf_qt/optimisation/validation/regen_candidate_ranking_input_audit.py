from leaf_qt.status_presentation import status_severity
"""
PHASE 11B.4A
Candidate Ranking Input Audit

Responsibilities:
- Verify that candidate ranking inputs are available and trustworthy.
- Confirm population architecture is master-gated.
- Confirm candidate geometry is present.
- Confirm objective/weight metadata exists where available.
- Prepare ranking architecture readiness.
- Do NOT rank candidates.
- Do NOT score candidates.
- Do NOT mutate candidates.
- Do NOT solve candidates.
- Do NOT commit live geometry.
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

OWNER_NAME = "REGEN_CANDIDATE_RANKING_INPUT_AUDIT"
PHASE = "11B.4A"

PASS_STATUS = "PASS_REGEN_CANDIDATE_RANKING_INPUT_AUDIT_PHASE_11B4A"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_RANKING_INPUT_AUDIT_PHASE_11B4A"


REQUIRED_GEOMETRY_KEYS = [
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
    "coolant_flow_fraction",
]


def attach_regen_candidate_ranking_input_audit(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_ranking_input_audit(results)
    results.update(payload)
    return results


def build_regen_candidate_ranking_input_audit(results):
    checks = []

    checks.extend(audit_population_master_gate(results))
    checks.extend(audit_population_candidates(results))
    checks.extend(audit_ranking_safety_locks(results))

    failed_checks = [check for check in checks if not check["passed"]]
    ready = len(failed_checks) == 0

    status = PASS_STATUS if ready else FAIL_STATUS

    report = build_ranking_input_audit_report(
        status=status,
        ready=ready,
        checks=checks,
        failed_checks=failed_checks,
        results=results,
    )

    return {
        "regen_candidate_ranking_input_audit_complete": True,
        "phase_11b_4a_regen_candidate_ranking_input_audit_complete": True,
        "regen_candidate_ranking_input_audit_ready": ready,
        "regen_candidate_ranking_input_audit_status": status,
        "regen_candidate_ranking_input_audit_checks": checks,
        "regen_candidate_ranking_input_audit_failed_checks": failed_checks,
        "regen_candidate_ranking_input_audit_report": report,

        # Compatibility aliases.
        "regen_ranking_input_audit_complete": True,
        "regen_ranking_input_audit_ready": ready,
        "regen_ranking_input_audit_status": status,
        "regen_ranking_input_audit_report": report,

        # Authorises development of the ranking owner only.
        "regen_candidate_ranking_owner_architecture_allowed": ready,
        "phase_11b_4b_candidate_ranking_owner_allowed": ready,

        # Explicit safety state: audit does not execute ranking.
        "regen_candidate_ranking_input_audit_ranking_executed": False,
        "regen_candidate_ranking_input_audit_scoring_executed": False,
        "regen_candidate_ranking_input_audit_mutation_executed": False,
        "regen_candidate_ranking_input_audit_solver_executed": False,
        "regen_candidate_ranking_input_audit_live_commit_executed": False,

        # Runtime permissions remain locked until later phases.
        "regen_candidate_runtime_ranking_allowed": False,
        "regen_candidate_runtime_scoring_allowed": False,
        "regen_candidate_runtime_mutation_allowed": False,
        "regen_candidate_runtime_solver_allowed": False,
        "regen_candidate_runtime_live_commit_allowed": False,
    }


def audit_population_master_gate(results):
    return [
        _check(
            "population_master_gate_complete",
            results.get("phase_11b_3e_regen_candidate_population_master_gate_complete") is True,
            "Population master gate phase 11B.3E is complete.",
            "Population master gate phase 11B.3E is not complete.",
        ),
        _check(
            "population_master_gate_ready",
            results.get("regen_candidate_population_master_gate_ready") is True,
            "Population master gate is ready.",
            "Population master gate is not ready.",
        ),
        _check(
            "population_master_gate_status_pass",
            results.get("regen_candidate_population_master_gate_status")
            == "PASS_REGEN_CANDIDATE_POPULATION_MASTER_GATE_PHASE_11B3E",
            "Population master gate status is PASS.",
            "Population master gate status is not PASS.",
        ),
        _check(
            "ranking_architecture_allowed_by_population_gate",
            results.get("phase_11b_4_candidate_ranking_architecture_allowed") is True,
            "Population master gate allows 11B.4 ranking architecture development.",
            "Population master gate does not allow ranking architecture development.",
        ),
    ]


def audit_population_candidates(results):
    checks = []

    population = results.get("regen_candidate_population")
    ids = results.get("regen_candidate_population_ids")
    count = results.get("regen_candidate_population_count")

    checks.append(
        _check(
            "population_payload_valid",
            isinstance(population, list) and len(population) > 0,
            "Population payload is present and non-empty.",
            "Population payload is missing or empty.",
        )
    )

    if not isinstance(population, list):
        return checks

    checks.append(
        _check(
            "population_count_matches",
            int(count or 0) == len(population),
            "Population count matches candidate list.",
            "Population count does not match candidate list.",
        )
    )

    checks.append(
        _check(
            "population_ids_valid",
            isinstance(ids, list)
            and len(ids) == len(population)
            and all(candidate.get("candidate_id") in ids for candidate in population if isinstance(candidate, dict)),
            "Population candidate IDs are valid.",
            "Population candidate IDs are invalid.",
        )
    )

    candidate_ids = []

    for index, candidate in enumerate(population):
        checks.extend(audit_candidate_for_ranking(candidate, index))
        if isinstance(candidate, dict):
            candidate_ids.append(candidate.get("candidate_id"))

    checks.append(
        _check(
            "candidate_ids_unique",
            len(candidate_ids) == len(set(candidate_ids)),
            "Candidate IDs are unique.",
            "Candidate IDs contain duplicates.",
        )
    )

    return checks


def audit_candidate_for_ranking(candidate, index):
    checks = []
    prefix = f"ranking_input_candidate_{index + 1:03d}"

    checks.append(
        _check(
            f"{prefix}_is_dict",
            isinstance(candidate, dict),
            f"Candidate {index + 1} is a dictionary.",
            f"Candidate {index + 1} is not a dictionary.",
        )
    )

    if not isinstance(candidate, dict):
        return checks

    checks.append(
        _check(
            f"{prefix}_has_id",
            bool(candidate.get("candidate_id")),
            f"Candidate {index + 1} has an id.",
            f"Candidate {index + 1} is missing an id.",
        )
    )

    checks.append(
        _check(
            f"{prefix}_not_previously_ranked",
            candidate.get("candidate_status") == "GENERATED_NOT_SOLVED_NOT_RANKED",
            f"Candidate {index + 1} has not been ranked or solved.",
            f"Candidate {index + 1} has unexpected status.",
        )
    )

    geometry = candidate.get("candidate_geometry")

    checks.append(
        _check(
            f"{prefix}_geometry_exists",
            isinstance(geometry, dict),
            f"Candidate {index + 1} has geometry.",
            f"Candidate {index + 1} has no valid geometry.",
        )
    )

    if isinstance(geometry, dict):
        for key in REQUIRED_GEOMETRY_KEYS:
            checks.append(
                _check(
                    f"{prefix}_geometry_has_{key}",
                    key in geometry,
                    f"Candidate {index + 1} geometry has '{key}'.",
                    f"Candidate {index + 1} geometry is missing '{key}'.",
                )
            )
            checks.append(
                _check(
                    f"{prefix}_geometry_positive_{key}",
                    _positive_number(geometry.get(key)),
                    f"Candidate {index + 1} geometry '{key}' is positive.",
                    f"Candidate {index + 1} geometry '{key}' is not positive.",
                )
            )

    metadata = candidate.get("candidate_metadata") or {}

    checks.append(
        _check(
            f"{prefix}_metadata_ranking_locked",
            metadata.get("ranking_allowed") is False,
            f"Candidate {index + 1} ranking lock is active.",
            f"Candidate {index + 1} ranking lock is not active.",
        )
    )

    checks.append(
        _check(
            f"{prefix}_metadata_mutation_locked",
            metadata.get("mutation_allowed") is False,
            f"Candidate {index + 1} mutation lock is active.",
            f"Candidate {index + 1} mutation lock is not active.",
        )
    )

    return checks


def audit_ranking_safety_locks(results):
    expected_false_keys = [
        "regen_candidate_population_runtime_ranking_allowed",
        "regen_candidate_population_runtime_mutation_allowed",
        "regen_candidate_population_runtime_solver_allowed",
        "regen_candidate_population_runtime_live_commit_allowed",
        "regen_candidate_population_master_gate_ranking_executed",
        "regen_candidate_population_master_gate_mutation_executed",
        "regen_candidate_population_master_gate_solver_executed",
        "regen_candidate_population_master_gate_live_commit_executed",
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


def build_ranking_input_audit_report(status, ready, checks, failed_checks, results):
    lines = [
        "LEAF PHASE 11B.4A CANDIDATE RANKING INPUT AUDIT",
        "================================================",
        "",
        f"Owner: {OWNER_NAME}",
        f"Phase: {PHASE}",
        f"Status: {status}",
        f"Ranking input audit ready: {ready}",
        f"Total checks: {len(checks)}",
        f"Failed checks: {len(failed_checks)}",
        "",
        "Purpose:",
        "- Verifies that candidate ranking has valid inputs.",
        "- Confirms population architecture has passed its master gate.",
        "- Confirms candidates have ids, geometry, and safety locks.",
        "- Does not perform ranking, scoring, mutation, solving, or live commit.",
        "",
        "Input Summary:",
        f"- Population count: {results.get('regen_candidate_population_count')}",
        f"- Population master gate status: {results.get('regen_candidate_population_master_gate_status')}",
        f"- Ranking architecture allowed by population gate: {results.get('phase_11b_4_candidate_ranking_architecture_allowed')}",
        "",
        "Forward Permission:",
        f"- 11B.4B Ranking Owner architecture allowed: {ready}",
        "- Runtime ranking allowed: False",
        "- Runtime scoring allowed: False",
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
        "Audit Checks:",
    ])

    for check in checks:
        label = LegacyCompatibilityProducer.marker_from_bool(check["passed"])
        message = check["pass_message"] if check["passed"] else check["fail_message"]
        lines.append(f"[{label}] {check['name']} — {message}")

    lines.extend([
        "",
        "Completion Meaning:",
        "- 11B.4A proves candidate ranking inputs are ready.",
        "- 11B.4B may create the ranking owner after this passes.",
        "- Ranking has not been executed by this phase.",
    ])

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }


def _positive_number(value):
    try:
        return float(value) > 0.0
    except Exception:
        return False
