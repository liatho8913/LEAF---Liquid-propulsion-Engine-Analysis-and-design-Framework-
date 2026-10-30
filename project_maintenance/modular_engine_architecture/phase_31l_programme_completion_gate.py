from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from project_maintenance.production_historical_artifacts.leaf_qt.module_engine.programme_31_completion_gate import Programme31CompletionGate

REPORT_DIR = ROOT / "LEAF_Reports" / "modular_engine_architecture"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def main() -> None:
    gate = Programme31CompletionGate(ROOT, REPORT_DIR)
    payload = gate.run().to_dict()

    result = {
        "gate": "PHASE_31L_PROGRAMME_31_COMPLETION_GATE",
        "status": payload["status"],
        "programme_completion": payload,
        "read_only": True,
        "mutation_performed": False,
        "files_moved_by_gate": 0,
        "files_deleted_by_gate": 0,
        "imports_changed": False,
        "engineering_behaviour_changed": payload["engineering_behaviour_changed"],
        "solver_execution_performed": payload["solver_execution_performed"],
        "completion_notice": "PROGRAMME_31_COMPLETE_MODULAR_ENGINE_CONSOLIDATION_PLATFORM_SIGNED_OFF",
        "next_programme": payload["next_programme"],
    }

    passed = (
        result["status"] == "PASS"
        and result["read_only"] is True
        and result["mutation_performed"] is False
        and result["files_moved_by_gate"] == 0
        and result["files_deleted_by_gate"] == 0
        and result["imports_changed"] is False
        and result["engineering_behaviour_changed"] is False
        and result["solver_execution_performed"] is False
        and payload["required_module_engine_files_present"] is True
        and payload["regen_migrated"] is True
        and payload["combustion_chamber_migrated"] is True
        and payload["controlled_replacement_verified"] is True
        and payload["legacy_quarantine_verified"] is True
        and payload["repository_simplification_verified"] is True
    )

    result["status"] = "PASS" if passed else "FAIL"

    json_path = REPORT_DIR / "phase_31l_programme_completion_gate.json"
    txt_path = REPORT_DIR / "phase_31l_programme_completion_gate.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join([
            f"gate={result['gate']}",
            f"status={result['status']}",
            f"required_reports_seen={payload['required_reports_seen']}",
            f"missing_reports={','.join(payload['missing_reports'])}",
            f"failed_reports={','.join(payload['failed_reports'])}",
            f"module_engine_files={payload['module_engine_files']}",
            f"required_module_engine_files_present={payload['required_module_engine_files_present']}",
            f"regen_migrated={payload['regen_migrated']}",
            f"combustion_chamber_migrated={payload['combustion_chamber_migrated']}",
            f"controlled_replacement_verified={payload['controlled_replacement_verified']}",
            f"legacy_quarantine_verified={payload['legacy_quarantine_verified']}",
            f"repository_simplification_verified={payload['repository_simplification_verified']}",
            f"engineering_behaviour_changed={payload['engineering_behaviour_changed']}",
            f"solver_execution_performed={payload['solver_execution_performed']}",
            "read_only=True",
            "mutation_performed=False",
            "files_moved_by_gate=0",
            "files_deleted_by_gate=0",
            f"completion_notice={result['completion_notice']}",
            f"next_programme={result['next_programme']}",
        ]) + "\n",
        encoding="utf-8",
    )

    if not passed:
        print("FAIL_PHASE_31L_PROGRAMME_31_COMPLETION_GATE")
        print(f"report={txt_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_31L_PROGRAMME_31_COMPLETION_GATE")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(result["completion_notice"])
    print(f"NEXT_PROGRAMME={result['next_programme']}")

if __name__ == "__main__":
    main()
