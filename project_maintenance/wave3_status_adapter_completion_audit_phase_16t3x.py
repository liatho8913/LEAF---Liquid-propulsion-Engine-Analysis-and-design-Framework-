from pathlib import Path

TARGETS = [
    {
        "phase": "16T.3W.1",
        "file": "leaf_qt/foundation_verification_harness.py",
        "tokens": [
            "phase_16t3w1_status_adapter_complete",
            "foundation_verification_harness_structured_findings",
            "foundation_verification_harness_global_status_payload",
            "foundation_verification_harness_adapter_report",
        ],
    },
    {
        "phase": "16T.3W.2",
        "file": "leaf_qt/engine_solver.py",
        "tokens": [
            "phase_16t3w2_status_adapter_complete",
            "phase_16t3w2_engine_solver_status_adapter_complete",
            "engine_solver_status_adapter_complete",
            "engine_solver_global_status_payload",
            "engine_solver_adapter_report",
        ],
    },
    {
        "phase": "16T.3W.3",
        "file": "leaf_qt/regen_system_signoff_validation_owner.py",
        "tokens": [
            "phase_16t3w3_status_adapter_complete",
            "regen_system_signoff_validation_owner_structured_findings",
            "regen_system_signoff_validation_owner_global_status_payload",
            "regen_system_signoff_validation_owner_adapter_report",
        ],
    },
    {
        "phase": "16T.3W.4",
        "file": "leaf_qt/regen_completion_gate_validation_owner.py",
        "tokens": [
            "phase_16t3w4_status_adapter_complete",
            "regen_completion_gate_validation_owner_structured_findings",
            "regen_completion_gate_validation_owner_global_status_payload",
            "regen_completion_gate_validation_owner_adapter_report",
        ],
    },
    {
        "phase": "16T.3W.5",
        "file": "leaf_qt/regen_cross_section_viewer.py",
        "tokens": [
            "phase_16t3w5_status_adapter_complete",
            "attach_regen_cross_section_viewer_status_adapter",
            "regen_cross_section_viewer_structured_findings",
            "regen_cross_section_viewer_global_status_payload",
            "regen_cross_section_viewer_adapter_report",
        ],
    },
    {
        "phase": "16T.3W.6",
        "file": "leaf_qt/regen_validation_master_gate.py",
        "tokens": [
            "phase_16t3w6_status_adapter_complete",
            "phase_16t3w6_regen_validation_master_gate_status_adapter_complete",
            "regen_validation_master_gate_status_adapter_complete",
            "regen_validation_master_gate_adapter_report",
        ],
    },
    {
        "phase": "16T.3W.7",
        "file": "leaf_qt/regen_unified_validation_integration_master_gate.py",
        "tokens": [
            "phase_16t3w7_status_adapter_complete",
            "regen_unified_validation_integration_master_gate_structured_findings",
            "regen_unified_validation_integration_master_gate_global_status_payload",
            "regen_unified_validation_integration_master_gate_adapter_report",
        ],
    },
    {
        "phase": "16T.3W.8",
        "file": "leaf_qt/regen_generation_validation_master_gate.py",
        "tokens": [
            "phase_16t3w8_status_adapter_complete",
            "regen_generation_validation_master_gate_structured_findings",
            "regen_generation_validation_master_gate_global_status_payload",
            "regen_generation_validation_master_gate_adapter_report",
        ],
    },
]

TESTS = [
    "project_maintenance/test_foundation_verification_harness_status_adapter_phase_16t3w1.py",
    "project_maintenance/test_engine_solver_status_adapter_phase_16t3w2.py",
    "project_maintenance/test_regen_system_signoff_validation_owner_phase_16t3w3.py",
    "project_maintenance/test_regen_completion_gate_validation_owner_phase_16t3w4.py",
    "project_maintenance/test_regen_cross_section_viewer_status_adapter_phase_16t3w5.py",
    "project_maintenance/test_regen_validation_master_gate_phase_16t3w6.py",
    "project_maintenance/test_regen_unified_validation_integration_master_gate_phase_16t3w7.py",
    "project_maintenance/test_regen_generation_validation_master_gate_phase_16t3w8.py",
]


def main():
    findings = []
    passed = True

    print("LEAF PHASE 16T.3X")
    print("WAVE 3 STATUS ADAPTER COMPLETION AUDIT")
    print("======================================")
    print()

    for target in TARGETS:
        path = Path(target["file"])
        exists = path.exists()
        missing = []

        if not exists:
            passed = False
            missing = target["tokens"]
        else:
            text = path.read_text(errors="replace")
            missing = [token for token in target["tokens"] if token not in text]
            if missing:
                passed = False

        status = "PASS" if exists and not missing else "FAIL"
        print(f"{target['phase']} | {target['file']} | {status}")

        if missing:
            for token in missing:
                print(f"  MISSING: {token}")

        findings.append({
            "phase": target["phase"],
            "file": target["file"],
            "exists": exists,
            "missing_tokens": missing,
            "passed": exists and not missing,
        })

    print()
    print("REGRESSION TEST FILE AUDIT")
    print("--------------------------")

    for test in TESTS:
        path = Path(test)
        exists = path.exists()
        status = "PASS" if exists else "FAIL"
        if not exists:
            passed = False
        print(f"{test} | {status}")

    print()
    print("SUMMARY")
    print("-------")
    print(f"wave3_target_count: {len(TARGETS)}")
    print(f"wave3_test_count: {len(TESTS)}")
    print(f"wave3_completion_audit_passed: {passed}")

    if not passed:
        raise SystemExit("FAIL_PHASE_16T3X_WAVE3_STATUS_ADAPTER_COMPLETION_AUDIT")

    print("PASS_PHASE_16T3X_WAVE3_STATUS_ADAPTER_COMPLETION_AUDIT")


if __name__ == "__main__":
    main()
