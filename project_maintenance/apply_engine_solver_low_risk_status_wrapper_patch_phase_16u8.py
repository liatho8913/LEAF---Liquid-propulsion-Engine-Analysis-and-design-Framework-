from __future__ import annotations

import json
import py_compile
from datetime import datetime
from pathlib import Path


PHASE = "16U.8"
PASS_BANNER = "PASS_PHASE_16U8_ENGINE_SOLVER_LOW_RISK_STATUS_WRAPPER_PATCH"

PLAN_JSON = Path("project_maintenance/engine_solver_status_patch_planner_phase_16u7.json")
OUT_JSON = Path("project_maintenance/engine_solver_low_risk_status_wrapper_patch_phase_16u8.json")
OUT_TXT = Path("project_maintenance/ENGINE_SOLVER_LOW_RISK_STATUS_WRAPPER_PATCH_PHASE_16U8.txt")

ENGINE = Path("leaf_qt/engine_solver.py")
GEOMETRY_SOLVER = Path("leaf_qt/regen_geometry_solver.py")


ENGINE_IMPORT = "from leaf_qt.solver_status_access import solver_fail, solver_pass\n"
GEOMETRY_IMPORT = "from leaf_qt.solver_status_access import solver_pass as status_solver_pass\n"


ENGINE_REPLACEMENTS = [
    ('if results.get("coupled_split_auto_tuned_status") != "PASS":',
     'if not solver_pass(results.get("coupled_split_auto_tuned_status")):'),

    ('passing = [item for item in screened if item["status"] != "FAIL"]',
     'passing = [item for item in screened if not solver_fail(item.get("status"))]'),

    ('if status != "FAIL":',
     'if not solver_fail(status):'),

    ('if item.get("status") == "PASS"',
     'if solver_pass(item.get("status"))'),

    ('if thermal_stress_failed_count > 0 and results.get("bond_coat_validation_status") != "PASS":',
     'if thermal_stress_failed_count > 0 and not solver_pass(results.get("bond_coat_validation_status")):'),

    ('if source_data_gate != "PASS":',
     'if not solver_pass(source_data_gate):'),

    ('if weighted_gate != "PASS":',
     'if not solver_pass(weighted_gate):'),

    ('if results.get("explicit_coating_thermal_stress_status") == "FAIL":',
     'if solver_fail(results.get("explicit_coating_thermal_stress_status")):'),

    ('if results.get("coating_stack_adhesion_risk_status") != "PASS":',
     'if not solver_pass(results.get("coating_stack_adhesion_risk_status")):'),

    ('if results.get("coating_stack_spallation_fatigue_status") != "PASS":',
     'if not solver_pass(results.get("coating_stack_spallation_fatigue_status")):'),

    ('if results.get("coating_stack_source_data_gate") != "PASS":',
     'if not solver_pass(results.get("coating_stack_source_data_gate")):'),

    ('if data_mode != "SOURCED_VALIDATION_MODE" or source_gate != "PASS":',
     'if data_mode != "SOURCED_VALIDATION_MODE" or not solver_pass(source_gate):'),

    ('if bond_status != "PASS":',
     'if not solver_pass(bond_status):'),

    ('if thermal_stress_status != "PASS":',
     'if not solver_pass(thermal_stress_status):'),

    ('if adhesion_status != "PASS":',
     'if not solver_pass(adhesion_status):'),

    ('if fatigue_status != "PASS":',
     'if not solver_pass(fatigue_status):'),

    ('if source_gate != "PASS" and final_acceptance == "VALIDATION_SUPPORT_ALLOWED":',
     'if not solver_pass(source_gate) and final_acceptance == "VALIDATION_SUPPORT_ALLOWED":'),

    ('if preview_status != "PASS":',
     'if not solver_pass(preview_status):'),

    ('if feasibility == "REGEN_ONLY_FEASIBLE" and viability == "PASS":',
     'if feasibility == "REGEN_ONLY_FEASIBLE" and solver_pass(viability):'),

    ('if results.get("coupled_split_auto_tuned_status") == "PASS":',
     'if solver_pass(results.get("coupled_split_auto_tuned_status")):'),

    ('if combined_status != "PASS":',
     'if not solver_pass(combined_status):'),

    ('if results.get("velocity_limited_combined_preview_status") == "FAIL":',
     'if solver_fail(results.get("velocity_limited_combined_preview_status")):'),

    ('if results.get("coupled_split_strategy_status") == "FAIL":',
     'if solver_fail(results.get("coupled_split_strategy_status")):'),

    ('if results.get("vl_split_strategy_status") == "PASS":',
     'if solver_pass(results.get("vl_split_strategy_status")):'),
]


GEOMETRY_REPLACEMENTS = [
    ('solver_pass = candidate_report.get("status") == "PASS" and best_candidate is not None',
     'solver_pass = status_solver_pass(candidate_report.get("status")) and best_candidate is not None'),
]


