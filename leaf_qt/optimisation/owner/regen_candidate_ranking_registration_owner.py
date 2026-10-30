"""
PHASE 11B.4D
Candidate Ranking Registration Owner

Responsibilities:
- Register the candidate ranking report bundle from 11B.4C.
- Expose ranking report keys for report viewers.
- Expose ranking export keys for export systems.
- Expose ranking registry entries for future optimisation/evolution systems.
- Do NOT audit final ranking completion.
- Do NOT master-gate ranking.
- Do NOT mutate candidates.
- Do NOT evolve generations.
- Do NOT solve candidates.
- Do NOT commit live geometry.
"""


OWNER_NAME = "REGEN_CANDIDATE_RANKING_REGISTRATION_OWNER"
PHASE = "11B.4D"

PASS_STATUS = "PASS_REGEN_CANDIDATE_RANKING_REGISTRATION_OWNER_PHASE_11B4D"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_RANKING_REGISTRATION_OWNER_PHASE_11B4D"

REPORT_KEY = "regen_candidate_ranking_report"
REPORT_BUNDLE_KEY = "regen_candidate_ranking_report_bundle"
EXPORT_BUNDLE_KEY = "regen_candidate_ranking_export_bundle"


def attach_regen_candidate_ranking_registration_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_ranking_registration_owner(results)
    results.update(payload)
    return results


def build_regen_candidate_ranking_registration_owner(results):
    blockers = []

    if results.get("phase_11b_4c_regen_candidate_ranking_report_owner_complete") is not True:
        blockers.append("Phase 11B.4C candidate ranking report owner is not complete.")

    if results.get("regen_candidate_ranking_report_owner_ready") is not True:
        blockers.append("Candidate ranking report owner is not ready.")

    report_bundle = results.get(REPORT_BUNDLE_KEY)

    if not isinstance(report_bundle, dict) or not report_bundle:
        blockers.append("Candidate ranking report bundle is missing or invalid.")
        report_bundle = {}

    export_bundle = results.get(EXPORT_BUNDLE_KEY)

    if not isinstance(export_bundle, dict) or not export_bundle:
        blockers.append("Candidate ranking export bundle is missing or invalid.")
        export_bundle = {}

    report_text = results.get("regen_candidate_ranking_report_text")

    if not isinstance(report_text, str) or not report_text.strip():
        blockers.append("Candidate ranking report text is missing or empty.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    registry_entry = build_ranking_registry_entry(
        ready=ready,
        blockers=blockers,
        report_bundle=report_bundle,
        export_bundle=export_bundle,
    )

    report_registry = build_ranking_report_registry(
        ready=ready,
        registry_entry=registry_entry,
    )

    viewer_registry = build_ranking_viewer_registry(
        ready=ready,
        registry_entry=registry_entry,
    )

    export_registry = build_ranking_export_registry(
        ready=ready,
        registry_entry=registry_entry,
        export_bundle=export_bundle,
    )

    optimisation_registry = build_future_optimisation_registry(
        ready=ready,
        registry_entry=registry_entry,
    )

    registration_report = build_ranking_registration_report(
        status=status,
        ready=ready,
        blockers=blockers,
        registry_entry=registry_entry,
        report_registry=report_registry,
        viewer_registry=viewer_registry,
        export_registry=export_registry,
        optimisation_registry=optimisation_registry,
    )

    return {
        "regen_candidate_ranking_registration_owner_complete": True,
        "phase_11b_4d_regen_candidate_ranking_registration_owner_complete": True,
        "regen_candidate_ranking_registration_ready": ready,
        "regen_candidate_ranking_registration_status": status,
        "regen_candidate_ranking_registration_blockers": blockers,

        "regen_candidate_ranking_registry_entry": registry_entry,
        "regen_candidate_ranking_report_registry": report_registry,
        "regen_candidate_ranking_viewer_registry": viewer_registry,
        "regen_candidate_ranking_export_registry": export_registry,
        "regen_candidate_ranking_future_optimisation_registry": optimisation_registry,
        "regen_candidate_ranking_registration_report": registration_report,

        "regen_candidate_ranking_registered_report_keys": (
            [REPORT_KEY] if ready else []
        ),
        "regen_candidate_ranking_registered_bundle_keys": (
            [REPORT_BUNDLE_KEY] if ready else []
        ),
        "regen_candidate_ranking_registered_export_keys": (
            ["regen_candidate_ranking_export"] if ready else []
        ),

        # Compatibility aliases.
        "regen_ranking_registration_owner_complete": True,
        "regen_ranking_registration_ready": ready,
        "regen_ranking_registration_status": status,
        "regen_ranking_registered_reports": report_registry,
        "regen_ranking_registered_viewer_bundles": viewer_registry,
        "regen_ranking_registered_export_bundles": export_registry,

        # Now registered.
        "regen_candidate_ranking_report_registered": ready,
        "regen_candidate_ranking_report_viewer_registered": ready,
        "regen_candidate_ranking_report_export_registered": ready,

        # Safety locks.
        "regen_candidate_ranking_registration_mutation_executed": False,
        "regen_candidate_ranking_registration_evolution_executed": False,
        "regen_candidate_ranking_registration_solver_executed": False,
        "regen_candidate_ranking_registration_live_commit_executed": False,
        "regen_candidate_ranking_registration_candidate_acceptance_executed": False,

        # Future phase permissions remain locked until audit + master gate.
        "regen_candidate_ranking_completion_audit_allowed": ready,
        "phase_11b_4e_candidate_ranking_completion_audit_allowed": ready,
        "regen_candidate_mutation_architecture_allowed": False,
        "regen_candidate_evolution_architecture_allowed": False,
    }


