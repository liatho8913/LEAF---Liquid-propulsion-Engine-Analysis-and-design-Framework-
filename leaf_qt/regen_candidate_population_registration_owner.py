"""
PHASE 11B.3C
Candidate Population Registration Owner

Responsibilities:
- Register the population report bundle created by 11B.3B.
- Expose registered report keys.
- Expose registered viewer/export bundle entries.
- Preserve safety locks.
- Do NOT rank candidates.
- Do NOT mutate candidates.
- Do NOT solve candidates.
- Do NOT commit live geometry.
"""


OWNER_NAME = "REGEN_CANDIDATE_POPULATION_REGISTRATION_OWNER"
PHASE = "11B.3C"

POPULATION_REPORT_KEY = "regen_candidate_population_report"
POPULATION_BUNDLE_KEY = "regen_candidate_population_report_bundle"


def attach_regen_candidate_population_registration_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_population_registration_owner(results)
    results.update(payload)
    return results


def build_regen_candidate_population_registration_owner(results):
    blockers = []

    if not results.get("phase_11b_3a_regen_candidate_population_generation_owner_complete"):
        blockers.append("Phase 11B.3A population generation owner is not complete.")

    if not results.get("phase_11b_3b_regen_candidate_population_report_owner_complete"):
        blockers.append("Phase 11B.3B population report owner is not complete.")

    report_bundle = results.get(POPULATION_BUNDLE_KEY)

    if not isinstance(report_bundle, dict):
        blockers.append("Population report bundle is missing or invalid.")

    report_text = results.get(POPULATION_REPORT_KEY)

    if not isinstance(report_text, str) or not report_text.strip():
        blockers.append("Population report text is missing or empty.")

    registered = not blockers

    registry_entry = build_registry_entry(
        registered=registered,
        blockers=blockers,
        report_bundle=report_bundle if isinstance(report_bundle, dict) else {},
        report_text=report_text if isinstance(report_text, str) else "",
    )

    report_registry = build_report_registry(registry_entry)
    viewer_registry = build_viewer_registry(registry_entry)
    export_registry = build_export_registry(registry_entry)

    status = (
        "PASS_REGEN_CANDIDATE_POPULATION_REGISTRATION_OWNER_PHASE_11B3C"
        if registered
        else "FAIL_REGEN_CANDIDATE_POPULATION_REGISTRATION_OWNER_PHASE_11B3C"
    )

    registration_report = build_registration_report(
        status=status,
        registered=registered,
        blockers=blockers,
        registry_entry=registry_entry,
        report_registry=report_registry,
        viewer_registry=viewer_registry,
        export_registry=export_registry,
    )

    return {
        "regen_candidate_population_registration_owner_complete": True,
        "phase_11b_3c_regen_candidate_population_registration_owner_complete": True,
        "regen_candidate_population_registration_status": status,
        "regen_candidate_population_registration_ready": registered,
        "regen_candidate_population_registration_blockers": blockers,

        "regen_candidate_population_registered_report_keys": (
            [POPULATION_REPORT_KEY] if registered else []
        ),
        "regen_candidate_population_registered_bundle_keys": (
            [POPULATION_BUNDLE_KEY] if registered else []
        ),

        "regen_candidate_population_registry_entry": registry_entry,
        "regen_candidate_population_report_registry": report_registry,
        "regen_candidate_population_viewer_registry": viewer_registry,
        "regen_candidate_population_export_registry": export_registry,
        "regen_candidate_population_registration_report": registration_report,

        # Compatibility aliases for broader LEAF report discovery.
        "regen_population_registered_reports": report_registry,
        "regen_population_registered_viewer_bundles": viewer_registry,
        "regen_population_registered_export_bundles": export_registry,

        # Safety locks.
        "regen_candidate_population_registration_ranking_allowed": False,
        "regen_candidate_population_registration_mutation_allowed": False,
        "regen_candidate_population_registration_solver_allowed": False,
        "regen_candidate_population_registration_live_commit_allowed": False,
    }


def build_registry_entry(
    registered,
    blockers,
    report_bundle,
    report_text,
):
    return {
        "registry_key": POPULATION_REPORT_KEY,
        "bundle_key": POPULATION_BUNDLE_KEY,
        "title": "Regen Candidate Population Report",
        "owner": OWNER_NAME,
        "phase": PHASE,
        "registered": registered,
        "complete": True,
        "blockers": list(blockers),
        "report_owner": report_bundle.get("owner"),
        "report_phase": report_bundle.get("phase"),
        "report_status": report_bundle.get("status"),
        "report_text_available": bool(report_text.strip()),
        "population_count": report_bundle.get("population_count"),
        "seed_candidate_id": report_bundle.get("seed_candidate_id"),
        "viewer_visible": registered,
        "export_visible": registered,
        "report_bundle_available": bool(report_bundle),
        "ranking_allowed": False,
        "mutation_allowed": False,
        "candidate_solving_allowed": False,
        "live_commit_allowed": False,
    }