def insert_import(text: str, import_line: str) -> tuple[str, bool]:
    if import_line.strip() in text:
        return text, False

    lines = text.splitlines(keepends=True)

    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1

    for idx, line in enumerate(lines):
        if line.startswith("from __future__ import"):
            insert_at = idx + 1

    while insert_at < len(lines) and lines[insert_at].strip() == "":
        insert_at += 1

    lines.insert(insert_at, import_line)
    return "".join(lines), True


def apply_replacements(path: Path, replacements: list[tuple[str, str]], import_line: str) -> dict:
    original = path.read_text(encoding="utf-8", errors="replace")
    text, import_added = insert_import(original, import_line)

    applied = []
    missing = []
    already_applied = []

    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
            applied.append({"old": old, "new": new})
        elif new in text:
            already_applied.append({"old": old, "new": new})
        else:
            missing.append({"old": old, "new": new})

    changed = text != original
    if changed:
        backup = path.with_suffix(path.suffix + ".phase_16u8_backup")
        if not backup.exists():
            backup.write_text(original, encoding="utf-8")
        path.write_text(text, encoding="utf-8")

    return {
        "file": str(path),
        "import_added": import_added,
        "applied_count": len(applied),
        "already_applied_count": len(already_applied),
        "missing_count": len(missing),
        "applied": applied,
        "already_applied": already_applied,
        "missing": missing,
        "changed": changed,
    }


def compile_file(path: Path) -> dict:
    try:
        py_compile.compile(str(path), doraise=True)
        return {"file": str(path), "compiled": True, "error": ""}
    except Exception as exc:
        return {"file": str(path), "compiled": False, "error": repr(exc)}


def run_patch() -> dict:
    if not PLAN_JSON.exists():
        raise FileNotFoundError(f"Missing {PLAN_JSON}. Run Phase 16U.7 first.")

    plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))

    engine_result = apply_replacements(ENGINE, ENGINE_REPLACEMENTS, ENGINE_IMPORT)
    geometry_result = apply_replacements(GEOMETRY_SOLVER, GEOMETRY_REPLACEMENTS, GEOMETRY_IMPORT)

    compile_results = [compile_file(ENGINE), compile_file(GEOMETRY_SOLVER)]

    engine_text = ENGINE.read_text(encoding="utf-8", errors="replace")
    geometry_text = GEOMETRY_SOLVER.read_text(encoding="utf-8", errors="replace")

    alias_conflict_present = "solver_pass = solver_pass(" in geometry_text

    passed = (
        plan.get("status") == "PASS_PHASE_16U7_ENGINE_SOLVER_STATUS_PATCH_PLANNER"
        and engine_result["missing_count"] == 0
        and geometry_result["missing_count"] == 0
        and all(item["compiled"] for item in compile_results)
        and ENGINE_IMPORT.strip() in engine_text
        and GEOMETRY_IMPORT.strip() in geometry_text
        and not alias_conflict_present
    )

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U8_ENGINE_SOLVER_LOW_RISK_STATUS_WRAPPER_PATCH",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "plan_status": plan.get("status"),
        "engine_result": engine_result,
        "geometry_result": geometry_result,
        "compile_results": compile_results,
        "alias_conflict_present": alias_conflict_present,
        "phase_16u8_engine_solver_low_risk_status_wrapper_patch_complete": passed,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.8",
        "ENGINE SOLVER LOW-RISK STATUS WRAPPER PATCH",
        "============================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase patches only low-risk Wave A solver status consumers.",
        "No solver equations are changed.",
        "No numerical calculations are changed.",
        "",
        "FILES MODIFIED",
        "--------------",
        "leaf_qt/engine_solver.py",
        "leaf_qt/regen_geometry_solver.py",
        "",
        "SUMMARY",
        "-------",
        f"engine_solver applied: {engine_result['applied_count']}",
        f"engine_solver already applied: {engine_result['already_applied_count']}",
        f"engine_solver missing: {engine_result['missing_count']}",
        f"regen_geometry_solver applied: {geometry_result['applied_count']}",
        f"regen_geometry_solver already applied: {geometry_result['already_applied_count']}",
        f"regen_geometry_solver missing: {geometry_result['missing_count']}",
        f"alias conflict present: {alias_conflict_present}",
        "",
        "COMPILE RESULTS",
        "---------------",
    ]

    for item in compile_results:
        lines.append(f"{item['file']}: {'PASS' if item['compiled'] else 'FAIL'} {item['error']}")

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.8 COMPLETE." if passed else "PHASE 16U.8 FAILED.",
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.9 — ENGINE SOLVER LOW-RISK STATUS WRAPPER REGRESSION",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run_patch()
    print(result["status"])
    print(f"engine_applied={result['engine_result']['applied_count']}")
    print(f"engine_missing={result['engine_result']['missing_count']}")
    print(f"geometry_applied={result['geometry_result']['applied_count']}")
    print(f"geometry_missing={result['geometry_result']['missing_count']}")
    print(f"alias_conflict_present={result['alias_conflict_present']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
    if not result["phase_16u8_engine_solver_low_risk_status_wrapper_patch_complete"]:
        raise SystemExit(1)