def build_ranking_registry_entry(
    ready,
    blockers,
    report_bundle,
    export_bundle,
):
    return {
        "registry_key": REPORT_KEY,
        "bundle_key": REPORT_BUNDLE_KEY,
        "export_key": export_bundle.get("export_key", "regen_candidate_ranking_export"),
        "title": "Regen Candidate Ranking Report",
        "owner": OWNER_NAME,
        "phase": PHASE,
        "registered": ready,
        "complete": True,
        "blockers": list(blockers),
        "source_report_owner": report_bundle.get("owner"),
        "source_report_phase": report_bundle.get("phase"),
        "source_report_status": report_bundle.get("status"),
        "objective": report_bundle.get("objective"),
        "best_candidate_id": report_bundle.get("best_candidate_id"),
        "ranked_candidate_count": report_bundle.get("ranked_candidate_count"),
        "viewer_visible": ready,
        "export_visible": ready,
        "future_optimisation_visible": ready,
        "report_bundle_available": bool(report_bundle),
        "export_bundle_available": bool(export_bundle),
        "ranking_registered": ready,
        "mutation_allowed": False,
        "evolution_allowed": False,
        "solver_allowed": False,
        "live_commit_allowed": False,
        "candidate_acceptance_allowed": False,
    }


def build_ranking_report_registry(ready, registry_entry):
    if not ready:
        return {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "registered_report_keys": [],
            "reports": {},
        }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "registered_report_keys": [REPORT_KEY],
        "reports": {
            REPORT_KEY: {
                "title": registry_entry.get("title"),
                "bundle_key": registry_entry.get("bundle_key"),
                "source_owner": registry_entry.get("source_report_owner"),
                "source_phase": registry_entry.get("source_report_phase"),
                "status": registry_entry.get("source_report_status"),
                "objective": registry_entry.get("objective"),
                "best_candidate_id": registry_entry.get("best_candidate_id"),
                "ranked_candidate_count": registry_entry.get("ranked_candidate_count"),
            }
        },
    }


def build_ranking_viewer_registry(ready, registry_entry):
    if not ready:
        return {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "viewer_report_keys": [],
            "viewer_sections": {},
        }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "viewer_report_keys": [REPORT_KEY],
        "viewer_sections": {
            REPORT_KEY: {
                "title": "Candidate Ranking",
                "display_type": "text_report",
                "report_key": REPORT_KEY,
                "bundle_key": REPORT_BUNDLE_KEY,
                "visible": True,
                "category": "Regen Ranking",
                "priority": 40,
            }
        },
    }