def build_report_registry(registry_entry):
    if not registry_entry.get("registered"):
        return {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "registered_report_keys": [],
            "reports": {},
        }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "registered_report_keys": [POPULATION_REPORT_KEY],
        "reports": {
            POPULATION_REPORT_KEY: {
                "title": registry_entry.get("title"),
                "bundle_key": registry_entry.get("bundle_key"),
                "source_owner": registry_entry.get("report_owner"),
                "source_phase": registry_entry.get("report_phase"),
                "status": registry_entry.get("report_status"),
                "population_count": registry_entry.get("population_count"),
                "seed_candidate_id": registry_entry.get("seed_candidate_id"),
            }
        },
    }


def build_viewer_registry(registry_entry):
    if not registry_entry.get("registered"):
        return {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "viewer_report_keys": [],
            "viewer_sections": {},
        }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "viewer_report_keys": [POPULATION_REPORT_KEY],
        "viewer_sections": {
            POPULATION_REPORT_KEY: {
                "title": "Candidate Population",
                "display_type": "text_report",
                "report_key": POPULATION_REPORT_KEY,
                "bundle_key": POPULATION_BUNDLE_KEY,
                "visible": True,
                "category": "Regen Population",
            }
        },
    }


def build_export_registry(registry_entry):
    if not registry_entry.get("registered"):
        return {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "export_report_keys": [],
            "export_sections": {},
        }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "export_report_keys": [POPULATION_REPORT_KEY],
        "export_sections": {
            POPULATION_REPORT_KEY: {
                "title": "Regen Candidate Population Report",
                "formats": ["txt", "json"],
                "report_key": POPULATION_REPORT_KEY,
                "bundle_key": POPULATION_BUNDLE_KEY,
                "exportable": True,
                "category": "regen_population",
            }
        },
    }


def build_registration_report(
    status,
    registered,
    blockers,
    registry_entry,
    report_registry,
    viewer_registry,
    export_registry,
):
    lines = [
        "LEAF PHASE 11B.3C CANDIDATE POPULATION REGISTRATION OWNER",
        "==========================================================",
        "",
        f"Owner: {OWNER_NAME}",
        f"Phase: {PHASE}",
        f"Status: {status}",
        f"Registered: {registered}",
        "",
        "Purpose:",
        "- Registers the regen candidate population report into LEAF discovery systems.",
        "- Makes the population report available to viewer and export architecture.",
        "- Keeps generated candidates non-ranked, non-mutated, non-solved, and non-committed.",
        "",
        "Registered Report Keys:",
    ]

    keys = report_registry.get("registered_report_keys") or []
    if keys:
        for key in keys:
            lines.append(f"- {key}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Viewer Report Keys:",
    ])

    viewer_keys = viewer_registry.get("viewer_report_keys") or []
    if viewer_keys:
        for key in viewer_keys:
            lines.append(f"- {key}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Export Report Keys:",
    ])

    export_keys = export_registry.get("export_report_keys") or []
    if export_keys:
        for key in export_keys:
            lines.append(f"- {key}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Blockers:",
    ])

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Registry Entry:",
        f"- Registry key: {registry_entry.get('registry_key')}",
        f"- Bundle key: {registry_entry.get('bundle_key')}",
        f"- Population count: {registry_entry.get('population_count')}",
        f"- Seed candidate id: {registry_entry.get('seed_candidate_id')}",
        f"- Viewer visible: {registry_entry.get('viewer_visible')}",
        f"- Export visible: {registry_entry.get('export_visible')}",
        "",
        "Safety Locks:",
        f"- Ranking allowed: {registry_entry.get('ranking_allowed')}",
        f"- Mutation allowed: {registry_entry.get('mutation_allowed')}",
        f"- Candidate solving allowed: {registry_entry.get('candidate_solving_allowed')}",
        f"- Live commit allowed: {registry_entry.get('live_commit_allowed')}",
        "",
        "Completion Meaning:",
        "- 11B.3C proves the population report is registered.",
        "- It does not prove completion audit readiness.",
        "- It does not prove master gate readiness.",
        "- Those are handled by 11B.3D and 11B.3E.",
    ])

    return "\n".join(lines)
