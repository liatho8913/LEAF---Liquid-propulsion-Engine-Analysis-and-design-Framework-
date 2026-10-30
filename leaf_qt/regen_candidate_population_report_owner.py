"""
PHASE 11B.3B
Candidate Population Report Owner

Responsibilities:
- Consume population payload from Phase 11B.3A.
- Build a dedicated foundation-compliant report.
- Expose report ownership metadata.
- Keep reports separate from scalar outputs.
- Do NOT rank candidates.
- Do NOT mutate candidates.
- Do NOT solve candidates.
- Do NOT commit live geometry.
"""


REPORT_KEY = "regen_candidate_population_report"
REPORT_TITLE = "Regen Candidate Population Report"
OWNER_NAME = "REGEN_CANDIDATE_POPULATION_REPORT_OWNER"
PHASE = "11B.3B"


def attach_regen_candidate_population_report_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_population_report_owner(results)
    results.update(payload)
    return results


def build_regen_candidate_population_report_owner(results):
    population_ready = bool(results.get("regen_candidate_population_generation_ready"))
    population = results.get("regen_candidate_population") or []
    seed = results.get("regen_candidate_population_seed") or {}
    statistics = results.get("regen_candidate_population_statistics") or {}
    blockers = list(results.get("regen_candidate_population_generation_blockers") or [])

    report_blockers = []

    if not results.get("phase_11b_3a_regen_candidate_population_generation_owner_complete"):
        report_blockers.append(
            "Phase 11B.3A population generation owner is not complete."
        )

    if not population_ready:
        report_blockers.append(
            "Population generation is not ready; report is generated in blocked state."
        )

    if not isinstance(population, list):
        report_blockers.append("Population payload is not a list.")
        population = []

    report_text = build_population_report_text(
        population_ready=population_ready,
        seed=seed,
        population=population,
        statistics=statistics,
        generation_blockers=blockers,
        report_blockers=report_blockers,
        results=results,
    )

    report_bundle = {
        "report_key": REPORT_KEY,
        "report_title": REPORT_TITLE,
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": (
            "PASS_REGEN_CANDIDATE_POPULATION_REPORT_OWNER_PHASE_11B3B"
            if not report_blockers
            else "WARN_REGEN_CANDIDATE_POPULATION_REPORT_OWNER_PHASE_11B3B"
        ),
        "complete": True,
        "population_ready": population_ready,
        "population_count": len(population),
        "seed_candidate_id": seed.get("seed_candidate_id"),
        "blockers": report_blockers,
        "text": report_text,
        "architecture": {
            "generation_owner_required": True,
            "report_owner_complete": True,
            "registration_owner_complete": False,
            "completion_audit_complete": False,
            "master_gate_complete": False,
            "ranking_allowed": False,
            "mutation_allowed": False,
            "candidate_solving_allowed": False,
            "live_commit_allowed": False,
        },
    }

    return {
        "regen_candidate_population_report_owner_complete": True,
        "phase_11b_3b_regen_candidate_population_report_owner_complete": True,
        "regen_candidate_population_report_owner_status": report_bundle["status"],
        "regen_candidate_population_report_owner_blockers": report_blockers,
        "regen_candidate_population_report_bundle": report_bundle,
        "regen_candidate_population_report": report_text,

        # Safety locks
        "regen_candidate_population_report_ranking_allowed": False,
        "regen_candidate_population_report_mutation_allowed": False,
        "regen_candidate_population_report_solver_allowed": False,
        "regen_candidate_population_report_live_commit_allowed": False,
    }


def build_population_report_text(
    population_ready,
    seed,
    population,
    statistics,
    generation_blockers,
    report_blockers,
    results,
):
    lines = [
        "LEAF PHASE 11B.3B CANDIDATE POPULATION REPORT OWNER",
        "====================================================",
        "",
        f"Owner: {OWNER_NAME}",
        f"Phase: {PHASE}",
        "",
        "Purpose:",
        "- Owns reporting for generated regen candidate populations.",
        "- Converts raw generated population data into an auditable report.",
        "- Keeps population details out of the main scalar output table.",
        "",
        "Architecture State:",
        f"- Population generation ready: {population_ready}",
        f"- Report owner complete: True",
        "- Registration owner complete: False",
        "- Completion audit complete: False",
        "- Master gate complete: False",
        "- Ranking allowed: False",
        "- Mutation allowed: False",
        "- Candidate solving allowed: False",
        "- Live geometry commit allowed: False",
        "",
        "Seed Candidate:",
        f"- Seed candidate id: {seed.get('seed_candidate_id')}",
        f"- Seed source: {seed.get('seed_source')}",
        "",
        "Population Summary:",
        f"- Population count: {len(population)}",
        f"- Candidate IDs: {', '.join(_candidate_ids(population)) if population else 'None'}",
        "",
        "Generation Blockers:",
    ]

    if generation_blockers:
        for blocker in generation_blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Report Blockers:",
    ])

    if report_blockers:
        for blocker in report_blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Population Statistics:",
    ])

    if statistics:
        for key, value in statistics.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Candidate Geometry Table:",
        "candidate_id | reason | Nch | width_m | height_m | rib_m | wall_m | coolant_fraction",
        "-------------|--------|-----|---------|----------|-------|--------|-----------------",
    ])

    if population:
        for candidate in population:
            geometry = candidate.get("candidate_geometry") or {}
            lines.append(
                f"{candidate.get('candidate_id')} | "
                f"{candidate.get('candidate_reason')} | "
                f"{geometry.get('number_of_coolant_channels')} | "
                f"{geometry.get('coolant_channel_width')} | "
                f"{geometry.get('coolant_channel_height')} | "
                f"{geometry.get('rib_width')} | "
                f"{geometry.get('hot_gas_wall_thickness')} | "
                f"{geometry.get('coolant_flow_fraction')}"
            )
    else:
        lines.append("None | None | None | None | None | None | None | None")

    lines.extend([
        "",
        "Safety Locks:",
        f"- Solver executed: {bool(results.get('regen_candidate_population_solver_executed'))}",
        f"- Ranking executed: {bool(results.get('regen_candidate_population_ranking_executed'))}",
        f"- Mutation executed: {bool(results.get('regen_candidate_population_mutation_executed'))}",
        f"- Live geometry modified: {bool(results.get('regen_candidate_population_live_geometry_modified'))}",
        f"- Candidate committed: {bool(results.get('regen_candidate_population_candidate_committed'))}",
        "",
        "Completion Meaning:",
        "- This phase proves that generated populations are report-owned.",
        "- It does not prove registration, completion audit, or master gate readiness.",
        "- Those are covered by 11B.3C, 11B.3D, and 11B.3E.",
    ])

    return "\n".join(lines)


def _candidate_ids(population):
    ids = []

    for candidate in population:
        if isinstance(candidate, dict):
            ids.append(str(candidate.get("candidate_id")))

    return ids
