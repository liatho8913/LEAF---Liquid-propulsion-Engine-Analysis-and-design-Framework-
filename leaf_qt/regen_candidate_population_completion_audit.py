from leaf_qt.status_presentation import status_severity
"""
PHASE 11B.3D
Candidate Population Completion Audit

Responsibilities:
- Audit the complete 11B.3 population architecture.
- Verify generation, report, and registration ownership.
- Verify population payload validity.
- Verify report/viewer/export registration.
- Verify safety locks.
- Do NOT rank candidates.
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

OWNER_NAME = "REGEN_CANDIDATE_POPULATION_COMPLETION_AUDIT"
PHASE = "11B.3D"

PASS_STATUS = "PASS_REGEN_CANDIDATE_POPULATION_COMPLETION_AUDIT_PHASE_11B3D"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_POPULATION_COMPLETION_AUDIT_PHASE_11B3D"


REQUIRED_CANDIDATE_KEYS = [
    "candidate_id",
    "candidate_generation",
    "candidate_parent",
    "candidate_geometry",
    "candidate_status",
    "candidate_metadata",
]

REQUIRED_GEOMETRY_KEYS = [
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
    "coolant_flow_fraction",
]


def attach_regen_candidate_population_completion_audit(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_population_completion_audit(results)
    results.update(payload)
    return results


def build_regen_candidate_population_completion_audit(results):
    checks = []

    checks.extend(audit_required_owners(results))
    checks.extend(audit_population_payload(results))
    checks.extend(audit_population_statistics(results))
    checks.extend(audit_report_bundle(results))
    checks.extend(audit_registration(results))
    checks.extend(audit_safety_locks(results))

    failed_checks = [check for check in checks if not check["passed"]]
    passed = len(failed_checks) == 0

    status = PASS_STATUS if passed else FAIL_STATUS

    audit_report = build_completion_audit_report(
        status=status,
        passed=passed,
        checks=checks,
        failed_checks=failed_checks,
    )

    return {
        "regen_candidate_population_completion_audit_complete": True,
        "phase_11b_3d_regen_candidate_population_completion_audit_complete": True,
        "regen_candidate_population_completion_audit_ready": passed,
        "regen_candidate_population_completion_audit_status": status,
        "regen_candidate_population_completion_audit_checks": checks,
        "regen_candidate_population_completion_audit_failed_checks": failed_checks,
        "regen_candidate_population_completion_audit_report": audit_report,

        # Compatibility aliases.
        "regen_population_completion_audit_complete": True,
        "regen_population_completion_audit_ready": passed,
        "regen_population_completion_audit_status": status,
        "regen_population_completion_audit_report": audit_report,

        # Safety locks remain active until 11B.4+.
        "regen_candidate_population_completion_audit_ranking_allowed": False,
        "regen_candidate_population_completion_audit_mutation_allowed": False,
        "regen_candidate_population_completion_audit_solver_allowed": False,
        "regen_candidate_population_completion_audit_live_commit_allowed": False,
    }


def audit_required_owners(results):
    return [
        _check(
            "generation_owner_complete",
            bool(results.get("phase_11b_3a_regen_candidate_population_generation_owner_complete")),
            "Phase 11B.3A population generation owner is complete.",
            "Phase 11B.3A population generation owner is missing.",
        ),
        _check(
            "report_owner_complete",
            bool(results.get("phase_11b_3b_regen_candidate_population_report_owner_complete")),
            "Phase 11B.3B population report owner is complete.",
            "Phase 11B.3B population report owner is missing.",
        ),
        _check(
            "registration_owner_complete",
            bool(results.get("phase_11b_3c_regen_candidate_population_registration_owner_complete")),
            "Phase 11B.3C population registration owner is complete.",
            "Phase 11B.3C population registration owner is missing.",
        ),
    ]


def audit_population_payload(results):
    checks = []

    population = results.get("regen_candidate_population")
    population_count = results.get("regen_candidate_population_count")
    population_ids = results.get("regen_candidate_population_ids")

    checks.append(
        _check(
            "population_is_list",
            isinstance(population, list),
            "Population payload is a list.",
            "Population payload is missing or not a list.",
        )
    )

    if not isinstance(population, list):
        return checks

    checks.append(
        _check(
            "population_count_positive",
            len(population) > 0,
            "Population contains at least one candidate.",
            "Population is empty.",
        )
    )

    checks.append(
        _check(
            "population_count_matches_payload",
            int(population_count or 0) == len(population),
            "Population count matches payload length.",
            "Population count does not match payload length.",
        )
    )

    checks.append(
        _check(
            "population_ids_match_payload",
            isinstance(population_ids, list)
            and len(population_ids) == len(population)
            and all(candidate.get("candidate_id") in population_ids for candidate in population if isinstance(candidate, dict)),
            "Population IDs match candidate payload.",
            "Population IDs are missing or inconsistent with candidate payload.",
        )
    )

    candidate_ids = []

    for index, candidate in enumerate(population):
        checks.extend(audit_single_candidate(candidate, index))
        if isinstance(candidate, dict):
            candidate_ids.append(candidate.get("candidate_id"))

    checks.append(
        _check(
            "population_candidate_ids_unique",
            len(candidate_ids) == len(set(candidate_ids)),
            "Population candidate IDs are unique.",
            "Population candidate IDs contain duplicates.",
        )
    )

    return checks


def audit_single_candidate(candidate, index):
    checks = []

    prefix = f"candidate_{index + 1:03d}"

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

    for key in REQUIRED_CANDIDATE_KEYS:
        checks.append(
            _check(
                f"{prefix}_has_{key}",
                key in candidate,
                f"Candidate {index + 1} has key '{key}'.",
                f"Candidate {index + 1} is missing key '{key}'.",
            )
        )

    geometry = candidate.get("candidate_geometry")

    checks.append(
        _check(
            f"{prefix}_geometry_is_dict",
            isinstance(geometry, dict),
            f"Candidate {index + 1} geometry is a dictionary.",
            f"Candidate {index + 1} geometry is missing or invalid.",
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
            f"{prefix}_not_ranked",
            candidate.get("candidate_status") == "GENERATED_NOT_SOLVED_NOT_RANKED",
            f"Candidate {index + 1} is generated but not solved/ranked.",
            f"Candidate {index + 1} has an unexpected status.",
        )
    )

    checks.append(
        _check(
            f"{prefix}_metadata_phase",
            metadata.get("phase") == "11B.3A",
            f"Candidate {index + 1} preserves generation phase metadata.",
            f"Candidate {index + 1} does not preserve generation phase metadata.",
        )
    )

    checks.append(
        _check(
            f"{prefix}_metadata_solver_locked",
            metadata.get("solver_executed") is False,
            f"Candidate {index + 1} solver execution lock is active.",
            f"Candidate {index + 1} solver execution lock is not active.",
        )
    )

    return checks


def audit_population_statistics(results):
    statistics = results.get("regen_candidate_population_statistics")

    checks = [
        _check(
            "population_statistics_is_dict",
            isinstance(statistics, dict),
            "Population statistics payload is a dictionary.",
            "Population statistics payload is missing or invalid.",
        )
    ]

    if not isinstance(statistics, dict):
        return checks

    checks.append(
        _check(
            "population_statistics_size_matches",
            int(statistics.get("population_size") or 0)
            == int(results.get("regen_candidate_population_count") or 0),
            "Population statistics size matches population count.",
            "Population statistics size does not match population count.",
        )
    )

    for key in REQUIRED_GEOMETRY_KEYS:
        checks.append(
            _check(
                f"population_statistics_has_{key}",
                key in statistics,
                f"Population statistics include '{key}'.",
                f"Population statistics are missing '{key}'.",
            )
        )

    return checks


def audit_report_bundle(results):
    bundle = results.get("regen_candidate_population_report_bundle")
    report_text = results.get("regen_candidate_population_report")

    checks = [
        _check(
            "report_bundle_is_dict",
            isinstance(bundle, dict),
            "Population report bundle exists.",
            "Population report bundle is missing.",
        ),
        _check(
            "report_text_exists",
            isinstance(report_text, str) and bool(report_text.strip()),
            "Population report text exists.",
            "Population report text is missing.",
        ),
    ]

    if isinstance(bundle, dict):
        checks.extend([
            _check(
                "report_bundle_owner_correct",
                bundle.get("owner") == "REGEN_CANDIDATE_POPULATION_REPORT_OWNER",
                "Population report bundle owner is correct.",
                "Population report bundle owner is incorrect.",
            ),
            _check(
                "report_bundle_phase_correct",
                bundle.get("phase") == "11B.3B",
                "Population report bundle phase is correct.",
                "Population report bundle phase is incorrect.",
            ),
            _check(
                "report_bundle_complete",
                bundle.get("complete") is True,
                "Population report bundle is marked complete.",
                "Population report bundle is not marked complete.",
            ),
        ])

    return checks


def audit_registration(results):
    checks = []

    report_registry = results.get("regen_candidate_population_report_registry")
    viewer_registry = results.get("regen_candidate_population_viewer_registry")
    export_registry = results.get("regen_candidate_population_export_registry")
    registry_entry = results.get("regen_candidate_population_registry_entry")

    checks.extend([
        _check(
            "registry_entry_exists",
            isinstance(registry_entry, dict),
            "Population registry entry exists.",
            "Population registry entry is missing.",
        ),
        _check(
            "report_registry_exists",
            isinstance(report_registry, dict),
            "Population report registry exists.",
            "Population report registry is missing.",
        ),
        _check(
            "viewer_registry_exists",
            isinstance(viewer_registry, dict),
            "Population viewer registry exists.",
            "Population viewer registry is missing.",
        ),
        _check(
            "export_registry_exists",
            isinstance(export_registry, dict),
            "Population export registry exists.",
            "Population export registry is missing.",
        ),
    ])

    if isinstance(registry_entry, dict):
        checks.append(
            _check(
                "registry_entry_registered",
                registry_entry.get("registered") is True,
                "Population registry entry is registered.",
                "Population registry entry is not registered.",
            )
        )

    if isinstance(report_registry, dict):
        checks.append(
            _check(
                "report_registry_contains_population_report",
                "regen_candidate_population_report"
                in (report_registry.get("registered_report_keys") or []),
                "Report registry contains population report key.",
                "Report registry does not contain population report key.",
            )
        )

    if isinstance(viewer_registry, dict):
        checks.append(
            _check(
                "viewer_registry_contains_population_report",
                "regen_candidate_population_report"
                in (viewer_registry.get("viewer_report_keys") or []),
                "Viewer registry contains population report key.",
                "Viewer registry does not contain population report key.",
            )
        )

    if isinstance(export_registry, dict):
        checks.append(
            _check(
                "export_registry_contains_population_report",
                "regen_candidate_population_report"
                in (export_registry.get("export_report_keys") or []),
                "Export registry contains population report key.",
                "Export registry does not contain population report key.",
            )
        )

    return checks


def audit_safety_locks(results):
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


def build_completion_audit_report(status, passed, checks, failed_checks):
    lines = [
        "LEAF PHASE 11B.3D CANDIDATE POPULATION COMPLETION AUDIT",
        "========================================================",
        "",
        f"Owner: {OWNER_NAME}",
        f"Phase: {PHASE}",
        f"Status: {status}",
        f"Audit passed: {passed}",
        f"Total checks: {len(checks)}",
        f"Failed checks: {len(failed_checks)}",
        "",
        "Purpose:",
        "- Proves that the population generation, reporting, and registration stack is complete.",
        "- Blocks the master gate if required architecture is missing.",
        "- Keeps ranking, mutation, solving, and live commit locked.",
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
        "- 11B.3D proves the population subsystem is complete up to registration.",
        "- 11B.3E must still master-gate the subsystem before ranking is allowed.",
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