def build_ranking_export_registry(ready, registry_entry, export_bundle):
    if not ready:
        return {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "export_report_keys": [],
            "export_sections": {},
        }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "export_report_keys": [REPORT_KEY],
        "export_sections": {
            REPORT_KEY: {
                "title": "Regen Candidate Ranking Report",
                "formats": export_bundle.get("formats", ["txt", "json"]),
                "report_key": REPORT_KEY,
                "bundle_key": REPORT_BUNDLE_KEY,
                "export_key": registry_entry.get("export_key"),
                "exportable": True,
                "category": "regen_ranking",
            }
        },
    }


def build_future_optimisation_registry(ready, registry_entry):
    if not ready:
        return {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "optimisation_keys": [],
            "optimisation_sections": {},
        }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "optimisation_keys": [
            "ranked_population",
            "best_ranked_candidate",
            "ranking_statistics",
        ],
        "optimisation_sections": {
            "ranked_population": {
                "source_report_key": REPORT_KEY,
                "description": "Ranked candidate population prepared for future optimisation stages.",
                "available": True,
            },
            "best_ranked_candidate": {
                "source_report_key": REPORT_KEY,
                "description": "Best candidate selected by ranking owner.",
                "available": True,
            },
            "ranking_statistics": {
                "source_report_key": REPORT_KEY,
                "description": "Score statistics for ranked population.",
                "available": True,
            },
        },
    }


def build_ranking_registration_report(
    status,
    ready,
    blockers,
    registry_entry,
    report_registry,
    viewer_registry,
    export_registry,
    optimisation_registry,
):
    lines = [
        "LEAF PHASE 11B.4D CANDIDATE RANKING REGISTRATION OWNER",
        "=======================================================",
        "",
        f"Owner: {OWNER_NAME}",
        f"Phase: {PHASE}",
        f"Status: {status}",
        f"Registration ready: {ready}",
        "",
        "Purpose:",
        "- Registers candidate ranking reports into LEAF discovery systems.",
        "- Makes ranking output visible to report viewers and export systems.",
        "- Makes ranking output discoverable for future optimisation/evolution systems.",
        "- Does not audit final ranking completion or master-gate mutation.",
        "",
        "Blockers:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Registered Report Keys:",
    ])

    report_keys = report_registry.get("registered_report_keys") or []

    if report_keys:
        for key in report_keys:
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
        "Future Optimisation Keys:",
    ])

    optimisation_keys = optimisation_registry.get("optimisation_keys") or []

    if optimisation_keys:
        for key in optimisation_keys:
            lines.append(f"- {key}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Registry Entry:",
        f"- Registry key: {registry_entry.get('registry_key')}",
        f"- Bundle key: {registry_entry.get('bundle_key')}",
        f"- Export key: {registry_entry.get('export_key')}",
        f"- Objective: {registry_entry.get('objective')}",
        f"- Best candidate id: {registry_entry.get('best_candidate_id')}",
        f"- Ranked candidate count: {registry_entry.get('ranked_candidate_count')}",
        f"- Viewer visible: {registry_entry.get('viewer_visible')}",
        f"- Export visible: {registry_entry.get('export_visible')}",
        f"- Future optimisation visible: {registry_entry.get('future_optimisation_visible')}",
        "",
        "Safety Locks:",
        f"- Mutation allowed: {registry_entry.get('mutation_allowed')}",
        f"- Evolution allowed: {registry_entry.get('evolution_allowed')}",
        f"- Solver allowed: {registry_entry.get('solver_allowed')}",
        f"- Live commit allowed: {registry_entry.get('live_commit_allowed')}",
        f"- Candidate acceptance allowed: {registry_entry.get('candidate_acceptance_allowed')}",
        "",
        "Completion Meaning:",
        "- 11B.4D proves ranking output is registered.",
        "- 11B.4E must audit ranking completion.",
        "- 11B.4F must master-gate ranking before mutation architecture begins.",
    ])

    return "\n".join(lines)
