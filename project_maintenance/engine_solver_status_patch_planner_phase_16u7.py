from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


PHASE = "16U.7"
PASS_BANNER = "PASS_PHASE_16U7_ENGINE_SOLVER_STATUS_PATCH_PLANNER"

IN_JSON = Path("project_maintenance/engine_solver_status_consumer_integration_audit_phase_16u6.json")
OUT_JSON = Path("project_maintenance/engine_solver_status_patch_planner_phase_16u7.json")
OUT_TXT = Path("project_maintenance/ENGINE_SOLVER_STATUS_PATCH_PLANNER_PHASE_16U7.txt")


@dataclass(frozen=True)
class PatchPlanItem:
    file: str
    line: int
    migration_group: str
    risk: str
    current_snippet: str
    proposed_snippet: str
    wrapper_imports_required: tuple[str, ...]
    patch_batch: str
    regression_required: bool
    reason: str


def propose_patch(snippet: str, migration_group: str) -> tuple[str, tuple[str, ...]]:
    s = snippet.strip()

    replacements = [
        ('results.get("coupled_split_auto_tuned_status") != "PASS"', 'not solver_pass(results.get("coupled_split_auto_tuned_status"))'),
        ('results.get("coupled_split_auto_tuned_status") == "PASS"', 'solver_pass(results.get("coupled_split_auto_tuned_status"))'),
        ('results.get("velocity_limited_combined_preview_status") == "FAIL"', 'solver_fail(results.get("velocity_limited_combined_preview_status"))'),
        ('results.get("coupled_split_strategy_status") == "FAIL"', 'solver_fail(results.get("coupled_split_strategy_status"))'),
        ('results.get("vl_split_strategy_status") == "PASS"', 'solver_pass(results.get("vl_split_strategy_status"))'),
        ('results.get("bond_coat_validation_status") != "PASS"', 'not solver_pass(results.get("bond_coat_validation_status"))'),
        ('source_data_gate != "PASS"', 'not solver_pass(source_data_gate)'),
        ('weighted_gate != "PASS"', 'not solver_pass(weighted_gate)'),
        ('results.get("explicit_coating_thermal_stress_status") == "FAIL"', 'solver_fail(results.get("explicit_coating_thermal_stress_status"))'),
        ('results.get("coating_stack_adhesion_risk_status") != "PASS"', 'not solver_pass(results.get("coating_stack_adhesion_risk_status"))'),
        ('results.get("coating_stack_spallation_fatigue_status") != "PASS"', 'not solver_pass(results.get("coating_stack_spallation_fatigue_status"))'),
        ('results.get("coating_stack_source_data_gate") != "PASS"', 'not solver_pass(results.get("coating_stack_source_data_gate"))'),
        ('source_gate != "PASS"', 'not solver_pass(source_gate)'),
        ('bond_status != "PASS"', 'not solver_pass(bond_status)'),
        ('thermal_stress_status != "PASS"', 'not solver_pass(thermal_stress_status)'),
        ('adhesion_status != "PASS"', 'not solver_pass(adhesion_status)'),
        ('fatigue_status != "PASS"', 'not solver_pass(fatigue_status)'),
        ('preview_status != "PASS"', 'not solver_pass(preview_status)'),
        ('combined_status != "PASS"', 'not solver_pass(combined_status)'),
        ('viability == "PASS"', 'solver_pass(viability)'),
        ('item.get("status") == "PASS"', 'solver_pass(item.get("status"))'),
        ('item["status"] != "FAIL"', 'not solver_fail(item.get("status"))'),
        ('status != "FAIL"', 'not solver_fail(status)'),
        ('candidate_report.get("status") == "PASS"', 'solver_pass(candidate_report.get("status"))'),
    ]

    proposed = s
    for old, new in replacements:
        proposed = proposed.replace(old, new)

    wrappers = []
    if "solver_pass(" in proposed:
        wrappers.append("solver_pass")
    if "solver_fail(" in proposed:
        wrappers.append("solver_fail")

    return proposed, tuple(sorted(set(wrappers)))


