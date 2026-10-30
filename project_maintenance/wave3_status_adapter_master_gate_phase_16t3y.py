from pathlib import Path
import subprocess
import sys

COMPLETION_AUDIT = Path(
    "project_maintenance/wave3_status_adapter_completion_audit_phase_16t3x.py"
)

REQUIRED_PHASES = [
    "16T.3W.1",
    "16T.3W.2",
    "16T.3W.3",
    "16T.3W.4",
    "16T.3W.5",
    "16T.3W.6",
    "16T.3W.7",
    "16T.3W.8",
]

TARGET_TOKENS = [
    ("leaf_qt/foundation_verification_harness.py", "phase_16t3w1_status_adapter_complete"),
    ("leaf_qt/engine_solver.py", "phase_16t3w2_status_adapter_complete"),
    ("leaf_qt/regen_system_signoff_validation_owner.py", "phase_16t3w3_status_adapter_complete"),
    ("leaf_qt/regen_completion_gate_validation_owner.py", "phase_16t3w4_status_adapter_complete"),
    ("leaf_qt/regen_cross_section_viewer.py", "phase_16t3w5_status_adapter_complete"),
    ("leaf_qt/regen_validation_master_gate.py", "phase_16t3w6_status_adapter_complete"),
    ("leaf_qt/regen_unified_validation_integration_master_gate.py", "phase_16t3w7_status_adapter_complete"),
    ("leaf_qt/regen_generation_validation_master_gate.py", "phase_16t3w8_status_adapter_complete"),
]


def run_completion_audit():
    if not COMPLETION_AUDIT.exists():
        return False, "Completion audit file missing."

    completed = subprocess.run(
        [sys.executable, str(COMPLETION_AUDIT)],
        text=True,
        capture_output=True,
    )

    output = (completed.stdout or "") + (completed.stderr or "")

    if completed.returncode != 0:
        return False, output

    if "PASS_PHASE_16T3X_WAVE3_STATUS_ADAPTER_COMPLETION_AUDIT" not in output:
        return False, output

    return True, output


def main():
    print("LEAF PHASE 16T.3Y")
    print("WAVE 3 STATUS ADAPTER MASTER GATE")
    print("=================================")
    print()

    findings = []
    passed = True

    audit_passed, audit_output = run_completion_audit()
    print("completion_audit_passed:", audit_passed)

    if not audit_passed:
        passed = False
        findings.append("Completion audit did not pass.")

    print()
    print("TARGET TOKEN CHECK")
    print("------------------")

    for file_name, token in TARGET_TOKENS:
        path = Path(file_name)
        exists = path.exists()
        token_present = exists and token in path.read_text(errors="replace")

        status = "PASS" if exists and token_present else "FAIL"
        print(f"{file_name} | {token} | {status}")

        if not exists:
            passed = False
            findings.append(f"Missing file: {file_name}")
        elif not token_present:
            passed = False
            findings.append(f"Missing token {token} in {file_name}")

    print()
    print("MASTER GATE SUMMARY")
    print("-------------------")
    print(f"required_phase_count: {len(REQUIRED_PHASES)}")
    print(f"target_token_count: {len(TARGET_TOKENS)}")
    print(f"master_gate_passed: {passed}")

    if findings:
        print()
        print("FINDINGS")
        print("--------")
        for item in findings:
            print("-", item)

    if not passed:
        raise SystemExit("FAIL_PHASE_16T3Y_WAVE3_STATUS_ADAPTER_MASTER_GATE")

    print("PASS_PHASE_16T3Y_WAVE3_STATUS_ADAPTER_MASTER_GATE")


if __name__ == "__main__":
    main()
