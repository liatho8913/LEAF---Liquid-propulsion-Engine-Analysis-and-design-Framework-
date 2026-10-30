from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


WAVE2_MODULES = [
    {
        "phase": "16T.3Q.1",
        "name": "Regen Geometry Master Gate",
        "source": "leaf_qt/regen_geometry_master_gate.py",
        "required": [
            "phase_16t3q1_status_adapter_complete",
            "structured_findings",
            "global_status",
            "global_status_payload",
            "adapter_report",
        ],
    },
    {
        "phase": "16T.3Q.2",
        "name": "Regen Candidate Population Master Gate",
        "source": "leaf_qt/regen_candidate_population_master_gate.py",
        "required": [
            "phase_16t3q2_status_adapter_complete",
            "structured_findings",
            "global_status",
            "global_status_payload",
            "adapter_report",
        ],
    },
    {
        "phase": "16T.3Q.3",
        "name": "Regen Candidate Ranking Master Gate",
        "source": "leaf_qt/regen_candidate_ranking_master_gate.py",
        "required": [
            "phase_16t3q3_status_adapter_complete",
            "structured_findings",
            "global_status",
            "global_status_payload",
            "adapter_report",
        ],
    },
    {
        "phase": "16T.3Q.4",
        "name": "Regen Evolution Loop Master Gate",
        "source": "leaf_qt/regen_evolution_loop_master_gate.py",
        "required": [
            "phase_16t3q4_status_adapter_complete",
            "structured_findings",
            "global_status",
            "global_status_payload",
            "adapter_report",
        ],
    },
    {
        "phase": "16T.3Q.5",
        "name": "Regen Candidate Mutation Master Gate",
        "source": "leaf_qt/regen_candidate_mutation_master_gate.py",
        "required": [
            "phase_16t3q5_status_adapter_complete",
            "structured_findings",
            "global_status",
            "global_status_payload",
            "adapter_report",
        ],
    },
    {
        "phase": "16T.3Q.6",
        "name": "Regen Optimisation Master Gate",
        "source": "leaf_qt/regen_optimisation_master_gate.py",
        "required": [
            "phase_16t3q6_status_adapter_complete",
            "structured_findings",
            "global_status",
            "global_status_payload",
            "adapter_report",
        ],
    },
    {
        "phase": "16T.3Q.7",
        "name": "Regen Scalability Master Gate",
        "source": "leaf_qt/regen_scalability_master_gate.py",
        "required": [
            "phase_16t3q7_status_adapter_complete",
            "structured_findings",
            "global_status",
            "global_status_payload",
            "adapter_report",
        ],
    },
    {
        "phase": "16T.3Q.8",
        "name": "Regen Candidate Validator",
        "source": "leaf_qt/regen_candidate_validator.py",
        "required": [
            "phase_16t3q8_status_adapter_complete",
            "structured_findings",
            "global_status",
            "global_status_payload",
            "adapter_report",
        ],
    },
    {
        "phase": "16T.3Q.9",
        "name": "Regen Source Validation Gate",
        "source": "leaf_qt/regen_source_validation_gate.py",
        "required": [
            "phase_16t3q9_status_adapter_complete",
            "structured_findings",
            "global_status",
            "global_status_payload",
            "adapter_report",
        ],
    },
    {
        "phase": "16T.3Q.10",
        "name": "Regen Axial Geometry Master Gate",
        "source": "project_maintenance/production_historical_artifacts/leaf_qt/regen_axial_geometry_master_gate.py",
        "required": [
            "phase_16t3q10_status_adapter_complete",
            "structured_findings",
            "global_status",
            "global_status_payload",
            "adapter_report",
        ],
    },
    {
        "phase": "16T.3Q.11",
        "name": "Regen Candidate Acceptance Master Gate",
        "source": "leaf_qt/regen_candidate_acceptance_master_gate.py",
        "required": [
            "phase_16t3q11_status_adapter_complete",
            "structured_findings",
            "global_status",
            "global_status_payload",
            "adapter_report",
        ],
    },
    {
        "phase": "16T.3Q.12",
        "name": "Regen Variable Geometry Master Gate",
        "source": "project_maintenance/production_historical_artifacts/leaf_qt/regen_variable_geometry_master_gate.py",
        "required": [
            "phase_16t3q12_status_adapter_complete",
            "structured_findings",
            "global_status",
            "global_status_payload",
            "adapter_report",
        ],
    },
]