def build_engine_solver_status_patch_planner() -> dict:
    if not IN_JSON.exists():
        raise FileNotFoundError(f"Missing {IN_JSON}. Run Phase 16U.6 first.")

    source = json.loads(IN_JSON.read_text(encoding="utf-8"))
    low_risk = source.get("low_risk_candidates", [])

    deduped: dict[tuple[str, int, str], dict] = {}
    for item in low_risk:
        key = (item.get("file", ""), int(item.get("line", 0)), item.get("snippet", "").strip())
        deduped[key] = item

    patch_items: list[PatchPlanItem] = []

    for item in deduped.values():
        snippet = item.get("snippet", "").strip()
        proposed, imports = propose_patch(snippet, item.get("migration_group", ""))

        patch_items.append(
            PatchPlanItem(
                file=item.get("file", ""),
                line=int(item.get("line", 0)),
                migration_group=item.get("migration_group", ""),
                risk=item.get("risk", ""),
                current_snippet=snippet,
                proposed_snippet=proposed,
                wrapper_imports_required=imports,
                patch_batch="A1_LOW_RISK_EQUALITY_INEQUALITY",
                regression_required=True,
                reason=item.get("reason", ""),
            )
        )

    patch_items = sorted(patch_items, key=lambda p: (p.file, p.line, p.current_snippet))

    by_file: dict[str, int] = {}
    wrappers_required: set[str] = set()
    unchanged_proposals = []

    for item in patch_items:
        by_file[item.file] = by_file.get(item.file, 0) + 1
        wrappers_required.update(item.wrapper_imports_required)
        if item.current_snippet == item.proposed_snippet:
            unchanged_proposals.append(asdict(item))

    payload = {
        "phase": PHASE,
        "status": PASS_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "source_audit_status": source.get("status"),
        "source_low_risk_count": len(low_risk),
        "unique_patch_item_count": len(patch_items),
        "by_file": dict(sorted(by_file.items())),
        "wrappers_required": sorted(wrappers_required),
        "unchanged_proposal_count": len(unchanged_proposals),
        "unchanged_proposals": unchanged_proposals,
        "patch_plan": [asdict(item) for item in patch_items],
        "phase_16u7_engine_solver_status_patch_planner_complete": True,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.7",
        "ENGINE SOLVER STATUS PATCH PLANNER",
        "====================================",
        "",
        f"STATUS: {PASS_BANNER}",
        f"Generated: {payload['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase creates a deterministic patch plan.",
        "No production files are modified.",
        "No solver equations are modified.",
        "",
        "SUMMARY",
        "-------",
        f"Source low-risk findings: {payload['source_low_risk_count']}",
        f"Unique patch items: {payload['unique_patch_item_count']}",
        f"Unchanged proposals requiring manual review: {payload['unchanged_proposal_count']}",
        f"Wrappers required: {', '.join(payload['wrappers_required'])}",
        "",
        "PATCH ITEMS BY FILE",
        "-------------------",
    ]

    for file, count in payload["by_file"].items():
        lines.append(f"{file}: {count}")

    lines.extend(["", "PATCH PLAN", "----------"])
    for item in patch_items:
        lines.append(f"{item.file}:{item.line} [{item.migration_group}]")
        lines.append(f"  current:  {item.current_snippet}")
        lines.append(f"  proposed: {item.proposed_snippet}")
        lines.append(f"  imports:  {', '.join(item.wrapper_imports_required) or 'none'}")
        lines.append(f"  batch:    {item.patch_batch}")
        lines.append("")

    lines.extend(
        [
            "NEXT PHASE",
            "----------",
            "PHASE 16U.8 — ENGINE SOLVER LOW-RISK STATUS WRAPPER PATCH",
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.7 COMPLETE.",
            "The low-risk solver status patch plan is ready.",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = build_engine_solver_status_patch_planner()
    print(result["status"])
    print(f"source_low_risk_count={result['source_low_risk_count']}")
    print(f"unique_patch_item_count={result['unique_patch_item_count']}")
    print(f"unchanged_proposal_count={result['unchanged_proposal_count']}")
    print(f"wrappers_required={result['wrappers_required']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