TEST_HINTS = [
    "project_maintenance/test_regen_candidate_ranking_status_adapter_phase_16t3q3.py",
    "project_maintenance/test_regen_evolution_loop_status_adapter_phase_16t3q4.py",
    "project_maintenance/test_regen_candidate_mutation_status_adapter_phase_16t3q5.py",
    "project_maintenance/test_regen_optimisation_status_adapter_phase_16t3q6.py",
    "project_maintenance/test_regen_scalability_status_adapter_phase_16t3q7.py",
    "project_maintenance/test_regen_candidate_validator_status_adapter_phase_16t3q8.py",
    "project_maintenance/test_regen_source_validation_gate_status_adapter_phase_16t3q9.py",
    "project_maintenance/test_regen_axial_geometry_status_adapter_phase_16t3q10.py",
    "project_maintenance/test_regen_candidate_acceptance_status_adapter_phase_16t3q11.py",
    "project_maintenance/test_regen_variable_geometry_status_adapter_phase_16t3q12.py",
]


def audit_module(item):
    path = ROOT / item["source"]
    result = {
        "phase": item["phase"],
        "name": item["name"],
        "source": item["source"],
        "source_exists": path.exists(),
        "missing_required": [],
        "passed": False,
    }

    if not path.exists():
        result["missing_required"] = list(item["required"])
        return result

    text = path.read_text(errors="replace")
    result["missing_required"] = [
        token for token in item["required"]
        if token not in text
    ]
    result["passed"] = not result["missing_required"]
    return result


def run_wave2_status_adapter_completion_audit():
    module_results = [audit_module(item) for item in WAVE2_MODULES]

    tests = []
    for hint in TEST_HINTS:
        path = ROOT / hint
        tests.append(
            {
                "path": hint,
                "exists": path.exists(),
            }
        )

    missing_modules = [r for r in module_results if not r["source_exists"]]
    failed_modules = [r for r in module_results if not r["passed"]]
    missing_tests = [t for t in tests if not t["exists"]]

    passed = (
        len(module_results) == 12
        and not missing_modules
        and not failed_modules
    )

    status = (
        "PASS_WAVE2_STATUS_ADAPTER_COMPLETION_AUDIT_PHASE_16T3R"
        if passed
        else "FAIL_WAVE2_STATUS_ADAPTER_COMPLETION_AUDIT_PHASE_16T3R"
    )

    report_lines = [
        "LEAF PHASE 16T.3R",
        "WAVE 2 STATUS ADAPTER COMPLETION AUDIT",
        "======================================",
        "",
        f"Status: {status}",
        f"Modules audited: {len(module_results)} / 12",
        f"Modules passed: {sum(1 for r in module_results if r['passed'])} / 12",
        f"Missing source files: {len(missing_modules)}",
        f"Modules with missing adapter tokens: {len(failed_modules)}",
        f"Focused test files present: {sum(1 for t in tests if t['exists'])} / {len(tests)}",
        "",
        "Module Results:",
    ]

    for r in module_results:
        outcome = "PASS" if r["passed"] else "FAIL"
        report_lines.append(f"- {outcome} | {r['phase']} | {r['name']} | {r['source']}")
        if r["missing_required"]:
            for token in r["missing_required"]:
                report_lines.append(f"    missing: {token}")

    report_lines.extend(["", "Focused Test Files:"])

    for t in tests:
        outcome = "PRESENT" if t["exists"] else "MISSING"
        report_lines.append(f"- {outcome} | {t['path']}")

    report = "\n".join(report_lines)

    return {
        "phase": "16T.3R",
        "status": status,
        "passed": passed,
        "module_count": len(module_results),
        "module_pass_count": sum(1 for r in module_results if r["passed"]),
        "missing_source_files": missing_modules,
        "failed_modules": failed_modules,
        "missing_focused_tests": missing_tests,
        "module_results": module_results,
        "test_results": tests,
        "report": report,
    }


if __name__ == "__main__":
    result = run_wave2_status_adapter_completion_audit()
    print(result["report"])
    if not result["passed"]:
        raise SystemExit(1)
